translations = {
    "ar": {
        "app_title": "مدير قارئ ACR122U NFC",
        "tab_read": "قراءة البطاقة",
        "tab_write": "الكتابة على البطاقة",
        "tab_security": "الحماية والصلاحيات",
        "tab_emulation": "محاكاة لوحة المفاتيح",
        "tab_settings": "الإعدادات",

        "status_reader_connected": "القارئ متصل",
        "status_reader_disconnected": "القارئ غير متصل",
        "status_card_present": "البطاقة متصلة",
        "status_card_absent": "لا توجد بطاقة",

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

        "status_reader_connected": "Reader Connected",
        "status_reader_disconnected": "Reader Disconnected",
        "status_card_present": "Card Present",
        "status_card_absent": "No Card",

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
