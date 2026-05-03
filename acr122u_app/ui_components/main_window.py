from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QStatusBar, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from i18n import Translator
from reader import NFCReaderManager
from emulator import KeyboardEmulator

from ui_components.read_tab import ReadTab
from ui_components.write_tab import WriteTab
from ui_components.other_tab import OtherTab
from ui_components.cards_registry_tab import CardsRegistryTab
from ui_components.security_tab import SecurityTab
from ui_components.emulation_tab import EmulationTab
from ui_components.settings_tab import SettingsTab
from ui_components.log_panel import LogPanel
from ui_components.theme import ThemeManager
from ui_components.dashboard_tab import DashboardTab

class LEDIndicator(QLabel):
    def __init__(self, color="gray"):
        super().__init__()
        self.setFixedSize(16, 16)
        self.set_color(color)

    def set_color(self, color):
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 8px;
                border: 1px solid dark{color if color != "gray" else "gray"};
            }}
        """)

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
        self.resize(900, 700)

        # Apply global RTL/LTR direction based on language
        if self.translator.lang == "ar":
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        font = QFont("Segoe UI", 10)
        self.setFont(font)

        # Global Stylesheet - Default to Dark
        self.setStyleSheet(ThemeManager.get_dark_theme())

        # Main widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Header Info (Status)
        header_layout = QHBoxLayout()

        # Reader LED and status
        self.led_reader = LEDIndicator("red")
        header_layout.addWidget(self.led_reader)

        self.lbl_reader_status = QLabel(self.translator.get("status_reader_disconnected"))
        self.lbl_reader_status.setStyleSheet("color: #f44336; font-weight: bold;")
        header_layout.addWidget(self.lbl_reader_status)

        header_layout.addStretch()

        # Card LED and status
        self.led_card = LEDIndicator("gray")
        header_layout.addWidget(self.led_card)

        self.lbl_card_status = QLabel(self.translator.get("status_card_absent"))
        self.lbl_card_status.setStyleSheet("color: gray;")
        header_layout.addWidget(self.lbl_card_status)

        self.main_layout.addLayout(header_layout)

        # Tabs
        self.tabs = QTabWidget()
        self.tab_read = ReadTab(self.translator, self.nfc_manager, self.log, self.on_error_occurred, self.show_success_message)
        self.tab_write = WriteTab(self.translator, self.nfc_manager, self.log, self.on_error_occurred, self.show_success_message)
        self.tab_other = OtherTab(self.translator, self.nfc_manager, self.log, self.on_error_occurred, self.show_success_message)
        self.tab_cards = CardsRegistryTab(self.translator)
        self.tab_security = SecurityTab(self.translator, self.nfc_manager)
        self.tab_emulation = EmulationTab(self.translator, self.emulator)
        self.tab_settings = SettingsTab(self.translator, self.nfc_manager, self.on_lang_changed)
        self.tab_dashboard = DashboardTab(self.translator)

        # Final order: [READ] [WRITE] [OTHER] [CARDS] [SECURITY] [EMULATION] [SETTINGS] [DASHBOARD]
        self.tabs.addTab(self.tab_read, self.translator.get("tab_read"))
        self.tabs.addTab(self.tab_write, self.translator.get("tab_write"))
        self.tabs.addTab(self.tab_other, self.translator.get("tab_other"))
        self.tabs.addTab(self.tab_cards, self.translator.get("tab_cards"))
        self.tabs.addTab(self.tab_security, self.translator.get("tab_security"))
        self.tabs.addTab(self.tab_emulation, self.translator.get("tab_emulation"))
        self.tabs.addTab(self.tab_settings, self.translator.get("tab_settings"))
        self.tabs.addTab(self.tab_dashboard, self.translator.get("tab_dashboard"))

        self.main_layout.addWidget(self.tabs, stretch=2)

        # Log Section
        self.log_panel = LogPanel(self.translator)
        self.main_layout.addWidget(self.log_panel, stretch=1)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Waiting Overlay (Simple version)
        self.overlay = QFrame(self.central_widget)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 180); color: white;")
        self.overlay.hide()
        overlay_layout = QVBoxLayout(self.overlay)
        self.lbl_overlay = QLabel(self.translator.get("waiting_for_tag"))
        self.lbl_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_overlay.setStyleSheet("font-size: 18pt; font-weight: bold;")
        overlay_layout.addWidget(self.lbl_overlay)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay.resize(self.size())

    def show_waiting_overlay(self, message=None):
        if message:
            self.lbl_overlay.setText(message)
        else:
            self.lbl_overlay.setText(self.translator.get("waiting_for_tag"))
        self.overlay.show()
        self.overlay.raise_()

    def hide_waiting_overlay(self):
        self.overlay.hide()

    def setup_signals(self):
        self.nfc_manager.reader_connected.connect(self.on_reader_connected)
        self.nfc_manager.reader_disconnected.connect(self.on_reader_disconnected)
        self.nfc_manager.card_detected.connect(self.on_card_detected)
        self.nfc_manager.card_info_ready.connect(self.on_card_info_ready)
        self.nfc_manager.card_removed_signal.connect(self.on_card_removed)
        self.nfc_manager.error_occurred.connect(self.on_error_occurred)
        self.nfc_manager.pcsc_error_occurred.connect(self.on_pcsc_error)

    def log(self, message, is_error=False):
        self.log_panel.log(message, is_error)

    def on_reader_connected(self, reader_name):
        self.lbl_reader_status.setText(self.translator.get("status_reader_connected") + f" ({reader_name})")
        self.lbl_reader_status.setStyleSheet("color: #4caf50; font-weight: bold;")
        self.led_reader.set_color("#4caf50")
        self.log(self.translator.get("log_reader_found", reader_name))

    def on_reader_disconnected(self):
        self.lbl_reader_status.setText(self.translator.get("status_reader_disconnected"))
        self.lbl_reader_status.setStyleSheet("color: #f44336; font-weight: bold;")
        self.led_reader.set_color("#f44336")
        self.log(self.translator.get("log_reader_lost"), is_error=True)
        self.on_card_removed()

    def on_card_detected(self, uid):
        self.hide_waiting_overlay()
        self.lbl_card_status.setText(self.translator.get("status_card_present") + f" - UID: {uid}")
        self.lbl_card_status.setStyleSheet("color: #4caf50; font-weight: bold;")
        self.led_card.set_color("#4caf50")

        self.tab_read.set_uid(uid)
        self.tab_cards.set_current_uid(uid)
        self.log(self.translator.get("log_card_inserted", uid))
        self.tab_dashboard.log_action(uid, "DETECT", "Card Inserted")

        if self.emulator.enabled and self.tab_emulation.get_emulate_source() == "uid":
            self.emulator.type_string(uid)
        self.tab_emulation.update_emulated_card(uid)

        # Handle multi-step operations in OtherTab
        if hasattr(self, 'tab_other'):
            self.tab_other.handle_card_detected()

    def on_card_info_ready(self, info: dict):
        self.tab_read.show_card_info(info)
        self.tab_security.update_card_info(info)

        uid = info.get('uid_formatted') or self.tab_read.txt_uid.text()
        card_type = info.get('tag_type', '')

        ndef_text = ""
        for rec in info.get('ndef_records', []):
            content = rec.get('content', '')
            rec_type = rec.get('record_type', '')
            if 'text/plain' in rec_type or rec_type == 'Text':
                ndef_text = content
                break

        self.tab_emulation.update_emulated_card(uid, card_type, ndef_text)

        ndef_available = info.get('ndef_available', 0)
        if ndef_available:
            self.tab_write.update_card_capacity(ndef_available)

        if (self.emulator.enabled
                and self.tab_emulation.get_emulate_source() == "ndef"
                and ndef_text):
            self.emulator.type_string(ndef_text)

    def on_card_removed(self):
        self.lbl_card_status.setText(self.translator.get("status_card_absent"))
        self.lbl_card_status.setStyleSheet("color: gray;")
        self.led_card.set_color("gray")

        self.tab_read.clear_data()
        self.tab_security.clear_card_info()
        self.log(self.translator.get("log_card_removed"))

    def on_error_occurred(self, err_msg):
        self.log(f"Error: {err_msg}", is_error=True)
        self.status_bar.showMessage(err_msg, 5000)
        self.status_bar.setStyleSheet("color: #f44336; font-weight: bold;")

    def on_pcsc_error(self, err_msg):
        self.log(f"PC/SC Error: {err_msg}", is_error=True)
        self.status_bar.showMessage(err_msg, 10000)
        self.status_bar.setStyleSheet("color: orange; font-weight: bold;")

    def show_success_message(self, msg):
        self.status_bar.showMessage(msg, 5000)
        self.status_bar.setStyleSheet("color: #4caf50; font-weight: bold;")

    def on_lang_changed(self, lang):
        self.translator.set_language(lang)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(self.translator.get("app_title"))

        # Tabs
        self.tabs.setTabText(0, self.translator.get("tab_read"))
        self.tabs.setTabText(1, self.translator.get("tab_write"))
        self.tabs.setTabText(2, self.translator.get("tab_other"))
        self.tabs.setTabText(3, self.translator.get("tab_cards"))
        self.tabs.setTabText(4, self.translator.get("tab_security"))
        self.tabs.setTabText(5, self.translator.get("tab_emulation"))
        self.tabs.setTabText(6, self.translator.get("tab_settings"))
        self.tabs.setTabText(7, self.translator.get("tab_dashboard"))

        # Reader / Card Status
        if self.nfc_manager.reader:
            self.lbl_reader_status.setText(self.translator.get("status_reader_connected") + f" ({self.nfc_manager.reader})")
        else:
            self.lbl_reader_status.setText(self.translator.get("status_reader_disconnected"))

        if self.tab_read.txt_uid.text():
            self.lbl_card_status.setText(self.translator.get("status_card_present") + f" - UID: {self.tab_read.txt_uid.text()}")
        else:
            self.lbl_card_status.setText(self.translator.get("status_card_absent"))

        # Retranslate child tabs
        self.tab_read.retranslate_ui()
        self.tab_write.retranslate_ui()
        self.tab_other.retranslate_ui()
        self.tab_cards.retranslate_ui()
        self.tab_security.retranslate_ui()
        self.tab_emulation.retranslate_ui()
        self.tab_settings.retranslate_ui()
        self.tab_dashboard.retranslate_ui()
        self.log_panel.retranslate_ui()

        self.lbl_overlay.setText(self.translator.get("waiting_for_tag"))

        # Layout Direction
        if self.translator.lang == "ar":
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
