# برومبت Claude Code — تطوير NFC Manager إلى مستوى NFC Tools

## السياق الكامل

أنت تعمل على تطوير تطبيق Python/PyQt6 موجود لإدارة بطاقات NFC عبر قارئ ACR122U على Linux.

**المرجع المطلوب المطابقة:** تطبيق NFC Tools (wakdev) على Android/Desktop  
**الهدف:** تطبيق يظهر في قائمة التطبيقات (launcher) ويعمل بمستوى احترافي مطابق لـ NFC Tools

---

## البيئة والأجهزة

- **نظام التشغيل:** Linux
- **القارئ:** ACR122U (USB)
- **البطاقات:** NXP NTAG215 فقط (540 bytes / 135 pages / NDEF available: 492 bytes)
- **مدير كلمات السر:** KeePassXC (خارج التطبيق — لا نحتاج توليد كلمات سر داخل التطبيق)
- **الاستخدام الأساسي:** كتابة كلمة مرور على البطاقة وقراءتها لاحقاً

---

## البنية الحالية للكود (موجود ويعمل جزئياً)

```
acr122u_app/
├── main.py                    # نقطة الدخول
├── reader.py                  # NFCReaderManager — PC/SC عبر pyscard ✅ يعمل
├── nfc_utils.py               # ATR parsing + NDEF encode/decode ✅ يعمل
├── database.py                # SQLite عبر SQLAlchemy ✅ يعمل
├── diagnostics.py             # فحص pcscd + USB + صلاحيات ✅ يعمل
├── emulator.py                # محاكاة لوحة المفاتيح ✅ يعمل
├── i18n.py                    # ترجمة AR/EN كاملة ✅ يعمل
└── ui_components/
    ├── main_window.py         # النافذة الرئيسية
    ├── read_tab.py            # تبويب القراءة — يحتاج تطوير جذري
    ├── write_tab.py           # تبويب الكتابة — يحتاج تطوير
    ├── security_tab.py        # إدارة كلمة مرور NTAG
    ├── emulation_tab.py       # محاكاة الكيبورد
    ├── settings_tab.py        # إعدادات
    ├── dashboard_tab.py       # جدول سجل العمليات
    ├── log_panel.py           # لوحة السجل
    └── theme.py               # light/dark QSS — يحتاج تطوير
```

---

## تحليل NFC Tools — ما يجب تحقيقه بالضبط

### تبويب READ (الأهم)

NFC Tools يعرض عند قراءة NTAG215 هذه الحقول بالترتيب الدقيق:

```
┌─────────────────────────────────────────────┐
│  Tag type         │ ISO 14443-3A            │
│                   │ NXP – NTAG215           │
├───────────────────┼─────────────────────────┤
│  Technologies     │ NfcA, MifareUltralight, │
│  available        │ Ndef                    │
├───────────────────┼─────────────────────────┤
│  Serial number    │ 04:82:3E:01:2A:4D:03   │
├───────────────────┼─────────────────────────┤
│  ATQA             │ 0x0044                  │
├───────────────────┼─────────────────────────┤
│  SAK              │ 0x00                    │
├───────────────────┼─────────────────────────┤
│  Signature        │ Invalid / Valid         │
├───────────────────┼─────────────────────────┤
│  Protected by     │ No                      │
│  password         │                         │
├───────────────────┼─────────────────────────┤
│  Memory           │ 540 bytes :             │
│  information      │ 135 pages (4 bytes each)│
├───────────────────┼─────────────────────────┤
│  Data format      │ NFC Forum Type 2        │
├───────────────────┼─────────────────────────┤
│  Size             │ 52 / 492 Bytes          │
│                   │ (used / available)      │
├───────────────────┼─────────────────────────┤
│  Writable         │ Yes                     │
├───────────────────┼─────────────────────────┤
│  Can be made      │ Yes                     │
│  Read-Only        │                         │
├───────────────────┼─────────────────────────┤
│  Record 1 -       │ UTF-8 (en) : text/plain │
│  UTF-8 (en):      │ [محتوى النص المخزون]    │
│  text/plain       │                         │
└─────────────────────────────────────────────┘
```

