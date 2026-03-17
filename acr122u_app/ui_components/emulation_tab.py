from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox

class EmulationTab(QWidget):
    def __init__(self, translator, emulator):
        super().__init__()
        self.translator = translator
        self.emulator = emulator
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

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

    def on_emulation_toggled(self, state):
        self.emulator.set_enabled(state == 2)

    def on_emulation_suffix_changed(self, index):
        suffix = self.cmb_emulation_suffix.currentData()
        self.emulator.set_suffix(suffix)

    def retranslate_ui(self):
        self.chk_emulation.setText(self.translator.get("chk_emulation_enable"))
        self.lbl_emulation_suffix.setText(self.translator.get("lbl_emulation_suffix"))
        self.cmb_emulation_suffix.setItemText(0, self.translator.get("opt_none"))
        self.cmb_emulation_suffix.setItemText(1, self.translator.get("opt_enter"))
        self.cmb_emulation_suffix.setItemText(2, self.translator.get("opt_tab"))
