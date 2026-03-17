from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout
from database import DatabaseManager

class DashboardTab(QWidget):
    def __init__(self, translator):
        super().__init__()
        self.translator = translator
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Tools
        tools_layout = QHBoxLayout()
        self.btn_refresh = QPushButton(self.translator.get("btn_refresh_dashboard", "تحديث / Refresh"))
        self.btn_refresh.clicked.connect(self.load_data)
        tools_layout.addWidget(self.btn_refresh)
        tools_layout.addStretch()
        layout.addLayout(tools_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            self.translator.get("hdr_time", "الوقت / Time"),
            self.translator.get("hdr_uid", "المعرف / UID"),
            self.translator.get("hdr_action", "الإجراء / Action"),
            self.translator.get("hdr_details", "التفاصيل / Details")
        ])

        # Make it stretch
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table)

        self.load_data()

    def log_action(self, uid, action, details=""):
        self.db.add_record(uid, action, details)
        self.load_data()

    def load_data(self):
        records = self.db.get_recent_records()
        self.table.setRowCount(len(records))
        for row, r in enumerate(records):
            time_str = r.timestamp.strftime("%Y-%m-%d %H:%M:%S") if r.timestamp else ""
            self.table.setItem(row, 0, QTableWidgetItem(time_str))
            self.table.setItem(row, 1, QTableWidgetItem(r.uid))
            self.table.setItem(row, 2, QTableWidgetItem(r.action))
            self.table.setItem(row, 3, QTableWidgetItem(r.details))

    def retranslate_ui(self):
        self.btn_refresh.setText(self.translator.get("btn_refresh_dashboard", "تحديث / Refresh"))
        self.table.setHorizontalHeaderLabels([
            self.translator.get("hdr_time", "الوقت / Time"),
            self.translator.get("hdr_uid", "المعرف / UID"),
            self.translator.get("hdr_action", "الإجراء / Action"),
            self.translator.get("hdr_details", "التفاصيل / Details")
        ])
