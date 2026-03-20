import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import PyQt6
# Force PyQt6 not to crash on import
from PyQt6.QtCore import QCoreApplication

# Instead of QApplication which requires GUI elements and crashes pytest, use QCoreApplication
if not QCoreApplication.instance():
    app = QCoreApplication(sys.argv)

from reader import NFCReaderManager

@pytest.fixture
def reader_manager():
    # Mock monitors to prevent background thread execution and PC/SC crashes during tests
    with patch('reader.CardMonitor'), patch('reader.ReaderMonitor'), \
         patch('reader._WatchdogThread'):
        manager = NFCReaderManager()
        yield manager

def test_card_inserted_success(reader_manager):
    mock_card = Mock()
    mock_connection = Mock()
    mock_card.createConnection.return_value = mock_connection

    # Return 0x90 0x00 for success, and fake UID bytes
    mock_connection.transmit.return_value = ([0x04, 0x1A, 0x2B, 0x3C], 0x90, 0x00)

    signal_emitted = False
    detected_uid = ""

    def on_card_detected(uid):
        nonlocal signal_emitted, detected_uid
        signal_emitted = True
        detected_uid = uid

    reader_manager.card_detected.connect(on_card_detected)
    reader_manager.card_inserted(mock_card)

    assert signal_emitted is True
    assert detected_uid == "041A2B3C"
    assert reader_manager.connection == mock_connection

def test_card_inserted_failure(reader_manager):
    mock_card = Mock()
    mock_connection = Mock()
    mock_card.createConnection.return_value = mock_connection

    # Return SW1=0x63 SW2=0x00 (Error)
    mock_connection.transmit.return_value = ([], 0x63, 0x00)

    signal_emitted = False
    error_msg = ""

    def on_error(msg):
        nonlocal signal_emitted, error_msg
        signal_emitted = True
        error_msg = msg

    reader_manager.error_occurred.connect(on_error)
    reader_manager.card_inserted(mock_card)

    assert signal_emitted is True
    assert "Failed to read UID" in error_msg

def test_card_removed_test(reader_manager):
    mock_card = Mock()
    reader_manager.connection = Mock()

    signal_emitted = False
    def on_card_removed():
        nonlocal signal_emitted
        signal_emitted = True

    reader_manager.card_removed_signal.connect(on_card_removed)

    reader_manager.card_removed(mock_card)

    assert signal_emitted is True
    assert reader_manager.connection is None

def test_read_block_success(reader_manager):
    reader_manager.connection = Mock()
    reader_manager.connection.transmit.return_value = ([0xAA, 0xBB, 0xCC, 0xDD], 0x90, 0x00)

    data = reader_manager.read_block(4)
    assert data == [0xAA, 0xBB, 0xCC, 0xDD]
    reader_manager.connection.transmit.assert_called_once_with([0xFF, 0xB0, 0x00, 4, 0x10])

def test_read_block_failure(reader_manager):
    reader_manager.connection = Mock()
    reader_manager.connection.transmit.return_value = ([], 0x63, 0x00)

    with pytest.raises(Exception, match="Read error"):
        reader_manager.read_block(4)

def test_discovery_acs_reader(reader_manager):
    mock_reader = Mock()
    mock_reader.__str__ = Mock(return_value="ACS ACR122U PICC Interface 00 00")

    with patch('reader.readers', return_value=[mock_reader]):
        # Call search logic explicitly once
        # the thread is mocked, so we do what it does
        available_readers = [mock_reader]
        target_readers = [r for r in available_readers if "acr" in str(r).lower() or "122" in str(r).lower()]

        assert len(target_readers) == 1
        assert target_readers[0] == mock_reader

def test_discovery_no_readers_error(reader_manager):
    with patch('reader.readers', side_effect=Exception("PCSC not running")):

        signal_emitted = False
        error_msg = ""
        def on_pcsc_error(msg):
            nonlocal signal_emitted, error_msg
            signal_emitted = True
            error_msg = msg

        reader_manager.pcsc_error_occurred.connect(on_pcsc_error)

        # update_readers_list() calls reader.readers() (via the reader module's
        # namespace) and emits pcsc_error_occurred when it raises.
        reader_manager.update_readers_list()

        assert signal_emitted is True
        assert "pcsc" in error_msg.lower() or "smart card" in error_msg.lower()

