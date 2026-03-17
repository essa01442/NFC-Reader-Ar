from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class SecurityTab(QWidget):
    def __init__(self, translator):
        super().__init__()
        self.translator = translator
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.lbl_security_info = QLabel("Security features (Authentication, Lock) will go here in future expansion.")
        layout.addWidget(self.lbl_security_info)
        layout.addStretch()

    def retranslate_ui(self):
        pass # To be added later
