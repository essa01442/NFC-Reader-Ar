from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QScrollArea, QFrame, QMessageBox, QProgressBar,
    QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

class OtherTab(QWidget):
    def __init__(self, translator, nfc_manager, log_callback, error_callback, success_callback):
        super().__init__()
        self.translator = translator
        self.nfc_manager = nfc_manager
        self.log = log_callback
        self.on_error = error_callback
        self.on_success = success_callback

        self.copy_data = None
        self.is_waiting_for_copy_target = False

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        scroll_layout = QVBoxLayout(container)

        # ── Copy Tag ──────────────────────────────────────────────────
        self.grp_copy = QGroupBox(self.translator.get("other_copy_tag"))
        copy_layout = QVBoxLayout(self.grp_copy)

        self.lbl_copy_desc = QLabel(self.translator.get("other_copy_desc"))
        self.lbl_copy_desc.setWordWrap(True)
        copy_layout.addWidget(self.lbl_copy_desc)

        self.btn_copy = QPushButton(self.translator.get("btn_start"))
        self.btn_copy.clicked.connect(self._on_copy_clicked)
        copy_layout.addWidget(self.btn_copy)
        scroll_layout.addWidget(self.grp_copy)

        # ── Erase Tag ──────────────────────────────────────────────────
        self.grp_erase = QGroupBox(self.translator.get("other_erase_tag"))
        erase_layout = QVBoxLayout(self.grp_erase)

        self.lbl_erase_desc = QLabel(self.translator.get("other_erase_desc"))
        erase_layout.addWidget(self.lbl_erase_desc)

        self.btn_erase = QPushButton(self.translator.get("btn_start"))
        self.btn_erase.clicked.connect(self._on_erase_clicked)
        erase_layout.addWidget(self.btn_erase)
        scroll_layout.addWidget(self.grp_erase)

        # ── Password Management ───────────────────────────────────────
        self.grp_pwd = QGroupBox(self.translator.get("other_set_password") + " / " + self.translator.get("other_remove_password"))
        pwd_layout = QVBoxLayout(self.grp_pwd)

        # Set Password Row
        set_pwd_row = QHBoxLayout()
        self.lbl_new_password = QLabel(self.translator.get("lbl_new_password"))
        set_pwd_row.addWidget(self.lbl_new_password)
        self.txt_new_password = QLineEdit()
        self.txt_new_password.setPlaceholderText("AABBCCDD")
        self.txt_new_password.setMaxLength(8)
        self.txt_new_password.setFixedWidth(100)
        set_pwd_row.addWidget(self.txt_new_password)

        self.btn_set_pwd = QPushButton(self.translator.get("btn_set_password"))
        self.btn_set_pwd.clicked.connect(self._on_set_password)
        set_pwd_row.addWidget(self.btn_set_pwd)
        pwd_layout.addLayout(set_pwd_row)

        # Remove Password Row
        rem_pwd_row = QHBoxLayout()
        self.lbl_curr_password = QLabel(self.translator.get("lbl_current_password_remove"))
        rem_pwd_row.addWidget(self.lbl_curr_password)
        self.txt_curr_password = QLineEdit()
        self.txt_curr_password.setPlaceholderText("AABBCCDD")
        self.txt_curr_password.setMaxLength(8)
        self.txt_curr_password.setFixedWidth(100)
        rem_pwd_row.addWidget(self.txt_curr_password)

        self.btn_rem_pwd = QPushButton(self.translator.get("btn_remove_password"))
        self.btn_rem_pwd.clicked.connect(self._on_remove_password)
        rem_pwd_row.addWidget(self.btn_rem_pwd)
        pwd_layout.addLayout(rem_pwd_row)

        scroll_layout.addWidget(self.grp_pwd)

        # ── Lock Tag ──────────────────────────────────────────────────
        self.grp_lock = QGroupBox(self.translator.get("other_lock_tag"))
        lock_layout = QVBoxLayout(self.grp_lock)

        self.lbl_lock_desc = QLabel(self.translator.get("other_lock_desc"))
        self.lbl_lock_desc.setStyleSheet("color: #f44336; font-weight: bold;")
        lock_layout.addWidget(self.lbl_lock_desc)

        self.btn_lock = QPushButton(self.translator.get("btn_start"))
        self.btn_lock.setStyleSheet("background-color: #f44336;")
        self.btn_lock.clicked.connect(self._on_lock_clicked)
        lock_layout.addWidget(self.btn_lock)
        scroll_layout.addWidget(self.grp_lock)

        scroll_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def _on_copy_clicked(self):
        if not self.nfc_manager.connection:
            self.on_error(self.translator.get("warn_no_card"))
            return

        try:
            self.copy_data = self.nfc_manager.copy_tag_read()
            self.is_waiting_for_copy_target = True

            main_win = self.window()
            if hasattr(main_win, 'show_waiting_overlay'):
                main_win.show_waiting_overlay(self.translator.get("waiting_for_tag"))

            self.on_success(self.translator.get("operation_success") + " (Read)")
        except Exception as e:
            self.on_error(str(e))

    def handle_card_detected(self):
        """Called by main_window when a card is detected if we are in a multi-step operation."""
        if self.is_waiting_for_copy_target and self.copy_data:
            try:
                self.nfc_manager.copy_tag_write(self.copy_data)
                self.on_success(self.translator.get("operation_success") + " (Write)")
                self.copy_data = None
                self.is_waiting_for_copy_target = False

                main_win = self.window()
                if hasattr(main_win, 'hide_waiting_overlay'):
                    main_win.hide_waiting_overlay()

                QMessageBox.information(self, self.translator.get("msg_success"), self.translator.get("operation_success"))
            except Exception as e:
                self.on_error(str(e))
                self.is_waiting_for_copy_target = False
                main_win = self.window()
                if hasattr(main_win, 'hide_waiting_overlay'):
                    main_win.hide_waiting_overlay()

    def _on_erase_clicked(self):
        if not self.nfc_manager.connection:
            self.on_error(self.translator.get("warn_no_card"))
            return

        reply = QMessageBox.question(self, self.translator.get("msg_warning"), self.translator.get("other_erase_desc"),
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.nfc_manager.erase_tag()
                self.on_success(self.translator.get("operation_success"))
                QMessageBox.information(self, self.translator.get("msg_success"), self.translator.get("operation_success"))
            except Exception as e:
                self.on_error(str(e))

    def _on_lock_clicked(self):
        if not self.nfc_manager.connection:
            self.on_error(self.translator.get("warn_no_card"))
            return

        reply = QMessageBox.question(self, self.translator.get("msg_warning"), self.translator.get("warn_readonly_confirm"),
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.nfc_manager.set_read_only()
                self.on_success(self.translator.get("operation_success"))
                QMessageBox.information(self, self.translator.get("msg_success"), self.translator.get("operation_success"))
            except Exception as e:
                self.on_error(str(e))

    @staticmethod
    def _parse_hex(text: str, expected_bytes: int):
        text = text.strip().upper().replace(' ', '')
        if len(text) != expected_bytes * 2:
            raise ValueError(f"Expected {expected_bytes * 2} hex chars")
        return [int(text[i:i+2], 16) for i in range(0, len(text), 2)]

    def _on_set_password(self):
        if not self.nfc_manager.connection:
            self.on_error(self.translator.get("warn_no_card"))
            return

        pwd_text = self.txt_new_password.text().strip()
        try:
            pwd_bytes = self._parse_hex(pwd_text, 4)
            # Default PACK for simplicity or can add field
            self.nfc_manager.set_password(pwd_bytes, [0x00, 0x00])
            self.on_success(self.translator.get("log_password_set"))
            QMessageBox.information(self, self.translator.get("msg_success"), self.translator.get("log_password_set"))
        except Exception as e:
            self.on_error(str(e))

    def _on_remove_password(self):
        if not self.nfc_manager.connection:
            self.on_error(self.translator.get("warn_no_card"))
            return

        pwd_text = self.txt_curr_password.text().strip()
        try:
            pwd_bytes = None
            if pwd_text:
                pwd_bytes = self._parse_hex(pwd_text, 4)
            self.nfc_manager.remove_password(pwd_bytes)
            self.on_success(self.translator.get("log_password_removed"))
            QMessageBox.information(self, self.translator.get("msg_success"), self.translator.get("log_password_removed"))
        except Exception as e:
            self.on_error(str(e))

    def retranslate_ui(self):
        self.grp_copy.setTitle(self.translator.get("other_copy_tag"))
        self.lbl_copy_desc.setText(self.translator.get("other_copy_desc"))
        self.btn_copy.setText(self.translator.get("btn_start"))

        self.grp_erase.setTitle(self.translator.get("other_erase_tag"))
        self.lbl_erase_desc.setText(self.translator.get("other_erase_desc"))
        self.btn_erase.setText(self.translator.get("btn_start"))

        self.grp_pwd.setTitle(self.translator.get("other_set_password") + " / " + self.translator.get("other_remove_password"))
        self.lbl_new_password.setText(self.translator.get("lbl_new_password"))
        self.btn_set_pwd.setText(self.translator.get("btn_set_password"))
        self.lbl_curr_password.setText(self.translator.get("lbl_current_password_remove"))
        self.btn_rem_pwd.setText(self.translator.get("btn_remove_password"))

        self.grp_lock.setTitle(self.translator.get("other_lock_tag"))
        self.lbl_lock_desc.setText(self.translator.get("other_lock_desc"))
        self.btn_lock.setText(self.translator.get("btn_start"))
