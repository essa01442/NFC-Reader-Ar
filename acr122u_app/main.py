import sys
from PyQt6.QtWidgets import QApplication
from ui import AppMainWindow
from PyQt6.QtCore import pyqtSignal

def main():
    app = QApplication(sys.argv)
    window = AppMainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
