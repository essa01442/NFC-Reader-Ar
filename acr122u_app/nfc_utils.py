"""NFC utility functions: card type detection, ATR parsing, and NDEF parsing.

Used by NFCReaderManager (via ACR122U / PC-SC) to provide rich card information
similar to what commercial NFC Tools apps display.
"""

# ---------------------------------------------------------------------------
# Card-type database keyed on (ATR[13], ATR[14]) for ACR122U contactless ATRs.
# ---------------------------------------------------------------------------
CARD_TYPE_DB = {
    (0x00, 0x01): {
        'tag_type': 'NXP MIFARE Classic 1K',
        'technologies': 'NfcA, MifareClassic',
        'atqa': '0x0004',
        'sak': '0x08',
        'memory_bytes': 1024,
        'memory_pages': 64,
        'page_size': 16,
        'data_format': 'Proprietary',
        'writable': True,
        'read_only_capable': True,
    },
    (0x00, 0x02): {
        'tag_type': 'NXP MIFARE Classic 4K',
        'technologies': 'NfcA, MifareClassic',
        'atqa': '0x0002',
        'sak': '0x18',
        'memory_bytes': 4096,
        'memory_pages': 256,
        'page_size': 16,
        'data_format': 'Proprietary',
        'writable': True,
        'read_only_capable': True,
    },
    (0x00, 0x03): {
        'tag_type': 'NXP MIFARE Classic Mini',
        'technologies': 'NfcA, MifareClassic',
        'atqa': '0x0004',
        'sak': '0x09',
        'memory_bytes': 320,
        'memory_pages': 20,
        'page_size': 16,
        'data_format': 'Proprietary',
        'writable': True,
        'read_only_capable': True,
    },
    (0x00, 0x26): {
        'tag_type': 'NXP MIFARE Ultralight',
        'technologies': 'NfcA, MifareUltralight, Ndef',
        'atqa': '0x0044',
        'sak': '0x00',
        'memory_bytes': 64,
        'memory_pages': 16,
        'page_size': 4,
        'data_format': 'NFC Forum Type 2',
        'writable': True,
        'read_only_capable': True,
    },
    (0x00, 0x3A): {
        'tag_type': 'NXP MIFARE DESFire',
        'technologies': 'NfcA, IsoDep',
        'atqa': '0x0344',
        'sak': '0x20',
        'memory_bytes': 8192,
        'memory_pages': 0,
        'page_size': 0,
        'data_format': 'NFC Forum Type 4',
        'writable': True,
        'read_only_capable': True,
    },
    (0x00, 0x3B): {
        'tag_type': 'NXP MIFARE DESFire EV1',
        'technologies': 'NfcA, IsoDep',
        'atqa': '0x0344',
        'sak': '0x20',
        'memory_bytes': 8192,
        'memory_pages': 0,
        'page_size': 0,
        'data_format': 'NFC Forum Type 4',
        'writable': True,
        'read_only_capable': True,
    },
    (0x00, 0x14): {
        'tag_type': 'ISO 14443-4 Type B',
        'technologies': 'NfcB, IsoDep',
        'atqa': 'N/A',
        'sak': 'N/A',
        'memory_bytes': 0,
        'memory_pages': 0,
        'page_size': 0,
        'data_format': 'ISO 14443-4',
        'writable': False,
        'read_only_capable': False,
    },
}

# NTAG identification from CC byte 2 (page 3, byte offset 2).
# Values: (tag_name, total_bytes, total_pages, user_bytes, ndef_available_bytes)
NTAG_BY_CC2 = {
    0x12: ('NXP NTAG213', 180, 45, 144, 132),
    0x3E: ('NXP NTAG215', 540, 135, 504, 492),
    0x6D: ('NXP NTAG215', 540, 135, 504, 492),
    0xE1: ('NXP NTAG216', 924, 231, 888, 872),
}

# NDEF URI prefix table (NFC Forum URI Record Type Definition)
_URI_PREFIXES = [
    '', 'http://www.', 'https://www.', 'http://', 'https://',
    'tel:', 'mailto:', 'ftp://anonymous:anonymous@', 'ftp://ftp.',
    'ftps://', 'sftp://', 'smb://', 'nfs://', 'ftp://', 'dav://',
    'news:', 'telnet://', 'imap:', 'rtsp://', 'urn:', 'pop:',
    'sip:', 'sips:', 'tftp:', 'btspp://', 'btl2cap://', 'btgoep://',
    'tcpobex://', 'irdaobex://', 'file://', 'urn:epc:id:',
    'urn:epc:tag:', 'urn:epc:pat:', 'urn:epc:raw:', 'urn:epc:',
    'urn:nfc:',
]


# ---------------------------------------------------------------------------
# ATR parsing
# ---------------------------------------------------------------------------

