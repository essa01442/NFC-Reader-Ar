from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSpinBox, QMessageBox, QTextEdit, QGroupBox, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Maximum NDEF payload that fits on the most common small card (NTAG213: 132 bytes).
# Overhead: TLV header (2) + NDEF record header (3) + type byte (1) +
#           status byte (1) + lang "en" (2) + terminator (1) = 10 bytes.
_NTAG213_NDEF_CAPACITY = 132
_NDEF_OVERHEAD = 10
_DEFAULT_MAX_TEXT_BYTES = _NTAG213_NDEF_CAPACITY - _NDEF_OVERHEAD  # 122 bytes


class WriteTab(QWidget):
    def __init__(self, translator, nfc_manager, log_callback, error_callback, success_callback):
        super().__init__()
        self.translator = translator
        self.nfc_manager = nfc_manager
        self.log = log_callback
        self.on_error = error_callback
        self.on_success = success_callback
        # Maximum text bytes – updated when card info is received
        self._max_text_bytes = _DEFAULT_MAX_TEXT_BYTES
        self.init_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # ── Section 1: Write Text / Password ──────────────────────────
        self.grp_text = QGroupBox(self.translator.get("section_write_text"))
        text_layout = QVBoxLayout(self.grp_text)
        text_layout.setSpacing(6)

        self.lbl_text_to_write = QLabel(self.translator.get("lbl_text_to_write"))
        text_layout.addWidget(self.lbl_text_to_write)

        self.txt_ndef_text = QTextEdit()
        self.txt_ndef_text.setPlaceholderText(self.translator.get("lbl_text_hint"))
        self.txt_ndef_text.setMaximumHeight(100)
        mono = QFont("Monospace", 10)
        self.txt_ndef_text.setFont(mono)
        self.txt_ndef_text.textChanged.connect(self._on_ndef_text_changed)
        text_layout.addWidget(self.txt_ndef_text)

        # Character / byte counter row
        counter_row = QHBoxLayout()
        self.lbl_char_count = QLabel(self.translator.get("lbl_char_count", "0"))
        self.lbl_char_count.setStyleSheet("color: gray; font-size: 9pt;")
        counter_row.addWidget(self.lbl_char_count)
        counter_row.addStretch()
        text_layout.addLayout(counter_row)

        # Language code + write button row
        lang_btn_row = QHBoxLayout()
        self.lbl_text_lang = QLabel(self.translator.get("lbl_text_lang"))
        lang_btn_row.addWidget(self.lbl_text_lang)
        self.txt_lang = QLineEdit("en")
        self.txt_lang.setFixedWidth(50)
        self.txt_lang.setMaxLength(8)
        lang_btn_row.addWidget(self.txt_lang)
        lang_btn_row.addStretch()
        self.btn_write_text = QPushButton(self.translator.get("btn_write_text"))
        self.btn_write_text.setMinimumHeight(34)
        self.btn_write_text.clicked.connect(self._on_write_text_clicked)
        lang_btn_row.addWidget(self.btn_write_text)
        text_layout.addLayout(lang_btn_row)

        layout.addWidget(self.grp_text)

        # ── Divider ────────────────────────────────────────────────────
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # ── Section 2: Write Raw Block (Advanced) ─────────────────────
        self.grp_raw = QGroupBox(self.translator.get("section_write_raw"))
        raw_layout = QVBoxLayout(self.grp_raw)
        raw_layout.setSpacing(6)

        self.lbl_write_data = QLabel(self.translator.get("lbl_write_data"))
        raw_layout.addWidget(self.lbl_write_data)

        self.txt_write_data = QLineEdit()
        self.txt_write_data.setPlaceholderText("Hex Data – exactly 4 bytes (8 hex chars) or 16 bytes (32 hex chars)")
        self.txt_write_data.textChanged.connect(self.validate_hex_input)
        raw_layout.addWidget(self.txt_write_data)

        btn_layout = QHBoxLayout()
        self.lbl_write_block = QLabel(self.translator.get("lbl_block"))
        self.spin_write_block = QSpinBox()
        self.spin_write_block.setRange(0, 255)
        self.btn_write = QPushButton(self.translator.get("btn_write"))
        self.btn_write.clicked.connect(self.on_write_clicked)

        btn_layout.addWidget(self.lbl_write_block)
        btn_layout.addWidget(self.spin_write_block)
        btn_layout.addWidget(self.btn_write)
        btn_layout.addStretch()
        raw_layout.addLayout(btn_layout)

        layout.addWidget(self.grp_raw)
        layout.addStretch()

    # ------------------------------------------------------------------
    # Slot: update byte counter and border colour as user types
    # ------------------------------------------------------------------

    def _on_ndef_text_changed(self):
        text = self.txt_ndef_text.toPlainText()
        byte_len = len(text.encode('utf-8'))
        self.lbl_char_count.setText(
            self.translator.get("lbl_char_count", str(len(text)))
            + f"  ({byte_len} bytes)"
        )
        if byte_len > self._max_text_bytes:
            self.lbl_char_count.setStyleSheet("color: red; font-size: 9pt; font-weight: bold;")
        else:
            self.lbl_char_count.setStyleSheet("color: gray; font-size: 9pt;")

    # ------------------------------------------------------------------
    # Write Text / Password as NDEF
    # ------------------------------------------------------------------

    def _on_write_text_clicked(self):
        text = self.txt_ndef_text.toPlainText()
        if not text.strip():
            err_msg = self.translator.get("err_text_empty")
            self.on_error(err_msg)
            QMessageBox.warning(self, self.translator.get("msg_warning"), err_msg)
            return

        byte_len = len(text.encode('utf-8'))
        if byte_len > self._max_text_bytes:
            err_msg = self.translator.get("err_text_too_long", str(byte_len), str(self._max_text_bytes))
            self.on_error(err_msg)
            QMessageBox.warning(self, self.translator.get("msg_warning"), err_msg)
            return

        lang = self.txt_lang.text().strip() or 'en'

        reply = QMessageBox.question(
            self, self.translator.get("msg_warning"),
            self.translator.get("msg_write_text_warn"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            pages = self.nfc_manager.write_ndef_text(text, lang)
            msg = self.translator.get("log_write_text_success", str(pages))
            self.log(msg)
            self.on_success(msg)

            main_win = self.window()
            if hasattr(main_win, 'tab_dashboard') and hasattr(main_win, 'tab_read'):
                uid = main_win.tab_read.txt_uid.text()
                preview = text[:40] + ('…' if len(text) > 40 else '')
                main_win.tab_dashboard.log_action(uid, "WRITE NDEF", preview)

            QMessageBox.information(
                self, self.translator.get("msg_success"),
                self.translator.get("log_write_text_success", str(pages))
            )
        except Exception as e:
            err_msg = self.translator.get("log_write_error", str(e))
            self.log(err_msg)
            self.on_error(err_msg)
            QMessageBox.critical(self, self.translator.get("msg_error"), err_msg)

    # ------------------------------------------------------------------
    # Raw hex block write (existing behaviour)
    # ------------------------------------------------------------------

    def validate_hex_input(self):
        hex_str = self.txt_write_data.text().replace(" ", "")

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

        if color:
            self.txt_write_data.setStyleSheet(f"border: 1px solid {color};")
        else:
            self.txt_write_data.setStyleSheet("")

    def on_write_clicked(self):
        hex_str = self.txt_write_data.text().replace(" ", "")

        if not hex_str:
            err_msg = self.translator.get("msg_error") + ": Empty data"
            self.on_error(err_msg)
            QMessageBox.critical(self, self.translator.get("msg_error"), err_msg)
            return

        if len(hex_str) % 2 != 0:
            err_msg = self.translator.get("msg_error") + ": Hex string must have an even number of characters."
            self.on_error(err_msg)
            QMessageBox.critical(self, self.translator.get("msg_error"), err_msg)
            return

        try:
            data_bytes = bytes.fromhex(hex_str)
        except ValueError:
            err_msg = self.translator.get("msg_error") + ": Invalid hex data"
            self.on_error(err_msg)
            QMessageBox.critical(self, self.translator.get("msg_error"), err_msg)
            return

        if len(data_bytes) not in (4, 16):
            err_msg = self.translator.get("msg_error") + ": Data must be exactly 4 or 16 bytes long."
            self.on_error(err_msg)
            QMessageBox.critical(self, self.translator.get("msg_error"), err_msg)
            return

        block_num = self.spin_write_block.value()

        reply = QMessageBox.question(
            self, self.translator.get("msg_warning"),
            self.translator.get("msg_write_warn"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.nfc_manager.write_block(block_num, data_bytes)
                msg = self.translator.get("log_write_success") + f" (Block {block_num})"
                self.log(msg)
                self.on_success(msg)

                main_win = self.window()
                if hasattr(main_win, 'tab_dashboard') and hasattr(main_win, 'tab_read'):
                    uid = main_win.tab_read.txt_uid.text()
                    main_win.tab_dashboard.log_action(uid, "WRITE", f"Block {block_num}: {hex_str}")

                QMessageBox.information(self, self.translator.get("msg_success"), self.translator.get("log_write_success"))
            except Exception as e:
                err_msg = self.translator.get("log_write_error", str(e))
                self.log(err_msg)
                self.on_error(err_msg)

    # ------------------------------------------------------------------
    # Public API: update the max-text-bytes hint when card info changes
    # ------------------------------------------------------------------

    def update_card_capacity(self, ndef_available: int):
        """Called when a card is inserted so the byte limit reflects the card."""
        if ndef_available > _NDEF_OVERHEAD:
            self._max_text_bytes = ndef_available - _NDEF_OVERHEAD
        else:
            self._max_text_bytes = _DEFAULT_MAX_TEXT_BYTES
        # Refresh the counter colour
        self._on_ndef_text_changed()

    # ------------------------------------------------------------------
    # Retranslation
    # ------------------------------------------------------------------

    def retranslate_ui(self):
        self.grp_text.setTitle(self.translator.get("section_write_text"))
        self.lbl_text_to_write.setText(self.translator.get("lbl_text_to_write"))
        self.txt_ndef_text.setPlaceholderText(self.translator.get("lbl_text_hint"))
        self.lbl_text_lang.setText(self.translator.get("lbl_text_lang"))
        self.btn_write_text.setText(self.translator.get("btn_write_text"))

        self.grp_raw.setTitle(self.translator.get("section_write_raw"))
        self.lbl_write_data.setText(self.translator.get("lbl_write_data"))
        self.lbl_write_block.setText(self.translator.get("lbl_block"))
        self.btn_write.setText(self.translator.get("btn_write"))
        self._on_ndef_text_changed()