**الحقل المفقود حالياً في read_tab.py:** حقل **Signature** (Invalid/Valid)  
هذا يتطلب إرسال APDU خاص للـ NTAG لطلب التوقيع ثم التحقق منه.

**طريقة عرض NFC Tools:**
- كل حقل في صف مستقل: Label يسار + Value يمين
- لون أيقونة مميز لكل صف (دائرة ملونة أو أيقونة SVG)
- عند الضغط على أي صف → Copy to clipboard
- النتيجة تظهر فوراً بمجرد وضع البطاقة (لا زر "قراءة")

### تبويب WRITE

NFC Tools في تبويب الكتابة:
- زر **"Add a record"** يفتح قائمة لاختيار نوع السجل
- أنواع السجلات المدعومة في NFC Tools:
  - Text (plain text) ← **الأهم لحالتنا**
  - URL/URI
  - Email
  - Phone number
  - Contact (vCard)
  - WiFi configuration
  - Custom / RAW
- بعد إضافة السجلات → زر **"Write"** ينتظر البطاقة
- عداد bytes متبقية يُحدَّث لحظياً

**لحالتنا نحتاج:** Text فقط (لكلمات السر من KeePassXC)

### تبويب OTHER

هذا التبويب مفقود كلياً من تطبيقنا الحالي. NFC Tools يحتوي على:

1. **Copy tag** — نسخ محتوى بطاقة إلى بطاقة أخرى
2. **Erase tag** — مسح كل محتوى البطاقة (كتابة NDEF فارغ)
3. **Format tag** — إعادة تهيئة البطاقة
4. **Set password** — تعيين كلمة مرور (موجود في security_tab لكن يجب نقله هنا)
5. **Remove password** — إزالة كلمة المرور
6. **Set read-only (lock)** — قفل نهائي لا رجعة فيه

### تبويب إدارة البطاقات (جديد خاص بنا)

هذا التبويب غير موجود في NFC Tools لكنه ضروري لحالة الاستخدام:
- جدول يربط رقم البطاقة (1-200) بمعلوماتها (دومين، ملاحظة)
- عند قراءة بطاقة → ابحث بالـ Serial UID وأظهر معلوماتها المحفوظة
- إضافة/تعديل/حذف سجلات
- تصدير CSV

---

## المهام المطلوبة بالترتيب

### المهمة 1: إضافة حقل Signature لـ read_tab.py

في reader.py، أضف دالة لطلب Signature APDU:

```python
def get_ntag_signature(self) -> tuple[bool, str]:
    """
    اطلب NTAG Originality Signature عبر APDU 0x3C 00
    Returns: (is_valid: bool, signature_hex: str)
    
    APDU للطلب عبر ACR122U:
    FF 00 00 00 04 D4 42 01 3C 00
    (InDataExchange: cmd=0x3C, addr=0x00)
    
    الاستجابة الصحيحة: 32 bytes signature + SW 9000
    يمكن التحقق منها مقابل مفتاح NXP العام المعروف
    لكن بشكل مبسط: إذا جاءت 32 byte → Valid، وإلا → Invalid
    """
```

في read_tab.py، أضف صف Signature بين SAK و Protected by password.

### المهمة 2: تطوير theme.py جذرياً

فعّل الـ dark theme كافتراضي وحسّن التصميم ليشبه NFC Tools:

```python
# الألوان المطلوبة (مستوحاة من NFC Tools):
BACKGROUND = "#1a1a2e"        # خلفية داكنة
SURFACE = "#16213e"           # بطاقات/panels
ACCENT = "#0f3460"            # أزرق داكن
HIGHLIGHT = "#533483"         # بنفسجي للـ active
TEXT_PRIMARY = "#e0e0e0"
TEXT_SECONDARY = "#9e9e9e"
SUCCESS = "#4caf50"           # أخضر للحالة OK
ERROR = "#f44336"             # أحمر للخطأ
WARNING = "#ff9800"           # برتقالي للتحذير
BORDER = "#2d2d44"
```

كل صف في read_tab يجب أن يكون:
- خلفية فاتحة قليلاً عند hover
- قابل للنقر لنسخ القيمة
- أيقونة صغيرة SVG على اليسار (أو دائرة ملونة)

