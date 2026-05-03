from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from database import DatabaseManager

class CardsRegistryTab(QWidget):
    def __init__(self, translator):
        super().__init__()
        self.translator = translator
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # ── Form Group ────────────────────────────────────────────────
        self.grp_form = QGroupBox(self.translator.get("btn_add_card"))
        form_layout = QVBoxLayout(self.grp_form)

        row1 = QHBoxLayout()
        self.lbl_num = QLabel(self.translator.get("cards_number"))
        self.txt_num = QLineEdit()
        self.txt_num.setPlaceholderText("1-200")
        self.txt_num.setFixedWidth(60)

        self.lbl_uid = QLabel(self.translator.get("cards_uid"))
        self.txt_uid = QLineEdit()
        self.txt_uid.setPlaceholderText("04823E...")

        row1.addWidget(self.lbl_num)
        row1.addWidget(self.txt_num)
        row1.addWidget(self.lbl_uid)
        row1.addWidget(self.txt_uid)
        form_layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.lbl_domain = QLabel(self.translator.get("cards_domain"))
        self.txt_domain = QLineEdit()
        self.txt_domain.setPlaceholderText("google.com")

        row2.addWidget(self.lbl_domain)
        row2.addWidget(self.txt_domain)
        form_layout.addLayout(row2)

        row3 = QHBoxLayout()
        self.lbl_note = QLabel(self.translator.get("cards_note"))
        self.txt_note = QLineEdit()

        row3.addWidget(self.lbl_note)
        row3.addWidget(self.txt_note)
        form_layout.addLayout(row3)

        self.btn_save = QPushButton(self.translator.get("btn_add_card"))
        self.btn_save.clicked.connect(self._on_save_clicked)
        form_layout.addWidget(self.btn_save)

        layout.addWidget(self.grp_form)

        # ── Table ─────────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            self.translator.get("cards_number"),
            self.translator.get("cards_uid"),
            self.translator.get("cards_domain"),
            self.translator.get("cards_note"),
            ""
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        entries = self.db.get_all_registry_entries()
        self.table.setRowCount(len(entries))
        for row, e in enumerate(entries):
            self.table.setItem(row, 0, QTableWidgetItem(str(e.card_number)))
            self.table.setItem(row, 1, QTableWidgetItem(e.uid))
            self.table.setItem(row, 2, QTableWidgetItem(e.domain))
            self.table.setItem(row, 3, QTableWidgetItem(e.note))

            btn_del = QPushButton(self.translator.get("btn_delete_card"))
            btn_del.setProperty("card_number", e.card_number)
            btn_del.clicked.connect(self._on_delete_clicked)
            self.table.setCellWidget(row, 4, btn_del)

    def _on_save_clicked(self):
        try:
            num = int(self.txt_num.text())
            uid = self.txt_uid.text().strip()
            domain = self.txt_domain.text().strip()
            note = self.txt_note.text().strip()

            if not uid:
                raise ValueError("UID required")

            if self.db.upsert_card_registry(num, uid, domain, note):
                self.load_data()
                self.txt_num.clear()
                self.txt_uid.clear()
                self.txt_domain.clear()
                self.txt_note.clear()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def _on_delete_clicked(self):
        btn = self.sender()
        num = btn.property("card_number")
        if self.db.delete_card_from_registry(num):
            self.load_data()

    def set_current_uid(self, uid):
        self.txt_uid.setText(uid)

    def retranslate_ui(self):
        self.grp_form.setTitle(self.translator.get("btn_add_card"))
        self.lbl_num.setText(self.translator.get("cards_number"))
        self.lbl_uid.setText(self.translator.get("cards_uid"))
        self.lbl_domain.setText(self.translator.get("cards_domain"))
        self.lbl_note.setText(self.translator.get("cards_note"))
        self.btn_save.setText(self.translator.get("btn_add_card"))

        self.table.setHorizontalHeaderLabels([
            self.translator.get("cards_number"),
            self.translator.get("cards_uid"),
            self.translator.get("cards_domain"),
            self.translator.get("cards_note"),
            ""
        ])
        self.load_data()
