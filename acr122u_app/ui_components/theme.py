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
        # Colors inspired by NFC Tools:
        # BACKGROUND = "#1a1a2e"
        # SURFACE = "#16213e"
        # ACCENT = "#0f3460"
        # HIGHLIGHT = "#533483"
        # TEXT_PRIMARY = "#e0e0e0"
        # SUCCESS = "#4caf50"
        # ERROR = "#f44336"
        # BORDER = "#2d2d44"

        return """
            QMainWindow {
                background-color: #1a1a2e;
            }
            QWidget {
                color: #e0e0e0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            QTabWidget::pane {
                border: 1px solid #2d2d44;
                background-color: #16213e;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #0f3460;
                color: #e0e0e0;
                padding: 10px 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: #533483;
                font-weight: bold;
            }
            QPushButton {
                background-color: #0f3460;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #533483;
            }
            QPushButton:pressed {
                background-color: #16213e;
            }
            QPushButton:disabled {
                background-color: #2d2d44;
                color: #9e9e9e;
            }
            QLineEdit, QTextEdit, QSpinBox, QComboBox {
                background-color: #16213e;
                border: 1px solid #2d2d44;
                padding: 6px;
                border-radius: 4px;
                color: #e0e0e0;
            }
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 1px solid #533483;
            }
            QGroupBox {
                border: 1px solid #2d2d44;
                border-radius: 6px;
                margin-top: 14px;
                background-color: #16213e;
                padding-top: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                color: #e0e0e0;
            }
            QStatusBar {
                background-color: #16213e;
                border-top: 1px solid #2d2d44;
                color: #e0e0e0;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #1a1a2e;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #2d2d44;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #533483;
            }
            QHeaderView::section {
                background-color: #0f3460;
                color: white;
                padding: 4px;
                border: 1px solid #2d2d44;
            }
            QTableWidget {
                gridline-color: #2d2d44;
                background-color: #16213e;
                alternate-background-color: #1a1a2e;
            }
        """
