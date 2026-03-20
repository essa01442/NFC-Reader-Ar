translations = {
    "ar": {
        "app_title": "مدير قارئ ACR122U NFC",
        "tab_read": "قراءة البطاقة",
        "tab_write": "الكتابة على البطاقة",
        "tab_security": "الحماية والصلاحيات",
        "tab_emulation": "محاكاة لوحة المفاتيح",
        "tab_settings": "الإعدادات",

        "security_title": "الصلاحيات وتشخيص الجهاز",
        "btn_run_diagnostics": "▶ تشغيل التشخيص",
        "btn_running_diagnostics": "⏳ جاري التشخيص...",
        "btn_copy_commands": "📋 نسخ الأوامر",
        "btn_copied": "✔ تم النسخ!",
        "diag_pcscd": "خدمة PC/SC",
        "diag_permissions": "صلاحيات المستخدم",
        "diag_usb": "أجهزة USB المتصلة",
        "diag_details": "التفاصيل",
        "diag_fix_title": "أوامر الإصلاح",
        "diag_fix_intro": "إذا لم يتم اكتشاف الجهاز، نفّذ الأوامر التالية في الطرفية:",
        "diag_running": "جاري التشخيص، يُرجى الانتظار...",

        "status_reader_connected": "القارئ متصل",
        "status_reader_disconnected": "القارئ غير متصل",
        "status_card_present": "البطاقة متصلة",
        "status_card_absent": "لا توجد بطاقة",

        # Card Info section
        "section_card_info": "معلومات البطاقة",
        "lbl_tag_type": "نوع البطاقة:",
        "lbl_technologies": "التقنيات المتاحة:",
        "lbl_serial_number": "الرقم التسلسلي:",
        "lbl_atqa": "ATQA:",
        "lbl_sak": "SAK:",
        "lbl_password_protected": "محمية بكلمة مرور:",
        "lbl_memory_info": "معلومات الذاكرة:",
        "lbl_data_format": "تنسيق البيانات:",
        "lbl_size": "الحجم:",
        "lbl_writable": "قابلة للكتابة:",
        "lbl_read_only_capable": "يمكن جعلها للقراءة فقط:",
        "val_yes": "نعم",
        "val_no": "لا",
        "val_unknown": "غير معروف",
        "val_none": "لا يوجد",

        # NDEF records section
        "section_ndef": "سجلات NDEF",
        "lbl_record": "سجل {}:",
        "no_ndef": "لا توجد سجلات NDEF",

        # Raw block reader section
        "section_raw_read": "قراءة كتلة/صفحة (متقدم)",
        "lbl_uid": "المعرف الفريد (UID):",
        "lbl_data": "بيانات البطاقة:",
        "btn_read": "قراءة البيانات",
        "btn_clear_log": "مسح السجل",

        "lbl_write_data": "البيانات المراد كتابتها:",
        "lbl_block": "رقم الكتلة / الصفحة:",
        "btn_write": "كتابة البيانات",
        "msg_write_warn": "تحذير: الكتابة قد تمحو البيانات السابقة. هل تريد المتابعة؟",

        "lbl_emulation_mode": "وضع محاكاة الكيبورد:",
        "chk_emulation_enable": "تفعيل وضع المحاكاة",
        "lbl_emulation_suffix": "الإجراء بعد الإدخال:",
        "opt_none": "لا شيء",
        "opt_enter": "إضافة Enter",
        "opt_tab": "إضافة Tab",

        "lbl_language": "لغة الواجهة / Language:",
        "btn_apply_lang": "تطبيق اللغة",

        "log_title": "سجل العمليات",
        "log_reader_found": "تم العثور على القارئ: {}",
        "log_reader_lost": "تم فصل القارئ.",
        "log_card_inserted": "تم إدخال بطاقة. UID: {}",
        "log_card_removed": "تم إزالة البطاقة.",
        "log_read_success": "تمت القراءة بنجاح.",
        "log_read_error": "خطأ في القراءة: {}",
        "log_write_success": "تمت الكتابة بنجاح.",
        "log_write_error": "خطأ في الكتابة: {}",

        "tab_dashboard": "لوحة القيادة",
        "btn_save_log": "حفظ السجل",
        "opt_all": "الكل",
        "opt_info": "معلومات",
        "opt_error": "أخطاء",

        # Full memory dump section
        "section_full_memory": "تفريغ الذاكرة الكاملة",
        "no_memory_data": "لا توجد بيانات ذاكرة",

        # Card protection management
        "section_card_protection": "إدارة حماية البطاقة",
        "lbl_new_password": "كلمة المرور الجديدة (8 أحرف هكس):",
        "lbl_pack_code": "رمز التأكيد PACK (4 أحرف هكس):",
        "lbl_current_password_remove": "كلمة المرور الحالية (لإزالتها):",
        "btn_set_password": "🔒 تعيين كلمة المرور",
        "btn_remove_password": "🔓 إزالة كلمة المرور",
        "btn_set_readonly": "⚠️ تعيين للقراءة فقط (لا رجعة)",
        "warn_readonly_confirm": "تحذير: هذا الإجراء دائم ولا يمكن التراجع عنه!\nهل أنت متأكد من تعيين البطاقة للقراءة فقط؟",
        "warn_no_card": "لا توجد بطاقة متصلة",
        "warn_invalid_hex_password": "كلمة المرور يجب أن تكون 8 أحرف هكساديسيمال (مثال: AABBCCDD)",
        "warn_invalid_hex_pack": "رمز التأكيد يجب أن يكون 4 أحرف هكساديسيمال (مثال: AABB)",
        "log_password_set": "تم تعيين كلمة المرور بنجاح.",
        "log_password_removed": "تم إزالة كلمة المرور بنجاح.",
        "log_readonly_set": "تم تعيين البطاقة للقراءة فقط بنجاح.",
        "log_protection_error": "خطأ في إدارة الحماية: {}",
        "lbl_protection_note": "ملاحظة: عمليات الحماية تدعم بطاقات NTAG213/215/216",

        # Emulation tab display
        "section_last_emulated": "آخر بطاقة محاكاة",
        "lbl_emulated_uid": "المعرف الفريد المُحاكى:",
        "lbl_emulated_type": "نوع البطاقة:",
        "no_emulated_card": "لم يتم محاكاة أي بطاقة بعد",

        "msg_error": "خطأ",
        "msg_success": "نجاح",
        "msg_warning": "تحذير",
        "btn_yes": "نعم",
        "btn_no": "لا",
    },
    "en": {
        "app_title": "ACR122U NFC Reader Manager",
        "tab_read": "Read Card",
        "tab_write": "Write Card",
        "tab_security": "Security & Permissions",
        "tab_emulation": "Keyboard Emulation",
        "tab_settings": "Settings",

        "security_title": "Permissions & Device Diagnostics",
        "btn_run_diagnostics": "▶ Run Diagnostics",
        "btn_running_diagnostics": "⏳ Running...",
        "btn_copy_commands": "📋 Copy Commands",
        "btn_copied": "✔ Copied!",
        "diag_pcscd": "PC/SC Service",
        "diag_permissions": "User Permissions",
        "diag_usb": "Connected USB Devices",
        "diag_details": "Details",
        "diag_fix_title": "Fix Commands",
        "diag_fix_intro": "If the device is not detected, run the following commands in a terminal:",
        "diag_running": "Running diagnostics, please wait...",

        "status_reader_connected": "Reader Connected",
        "status_reader_disconnected": "Reader Disconnected",
        "status_card_present": "Card Present",
        "status_card_absent": "No Card",

        # Card Info section
        "section_card_info": "Card Information",
        "lbl_tag_type": "Tag type:",
        "lbl_technologies": "Technologies available:",
        "lbl_serial_number": "Serial number:",
        "lbl_atqa": "ATQA:",
        "lbl_sak": "SAK:",
        "lbl_password_protected": "Protected by password:",
        "lbl_memory_info": "Memory information:",
        "lbl_data_format": "Data format:",
        "lbl_size": "Size:",
        "lbl_writable": "Writable:",
        "lbl_read_only_capable": "Can be made Read-Only:",
        "val_yes": "Yes",
        "val_no": "No",
        "val_unknown": "Unknown",
        "val_none": "None",

        # NDEF records section
        "section_ndef": "NDEF Records",
        "lbl_record": "Record {}:",
        "no_ndef": "No NDEF records",

        # Raw block reader section
        "section_raw_read": "Read Block / Page (Advanced)",
        "lbl_uid": "Unique ID (UID):",
        "lbl_data": "Card Data:",
        "btn_read": "Read Data",
        "btn_clear_log": "Clear Log",

        "lbl_write_data": "Data to Write:",
        "lbl_block": "Block / Page Number:",
        "btn_write": "Write Data",
        "msg_write_warn": "Warning: Writing may overwrite previous data. Continue?",

        "lbl_emulation_mode": "Keyboard Emulation Mode:",
        "chk_emulation_enable": "Enable Emulation Mode",
        "lbl_emulation_suffix": "Action after input:",
        "opt_none": "None",
        "opt_enter": "Add Enter",
        "opt_tab": "Add Tab",

        "lbl_language": "لغة الواجهة / Language:",
        "btn_apply_lang": "Apply Language",

        "log_title": "Activity Log",
        "log_reader_found": "Reader found: {}",
        "log_reader_lost": "Reader disconnected.",
        "log_card_inserted": "Card inserted. UID: {}",
        "log_card_removed": "Card removed.",
        "log_read_success": "Read successful.",
        "log_read_error": "Read error: {}",
        "log_write_success": "Write successful.",
        "log_write_error": "Write error: {}",

        "tab_dashboard": "Dashboard",
        "btn_save_log": "Save Log",
        "opt_all": "All",
        "opt_info": "Info",
        "opt_error": "Errors",

        # Full memory dump section
        "section_full_memory": "Full Memory Dump",
        "no_memory_data": "No memory data",

        # Card protection management
        "section_card_protection": "Card Protection Management",
        "lbl_new_password": "New Password (8 hex chars):",
        "lbl_pack_code": "PACK Code (4 hex chars):",
        "lbl_current_password_remove": "Current Password (to remove):",
        "btn_set_password": "🔒 Set Password",
        "btn_remove_password": "🔓 Remove Password",
        "btn_set_readonly": "⚠️ Set Read-Only (Irreversible!)",
        "warn_readonly_confirm": "Warning: This action is PERMANENT and cannot be undone!\nAre you sure you want to set the card to read-only?",
        "warn_no_card": "No card connected",
        "warn_invalid_hex_password": "Password must be 8 hexadecimal characters (example: AABBCCDD)",
        "warn_invalid_hex_pack": "PACK code must be 4 hexadecimal characters (example: AABB)",
        "log_password_set": "Password set successfully.",
        "log_password_removed": "Password removed successfully.",
        "log_readonly_set": "Card set to read-only successfully.",
        "log_protection_error": "Protection management error: {}",
        "lbl_protection_note": "Note: Protection operations support NTAG213/215/216 cards",

        # Emulation tab display
        "section_last_emulated": "Last Emulated Card",
        "lbl_emulated_uid": "Emulated UID:",
        "lbl_emulated_type": "Card Type:",
        "no_emulated_card": "No card emulated yet",

        "msg_error": "Error",
        "msg_success": "Success",
        "msg_warning": "Warning",
        "btn_yes": "Yes",
        "btn_no": "No",
    }
}

class Translator:
    def __init__(self, lang="ar"):
        self.lang = lang

    def set_language(self, lang):
        if lang in translations:
            self.lang = lang

    def get(self, key, *args):
        text = translations.get(self.lang, translations["ar"]).get(key, key)
        if args:
            try:
                text = text.format(*args)
            except Exception:
                pass
        return text
