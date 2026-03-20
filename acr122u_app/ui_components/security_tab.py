import platform
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox, QScrollArea, QFrame, QApplication
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
    def __init__(self, translator):
        super().__init__()
        self.translator = translator
        self._worker = None
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
