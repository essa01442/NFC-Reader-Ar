from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox,
    QGroupBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class EmulationTab(QWidget):
    def __init__(self, translator, emulator):
        super().__init__()
        self.translator = translator
        self.emulator = emulator
        self._last_uid = ""
        self._last_card_type = ""
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

        # ── Last emulated card info ────────────────────────────────────────
        self.grp_last = QGroupBox(self.translator.get("section_last_emulated"))
        last_layout = QVBoxLayout(self.grp_last)
        last_layout.setSpacing(4)

        uid_row = QHBoxLayout()
        self.lbl_emulated_uid_key = QLabel(self.translator.get("lbl_emulated_uid"))
        self.lbl_emulated_uid_key.setFont(QFont("", -1, QFont.Weight.Bold))
        uid_row.addWidget(self.lbl_emulated_uid_key)
        self.lbl_emulated_uid_val = QLabel("—")
        self.lbl_emulated_uid_val.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        uid_row.addWidget(self.lbl_emulated_uid_val, stretch=1)
        last_layout.addLayout(uid_row)

        type_row = QHBoxLayout()
        self.lbl_emulated_type_key = QLabel(self.translator.get("lbl_emulated_type"))
        self.lbl_emulated_type_key.setFont(QFont("", -1, QFont.Weight.Bold))
        type_row.addWidget(self.lbl_emulated_type_key)
        self.lbl_emulated_type_val = QLabel("—")
        type_row.addWidget(self.lbl_emulated_type_val, stretch=1)
        last_layout.addLayout(type_row)

        self.lbl_no_emulated = QLabel(self.translator.get("no_emulated_card"))
        self.lbl_no_emulated.setStyleSheet("color: gray; font-style: italic;")
        last_layout.addWidget(self.lbl_no_emulated)

        layout.addWidget(self.grp_last)
        layout.addStretch()

    def on_emulation_toggled(self, state):
        self.emulator.set_enabled(state == 2)

    def on_emulation_suffix_changed(self, index):
        suffix = self.cmb_emulation_suffix.currentData()
        self.emulator.set_suffix(suffix)

    def update_emulated_card(self, uid: str, card_type: str = ""):
        """Update the display with the last emulated card's info."""
        self._last_uid = uid
        self._last_card_type = card_type
        self.lbl_emulated_uid_val.setText(uid or "—")
        self.lbl_emulated_type_val.setText(card_type or "—")
        self.lbl_no_emulated.setVisible(not uid)

    def clear_emulated_card(self):
        """Clear last emulated card display."""
        self._last_uid = ""
        self._last_card_type = ""
        self.lbl_emulated_uid_val.setText("—")
        self.lbl_emulated_type_val.setText("—")
        self.lbl_no_emulated.setVisible(True)

    def retranslate_ui(self):
        self.chk_emulation.setText(self.translator.get("chk_emulation_enable"))
        self.lbl_emulation_suffix.setText(self.translator.get("lbl_emulation_suffix"))
        self.cmb_emulation_suffix.setItemText(0, self.translator.get("opt_none"))
        self.cmb_emulation_suffix.setItemText(1, self.translator.get("opt_enter"))
        self.cmb_emulation_suffix.setItemText(2, self.translator.get("opt_tab"))
        self.grp_last.setTitle(self.translator.get("section_last_emulated"))
        self.lbl_emulated_uid_key.setText(self.translator.get("lbl_emulated_uid"))
        self.lbl_emulated_type_key.setText(self.translator.get("lbl_emulated_type"))
        self.lbl_no_emulated.setText(self.translator.get("no_emulated_card"))
