from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QSpinBox

class ReadTab(QWidget):
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

        # UID section
        uid_layout = QHBoxLayout()
        self.lbl_uid = QLabel(self.translator.get("lbl_uid"))
        uid_layout.addWidget(self.lbl_uid)
        self.txt_uid = QLineEdit()
        self.txt_uid.setReadOnly(True)
        uid_layout.addWidget(self.txt_uid)
        layout.addLayout(uid_layout)

        # Data section
        data_layout = QVBoxLayout()
        self.lbl_data = QLabel(self.translator.get("lbl_data"))
        data_layout.addWidget(self.lbl_data)
        self.txt_read_data = QTextEdit()
        self.txt_read_data.setReadOnly(True)
        data_layout.addWidget(self.txt_read_data)

        btn_layout = QHBoxLayout()
        self.btn_read = QPushButton(self.translator.get("btn_read"))
        self.btn_read.clicked.connect(self.on_read_clicked)
        self.spin_read_block = QSpinBox()
        self.spin_read_block.setRange(0, 255)

        self.lbl_read_block = QLabel(self.translator.get("lbl_block"))
        btn_layout.addWidget(self.lbl_read_block)
        btn_layout.addWidget(self.spin_read_block)
        btn_layout.addWidget(self.btn_read)
        btn_layout.addStretch()

        data_layout.addLayout(btn_layout)
        layout.addLayout(data_layout)

    def on_read_clicked(self):
        block_num = self.spin_read_block.value()
        try:
            data = self.nfc_manager.read_block(block_num)
            hex_data = " ".join([f"{b:02X}" for b in data])
            self.txt_read_data.setText(hex_data)
            msg = self.translator.get("log_read_success") + f" (Block {block_num})"
            self.log(msg)
            self.on_success(msg)
        except Exception as e:
            err_msg = self.translator.get("log_read_error", str(e))
            self.log(err_msg)
            self.on_error(err_msg)

    def set_uid(self, uid):
        self.txt_uid.setText(uid)

    def clear_data(self):
        self.txt_uid.clear()
        self.txt_read_data.clear()

    def retranslate_ui(self):
        self.lbl_uid.setText(self.translator.get("lbl_uid"))
        self.lbl_data.setText(self.translator.get("lbl_data"))
        self.lbl_read_block.setText(self.translator.get("lbl_block"))
        self.btn_read.setText(self.translator.get("btn_read"))
