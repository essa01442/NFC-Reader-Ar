"""Tests for nfc_utils.py – ATR parsing, card-type detection, and NDEF parsing."""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nfc_utils import (
    parse_atr,
    refine_with_cc,
    parse_ndef_from_type2_memory,
    _parse_ndef_message,
    _decode_record,
)


# ---------------------------------------------------------------------------
# ATR parsing tests
# ---------------------------------------------------------------------------

class TestParseAtr:
    # ATR for NXP MIFARE Classic 1K (bytes 13-14 = 00 01)
    MIFARE_1K_ATR = [
        0x3B, 0x8F, 0x80, 0x01, 0x80, 0x4F, 0x0C, 0xA0,
        0x00, 0x00, 0x03, 0x06, 0x03, 0x00, 0x01, 0x00,
        0x00, 0x00, 0x00, 0x6A,
    ]

    # ATR for NXP MIFARE Ultralight / NTAG (bytes 13-14 = 00 26)
    ULTRALIGHT_ATR = [
        0x3B, 0x8F, 0x80, 0x01, 0x80, 0x4F, 0x0C, 0xA0,
        0x00, 0x00, 0x03, 0x06, 0x03, 0x00, 0x26, 0x00,
        0x00, 0x00, 0x00, 0x4A,
    ]

    def test_mifare_1k_detected(self):
        info = parse_atr(self.MIFARE_1K_ATR)
        assert info['tag_type'] == 'NXP MIFARE Classic 1K'
        assert info['atqa'] == '0x0004'
        assert info['sak'] == '0x08'
        assert info['memory_bytes'] == 1024
        assert info['page_size'] == 16

    def test_ultralight_detected(self):
        info = parse_atr(self.ULTRALIGHT_ATR)
        assert info['tag_type'] == 'NXP MIFARE Ultralight'
        assert info['atqa'] == '0x0044'
        assert info['sak'] == '0x00'
        assert info['data_format'] == 'NFC Forum Type 2'
        assert info['page_size'] == 4

    def test_empty_atr_returns_empty_dict(self):
        assert parse_atr([]) == {}
        assert parse_atr(None) == {}

    def test_short_atr_returns_empty_dict(self):
        assert parse_atr([0x3B, 0x8F]) == {}

    def test_unknown_atr_returns_tag_type_string(self):
        unknown_atr = list(self.MIFARE_1K_ATR)
        unknown_atr[13] = 0x99
        unknown_atr[14] = 0x99
        info = parse_atr(unknown_atr)
        assert 'Unknown' in info['tag_type']


# ---------------------------------------------------------------------------
# CC-based refinement (NTAG identification)
# ---------------------------------------------------------------------------

class TestRefineWithCC:
    # First 16 bytes of NTAG215 memory (pages 0-3)
    # Page 3 = CC = E1 10 6D 00
    NTAG215_PAGES_0_3 = [
        0x04, 0x82, 0x3E, 0x01,   # page 0: UID[0-2] + BCC0
        0x2A, 0x4D, 0x03, 0xFE,   # page 1: UID[3-6]
        0x48, 0x00, 0x00, 0x00,   # page 2: BCC1 + LOCK
        0xE1, 0x10, 0x6D, 0x00,   # page 3: CC
    ]

    BASE_ULTRALIGHT_INFO = {
        'tag_type': 'NXP MIFARE Ultralight',
        'memory_bytes': 64,
        'memory_pages': 16,
        'page_size': 4,
        'data_format': 'NFC Forum Type 2',
        'atqa': '0x0044',
        'sak': '0x00',
    }

    def test_ntag215_identified(self):
        info = refine_with_cc(self.BASE_ULTRALIGHT_INFO, self.NTAG215_PAGES_0_3)
        assert info['tag_type'] == 'NXP NTAG215'
        assert info['memory_bytes'] == 540
        assert info['memory_pages'] == 135
        assert info['ndef_available'] == 492
        assert 'Ndef' in info['technologies']

    def test_no_ndef_magic_unchanged(self):
        pages = list(self.NTAG215_PAGES_0_3)
        pages[12] = 0x00  # corrupt NDEF magic
        info = refine_with_cc(self.BASE_ULTRALIGHT_INFO, pages)
        assert info['tag_type'] == 'NXP MIFARE Ultralight'  # unchanged

    def test_too_short_data_unchanged(self):
        info = refine_with_cc(self.BASE_ULTRALIGHT_INFO, [0x01, 0x02])
        assert info['tag_type'] == 'NXP MIFARE Ultralight'

    def test_ntag213_cc(self):
        pages = list(self.NTAG215_PAGES_0_3)
        pages[14] = 0x12   # NTAG213 CC[2]
        info = refine_with_cc(self.BASE_ULTRALIGHT_INFO, pages)
        assert info['tag_type'] == 'NXP NTAG213'
        assert info['memory_bytes'] == 180