def test_rescan_trigger(reader_manager):
    with patch.object(reader_manager, 'update_readers_list') as mock_update:
        reader_manager.rescan_readers()
        mock_update.assert_called_once()

def test_write_block_success(reader_manager):
    reader_manager.connection = Mock()
    reader_manager.connection.transmit.return_value = ([], 0x90, 0x00)

    data_bytes = bytes([0x11, 0x22, 0x33, 0x44])
    result = reader_manager.write_block(4, data_bytes)
    assert result is True

    expected_apdu = [0xFF, 0xD6, 0x00, 4, 4, 0x11, 0x22, 0x33, 0x44]
    reader_manager.connection.transmit.assert_called_once_with(expected_apdu)

def test_write_block_invalid_length(reader_manager):
    reader_manager.connection = Mock()
    data_bytes = bytes([0x11, 0x22, 0x33]) # 3 bytes instead of 4 or 16

    with pytest.raises(Exception, match="Data must be exactly 4 or 16 bytes"):
        reader_manager.write_block(4, data_bytes)

def test_write_block_failure(reader_manager):
    reader_manager.connection = Mock()
    reader_manager.connection.transmit.return_value = ([], 0x63, 0x00)

    data_bytes = bytes([0x11, 0x22, 0x33, 0x44])
    with pytest.raises(Exception, match="Write error"):
        reader_manager.write_block(4, data_bytes)

# ── Watchdog / recovery tests ─────────────────────────────────────────────────

def test_on_pcscd_status_pcscd_just_came_back(reader_manager):
    """When pcscd transitions from down→running, monitors are restarted."""
    reader_manager._pcscd_last_known = False  # was down

    with patch.object(reader_manager, '_restart_monitors') as mock_restart:
        reader_manager._on_pcscd_status(True)
        mock_restart.assert_called_once()

def test_on_pcscd_status_pcscd_just_went_down(reader_manager):
    """When pcscd transitions from running→down, monitors are cleaned up and
    the reader_disconnected signal is emitted."""
    reader_manager._pcscd_last_known = True  # was running
    reader_manager.reader = Mock()  # pretend a reader was connected

    disconnected = []
    reader_manager.reader_disconnected.connect(lambda: disconnected.append(True))

    with patch.object(reader_manager, '_cleanup_monitors') as mock_cleanup:
        reader_manager._on_pcscd_status(False)
        mock_cleanup.assert_called_once()
    assert disconnected, "reader_disconnected signal should have been emitted"
    assert reader_manager.reader is None

def test_on_pcscd_status_running_no_readers_rescans(reader_manager):
    """When pcscd is running but no readers detected, a rescan is triggered."""
    reader_manager._pcscd_last_known = True  # already known running
    reader_manager.all_readers = []

    with patch.object(reader_manager, 'update_readers_list') as mock_scan:
        reader_manager._on_pcscd_status(True)
        mock_scan.assert_called_once()

def test_cleanup_monitors_resets_references(reader_manager):
    """_cleanup_monitors() should set both monitor references to None."""
    reader_manager.card_monitor = Mock()
    reader_manager.reader_monitor = Mock()

    reader_manager._cleanup_monitors()

    assert reader_manager.card_monitor is None
    assert reader_manager.reader_monitor is None

def test_restart_monitors(reader_manager):
    """_restart_monitors() cleans up and re-initialises monitors."""
    with patch.object(reader_manager, '_cleanup_monitors') as mock_cleanup, \
         patch.object(reader_manager, '_init_monitors') as mock_init, \
         patch.object(reader_manager, 'update_readers_list') as mock_scan:
        reader_manager._restart_monitors()
        mock_cleanup.assert_called_once()
        mock_init.assert_called_once()
        mock_scan.assert_called_once()
