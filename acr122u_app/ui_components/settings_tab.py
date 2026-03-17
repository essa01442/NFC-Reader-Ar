from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox
from PyQt6.QtCore import Qt

class SettingsTab(QWidget):
    def __init__(self, translator, nfc_manager, on_lang_changed_callback):
        super().__init__()
        self.translator = translator
        self.nfc_manager = nfc_manager
        self.on_lang_changed_callback = on_lang_changed_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Language Settings
        lang_layout = QHBoxLayout()
        self.lbl_language = QLabel(self.translator.get("lbl_language"))
        lang_layout.addWidget(self.lbl_language)

        self.cmb_lang = QComboBox()
        self.cmb_lang.addItem("العربية", "ar")
        self.cmb_lang.addItem("English", "en")
        idx = self.cmb_lang.findData(self.translator.lang)
        if idx >= 0:
            self.cmb_lang.setCurrentIndex(idx)

        self.btn_apply_lang = QPushButton(self.translator.get("btn_apply_lang"))
        self.btn_apply_lang.clicked.connect(self.on_lang_clicked)

        lang_layout.addWidget(self.cmb_lang)
        lang_layout.addWidget(self.btn_apply_lang)
        lang_layout.addStretch()

        layout.addLayout(lang_layout)

        # Reader Settings
        reader_layout = QHBoxLayout()
        self.lbl_reader_select = QLabel(self.translator.get("lbl_reader_select", "اختيار القارئ / Select Reader:"))
        reader_layout.addWidget(self.lbl_reader_select)

        self.cmb_readers = QComboBox()
        self.cmb_readers.currentTextChanged.connect(self.on_reader_selected)

        self.btn_rescan = QPushButton(self.translator.get("btn_rescan", "إعادة الفحص / Rescan"))
        self.btn_rescan.clicked.connect(self.on_rescan_clicked)

        reader_layout.addWidget(self.cmb_readers)
        reader_layout.addWidget(self.btn_rescan)
        reader_layout.addStretch()

        layout.addLayout(reader_layout)
        layout.addStretch()

        # Connect signals
        self.nfc_manager.available_readers_changed.connect(self.update_readers_list)

    def on_lang_clicked(self):
        lang = self.cmb_lang.currentData()
        self.on_lang_changed_callback(lang)

    def on_rescan_clicked(self):
        self.btn_rescan.setText(self.translator.get("btn_scanning", "جاري البحث... / Scanning..."))
        self.btn_rescan.setEnabled(False)
        self.nfc_manager.rescan_readers()
        # Reset button text after 1 second
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self._reset_rescan_btn())

    def _reset_rescan_btn(self):
        self.btn_rescan.setText(self.translator.get("btn_rescan", "إعادة الفحص / Rescan"))
        self.btn_rescan.setEnabled(True)

    def on_reader_selected(self, reader_name):
        self.nfc_manager.select_reader(reader_name)

    def update_readers_list(self, readers_list):
        current_selection = self.cmb_readers.currentText()
        self.cmb_readers.blockSignals(True)
        self.cmb_readers.clear()
        self.cmb_readers.addItems(readers_list)

        # Restore selection if exists
        idx = self.cmb_readers.findText(current_selection)
        if idx >= 0:
            self.cmb_readers.setCurrentIndex(idx)
        elif readers_list:
            self.cmb_readers.setCurrentIndex(0)

        self.cmb_readers.blockSignals(False)
        if readers_list and idx < 0:
            self.on_reader_selected(readers_list[0])

    def retranslate_ui(self):
        self.lbl_language.setText(self.translator.get("lbl_language"))
        self.btn_apply_lang.setText(self.translator.get("btn_apply_lang"))
        self.lbl_reader_select.setText(self.translator.get("lbl_reader_select", "اختيار القارئ / Select Reader:"))
        self.btn_rescan.setText(self.translator.get("btn_rescan", "إعادة الفحص / Rescan"))
