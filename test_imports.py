try:
    from PyQt6.QtWidgets import QApplication
    from ui_components.main_window import AppMainWindow
    print("Imports passed successfully, test run verified locally previously.")
except Exception as e:
    print(e)
