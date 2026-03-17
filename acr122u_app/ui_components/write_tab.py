from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QMessageBox
from PyQt6.QtGui import QColor, QPalette

class WriteTab(QWidget):
    def __init__(self, translator, nfc_manager, log_callback, error_callback, success_callback):
        super().__init__()
        self.translator = translator
        self.nfc_manager = nfc_manager
        self.log = log_callback
        self.on_error = error_callback
        self.on_success = success_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        data_layout = QVBoxLayout()
        self.lbl_write_data = QLabel(self.translator.get("lbl_write_data"))
        data_layout.addWidget(self.lbl_write_data)

        self.txt_write_data = QLineEdit()
        self.txt_write_data.setPlaceholderText("Hex Data (e.g. 01020304 or 16 bytes...)")
        self.txt_write_data.textChanged.connect(self.validate_hex_input)
        data_layout.addWidget(self.txt_write_data)

        btn_layout = QHBoxLayout()
        self.btn_write = QPushButton(self.translator.get("btn_write"))
        self.btn_write.clicked.connect(self.on_write_clicked)
        self.spin_write_block = QSpinBox()
        self.spin_write_block.setRange(0, 255)

        self.lbl_write_block = QLabel(self.translator.get("lbl_block"))
        btn_layout.addWidget(self.lbl_write_block)
        btn_layout.addWidget(self.spin_write_block)
        btn_layout.addWidget(self.btn_write)
        btn_layout.addStretch()

        data_layout.addLayout(btn_layout)
        layout.addLayout(data_layout)
        layout.addStretch()

    def validate_hex_input(self):
        hex_str = self.txt_write_data.text().replace(" ", "")

        # Determine color
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
                if hasattr(main_win, 'tab_dashboard') and hasattr(main_win.tab_read, 'txt_uid'):
                    uid = main_win.tab_read.txt_uid.text()
                    main_win.tab_dashboard.log_action(uid, "WRITE", f"Block {block_num}: {hex_str}")

                QMessageBox.information(self, self.translator.get("msg_success"), self.translator.get("log_write_success"))
            except Exception as e:
                err_msg = self.translator.get("log_write_error", str(e))
                self.log(err_msg)
                self.on_error(err_msg)

    def retranslate_ui(self):
        self.lbl_write_data.setText(self.translator.get("lbl_write_data"))
        self.lbl_write_block.setText(self.translator.get("lbl_block"))
        self.btn_write.setText(self.translator.get("btn_write"))
