try:
    from PyQt6.QtWidgets import QApplication
    import pynput
    # Pynput needs display
    import os
    os.environ["DISPLAY"] = ":99"
    from ui_components.main_window import AppMainWindow
    print("Imports passed successfully!")
except Exception as e:
    print(e)