def parse_atr(atr):
    """Parse ACR122U ATR bytes and return a card-info dict.

    The card-type is encoded in ATR[13] and ATR[14] (0-indexed) for
    standard ACR122U contactless-card ATRs.
    """
    result = {}
    if not atr or len(atr) < 15:
        return result

    key = (atr[13], atr[14])
    card_data = CARD_TYPE_DB.get(key)
    if card_data:
        result.update(card_data)
    else:
        result['tag_type'] = f'Unknown (ATR type bytes: {atr[13]:02X} {atr[14]:02X})'

    return result


def refine_with_cc(card_info, pages_0_3_data):
    """Refine Mifare-Ultralight card info using the Capability Container (CC).

    For NTAG213/215/216 the CC at page 3 (bytes 12-15 of a 16-byte read
    starting at page 0) identifies the exact tag variant.

    Returns an updated copy of *card_info*.
    """
    if not pages_0_3_data or len(pages_0_3_data) < 16:
        return card_info

    cc = pages_0_3_data[12:16]  # page 3 = bytes 12..15

    if cc[0] != 0xE1:            # not NFC Forum magic number
        return card_info

    ntag_info = NTAG_BY_CC2.get(cc[2])
    if ntag_info:
        name, total_bytes, total_pages, user_bytes, ndef_avail = ntag_info
        updated = dict(card_info)
        updated['tag_type'] = name
        updated['memory_bytes'] = total_bytes
        updated['memory_pages'] = total_pages
        updated['user_bytes'] = user_bytes
        updated['ndef_available'] = ndef_avail
        updated['technologies'] = 'NfcA, MifareUltralight, Ndef'
        updated['data_format'] = 'NFC Forum Type 2'
        cc_version = f'{(cc[1] >> 4) & 0x0F}.{cc[1] & 0x0F}'
        updated['cc_version'] = cc_version
        return updated

    return card_info


# ---------------------------------------------------------------------------
# NDEF parsing
# ---------------------------------------------------------------------------

def parse_ndef_from_type2_memory(all_pages_data, start_page=4):
    """Parse NDEF records from NFC Forum Type 2 tag memory.

    *all_pages_data* should be a flat bytes/list object starting from page 0.
    NDEF TLV data normally begins at page 4 (byte 16) for NTAG/Ultralight cards.

    Returns a list of record dicts with at minimum 'record_type' and 'content'.
    """
    records = []
    if isinstance(all_pages_data, list):
        all_pages_data = bytes(all_pages_data)

    start_byte = start_page * 4
    if start_byte >= len(all_pages_data):
        return records

    data = all_pages_data[start_byte:]
    pos = 0

    while pos < len(data):
        tlv_type = data[pos]
        pos += 1

        if tlv_type == 0x00:   # NULL TLV – skip
            continue
        if tlv_type == 0xFE:   # Terminator TLV
            break

        # Read TLV length
        if pos >= len(data):
            break
        length_byte = data[pos]
        pos += 1

        if length_byte == 0xFF:   # 3-byte length
            if pos + 2 > len(data):
                break
            length = (data[pos] << 8) | data[pos + 1]
            pos += 2
        else:
            length = length_byte

        if length == 0:
            continue
        if pos + length > len(data):
            break

        value = data[pos: pos + length]
        pos += length

        if tlv_type == 0x03:   # NDEF Message TLV
            records.extend(_parse_ndef_message(bytes(value)))

    return records


def _parse_ndef_message(msg_bytes):
    """Parse NDEF records from a raw NDEF message byte sequence."""
    records = []
    pos = 0

    while pos < len(msg_bytes):
        header = msg_bytes[pos]
        pos += 1

        tnf = header & 0x07
        il = bool(header & 0x08)   # ID Length present
        sr = bool(header & 0x10)   # Short Record
        me = bool(header & 0x40)   # Message End

        if pos >= len(msg_bytes):
            break
        type_length = msg_bytes[pos]
        pos += 1

        if sr:
            if pos >= len(msg_bytes):
                break
            payload_length = msg_bytes[pos]
            pos += 1
        else:
            if pos + 4 > len(msg_bytes):
                break
            payload_length = int.from_bytes(msg_bytes[pos: pos + 4], 'big')
            pos += 4

        id_length = 0
        if il:
            if pos >= len(msg_bytes):
                break
            id_length = msg_bytes[pos]
            pos += 1

        if pos + type_length > len(msg_bytes):
            break
        record_type = msg_bytes[pos: pos + type_length]
        pos += type_length

        pos += id_length   # skip ID field

        if pos + payload_length > len(msg_bytes):
            break
        payload = msg_bytes[pos: pos + payload_length]
        pos += payload_length

        records.append(_decode_record(tnf, record_type, payload))

        if me:
            break

    return records