### المهمة 3: إنشاء تبويب OTHER الجديد

ملف: `ui_components/other_tab.py`

```python
class OtherTab(QWidget):
    """
    يحتوي على:
    1. Copy Tag (نسخ بطاقة → بطاقة)
    2. Erase Tag (مسح NDEF)
    3. Set/Remove Password (نقل من security_tab)
    4. Lock Tag (Read-Only — تحذير مؤكد)
    
    كل عملية:
    - تعرض وصف واضح بالعربي
    - تطلب تأكيد للعمليات الخطرة
    - تظهر progress أثناء العملية
    - تسجل في السجل
    """
```

في reader.py أضف:
```python
def erase_tag(self):
    """اكتب NDEF فارغ: TLV Terminator فقط (0xFE)"""
    
def copy_tag_read(self) -> bytes:
    """اقرأ كل الصفحات وأرجعها كـ bytes للنسخ"""
    
def copy_tag_write(self, data: bytes):
    """اكتب bytes محفوظة من copy_tag_read"""
```

### المهمة 4: إنشاء تبويب إدارة البطاقات

ملف: `ui_components/cards_registry_tab.py`

مع جدول جديد في database.py:
```python
class CardRegistry(Base):
    __tablename__ = 'card_registry'
    id = Column(Integer, primary_key=True)
    card_number = Column(Integer, unique=True)  # 1-200
    uid = Column(String(50))                    # Serial من القارئ
    domain = Column(String(200))                # الدومين/الخدمة
    note = Column(String(500))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

**الربط مع read_tab:**
عند قراءة بطاقة → ابحث عن uid في card_registry → إذا وُجد، أظهر معلوماتها في بطاقة خضراء أعلى نتائج القراءة:
```
┌──────────────────────────────────┐
│ 🔖 بطاقة #42 — gmail.com         │
│    آخر تحديث: 2026-05-01         │
└──────────────────────────────────┘
```

### المهمة 5: ملف .desktop وسكريبت التثبيت

**ملف: `install.sh`**
```bash
#!/bin/bash
# تثبيت NFC Manager على Linux

APP_DIR="$HOME/.local/lib/nfc-manager"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor"

