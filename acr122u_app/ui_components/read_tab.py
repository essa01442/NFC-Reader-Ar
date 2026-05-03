from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QSpinBox, QScrollArea, QFrame,
    QGroupBox, QGridLayout, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from nfc_utils import parse_ndef_from_type2_memory


class _InfoRow(QWidget):
    """A two-column label row used inside the card-info panel."""

    def __init__(self, key_text, value_text="", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 3, 6, 3)
        layout.setSpacing(8)

        self.lbl_key = QLabel(key_text)
        self.lbl_key.setFixedWidth(220)
        self.lbl_key.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        bold = QFont()
        bold.setBold(True)
        self.lbl_key.setFont(bold)

        self.lbl_value = QLabel(value_text)
        self.lbl_value.setWordWrap(True)
        self.lbl_value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.lbl_value.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl_value.setToolTip("انقر للنسخ / Click to copy")

        layout.addWidget(self.lbl_key)
        layout.addWidget(self.lbl_value, stretch=1)

        self.mousePressEvent = self._on_click

    def set_value(self, text):
        self.lbl_value.setText(text)

    def _on_click(self, event):
        text = self.lbl_value.text()
        if text and text != "—":
            QApplication.clipboard().setText(text)
            # Visual feedback
            old_style = self.styleSheet()
            self.setStyleSheet("background-color: #533483;")
            QTimer.singleShot(200, lambda: self.setStyleSheet(old_style))