def _decode_record(tnf, record_type, payload):
    """Decode a single NDEF record into a human-readable dict."""
    record = {
        'tnf': tnf,
        'raw_type': record_type,
        'raw_payload': payload,
        'record_type': f'Unknown (TNF={tnf})',
        'content': ' '.join(f'{b:02X}' for b in payload),
    }

    if tnf == 0x01:   # NFC Forum Well-Known Type
        if record_type == b'T':
            _decode_text(record, payload)
        elif record_type == b'U':
            _decode_uri(record, payload)
        elif record_type == b'Sp':
            record['record_type'] = 'Smart Poster'
            record['content'] = f'(Smart Poster: {len(payload)} bytes)'
        else:
            record['record_type'] = f'WKT:{record_type.decode("ascii", errors="replace")}'

    elif tnf == 0x02:   # MIME type
        mime = record_type.decode('ascii', errors='replace')
        record['record_type'] = f'MIME: {mime}'
        try:
            record['content'] = payload.decode('utf-8', errors='replace')
        except Exception:
            pass

    elif tnf == 0x03:   # Absolute URI
        record['record_type'] = 'Absolute URI'
        try:
            record['content'] = record_type.decode('utf-8', errors='replace')
        except Exception:
            pass

    return record


def _decode_text(record, payload):
    if not payload:
        record['record_type'] = 'Text'
        record['content'] = ''
        return

    status = payload[0]
    is_utf16 = bool(status & 0x80)
    lang_len = status & 0x3F

    if len(payload) < 1 + lang_len:
        record['record_type'] = 'Text'
        record['content'] = ''
        return

    lang = payload[1: 1 + lang_len].decode('ascii', errors='replace')
    text_bytes = payload[1 + lang_len:]
    enc = 'UTF-16' if is_utf16 else 'UTF-8'

    try:
        text = text_bytes.decode('utf-16' if is_utf16 else 'utf-8', errors='replace')
    except Exception:
        text = text_bytes.decode('latin-1', errors='replace')

    record['record_type'] = f'{enc} ({lang}) : text/plain'
    record['content'] = text
    record['language'] = lang
    record['encoding'] = enc


def _decode_uri(record, payload):
    if not payload:
        record['record_type'] = 'URI'
        record['content'] = ''
        return

    code = payload[0]
    prefix = _URI_PREFIXES[code] if code < len(_URI_PREFIXES) else ''
    suffix = payload[1:].decode('utf-8', errors='replace')
    record['record_type'] = 'URI'
    record['content'] = prefix + suffix


# ---------------------------------------------------------------------------
# NDEF text encoding
# ---------------------------------------------------------------------------

def encode_ndef_text(text: str, lang: str = 'en') -> bytes:
    """Encode a plain-text string as a complete TLV-wrapped NDEF Text record.

    The returned bytes are ready to be written to an NFC Forum Type 2 tag
    starting at page 4 (the first user-data page for NTAG/Ultralight cards).

    Structure::

        03 <ndef_len> [FF <len_hi> <len_lo>] <ndef_record> FE

    The NDEF record inside uses TNF=0x01 (Well-Known), record type ``T``, and
    UTF-8 encoding.

    Args:
        text: The plain-text string to encode (may include any Unicode).
        lang: Two-letter ISO 639-1 language code (default ``'en'``).

    Returns:
        ``bytes`` containing the full TLV-wrapped NDEF message.
    """
    lang_bytes = lang.encode('ascii')
    text_bytes = text.encode('utf-8')

    # Payload: status_byte | lang_code | text
    status = len(lang_bytes) & 0x3F   # bit 7 = 0 → UTF-8
    payload = bytes([status]) + lang_bytes + text_bytes

    # NDEF record header flags:
    # MB=1, ME=1, CF=0, SR=1 (short) or SR=0 (long), IL=0, TNF=0x01
    record_type = b'T'
    if len(payload) <= 255:
        header = 0xD1   # MB ME SR TNF=01
        ndef_record = bytes([header, len(record_type), len(payload)]) + record_type + payload
    else:
        header = 0xC1   # MB ME TNF=01 (no SR)
        ndef_record = (
            bytes([header, len(record_type)])
            + len(payload).to_bytes(4, 'big')
            + record_type
            + payload
        )

    # TLV wrapper: 0x03 <length> <ndef_record> 0xFE
    if len(ndef_record) <= 254:
        tlv = bytes([0x03, len(ndef_record)]) + ndef_record + bytes([0xFE])
    else:
        tlv = (
            bytes([0x03, 0xFF])
            + len(ndef_record).to_bytes(2, 'big')
            + ndef_record
            + bytes([0xFE])
        )

    return tlv