# ---------------------------------------------------------------------------
# NDEF parsing tests
# ---------------------------------------------------------------------------

class TestParseNdefFromMemory:
    def _make_memory(self, ndef_msg_bytes, start_page=4, total_pages=16):
        """Build a fake tag memory with NDEF TLV at start_page."""
        mem = bytearray(total_pages * 4)
        offset = start_page * 4
        # Write NDEF TLV: type=03, length=N, data..., terminator=FE
        mem[offset] = 0x03
        mem[offset + 1] = len(ndef_msg_bytes)
        for i, b in enumerate(ndef_msg_bytes):
            mem[offset + 2 + i] = b
        mem[offset + 2 + len(ndef_msg_bytes)] = 0xFE
        return bytes(mem)

    def _make_text_ndef(self, text, lang='en'):
        """Build a raw NDEF Text record message."""
        lang_bytes = lang.encode('ascii')
        text_bytes = text.encode('utf-8')
        status = len(lang_bytes)   # UTF-8, language code length
        payload = bytes([status]) + lang_bytes + text_bytes
        # NDEF record: MB=1 ME=1 SR=1 IL=0 TNF=0x01, type_length=1, payload_length=N
        header = 0b11010001  # MB=1, ME=1, SR=1, TNF=1
        return bytes([header, 1, len(payload), ord('T')]) + payload

    def test_empty_memory_returns_no_records(self):
        mem = bytes(64)
        assert parse_ndef_from_type2_memory(mem) == []

    def test_text_record_decoded(self):
        msg = self._make_text_ndef('Hello NFC', lang='en')
        mem = self._make_memory(msg)
        records = parse_ndef_from_type2_memory(mem, start_page=4)
        assert len(records) == 1
        assert records[0]['content'] == 'Hello NFC'
        assert 'UTF-8' in records[0]['record_type']
        assert records[0].get('language') == 'en'

    def test_arabic_text_record(self):
        arabic_text = 'مرحبا'
        msg = self._make_text_ndef(arabic_text, lang='ar')
        mem = self._make_memory(msg)
        records = parse_ndef_from_type2_memory(mem, start_page=4)
        assert len(records) == 1
        assert records[0]['content'] == arabic_text

    def test_uri_record_decoded(self):
        # Build URI record: TNF=1, type='U', prefix=0x03 (http://)
        payload = bytes([0x03]) + b'example.com/test'
        header = 0b11010001  # MB=1 ME=1 SR=1 TNF=1
        msg = bytes([header, 1, len(payload), ord('U')]) + payload
        mem = self._make_memory(msg)
        records = parse_ndef_from_type2_memory(mem, start_page=4)
        assert len(records) == 1
        assert records[0]['record_type'] == 'URI'
        assert 'http://' in records[0]['content']
        assert 'example.com/test' in records[0]['content']

    def test_terminator_tlv_stops_parsing(self):
        mem = bytearray(64)
        # FE at page 4 byte 0 → terminator immediately
        mem[16] = 0xFE
        records = parse_ndef_from_type2_memory(bytes(mem), start_page=4)
        assert records == []

    def test_null_tlv_skipped(self):
        mem = bytearray(128)
        # NULL TLVs before NDEF TLV
        msg = self._make_text_ndef('Test')
        offset = 4 * 4  # page 4
        mem[offset] = 0x00   # NULL TLV
        mem[offset + 1] = 0x00
        mem[offset + 2] = 0x03
        mem[offset + 3] = len(msg)
        for i, b in enumerate(msg):
            mem[offset + 4 + i] = b
        mem[offset + 4 + len(msg)] = 0xFE
        records = parse_ndef_from_type2_memory(bytes(mem), start_page=4)
        assert len(records) == 1

    def test_list_input_accepted(self):
        msg = self._make_text_ndef('List input')
        mem = list(self._make_memory(msg))
        records = parse_ndef_from_type2_memory(mem, start_page=4)
        assert len(records) == 1


# ---------------------------------------------------------------------------
# _decode_record unit tests
# ---------------------------------------------------------------------------

