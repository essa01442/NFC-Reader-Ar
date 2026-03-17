import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QCheckBox, QComboBox, QMessageBox, QGroupBox, QSpinBox,
    QStatusBar, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QColor

from i18n import Translator
from reader import NFCReaderManager
from emulator import KeyboardEmulator

class AppMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.translator = Translator("ar")
        self.nfc_manager = NFCReaderManager()
        self.emulator = KeyboardEmulator()

        self.init_ui()
        self.setup_signals()

    def init_ui(self):
        self.setWindowTitle(self.translator.get("app_title"))
        self.resize(800, 600)

        # Apply global RTL/LTR direction based on language
        if self.translator.lang == "ar":
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        font = QFont("Segoe UI", 10)
        self.setFont(font)

        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header Info (Status)
        header_layout = QHBoxLayout()
        self.lbl_reader_status = QLabel(self.translator.get("status_reader_disconnected"))
        self.lbl_reader_status.setStyleSheet("color: red; font-weight: bold;")
        self.lbl_card_status = QLabel(self.translator.get("status_card_absent"))
        self.lbl_card_status.setStyleSheet("color: gray;")
        header_layout.addWidget(self.lbl_reader_status)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_card_status)
        main_layout.addLayout(header_layout)

        # Tabs
        self.tabs = QTabWidget()
        self.tab_read = self.create_read_tab()
        self.tab_write = self.create_write_tab()
        self.tab_security = self.create_security_tab()
        self.tab_emulation = self.create_emulation_tab()
        self.tab_settings = self.create_settings_tab()

        self.tabs.addTab(self.tab_read, self.translator.get("tab_read"))
        self.tabs.addTab(self.tab_write, self.translator.get("tab_write"))
        self.tabs.addTab(self.tab_security, self.translator.get("tab_security"))
        self.tabs.addTab(self.tab_emulation, self.translator.get("tab_emulation"))
        self.tabs.addTab(self.tab_settings, self.translator.get("tab_settings"))
        main_layout.addWidget(self.tabs, stretch=2)

        # Log Section
        self.log_group = QGroupBox(self.translator.get("log_title"))
        log_layout = QVBoxLayout(self.log_group)
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.btn_clear_log = QPushButton(self.translator.get("btn_clear_log"))
        self.btn_clear_log.clicked.connect(self.txt_log.clear)
        log_layout.addWidget(self.txt_log)
        log_layout.addWidget(self.btn_clear_log, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.log_group, stretch=1)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def create_read_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

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

        return tab

    def create_write_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        data_layout = QVBoxLayout()
        self.lbl_write_data = QLabel(self.translator.get("lbl_write_data"))
        data_layout.addWidget(self.lbl_write_data)
        self.txt_write_data = QLineEdit()
        self.txt_write_data.setPlaceholderText("Hex Data (e.g. 01020304 or 16 bytes...)")
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

        return tab

    def create_security_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.lbl_security_info = QLabel("Security features (Authentication, Lock) will go here in future expansion.")
        layout.addWidget(self.lbl_security_info)
        layout.addStretch()
        return tab

    def create_emulation_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.chk_emulation = QCheckBox(self.translator.get("chk_emulation_enable"))
        self.chk_emulation.stateChanged.connect(self.on_emulation_toggled)
        layout.addWidget(self.chk_emulation)

        opt_layout = QHBoxLayout()
        self.lbl_emulation_suffix = QLabel(self.translator.get("lbl_emulation_suffix"))
        opt_layout.addWidget(self.lbl_emulation_suffix)
        self.cmb_emulation_suffix = QComboBox()
        self.cmb_emulation_suffix.addItem(self.translator.get("opt_none"), "none")
        self.cmb_emulation_suffix.addItem(self.translator.get("opt_enter"), "enter")
        self.cmb_emulation_suffix.addItem(self.translator.get("opt_tab"), "tab")
        self.cmb_emulation_suffix.currentIndexChanged.connect(self.on_emulation_suffix_changed)
        opt_layout.addWidget(self.cmb_emulation_suffix)
        opt_layout.addStretch()

        layout.addLayout(opt_layout)
        layout.addStretch()
        return tab

    def create_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        lang_layout = QHBoxLayout()
        self.lbl_language = QLabel(self.translator.get("lbl_language"))
        lang_layout.addWidget(self.lbl_language)
        self.cmb_lang = QComboBox()
        self.cmb_lang.addItem("العربية", "ar")
        self.cmb_lang.addItem("English", "en")

        # Set current lang in combobox
        idx = self.cmb_lang.findData(self.translator.lang)
        if idx >= 0:
            self.cmb_lang.setCurrentIndex(idx)

        self.btn_apply_lang = QPushButton(self.translator.get("btn_apply_lang"))
        self.btn_apply_lang.clicked.connect(self.on_lang_changed)

        lang_layout.addWidget(self.cmb_lang)
        lang_layout.addWidget(self.btn_apply_lang)
        lang_layout.addStretch()

        layout.addLayout(lang_layout)
        layout.addStretch()
        return tab

    def setup_signals(self):
        self.nfc_manager.reader_connected.connect(self.on_reader_connected)
        self.nfc_manager.reader_disconnected.connect(self.on_reader_disconnected)
        self.nfc_manager.card_detected.connect(self.on_card_detected)
        self.nfc_manager.card_removed_signal.connect(self.on_card_removed)
        self.nfc_manager.error_occurred.connect(self.on_error_occurred)

    def log(self, message):
        self.txt_log.append(message)

    def on_reader_connected(self, reader_name):
        self.lbl_reader_status.setText(self.translator.get("status_reader_connected") + f" ({reader_name})")
        self.lbl_reader_status.setStyleSheet("color: green; font-weight: bold;")
        self.log(self.translator.get("log_reader_found", reader_name))

    def on_reader_disconnected(self):
        self.lbl_reader_status.setText(self.translator.get("status_reader_disconnected"))
        self.lbl_reader_status.setStyleSheet("color: red; font-weight: bold;")
        self.log(self.translator.get("log_reader_lost"))
        self.on_card_removed()

    def on_card_detected(self, uid):
        self.lbl_card_status.setText(self.translator.get("status_card_present") + f" - UID: {uid}")
        self.lbl_card_status.setStyleSheet("color: green; font-weight: bold;")
        self.txt_uid.setText(uid)
        self.log(self.translator.get("log_card_inserted", uid))

        # Emulation mode
        if self.emulator.enabled:
            self.emulator.type_string(uid)

    def on_card_removed(self):
        self.lbl_card_status.setText(self.translator.get("status_card_absent"))
        self.lbl_card_status.setStyleSheet("color: gray;")
        self.txt_uid.clear()
        self.txt_read_data.clear()
        self.log(self.translator.get("log_card_removed"))

    def on_error_occurred(self, err_msg):
        self.log(f"Error: {err_msg}")
        self.status_bar.showMessage(err_msg, 5000)
        self.status_bar.setStyleSheet("color: red; font-weight: bold;")

    def show_success_message(self, msg):
        self.status_bar.showMessage(msg, 5000)
        self.status_bar.setStyleSheet("color: green; font-weight: bold;")

    def on_read_clicked(self):
        block_num = self.spin_read_block.value()
        try:
            data = self.nfc_manager.read_block(block_num)
            hex_data = " ".join([f"{b:02X}" for b in data])
            self.txt_read_data.setText(hex_data)
            msg = self.translator.get("log_read_success") + f" (Block {block_num})"
            self.log(msg)
            self.show_success_message(msg)
        except Exception as e:
            err_msg = self.translator.get("log_read_error", str(e))
            self.log(err_msg)
            self.on_error_occurred(err_msg)
            QMessageBox.critical(self, self.translator.get("msg_error"), str(e))

    def on_write_clicked(self):
        hex_str = self.txt_write_data.text().replace(" ", "")

        if not hex_str:
            err_msg = self.translator.get("msg_error") + ": Empty data"
            self.on_error_occurred(err_msg)
            QMessageBox.critical(self, self.translator.get("msg_error"), err_msg)
            return

        if len(hex_str) % 2 != 0:
            err_msg = self.translator.get("msg_error") + ": Hex string must have an even number of characters."
            self.on_error_occurred(err_msg)
            QMessageBox.critical(self, self.translator.get("msg_error"), err_msg)
            return

        try:
            data_bytes = bytes.fromhex(hex_str)
        except ValueError:
            err_msg = self.translator.get("msg_error") + ": Invalid hex data"
            self.on_error_occurred(err_msg)
            QMessageBox.critical(self, self.translator.get("msg_error"), err_msg)
            return

        if len(data_bytes) not in (4, 16):
            err_msg = self.translator.get("msg_error") + ": Data must be exactly 4 or 16 bytes long."
            self.on_error_occurred(err_msg)
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
                self.show_success_message(msg)
                QMessageBox.information(self, self.translator.get("msg_success"), self.translator.get("log_write_success"))
            except Exception as e:
                err_msg = self.translator.get("log_write_error", str(e))
                self.log(err_msg)
                self.on_error_occurred(err_msg)
                QMessageBox.critical(self, self.translator.get("msg_error"), str(e))

    def on_emulation_toggled(self, state):
        self.emulator.set_enabled(state == 2)

    def on_emulation_suffix_changed(self, index):
        suffix = self.cmb_emulation_suffix.currentData()
        self.emulator.set_suffix(suffix)

    def on_lang_changed(self):
        lang = self.cmb_lang.currentData()
        self.translator.set_language(lang)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(self.translator.get("app_title"))

        # Tabs
        self.tabs.setTabText(0, self.translator.get("tab_read"))
        self.tabs.setTabText(1, self.translator.get("tab_write"))
        self.tabs.setTabText(2, self.translator.get("tab_security"))
        self.tabs.setTabText(3, self.translator.get("tab_emulation"))
        self.tabs.setTabText(4, self.translator.get("tab_settings"))

        # Reader / Card Status
        if self.nfc_manager.reader:
            self.lbl_reader_status.setText(self.translator.get("status_reader_connected") + f" ({self.nfc_manager.reader})")
        else:
            self.lbl_reader_status.setText(self.translator.get("status_reader_disconnected"))

        if self.txt_uid.text():
            self.lbl_card_status.setText(self.translator.get("status_card_present") + f" - UID: {self.txt_uid.text()}")
        else:
            self.lbl_card_status.setText(self.translator.get("status_card_absent"))

        # Log
        self.log_group.setTitle(self.translator.get("log_title"))
        self.btn_clear_log.setText(self.translator.get("btn_clear_log"))

        # Read Tab
        self.lbl_uid.setText(self.translator.get("lbl_uid"))
        self.lbl_data.setText(self.translator.get("lbl_data"))
        self.lbl_read_block.setText(self.translator.get("lbl_block"))
        self.btn_read.setText(self.translator.get("btn_read"))

        # Write Tab
        self.lbl_write_data.setText(self.translator.get("lbl_write_data"))
        self.lbl_write_block.setText(self.translator.get("lbl_block"))
        self.btn_write.setText(self.translator.get("btn_write"))

        # Emulation Tab
        self.chk_emulation.setText(self.translator.get("chk_emulation_enable"))
        self.lbl_emulation_suffix.setText(self.translator.get("lbl_emulation_suffix"))
        self.cmb_emulation_suffix.setItemText(0, self.translator.get("opt_none"))
        self.cmb_emulation_suffix.setItemText(1, self.translator.get("opt_enter"))
        self.cmb_emulation_suffix.setItemText(2, self.translator.get("opt_tab"))

        # Settings Tab
        self.lbl_language.setText(self.translator.get("lbl_language"))
        self.btn_apply_lang.setText(self.translator.get("btn_apply_lang"))

        # Layout Direction
        if self.translator.lang == "ar":
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AppMainWindow()
    window.show()
    sys.exit(app.exec())
