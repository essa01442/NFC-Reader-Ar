from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QSpinBox, QScrollArea, QFrame,
    QGroupBox, QGridLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class _InfoRow(QWidget):
    """A two-column label row used inside the card-info panel."""

    def __init__(self, key_text, value_text="", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        self.lbl_key = QLabel(key_text)
        self.lbl_key.setFixedWidth(200)
        bold = QFont()
        bold.setBold(True)
        self.lbl_key.setFont(bold)

        self.lbl_value = QLabel(value_text)
        self.lbl_value.setWordWrap(True)
        self.lbl_value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        layout.addWidget(self.lbl_key)
        layout.addWidget(self.lbl_value, stretch=1)

    def set_value(self, text):
        self.lbl_value.setText(text)


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

        # NDEF records
        self._populate_ndef_records(info.get('ndef_records', []))

    def clear_data(self):
        """Clear all displayed data (called on card removal)."""
        self.txt_uid.clear()
        self.txt_read_data.clear()

        unk = self.translator.get("val_unknown")
        for row in self._info_rows.values():
            row.set_value(unk)

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

            # Also show a decoded text representation alongside the hex
            decoded = bytes(data).decode('utf-8', errors='replace')
            printable = ''.join(c if c.isprintable() else '.' for c in decoded)
            display = f"HEX: {hex_data}\nTEXT: {printable}"

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
                self._ndef_layout.addWidget(content_label)

    # ------------------------------------------------------------------
    # Retranslation
    # ------------------------------------------------------------------

    def retranslate_ui(self):
        self.grp_info.setTitle(self.translator.get("section_card_info"))
        self.grp_ndef.setTitle(self.translator.get("section_ndef"))
        self.grp_raw.setTitle(self.translator.get("section_raw_read"))

        labels_map = {
            'tag_type':          'lbl_tag_type',
            'technologies':      'lbl_technologies',
            'serial_number':     'lbl_serial_number',
            'atqa':              'lbl_atqa',
            'sak':               'lbl_sak',
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

