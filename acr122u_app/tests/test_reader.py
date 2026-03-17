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
    # Mock CardMonitor and threading to prevent background execution during tests
    with patch('reader.CardMonitor'), patch('threading.Thread'):
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
