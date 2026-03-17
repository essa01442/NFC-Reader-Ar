from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QGroupBox, QComboBox, QMessageBox
from PyQt6.QtCore import Qt
import datetime

class LogPanel(QGroupBox):
    def __init__(self, translator):
        super().__init__()
        self.translator = translator
        self.init_ui()

    def init_ui(self):
        self.setTitle(self.translator.get("log_title"))
        layout = QVBoxLayout(self)

        # Tools layout
        tools_layout = QHBoxLayout()
        self.cmb_filter = QComboBox()
        self.cmb_filter.addItem("الكل / All", "all")
        self.cmb_filter.addItem("معلومات / Info", "info")
        self.cmb_filter.addItem("أخطاء / Error", "error")
        self.cmb_filter.currentIndexChanged.connect(self.apply_filter)

        self.btn_save_log = QPushButton(self.translator.get("btn_save_log", "حفظ السجل"))
        self.btn_save_log.clicked.connect(self.save_log)

        self.btn_clear_log = QPushButton(self.translator.get("btn_clear_log"))
        self.btn_clear_log.clicked.connect(self.clear_log)

        tools_layout.addWidget(self.cmb_filter)
        tools_layout.addStretch()
        tools_layout.addWidget(self.btn_save_log)
        tools_layout.addWidget(self.btn_clear_log)

        layout.addLayout(tools_layout)

        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        layout.addWidget(self.txt_log)

        # Store raw entries for filtering
        self.log_entries = []

    def log(self, message, is_error=False):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = {"time": timestamp, "msg": message, "error": is_error}
        self.log_entries.append(entry)
        self.apply_filter()

    def apply_filter(self):
        filter_type = self.cmb_filter.currentData()
        self.txt_log.clear()

        for entry in self.log_entries:
            if filter_type == "info" and entry["error"]:
                continue
            if filter_type == "error" and not entry["error"]:
                continue

            color = "red" if entry["error"] else "black"
            # Format nicely
            html = f"<span style='color: gray;'>[{entry['time']}]</span> <span style='color: {color};'>{entry['msg']}</span>"
            self.txt_log.append(html)

    def clear_log(self):
        self.log_entries.clear()
        self.txt_log.clear()

    def save_log(self):
        from PyQt6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(self, "Save Log", "", "Text Files (*.txt);;All Files (*)")
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    for entry in self.log_entries:
                        f.write(f"[{entry['time']}] {'ERROR: ' if entry['error'] else ''}{entry['msg']}\n")
                QMessageBox.information(self, "Success", "Log saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save log: {e}")

    def retranslate_ui(self):
        self.setTitle(self.translator.get("log_title"))
        self.btn_clear_log.setText(self.translator.get("btn_clear_log"))
        self.btn_save_log.setText(self.translator.get("btn_save_log", "حفظ السجل"))
        # Retranslate combobox items keeping their data
        self.cmb_filter.setItemText(0, self.translator.get("opt_all", "الكل / All"))
        self.cmb_filter.setItemText(1, self.translator.get("opt_info", "معلومات / Info"))
        self.cmb_filter.setItemText(2, self.translator.get("opt_error", "أخطاء / Error"))
