import platform
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox, QScrollArea, QFrame, QApplication,
    QLineEdit, QMessageBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from diagnostics import SystemDiagnostics


class _DiagnosticsWorker(QThread):
    """Run diagnostics in a background thread to avoid blocking the UI."""
    finished = pyqtSignal(dict)

    def run(self):
        result = SystemDiagnostics.run_full_diagnostics()
        self.finished.emit(result)


class SecurityTab(QWidget):
    def __init__(self, translator, nfc_manager=None):
        super().__init__()
        self.translator = translator
        self.nfc_manager = nfc_manager
        self._worker = None
        self._current_card_info = None
        self.init_ui()

    def init_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        # ── Title ─────────────────────────────────────────────────────────
        self.lbl_title = QLabel(self.translator.get(
            "security_title", "الصلاحيات وتشخيص الجهاز / Permissions & Device Diagnostics"))
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        self.lbl_title.setFont(font)
        outer.addWidget(self.lbl_title)

        # ── Card Protection Management ─────────────────────────────────────
        prot_group = QGroupBox(self.translator.get(
            "section_card_protection", "إدارة حماية البطاقة"))
        prot_layout = QVBoxLayout(prot_group)
        prot_layout.setSpacing(8)

        # Note label
        self.lbl_protection_note = QLabel(self.translator.get(
            "lbl_protection_note",
            "ملاحظة: عمليات الحماية تدعم بطاقات NTAG213/215/216"))
        self.lbl_protection_note.setWordWrap(True)
        self.lbl_protection_note.setStyleSheet("color: gray; font-style: italic;")
        prot_layout.addWidget(self.lbl_protection_note)

        # ─ Set password row ─────────────────────────────────────────────
        set_pwd_row = QHBoxLayout()
        self.lbl_new_password = QLabel(self.translator.get(
            "lbl_new_password", "كلمة المرور الجديدة (8 أحرف هكس):"))
        set_pwd_row.addWidget(self.lbl_new_password)
        self.txt_new_password = QLineEdit()
        self.txt_new_password.setPlaceholderText("AABBCCDD")
        self.txt_new_password.setMaxLength(8)
        self.txt_new_password.setFixedWidth(120)
        set_pwd_row.addWidget(self.txt_new_password)

        self.lbl_pack_code = QLabel(self.translator.get(
            "lbl_pack_code", "رمز التأكيد PACK (4 أحرف هكس):"))
        set_pwd_row.addWidget(self.lbl_pack_code)
        self.txt_pack_code = QLineEdit()
        self.txt_pack_code.setPlaceholderText("AABB")
        self.txt_pack_code.setMaxLength(4)
        self.txt_pack_code.setFixedWidth(80)
        set_pwd_row.addWidget(self.txt_pack_code)

        self.btn_set_password = QPushButton(self.translator.get(
            "btn_set_password", "🔒 تعيين كلمة المرور"))
        self.btn_set_password.clicked.connect(self._on_set_password)
        set_pwd_row.addWidget(self.btn_set_password)
        set_pwd_row.addStretch()
        prot_layout.addLayout(set_pwd_row)

        # ─ Remove password row ──────────────────────────────────────────
        rem_pwd_row = QHBoxLayout()
        self.lbl_current_password_remove = QLabel(self.translator.get(
            "lbl_current_password_remove", "كلمة المرور الحالية (لإزالتها):"))
        rem_pwd_row.addWidget(self.lbl_current_password_remove)
        self.txt_current_password = QLineEdit()
        self.txt_current_password.setPlaceholderText("AABBCCDD")
        self.txt_current_password.setMaxLength(8)
        self.txt_current_password.setFixedWidth(120)
        self.txt_current_password.setEchoMode(QLineEdit.EchoMode.Password)
        rem_pwd_row.addWidget(self.txt_current_password)

        self.btn_remove_password = QPushButton(self.translator.get(
            "btn_remove_password", "🔓 إزالة كلمة المرور"))
        self.btn_remove_password.clicked.connect(self._on_remove_password)
        rem_pwd_row.addWidget(self.btn_remove_password)
        rem_pwd_row.addStretch()
        prot_layout.addLayout(rem_pwd_row)

        # ─ Read-only row ─────────────────────────────────────────────────
        readonly_row = QHBoxLayout()
        self.btn_set_readonly = QPushButton(self.translator.get(
            "btn_set_readonly", "⚠️ تعيين للقراءة فقط (لا رجعة)"))
        self.btn_set_readonly.setStyleSheet(
            "QPushButton { color: white; background-color: #cc4400; }"
            "QPushButton:hover { background-color: #aa3300; }"
        )
        self.btn_set_readonly.clicked.connect(self._on_set_readonly)
        readonly_row.addWidget(self.btn_set_readonly)
        readonly_row.addStretch()
        prot_layout.addLayout(readonly_row)

        outer.addWidget(prot_group)

        # ── Run diagnostics button ─────────────────────────────────────────
        self.btn_run = QPushButton(self.translator.get(
            "btn_run_diagnostics", "▶ تشغيل التشخيص / Run Diagnostics"))
        self.btn_run.setFixedHeight(34)
        self.btn_run.clicked.connect(self._run_diagnostics)
        outer.addWidget(self.btn_run)

        # ── Status cards (pcscd / permissions / USB) ───────────────────────
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(8)

        self.card_pcscd = self._make_status_card(
            self.translator.get("diag_pcscd", "خدمة PC/SC"))
        self.card_perms = self._make_status_card(
            self.translator.get("diag_permissions", "صلاحيات المستخدم"))
        self.card_usb = self._make_status_card(
            self.translator.get("diag_usb", "أجهزة USB المتصلة"))

        cards_layout.addWidget(self.card_pcscd["frame"])
        cards_layout.addWidget(self.card_perms["frame"])
        cards_layout.addWidget(self.card_usb["frame"])
        outer.addLayout(cards_layout)

        # ── Detail area ────────────────────────────────────────────────────
        detail_group = QGroupBox(self.translator.get(
            "diag_details", "التفاصيل / Details"))
        detail_layout = QVBoxLayout(detail_group)
        self.txt_details = QTextEdit()
        self.txt_details.setReadOnly(True)
        self.txt_details.setMinimumHeight(100)
        self.txt_details.setMaximumHeight(180)
        detail_layout.addWidget(self.txt_details)
        outer.addWidget(detail_group)

        # ── Fix instructions (Linux only) ──────────────────────────────────
        sys_os = platform.system().lower()
        if "linux" in sys_os:
            fix_group = QGroupBox(self.translator.get(
                "diag_fix_title", "أوامر الإصلاح / Fix Commands"))
            fix_layout = QVBoxLayout(fix_group)

            self.lbl_fix_intro = QLabel(self.translator.get(
                "diag_fix_intro",
                "إذا لم يتم اكتشاف الجهاز، نفّذ الأوامر التالية في الطرفية:"))
            self.lbl_fix_intro.setWordWrap(True)
            fix_layout.addWidget(self.lbl_fix_intro)

            self.txt_fix = QTextEdit()
            self.txt_fix.setReadOnly(True)
            self.txt_fix.setMinimumHeight(120)
            self.txt_fix.setMaximumHeight(200)
            self.txt_fix.setFont(QFont("Monospace", 9))
            fix_layout.addWidget(self.txt_fix)

            self.btn_copy_fix = QPushButton(self.translator.get(
                "btn_copy_commands", "📋 نسخ الأوامر / Copy Commands"))
            self.btn_copy_fix.clicked.connect(self._copy_fix_commands)
            fix_layout.addWidget(self.btn_copy_fix)

            self._populate_fix_commands()
            outer.addWidget(fix_group)
        else:
            self.txt_fix = None
            self.btn_copy_fix = None

        outer.addStretch()

    # ── Card protection actions ───────────────────────────────────────────────

    def update_card_info(self, info: dict):
        """Called when a new card is detected; stores info for protection ops."""
        self._current_card_info = info

    def clear_card_info(self):
        """Called when card is removed."""
        self._current_card_info = None

    def _check_card_connected(self) -> bool:
        if not self.nfc_manager or not self.nfc_manager.connection:
            QMessageBox.warning(
                self,
                self.translator.get("msg_warning", "تحذير"),
                self.translator.get("warn_no_card", "لا توجد بطاقة متصلة"),
            )
            return False
        return True

    @staticmethod
    def _parse_hex(text: str, expected_bytes: int):
        """Parse a hex string into a list of bytes; raises ValueError on bad input."""
        text = text.strip().upper().replace(' ', '')
        if len(text) != expected_bytes * 2:
            raise ValueError(f"Expected {expected_bytes * 2} hex chars, got {len(text)}")
        return [int(text[i:i+2], 16) for i in range(0, len(text), 2)]

    def _on_set_password(self):
        if not self._check_card_connected():
            return

        pwd_text = self.txt_new_password.text().strip()
        pack_text = self.txt_pack_code.text().strip() or "0000"

        try:
            pwd_bytes = self._parse_hex(pwd_text, 4)
        except Exception:
            QMessageBox.warning(
                self,
                self.translator.get("msg_warning", "تحذير"),
                self.translator.get("warn_invalid_hex_password"),
            )
            return

        try:
            pack_bytes = self._parse_hex(pack_text, 2)
        except Exception:
            QMessageBox.warning(
                self,
                self.translator.get("msg_warning", "تحذير"),
                self.translator.get("warn_invalid_hex_pack"),
            )
            return

        try:
            self.nfc_manager.set_password(pwd_bytes, pack_bytes)
            QMessageBox.information(
                self,
                self.translator.get("msg_success", "نجاح"),
                self.translator.get("log_password_set"),
            )
            self.txt_new_password.clear()
            self.txt_pack_code.clear()
        except Exception as e:
            QMessageBox.critical(
                self,
                self.translator.get("msg_error", "خطأ"),
                self.translator.get("log_protection_error", str(e)),
            )

    def _on_remove_password(self):
        if not self._check_card_connected():
            return

        pwd_text = self.txt_current_password.text().strip()
        current_pwd = None
        if pwd_text:
            try:
                current_pwd = self._parse_hex(pwd_text, 4)
            except Exception:
                QMessageBox.warning(
                    self,
                    self.translator.get("msg_warning", "تحذير"),
                    self.translator.get("warn_invalid_hex_password"),
                )
                return

        try:
            self.nfc_manager.remove_password(current_pwd)
            QMessageBox.information(
                self,
                self.translator.get("msg_success", "نجاح"),
                self.translator.get("log_password_removed"),
            )
            self.txt_current_password.clear()
        except Exception as e:
            QMessageBox.critical(
                self,
                self.translator.get("msg_error", "خطأ"),
                self.translator.get("log_protection_error", str(e)),
            )

    def _on_set_readonly(self):
        if not self._check_card_connected():
            return

        reply = QMessageBox.question(
            self,
            self.translator.get("msg_warning", "تحذير"),
            self.translator.get("warn_readonly_confirm"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self.nfc_manager.set_read_only()
            QMessageBox.information(
                self,
                self.translator.get("msg_success", "نجاح"),
                self.translator.get("log_readonly_set"),
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.translator.get("msg_error", "خطأ"),
                self.translator.get("log_protection_error", str(e)),
            )

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _make_status_card(title: str) -> dict:
        """Create a small status card widget. Returns dict with frame and labels."""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setMinimumWidth(160)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setFont(QFont("", 9, QFont.Weight.Bold))

        lbl_icon = QLabel("⚪")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setFont(QFont("", 18))

        lbl_msg = QLabel("—")
        lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_msg.setWordWrap(True)

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_icon)
        layout.addWidget(lbl_msg)

        return {"frame": frame, "icon": lbl_icon, "msg": lbl_msg}

    def _set_card_status(self, card: dict, ok: bool | None, message: str):
        """Update a status card: ok=True→green, ok=False→red, None→gray."""
        if ok is True:
            card["icon"].setText("✅")
            card["frame"].setStyleSheet("QFrame { border: 2px solid green; border-radius: 6px; }")
        elif ok is False:
            card["icon"].setText("❌")
            card["frame"].setStyleSheet("QFrame { border: 2px solid red; border-radius: 6px; }")
        else:
            card["icon"].setText("⚪")
            card["frame"].setStyleSheet("QFrame { border: 2px solid gray; border-radius: 6px; }")
        card["msg"].setText(message)

    def _populate_fix_commands(self):
        if self.txt_fix is None:
            return
        commands = SystemDiagnostics.get_fix_commands()
        lines = []
        for desc, cmd in commands:
            lines.append(f"# {desc}")
            lines.append(cmd)
            lines.append("")
        self.txt_fix.setPlainText("\n".join(lines))

    def _copy_fix_commands(self):
        if self.txt_fix is None:
            return
        QApplication.clipboard().setText(self.txt_fix.toPlainText())
        if self.btn_copy_fix:
            original = self.btn_copy_fix.text()
            self.btn_copy_fix.setText(self.translator.get("btn_copied", "✔ تم النسخ / Copied!"))
            QTimer.singleShot(2000, lambda: self.btn_copy_fix.setText(original))

    # ── Diagnostics execution ─────────────────────────────────────────────

    def _run_diagnostics(self):
        self.btn_run.setEnabled(False)
        self.btn_run.setText(self.translator.get(
            "btn_running_diagnostics", "⏳ جاري التشخيص... / Running..."))
        self.txt_details.setPlainText(
            self.translator.get("diag_running", "جاري التشخيص، يُرجى الانتظار..."))

        # Reset cards
        self._set_card_status(self.card_pcscd, None, "—")
        self._set_card_status(self.card_perms, None, "—")
        self._set_card_status(self.card_usb, None, "—")

        self._worker = _DiagnosticsWorker()
        self._worker.finished.connect(self._on_diagnostics_done)
        self._worker.start()

    def _on_diagnostics_done(self, report: dict):
        self.btn_run.setEnabled(True)
        self.btn_run.setText(self.translator.get(
            "btn_run_diagnostics", "▶ تشغيل التشخيص / Run Diagnostics"))

        # Update status cards
        pcscd = report.get("pcscd", {})
        perms = report.get("permissions", {})
        usb = report.get("usb_devices", {})

        self._set_card_status(self.card_pcscd, pcscd.get("ok"), pcscd.get("message", ""))
        self._set_card_status(self.card_perms, perms.get("ok"), perms.get("message", ""))
        usb_devices = usb.get("devices", [])
        self._set_card_status(self.card_usb, bool(usb_devices), usb.get("message", ""))

        # Build detail text
        lines = []
        os_info = report.get("os", {})
        lines.append(f"🖥️  OS: {os_info.get('name','')} — {os_info.get('version','')}")
        lines.append("")
        lines.append(f"PC/SC: {pcscd.get('message','')}")
        groups = perms.get("groups", [])
        lines.append(f"المجموعات / Groups: {', '.join(groups) if groups else 'لا شيء / none'}")
        lines.append(f"صلاحيات: {perms.get('message','')}")
        lines.append("")
        lines.append(f"أجهزة USB: {usb.get('message','')}")
        for dev in usb_devices:
            lines.append(f"  • {dev.get('description','')}")

        self.txt_details.setPlainText("\n".join(lines))

    # ── Retranslation ─────────────────────────────────────────────────────

    def retranslate_ui(self):
        self.lbl_title.setText(self.translator.get(
            "security_title", "الصلاحيات وتشخيص الجهاز / Permissions & Device Diagnostics"))
        self.btn_run.setText(self.translator.get(
            "btn_run_diagnostics", "▶ تشغيل التشخيص / Run Diagnostics"))
        self.lbl_protection_note.setText(self.translator.get("lbl_protection_note"))
        self.lbl_new_password.setText(self.translator.get("lbl_new_password"))
        self.lbl_pack_code.setText(self.translator.get("lbl_pack_code"))
        self.lbl_current_password_remove.setText(self.translator.get("lbl_current_password_remove"))
        self.btn_set_password.setText(self.translator.get("btn_set_password"))
        self.btn_remove_password.setText(self.translator.get("btn_remove_password"))
        self.btn_set_readonly.setText(self.translator.get("btn_set_readonly"))
