import sys
from PyQt6.QtWidgets import QApplication
from ui_components.main_window import AppMainWindow
from PyQt6.QtCore import pyqtSignal

def main():
    app = QApplication(sys.argv)
    window = AppMainWindow()
    window.show()

    app.aboutToQuit.connect(window.nfc_manager.cleanup)

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