class ReadTab(QWidget):
    def __init__(self, translator, nfc_manager, log_callback, error_callback, success_callback):
        super().__init__()
        self.translator = translator
        self.nfc_manager = nfc_manager
        self.log = log_callback
        self.on_error = error_callback
        self.on_success = success_callback

        self._info_rows = {}    # key -> _InfoRow widget
        self._ndef_section = None

        self.init_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def init_ui(self):
        outer = QVBoxLayout(self)
        outer.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(10)

        # ── Registry Info Card (Hidden by default) ─────────────────────
        self.frame_registry = QFrame()
        self.frame_registry.setStyleSheet("""
            QFrame {
                background-color: #4caf50;
                border-radius: 8px;
                color: white;
            }
        """)
        self.frame_registry.setVisible(False)
        reg_layout = QVBoxLayout(self.frame_registry)
        self.lbl_registry_title = QLabel("")
        self.lbl_registry_title.setStyleSheet("font-weight: bold; font-size: 11pt;")
        reg_layout.addWidget(self.lbl_registry_title)
        self.lbl_registry_update = QLabel("")
        self.lbl_registry_update.setStyleSheet("font-size: 9pt;")
        reg_layout.addWidget(self.lbl_registry_update)
        layout.addWidget(self.frame_registry)

        # ── Card Information group ─────────────────────────────────────
        self.grp_info = QGroupBox(self.translator.get("section_card_info"))
        info_layout = QVBoxLayout(self.grp_info)
        info_layout.setSpacing(2)

        def add_row(key, tr_key):
            row = _InfoRow(self.translator.get(tr_key))
            info_layout.addWidget(row)
            self._info_rows[key] = row
            return row

        add_row('tag_type',          'lbl_tag_type')
        add_row('technologies',      'lbl_technologies')
        add_row('serial_number',     'lbl_serial_number')
        add_row('atqa',              'lbl_atqa')
        add_row('sak',               'lbl_sak')
        add_row('signature',         'lbl_signature')
        add_row('password_protected','lbl_password_protected')
        add_row('memory_info',       'lbl_memory_info')
        add_row('data_format',       'lbl_data_format')
        add_row('size',              'lbl_size')
        add_row('writable',          'lbl_writable')
        add_row('read_only_capable', 'lbl_read_only_capable')

        layout.addWidget(self.grp_info)

        # ── NDEF Records group ─────────────────────────────────────────
        self.grp_ndef = QGroupBox(self.translator.get("section_ndef"))
        self._ndef_layout = QVBoxLayout(self.grp_ndef)
        self._ndef_layout.setSpacing(4)

        self.lbl_no_ndef = QLabel(self.translator.get("no_ndef"))
        self.lbl_no_ndef.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._ndef_layout.addWidget(self.lbl_no_ndef)

        layout.addWidget(self.grp_ndef)

        # ── Raw block reader (advanced) ────────────────────────────────
        self.grp_raw = QGroupBox(self.translator.get("section_raw_read"))
        raw_layout = QVBoxLayout(self.grp_raw)

        uid_row = QHBoxLayout()
        self.lbl_uid = QLabel(self.translator.get("lbl_uid"))
        uid_row.addWidget(self.lbl_uid)
        self.txt_uid = QLineEdit()
        self.txt_uid.setReadOnly(True)
        uid_row.addWidget(self.txt_uid)
        raw_layout.addLayout(uid_row)

        self.lbl_data = QLabel(self.translator.get("lbl_data"))
        raw_layout.addWidget(self.lbl_data)
        self.txt_read_data = QTextEdit()
        self.txt_read_data.setReadOnly(True)
        self.txt_read_data.setMaximumHeight(130)
        raw_layout.addWidget(self.txt_read_data)

        btn_row = QHBoxLayout()
        self.lbl_read_block = QLabel(self.translator.get("lbl_block"))
        self.spin_read_block = QSpinBox()
        self.spin_read_block.setRange(0, 255)
        self.btn_read = QPushButton(self.translator.get("btn_read"))
        self.btn_read.clicked.connect(self.on_read_clicked)

        btn_row.addWidget(self.lbl_read_block)
        btn_row.addWidget(self.spin_read_block)
        btn_row.addWidget(self.btn_read)
        btn_row.addStretch()
        raw_layout.addLayout(btn_row)

        layout.addWidget(self.grp_raw)

        # ── Full memory dump ────────────────────────────────────────────
        self.grp_memory = QGroupBox(self.translator.get("section_full_memory"))
        memory_layout = QVBoxLayout(self.grp_memory)

        self.txt_memory_dump = QTextEdit()
        self.txt_memory_dump.setReadOnly(True)
        self.txt_memory_dump.setFont(QFont("Monospace", 9))
        self.txt_memory_dump.setMinimumHeight(200)
        self.txt_memory_dump.setPlaceholderText(self.translator.get("no_memory_data"))
        memory_layout.addWidget(self.txt_memory_dump)

        layout.addWidget(self.grp_memory)
        layout.addStretch()

        scroll.setWidget(container)
        outer.addWidget(scroll)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_uid(self, uid):
        self.txt_uid.setText(uid)

    def show_card_info(self, info: dict):
        """Populate all card-info rows from the *info* dict emitted by
        NFCReaderManager.card_info_ready.
        """
        t = self.translator
        yes = t.get("val_yes")
        no  = t.get("val_no")
        unk = t.get("val_unknown")

        def _val(key, default=unk):
            v = info.get(key)
            return str(v) if v not in (None, '', 0) else default

        self._info_rows['tag_type'].set_value(_val('tag_type'))
        self._info_rows['technologies'].set_value(_val('technologies'))

        # UID formatted with colons
        uid_raw = info.get('uid_raw', [])
        uid_fmt = info.get('uid_formatted') or ':'.join(
            bytes([b]).hex().upper() for b in uid_raw
        ) or unk
        self._info_rows['serial_number'].set_value(uid_fmt)

        self._info_rows['atqa'].set_value(_val('atqa'))
        self._info_rows['sak'].set_value(_val('sak'))

        # Signature
        sig_status = info.get('signature', 'N/A')
        if sig_status == 'Valid':
            self._info_rows['signature'].set_value(t.get("val_valid"))
            self._info_rows['signature'].lbl_value.setStyleSheet("color: #4caf50; font-weight: bold;")
        elif sig_status == 'Invalid':
            self._info_rows['signature'].set_value(t.get("val_invalid"))
            self._info_rows['signature'].lbl_value.setStyleSheet("color: #f44336; font-weight: bold;")
        else:
            self._info_rows['signature'].set_value(unk)
            self._info_rows['signature'].lbl_value.setStyleSheet("")

        self._info_rows['password_protected'].set_value(
            yes if info.get('password_protected') else no
        )

        # Memory information
        mem_bytes = info.get('memory_bytes', 0)
        mem_pages = info.get('memory_pages', 0)
        page_size = info.get('page_size', 0)
        if mem_bytes and mem_pages and page_size:
            mem_str = f"{mem_bytes} bytes : {mem_pages} pages ({page_size} bytes each)"
        elif mem_bytes:
            mem_str = f"{mem_bytes} bytes"
        else:
            mem_str = unk
        self._info_rows['memory_info'].set_value(mem_str)

        self._info_rows['data_format'].set_value(_val('data_format'))

        # Size: used / available
        ndef_used = info.get('ndef_used', 0)
        ndef_avail = info.get('ndef_available', 0)
        if ndef_avail:
            size_str = f"{ndef_used} / {ndef_avail} Bytes"
        elif mem_bytes:
            size_str = f"{mem_bytes} Bytes"
        else:
            size_str = unk
        self._info_rows['size'].set_value(size_str)

        self._info_rows['writable'].set_value(
            yes if info.get('writable') else (no if 'writable' in info else unk)
        )
        self._info_rows['read_only_capable'].set_value(
            yes if info.get('read_only_capable') else (no if 'read_only_capable' in info else unk)
        )

        # Registry Info
        reg = info.get('registry_info')
        if reg:
            self.lbl_registry_title.setText(t.get("registry_found", reg['card_number'], reg['domain']))
            self.lbl_registry_update.setText(t.get("registry_last_update", reg['updated_at']))
            self.frame_registry.setVisible(True)
        else:
            self.frame_registry.setVisible(False)

        # NDEF records
        self._populate_ndef_records(info.get('ndef_records', []))

        # Full memory dump
        raw_pages = info.get('raw_pages')
        if raw_pages:
            self._populate_memory_dump(raw_pages, info.get('page_size', 4))
        else:
            self.txt_memory_dump.clear()

    def clear_data(self):
        """Clear all displayed data (called on card removal)."""
        self.txt_uid.clear()
        self.txt_read_data.clear()
        self.txt_memory_dump.clear()
        self.frame_registry.setVisible(False)

        for row in self._info_rows.values():
            row.set_value("")
            if hasattr(row, 'lbl_value'):
                row.lbl_value.setStyleSheet("")

        self._clear_ndef_section()
        self.lbl_no_ndef.show()

    # ------------------------------------------------------------------
    # Block reader
    # ------------------------------------------------------------------

    def on_read_clicked(self):
        block_num = self.spin_read_block.value()
        try:
            data = self.nfc_manager.read_block(block_num)
            hex_data = " ".join([f"{b:02X}" for b in data])

            # Try NDEF decoding first so meaningful text is shown when the
            # block contains user data (e.g. page 4+ on NTAG/Ultralight).
            ndef_text = None
            try:
                records = parse_ndef_from_type2_memory(bytes(data), start_page=0)
                if records:
                    ndef_text = ' | '.join(
                        r['content'] for r in records if r.get('content')
                    )
            except Exception:
                pass

            if ndef_text:
                display = f"HEX: {hex_data}\nNDEF: {ndef_text}"
            else:
                # Only include the TEXT line when at least half the bytes are
                # printable ASCII; otherwise the result is just garbled noise.
                printable = [chr(b) for b in data if 32 <= b < 127]
                if len(printable) > len(data) // 2:
                    text_str = ''.join(
                        chr(b) if 32 <= b < 127 else '.' for b in data
                    )
                    display = f"HEX: {hex_data}\nTEXT: {text_str}"
                else:
                    display = f"HEX: {hex_data}"

            self.txt_read_data.setText(display)
            msg = self.translator.get("log_read_success") + f" (Block {block_num})"
            self.log(msg)
            self.on_success(msg)

            main_win = self.window()
            if hasattr(main_win, 'tab_dashboard'):
                main_win.tab_dashboard.log_action(
                    self.txt_uid.text(), "READ", f"Block {block_num}: {hex_data}"
                )
        except Exception as e:
            err_msg = self.translator.get("log_read_error", str(e))
            self.log(err_msg)
            self.on_error(err_msg)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _populate_memory_dump(self, raw_pages: bytes, page_size: int = 4):
        """Render the full card memory as a formatted hex + ASCII dump."""
        lines = []
        if page_size <= 0:
            page_size = 4
        total_bytes = len(raw_pages)
        total_pages = total_bytes // page_size

        for page_num in range(total_pages):
            offset = page_num * page_size
            chunk = raw_pages[offset: offset + page_size]
            hex_part = ' '.join(f'{b:02X}' for b in chunk)
            text_part = ''.join(
                chr(b) if 32 <= b < 127 else '.' for b in chunk
            )
            lines.append(f"Page {page_num:03d} | {hex_part:<{page_size * 3 - 1}} | {text_part}")

        self.txt_memory_dump.setPlainText('\n'.join(lines))

    def _clear_ndef_section(self):
        while self._ndef_layout.count() > 0:
            item = self._ndef_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Re-add the placeholder label
        self.lbl_no_ndef = QLabel(self.translator.get("no_ndef"))
        self.lbl_no_ndef.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._ndef_layout.addWidget(self.lbl_no_ndef)

    def _populate_ndef_records(self, records):
        self._clear_ndef_section()
        if not records:
            self.lbl_no_ndef.show()
            return

        self.lbl_no_ndef.hide()
        for idx, rec in enumerate(records, start=1):
            rec_type = rec.get('record_type', 'Unknown')
            content  = rec.get('content', '')

            rec_label = QLabel(f"<b>{self.translator.get('lbl_record', str(idx))}</b> {rec_type}")
            rec_label.setWordWrap(True)
            self._ndef_layout.addWidget(rec_label)

            if content:
                content_label = QLabel(content)
                content_label.setWordWrap(True)
                content_label.setTextInteractionFlags(
                    Qt.TextInteractionFlag.TextSelectableByMouse
                )
                content_label.setIndent(16)
                content_label.setCursor(Qt.CursorShape.PointingHandCursor)
                content_label.setToolTip("انقر للنسخ / Click to copy")

                # Make it clickable to copy
                def make_copy_fn(text):
                    return lambda event: QApplication.clipboard().setText(text)
                content_label.mousePressEvent = make_copy_fn(content)

                self._ndef_layout.addWidget(content_label)

    # ------------------------------------------------------------------
    # Retranslation
    # ------------------------------------------------------------------

    def retranslate_ui(self):
        self.grp_info.setTitle(self.translator.get("section_card_info"))
        self.grp_ndef.setTitle(self.translator.get("section_ndef"))
        self.grp_raw.setTitle(self.translator.get("section_raw_read"))
        self.grp_memory.setTitle(self.translator.get("section_full_memory"))
        self.txt_memory_dump.setPlaceholderText(self.translator.get("no_memory_data"))

        labels_map = {
            'tag_type':          'lbl_tag_type',
            'technologies':      'lbl_technologies',
            'serial_number':     'lbl_serial_number',
            'atqa':              'lbl_atqa',
            'sak':               'lbl_sak',
            'signature':         'lbl_signature',
            'password_protected':'lbl_password_protected',
            'memory_info':       'lbl_memory_info',
            'data_format':       'lbl_data_format',
            'size':              'lbl_size',
            'writable':          'lbl_writable',
            'read_only_capable': 'lbl_read_only_capable',
        }
        for key, tr_key in labels_map.items():
            self._info_rows[key].lbl_key.setText(self.translator.get(tr_key))

        self.lbl_uid.setText(self.translator.get("lbl_uid"))
        self.lbl_data.setText(self.translator.get("lbl_data"))
        self.lbl_read_block.setText(self.translator.get("lbl_block"))
        self.btn_read.setText(self.translator.get("btn_read"))