# 1. نسخ الملفات
mkdir -p "$APP_DIR"
cp -r acr122u_app/* "$APP_DIR/"

# 2. إنشاء virtual environment
python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install -r requirements.txt

# 3. wrapper script
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/nfc-manager" << 'EOF'
#!/bin/bash
cd ~/.local/lib/nfc-manager
source venv/bin/activate
python main.py "$@"
EOF
chmod +x "$BIN_DIR/nfc-manager"

# 4. أيقونة SVG
mkdir -p "$ICON_DIR/scalable/apps"
cp nfc-manager.svg "$ICON_DIR/scalable/apps/"

# 5. .desktop file
mkdir -p "$DESKTOP_DIR"
cat > "$DESKTOP_DIR/nfc-manager.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=NFC Manager
Name[ar]=مدير NFC
GenericName=NFC Card Manager
GenericName[ar]=مدير بطاقات NFC
Comment=Read, write and manage NFC cards with ACR122U
Comment[ar]=قراءة وكتابة وإدارة بطاقات NFC عبر ACR122U
Exec=$BIN_DIR/nfc-manager
Icon=nfc-manager
Categories=Utility;Security;System;
Keywords=NFC;RFID;ACR122U;card;password;
StartupWMClass=nfc-manager
StartupNotify=true
Terminal=false
EOF

# 6. تحديث قاعدة بيانات الأيقونات
update-icon-caches "$ICON_DIR" 2>/dev/null || true
gtk-update-icon-cache "$ICON_DIR" 2>/dev/null || true

# 7. تحديث قائمة التطبيقات
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

echo "✅ تم التثبيت بنجاح!"
echo "يمكنك الآن تشغيل التطبيق بالأمر: nfc-manager"
echo "أو البحث عنه في قائمة التطبيقات بـ: NFC Manager"
```

**ملف الأيقونة: `nfc-manager.svg`**
أيقونة SVG احترافية تمثل NFC (دوائر موجية + قفل أو بطاقة).

### المهمة 6: تحسينات UX في main_window.py

1. **الـ header:** أضف اسم القارئ المكتشف بجانب LED
2. **انتظار البطاقة:** عند الضغط Write أو Copy → شاشة "ضع البطاقة الآن" مع animation
3. **Copy on click:** كل حقل في read_tab قابل للنقر لنسخ قيمته
4. **Auto-read:** البطاقة تُقرأ تلقائياً عند وضعها (موجود لكن يحتاج تأكيد يعمل)
5. **Status bar دائمة:** تعرض دائماً: حالة القارئ | آخر بطاقة مقروءة | الوقت

---

## ترتيب التبويبات النهائي (مثل NFC Tools)

```
[READ] [WRITE] [OTHER] [CARDS] [SETTINGS]
```

بالعربي:
```
[قراءة] [كتابة] [عمليات] [بطاقاتي] [الإعدادات]
```

---

## ملاحظات تقنية مهمة

### Signature APDU للـ NTAG:
```python
# عبر ACR122U InDataExchange
SIGNATURE_APDU = [0xFF, 0x00, 0x00, 0x00, 0x05, 0xD4, 0x42, 0x01, 0x3C, 0x00]
# Response: [0xD5, 0x43, 0x00, <32 bytes signature>, SW1, SW2]
# إذا كان len(response) >= 34 → Valid
# إذا SW1 != 0x90 → Invalid
```

### Erase Tag:
```python
# كتابة TLV Terminator فقط على page 4
erase_data = bytes([0xFE, 0x00, 0x00, 0x00])  # terminator + padding
write_block(4, list(erase_data))
```

### Copy Tag:
```python
# قراءة pages 4-134 (user area) + كتابتها على بطاقة ثانية
# لا تنسخ pages 0-3 (UID + config) لأنها فريدة
```

---

## ملف i18n.py — مفاتيح جديدة تحتاج إضافة

```python
# تبويب OTHER
"tab_other": {"ar": "عمليات", "en": "Other"},
"other_copy_tag": {"ar": "نسخ البطاقة", "en": "Copy Tag"},
"other_erase_tag": {"ar": "مسح البطاقة", "en": "Erase Tag"},
"other_set_password": {"ar": "تعيين كلمة المرور", "en": "Set Password"},
"other_remove_password": {"ar": "إزالة كلمة المرور", "en": "Remove Password"},
"other_lock_tag": {"ar": "قفل البطاقة (نهائي)", "en": "Lock Tag (Irreversible)"},

# تبويب CARDS
"tab_cards": {"ar": "بطاقاتي", "en": "My Cards"},
"cards_number": {"ar": "رقم البطاقة", "en": "Card #"},
"cards_uid": {"ar": "الرقم التسلسلي", "en": "UID"},
"cards_domain": {"ar": "الدومين/الخدمة", "en": "Domain/Service"},
"cards_note": {"ar": "ملاحظة", "en": "Note"},

# Signature
"lbl_signature": {"ar": "التوقيع", "en": "Signature"},
"val_valid": {"ar": "صحيح ✓", "en": "Valid ✓"},
"val_invalid": {"ar": "غير صحيح", "en": "Invalid"},

# انتظار البطاقة
"waiting_for_tag": {"ar": "ضع البطاقة على القارئ...", "en": "Place tag on reader..."},
"operation_success": {"ar": "تمت العملية بنجاح ✓", "en": "Operation successful ✓"},
```

---

## الناتج المتوقع

بعد تنفيذ كل المهام:

1. `nfc-manager` يعمل من Terminal
2. يظهر في قائمة تطبيقات Linux باسم "NFC Manager" مع أيقونة
3. تبويب READ يعرض نفس حقول NFC Tools بما فيها Signature
4. تبويب OTHER يحتوي Copy/Erase/Password/Lock
5. تبويب CARDS لإدارة 200 بطاقة مع ربطها بـ UID
6. Dark theme احترافي مشابه لـ NFC Tools
7. كل حقل قابل للنسخ بالنقر

---

## أمر التشغيل الحالي (للاختبار)
```bash
cd acr122u_app && python main.py
```

## أمر التثبيت
```bash
chmod +x install.sh && ./install.sh
```