class TestDecodeRecord:
    def test_text_record(self):
        lang = b'en'
        text = 'Hello'
        payload = bytes([len(lang)]) + lang + text.encode('utf-8')
        rec = _decode_record(0x01, b'T', payload)
        assert rec['content'] == 'Hello'
        assert rec.get('language') == 'en'

    def test_uri_with_prefix(self):
        payload = bytes([0x04]) + b'example.com'  # 0x04 = https://
        rec = _decode_record(0x01, b'U', payload)
        assert rec['content'] == 'https://example.com'

    def test_uri_no_prefix(self):
        payload = bytes([0x00]) + b'custom:data'  # 0x00 = no prefix
        rec = _decode_record(0x01, b'U', payload)
        assert rec['content'] == 'custom:data'

    def test_mime_record(self):
        rec = _decode_record(0x02, b'text/plain', b'Hello MIME')
        assert 'MIME' in rec['record_type']
        assert rec['content'] == 'Hello MIME'

    def test_unknown_tnf(self):
        rec = _decode_record(0x07, b'X', b'\x01\x02')
        assert 'Unknown' in rec['record_type']


# ---------------------------------------------------------------------------
# reader.py _collect_card_info integration smoke test
# ---------------------------------------------------------------------------

class TestCollectCardInfo:
    """Smoke-tests for NFCReaderManager._collect_card_info using mocks."""

    def _make_manager(self):
        from unittest.mock import Mock, patch
        with patch('reader.CardMonitor'), patch('reader.ReaderMonitor'), \
             patch('reader._WatchdogThread'):
            from reader import NFCReaderManager
            manager = NFCReaderManager()
        return manager

    def test_collect_info_with_ntag_connection(self):
        from unittest.mock import Mock
        manager = self._make_manager()

        # Simulate NTAG215 ATR
        ntag215_atr = [
            0x3B, 0x8F, 0x80, 0x01, 0x80, 0x4F, 0x0C, 0xA0,
            0x00, 0x00, 0x03, 0x06, 0x03, 0x00, 0x26, 0x00,
            0x00, 0x00, 0x00, 0x4A,
        ]

        # Build a 16-page (64-byte) fake NTAG memory with NDEF CC at page 3
        # and a text record "Test" at page 4
        ntag215_cc = [0xE1, 0x10, 0x6D, 0x00]
        text_payload = bytes([2]) + b'en' + b'Test'
        ndef_msg = bytes([0b11010001, 1, len(text_payload), ord('T')]) + text_payload
        ndef_tlv = bytes([0x03, len(ndef_msg)]) + ndef_msg + bytes([0xFE])

        mem = bytearray(540)  # 135 pages × 4 bytes
        # Page 3: CC
        mem[12:16] = ntag215_cc
        # Page 4+: NDEF TLV
        for i, b in enumerate(ndef_tlv):
            mem[16 + i] = b

        conn_mock = Mock()
        conn_mock.getATR.return_value = ntag215_atr

        # First transmit call (UID) was handled outside; here getATR is used.
        # _read_all_pages_type2 calls transmit repeatedly; return 16 bytes each time.
        read_responses = []
        page = 0
        while page < 135:
            chunk = list(mem[page * 4: page * 4 + 16])
            read_responses.append((chunk, 0x90, 0x00))
            page += 4
        conn_mock.transmit.side_effect = read_responses

        manager.connection = conn_mock

        uid_data = [0x04, 0x82, 0x3E, 0x01, 0x2A, 0x4D, 0x03]
        info = manager._collect_card_info(uid_data)

        assert info['uid_formatted'] == '04:82:3E:01:2A:4D:03'
        assert info['tag_type'] == 'NXP NTAG215'
        assert info['atqa'] == '0x0044'
        assert info['memory_bytes'] == 540
        assert len(info['ndef_records']) == 1
        assert info['ndef_records'][0]['content'] == 'Test'

    def test_collect_info_graceful_on_connection_error(self):
        from unittest.mock import Mock
        manager = self._make_manager()

        conn_mock = Mock()
        conn_mock.getATR.side_effect = Exception("connection lost")
        conn_mock.transmit.side_effect = Exception("transmit failed")
        manager.connection = conn_mock

        uid_data = [0x04, 0x11, 0x22]
        info = manager._collect_card_info(uid_data)

        # Should return a dict with defaults, not raise
        assert isinstance(info, dict)
        assert info['uid_formatted'] == '04:11:22'
        assert info['ndef_records'] == []
