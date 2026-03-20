class ThemeManager:
    """Manages the UI theming logic (Dark Mode/Light Mode)"""

    @staticmethod
    def get_light_theme():
        return """
            QMainWindow {
                background-color: #f5f6fa;
            }
            QWidget {
                color: #2f3640;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #dcdde1;
                background-color: #ffffff;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #3a86c8;
                color: white;
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2a6099;
                font-weight: bold;
            }
            QTabBar::tab:!selected {
                opacity: 0.8;
            }
            QPushButton {
                background-color: #0097e6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00a8ff;
            }
            QPushButton:pressed {
                background-color: #0082c8;
            }
            QPushButton:disabled {
                background-color: #dcdde1;
                color: #7f8fa6;
            }
            QLineEdit, QTextEdit, QSpinBox, QComboBox {
                background-color: #ffffff;
                border: 1px solid #dcdde1;
                padding: 6px;
                border-radius: 4px;
                color: #2f3640;
            }
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 1px solid #0097e6;
            }
            QGroupBox {
                border: 1px solid #dcdde1;
                border-radius: 6px;
                margin-top: 14px;
                background-color: #ffffff;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #2a6099;
            }
            QStatusBar {
                background-color: #ffffff;
                border-top: 1px solid #dcdde1;
            }
        """

    @staticmethod
    def get_dark_theme():
        return """
            QMainWindow {
                background-color: #1e272e;
            }
            QWidget {
                color: #d2dae2;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #485460;
                background-color: #2c3e50;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #3a86c8;
                color: white;
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2a6099;
                font-weight: bold;
            }
            QPushButton {
                background-color: #0097e6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00a8ff;
            }
            QPushButton:pressed {
                background-color: #0082c8;
            }
            QPushButton:disabled {
                background-color: #485460;
                color: #808e9b;
            }
            QLineEdit, QTextEdit, QSpinBox, QComboBox {
                background-color: #34495e;
                border: 1px solid #485460;
                padding: 6px;
                border-radius: 4px;
                color: #ecf0f1;
            }
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 1px solid #0097e6;
            }
            QGroupBox {
                border: 1px solid #485460;
                border-radius: 6px;
                margin-top: 14px;
                background-color: #2c3e50;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #3a86c8;
            }
            QStatusBar {
                background-color: #2c3e50;
                border-top: 1px solid #485460;
            }
        """
