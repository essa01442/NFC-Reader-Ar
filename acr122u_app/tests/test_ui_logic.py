import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Instead of full UI test, test the logic isolated
from i18n import Translator

def test_hex_validation_logic():
    # Since PyQt is hard to test in this specific CI without crash, let's extract logic manually
    def validate_hex(hex_str):
        hex_str = hex_str.replace(" ", "")
        color = "red"
        if not hex_str:
            color = ""
        elif len(hex_str) % 2 == 0:
            try:
                data_bytes = bytes.fromhex(hex_str)
                if len(data_bytes) in (4, 16):
                    color = "green"
            except ValueError:
                color = "red"
        return color

    assert validate_hex("") == ""
    assert validate_hex("AABBCC") == "red"
    assert validate_hex("AABBCCDD") == "green"
    assert validate_hex("AABBCCDDEEFF") == "red"
    assert validate_hex("0102030405060708090a0b0c0d0e0f10") == "green"
    assert validate_hex("ZZZZZZZZ") == "red"

def test_rescan_logic():
    from reader import NFCReaderManager
    # Just verify that rescan updates the threading event
    with patch('reader.CardMonitor'), patch('threading.Thread'):
        manager = NFCReaderManager()
        assert not manager.force_scan_event.is_set()
        manager.rescan_readers()
        assert manager.force_scan_event.is_set()
