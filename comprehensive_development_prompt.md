# برومبت شامل لتطوير مدير قارئ ACR122U NFC - نسخة احترافية متقدمة

## نظرة عامة على المشروع الحالي

أنت تعمل على تطوير تطبيق Python احترافي لإدارة قارئ ACR122U NFC. المشروع الحالي يعمل ولكنه يحتاج إلى تحسينات جذرية في الجودة والواجهة والوظائف.

### البنية الحالية:
```
acr122u_app/
├── main.py                    # نقطة الدخول
├── reader.py                  # مدير القارئ (NFCReaderManager)
├── emulator.py                # محاكي لوحة المفاتيح
├── i18n.py                    # نظام الترجمة (AR/EN)
├── ui_components/
│   ├── main_window.py         # النافذة الرئيسية
│   ├── read_tab.py            # تبويب القراءة
│   ├── write_tab.py           # تبويب الكتابة
│   ├── security_tab.py        # تبويب الأمان
│   ├── emulation_tab.py       # تبويب المحاكاة
│   ├── settings_tab.py        # تبويب الإعدادات
│   └── log_panel.py           # لوحة السجلات
└── tests/                     # اختبارات pytest
```

### التقنيات:
- Python 3.10+
- PyQt6 (واجهة رسومية)
- pyscard (التواصل مع PC/SC)
- pynput (محاكاة لوحة المفاتيح)

---

## 🔴 المشكلة الحالية (CRITICAL)

### الأعراض:
1. **القارئ لا يُكتشف تلقائياً** - رسالة "القارئ غير متصل" باللون الأحمر
2. LED أحمر بجانب حالة القارئ
3. البطاقات لا تُقرأ حتى بعد توصيل القارئ

### التشخيص التقني:

#### في `reader.py` - السطور 70-111:
```python
def _search_for_reader(self):
    # المشكلة: قد يفشل readers() إذا كانت خدمة PC/SC غير نشطة
    # المشكلة: Backoff يبدأ من 1 ثانية وقد يكون بطيئاً
    # المشكلة: لا توجد رسائل تشخيصية كافية
```

### الحلول المطلوبة:

#### 1. تحسين آلية الاكتشاف:
```python
def _search_for_reader(self):
    """
    IMPROVEMENTS NEEDED:
    - أضف محاولات إعادة الاتصال عند فشل PC/SC
    - أضف logging مفصل لكل مرحلة
    - قلل زمن backoff الأولي إلى 0.5 ثانية
    - أضف كشف تلقائي لحالة خدمة PC/SC
    - أضف emit لإشارة جديدة: pcsc_status_changed(bool is_running)
    """
```

#### 2. إضافة تشخيص ذاتي:
```python
# ملف جديد: diagnostics.py
class SystemDiagnostics:
    """
    يجب أن يفحص:
    - حالة خدمة PC/SC (Linux: pcscd, Windows: Smart Card)
    - المكتبات المثبتة (pyscard version)
    - القارئات المتاحة على مستوى النظام
    - الأذونات (Linux: user groups)
    - USB devices (lsusb على Linux)
    """
    
    def run_full_diagnostic(self) -> dict:
        """
        يعيد تقرير كامل:
        {
            'pcsc_service': {'running': bool, 'hint': str},
            'pyscard_version': str,
            'readers': [list],
            'permissions': {'ok': bool, 'groups': [list]},
            'usb_devices': [list],
            'os': {'name': str, 'version': str}
        }
        """
```

---

## 🎨 تطوير الواجهة الاحترافية

### المشاكل الحالية في الواجهة:

1. **تصميم قديم وبسيط**:
   - ألوان أساسية (أحمر/أخضر/رمادي)
   - لا توجد أيقونات
   - خطوط افتراضية
   - لا توجد انتقالات سلسة

2. **تجربة مستخدم ضعيفة**:
   - رسائل خطأ غير واضحة
   - لا توجد مؤشرات تحميل
   - لا توجد إرشادات للمبتدئين
   - لا توجد اختصارات لوحة مفاتيح

3. **عدم وجود مميزات حديثة**:
   - لا يوجد Dark Mode
   - لا توجد رسوم بيانية
   - لا يوجد تصدير للبيانات
   - لا توجد إشعارات نظامية

### التصميم الجديد المطلوب:

#### 1. نظام التصميم الحديث (Design System)

```python
# ملف جديد: ui_components/theme.py

class ModernTheme:
    """
    نظام تصميم احترافي مستوحى من Material Design 3 و Fluent Design
    """
    
    # نظام الألوان
    COLORS = {
        'light': {
            'primary': '#2563EB',        # أزرق حيوي
            'primary_dark': '#1E40AF',
            'primary_light': '#60A5FA',
            'secondary': '#10B981',      # أخضر نعناعي
            'secondary_dark': '#059669',
            'accent': '#F59E0B',         # كهرماني
            'error': '#EF4444',
            'warning': '#F97316',
            'success': '#10B981',
            'info': '#3B82F6',
            
            'surface': '#FFFFFF',
            'surface_variant': '#F3F4F6',
            'background': '#F9FAFB',
            'background_alt': '#F3F4F6',
            
            'text_primary': '#111827',
            'text_secondary': '#6B7280',
            'text_disabled': '#9CA3AF',
            
            'border': '#E5E7EB',
            'border_focus': '#2563EB',
            'divider': '#F3F4F6',
            
            'shadow': 'rgba(0, 0, 0, 0.1)',
            'shadow_strong': 'rgba(0, 0, 0, 0.2)',
        },
        
        'dark': {
            'primary': '#3B82F6',
            'primary_dark': '#2563EB',
            'primary_light': '#60A5FA',
            'secondary': '#34D399',
            'secondary_dark': '#10B981',
            'accent': '#FBBF24',
            'error': '#F87171',
            'warning': '#FB923C',
            'success': '#34D399',
            'info': '#60A5FA',
            
            'surface': '#1F2937',
            'surface_variant': '#374151',
            'background': '#111827',
            'background_alt': '#1F2937',
            
            'text_primary': '#F9FAFB',
            'text_secondary': '#D1D5DB',
            'text_disabled': '#6B7280',
            
            'border': '#374151',
            'border_focus': '#3B82F6',
            'divider': '#374151',
            
            'shadow': 'rgba(0, 0, 0, 0.3)',
            'shadow_strong': 'rgba(0, 0, 0, 0.5)',
        }
    }
    
    # Typography
    FONTS = {
        'family_primary': 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto',
        'family_mono': '"JetBrains Mono", "Fira Code", Consolas, monospace',
        'family_arabic': '"IBM Plex Sans Arabic", "Noto Sans Arabic", Arial',
        
        'size_xs': '11px',
        'size_sm': '13px',
        'size_base': '14px',
        'size_lg': '16px',
        'size_xl': '18px',
        'size_2xl': '24px',
        'size_3xl': '32px',
        
        'weight_regular': '400',
        'weight_medium': '500',
        'weight_semibold': '600',
        'weight_bold': '700',
    }
    
    # Spacing
    SPACING = {
        'xs': '4px',
        'sm': '8px',
        'md': '12px',
        'lg': '16px',
        'xl': '24px',
        '2xl': '32px',
        '3xl': '48px',
    }
    
    # Border Radius
    RADIUS = {
        'sm': '6px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        'full': '9999px',
    }
    
    # Shadows
    SHADOWS = {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
    }
    
    # Animations
    ANIMATIONS = {
        'duration_fast': 150,      # ms
        'duration_normal': 250,
        'duration_slow': 350,
        'easing': 'cubic-bezier(0.4, 0.0, 0.2, 1)',
    }
    
    @classmethod
    def get_stylesheet(cls, mode='light') -> str:
        """
        يولد QSS (Qt StyleSheet) كامل للتطبيق
        
        يجب أن يشمل:
        - أنماط لجميع المكونات (QPushButton, QLineEdit, etc.)
        - Hover states و Focus states
        - Disabled states
        - Transitions سلسة
        - دعم RTL/LTR
        """
        colors = cls.COLORS[mode]
        fonts = cls.FONTS
        spacing = cls.SPACING
        radius = cls.RADIUS
        
        return f"""
        /* Global Styles */
        QWidget {{
            background-color: {colors['background']};
            color: {colors['text_primary']};
            font-family: {fonts['family_primary']};
            font-size: {fonts['size_base']};
        }}
        
        /* Primary Button */
        QPushButton {{
            background-color: {colors['primary']};
            color: white;
            border: none;
            border-radius: {radius['md']};
            padding: {spacing['md']} {spacing['xl']};
            font-weight: {fonts['weight_medium']};
            font-size: {fonts['size_base']};
        }}
        
        QPushButton:hover {{
            background-color: {colors['primary_dark']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['primary_dark']};
            transform: translateY(1px);
        }}
        
        QPushButton:disabled {{
            background-color: {colors['surface_variant']};
            color: {colors['text_disabled']};
        }}
        
        /* Secondary Button */
        QPushButton[class="secondary"] {{
            background-color: transparent;
            color: {colors['primary']};
            border: 2px solid {colors['primary']};
        }}
        
        QPushButton[class="secondary"]:hover {{
            background-color: {colors['primary_light']}22;
        }}
        
        /* Input Fields */
        QLineEdit, QTextEdit, QSpinBox {{
            background-color: {colors['surface']};
            border: 2px solid {colors['border']};
            border-radius: {radius['md']};
            padding: {spacing['md']};
            color: {colors['text_primary']};
            font-size: {fonts['size_base']};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {{
            border-color: {colors['border_focus']};
            outline: none;
        }}
        
        /* Cards & Panels */
        QGroupBox {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: {radius['lg']};
            padding: {spacing['xl']};
            margin-top: {spacing['xl']};
            font-weight: {fonts['weight_semibold']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {spacing['lg']};
            padding: 0 {spacing['sm']};
        }}
        
        /* Tabs */
        QTabWidget::pane {{
            border: none;
            background-color: {colors['surface']};
            border-radius: {radius['lg']};
        }}
        
        QTabBar::tab {{
            background-color: transparent;
            color: {colors['text_secondary']};
            padding: {spacing['md']} {spacing['xl']};
            margin-right: {spacing['sm']};
            border-radius: {radius['md']} {radius['md']} 0 0;
            font-weight: {fonts['weight_medium']};
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors['surface']};
            color: {colors['primary']};
            border-bottom: 3px solid {colors['primary']};
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors['surface_variant']};
        }}
        
        /* Status Bar */
        QStatusBar {{
            background-color: {colors['surface']};
            border-top: 1px solid {colors['border']};
            padding: {spacing['sm']};
        }}
        
        /* Scrollbars */
        QScrollBar:vertical {{
            background-color: {colors['background']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['text_disabled']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['text_secondary']};
        }}
        
        /* ComboBox */
        QComboBox {{
            background-color: {colors['surface']};
            border: 2px solid {colors['border']};
            border-radius: {radius['md']};
            padding: {spacing['md']};
            color: {colors['text_primary']};
        }}
        
        QComboBox:hover {{
            border-color: {colors['primary_light']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        
        /* Table */
        QTableWidget {{
            background-color: {colors['surface']};
            border: 1px solid {colors['border']};
            border-radius: {radius['lg']};
            gridline-color: {colors['divider']};
        }}
        
        QTableWidget::item {{
            padding: {spacing['md']};
        }}
        
        QTableWidget::item:selected {{
            background-color: {colors['primary_light']}33;
            color: {colors['primary']};
        }}
        
        QHeaderView::section {{
            background-color: {colors['surface_variant']};
            border: none;
            border-bottom: 2px solid {colors['divider']};
            padding: {spacing['md']};
            font-weight: {fonts['weight_semibold']};
        }}
        """
```

#### 2. مكونات UI حديثة

```python
# ملف جديد: ui_components/modern_components.py

class ModernCard(QFrame):
    """
    بطاقة حديثة بظل وانتقالات سلسة
    
    Features:
    - ظل ديناميكي عند hover
    - حدود دائرية
    - padding داخلي
    - اختياري: أيقونة في الأعلى
    - اختياري: عنوان + وصف
    """
    
    def __init__(self, title=None, icon=None, description=None):
        super().__init__()
        self.setup_ui(title, icon, description)
        
    def setup_ui(self, title, icon, description):
        """
        Layout:
        ┌─────────────────┐
        │  [Icon]         │
        │  Title          │
        │  Description    │
        │  [Content]      │
        └─────────────────┘
        """


class StatusIndicator(QWidget):
    """
    مؤشر حالة حديث مع رسوم متحركة
    
    States:
    - connected (أخضر نابض)
    - disconnected (رمادي)
    - error (أحمر وامض)
    - warning (برتقالي)
    - scanning (أزرق دوار)
    """
    
    def __init__(self, state='disconnected'):
        super().__init__()
        self.state = state
        self.animation = QPropertyAnimation(self, b"pulse")
        self.setup_ui()
        
    def set_state(self, state):
        """يبدل الحالة مع انتقال سلس"""
        

class ModernButton(QPushButton):
    """
    زر حديث مع أيقونة واختياري: loading state
    
    Features:
    - أيقونة على اليسار/اليمين
    - loading spinner عند الضغط
    - ripple effect عند النقر
    - variants: primary, secondary, success, danger
    """
    
    def __init__(self, text, icon=None, variant='primary', loading=False):
        super().__init__(text)
        self.icon = icon
        self.variant = variant
        self.is_loading = loading
        

class ProgressIndicator(QWidget):
    """
    مؤشر تقدم دائري حديث (مثل Material Design)
    
    Types:
    - determinate (نسبة مئوية)
    - indeterminate (دوران مستمر)
    """
    

class NotificationToast(QWidget):
    """
    إشعار منبثق من الزاوية
    
    Types:
    - success (أخضر)
    - error (أحمر)
    - warning (برتقالي)
    - info (أزرق)
    
    Features:
    - ظهور من الأسفل/الأعلى
    - اختفاء تلقائي بعد 3-5 ثواني
    - زر إغلاق
    - أيقونة حسب النوع
    """
    

class DataTable(QTableWidget):
    """
    جدول بيانات احترافي
    
    Features:
    - تصفية حية (live filter)
    - فرز قابل للنقر
    - تصدير إلى CSV/Excel
    - نسخ الصفوف
    - تحديد متعدد
    - سياق menu بالنقر اليمين
    """
    

class SearchBar(QLineEdit):
    """
    شريط بحث حديث
    
    Features:
    - أيقونة بحث على اليسار
    - زر مسح على اليمين (يظهر عند الكتابة)
    - placeholder text
    - تسليط الضوء على النتائج
    - اختصارات (Ctrl+F للتركيز)
    """
```

#### 3. النافذة الرئيسية المحسنة

```python
# تحديث: ui_components/main_window.py

class ModernMainWindow(QMainWindow):
    """
    نافذة رئيسية احترافية محسنة بالكامل
    
    NEW FEATURES:
    - شريط عنوان مخصص (custom title bar)
    - شريط جانبي للتنقل بدلاً من tabs
    - لوحة معلومات (Dashboard) كصفحة رئيسية
    - شريط إشعارات في الأعلى
    - شريط حالة محسن في الأسفل
    - دعم Dark/Light mode
    - دعم ملء الشاشة
    - حفظ/استعادة موضع النافذة
    """
    
    def __init__(self):
        super().__init__()
        self.theme_mode = 'light'  # or 'dark'
        self.translator = Translator("ar")
        self.nfc_manager = NFCReaderManager()
        self.diagnostics = SystemDiagnostics()
        
        self.init_ui()
        self.setup_shortcuts()
        self.load_settings()
        
    def init_ui(self):
        """
        Layout الجديد:
        
        ┌──────────────────────────────────────────────┐
        │ [Custom Title Bar]                      ⚙ ─ □ × │
        ├──────────────────────────────────────────────┤
        │ [Notification Bar - يظهر عند الحاجة]         │
        ├────────┬─────────────────────────────────────┤
        │        │ ┌─ Dashboard ───────────────────┐   │
        │ Side   │ │ ┌─────┐  ┌─────┐  ┌─────┐   │   │
        │ Nav    │ │ │Card │  │Card │  │Card │   │   │
        │        │ │ └─────┘  └─────┘  └─────┘   │   │
        │ 📊     │ │                              │   │
        │ 📖     │ │ ┌── Recent Activity ────┐   │   │
        │ ✏️     │ │ │                        │   │   │
        │ 🔐     │ │ │  [Activity Log]        │   │   │
        │ ⚙️     │ │ └────────────────────────┘   │   │
        │        │ └──────────────────────────────┘   │
        ├────────┴─────────────────────────────────────┤
        │ Status: ● Connected | Cards: 15 | Time: 14:30│
        └──────────────────────────────────────────────┘
        """
        
        # Custom title bar
        self.create_custom_titlebar()
        
        # Notification bar (hidden by default)
        self.notification_bar = NotificationBar()
        
        # Main content area
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        
        # Side navigation
        self.side_nav = SideNavigation()
        self.side_nav.page_changed.connect(self.change_page)
        main_layout.addWidget(self.side_nav)
        
        # Content stack
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.create_dashboard_page())
        self.content_stack.addWidget(self.create_read_page())
        self.content_stack.addWidget(self.create_write_page())
        self.content_stack.addWidget(self.create_security_page())
        self.content_stack.addWidget(self.create_settings_page())
        main_layout.addWidget(self.content_stack)
        
        self.setCentralWidget(main_widget)
        
        # Enhanced status bar
        self.create_modern_statusbar()
        
    def create_dashboard_page(self) -> QWidget:
        """
        لوحة معلومات شاملة - NEW!
        
        يجب أن تعرض:
        - بطاقات إحصائيات (عدد القراءات اليوم، إجمالي البطاقات، معدل النجاح)
        - رسم بياني لنشاط القراءة (خط زمني)
        - قائمة آخر البطاقات المقروءة (5-10 بطاقات)
        - حالة القارئ (بصري جذاب)
        - روابط سريعة لأكثر الإجراءات استخداماً
        """
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        
        # Stats Cards Row
        stats_row = QHBoxLayout()
        
        # Card 1: Reader Status
        reader_card = ModernCard(
            title=self.translator.get("reader_status"),
            icon="reader_icon.svg"
        )
        stats_row.addWidget(reader_card)
        
        # Card 2: Today's Reads
        reads_card = ModernCard(
            title=self.translator.get("today_reads"),
            icon="stats_icon.svg"
        )
        stats_row.addWidget(reads_card)
        
        # Card 3: Success Rate
        success_card = ModernCard(
            title=self.translator.get("success_rate"),
            icon="success_icon.svg"
        )
        stats_row.addWidget(success_card)
        
        layout.addLayout(stats_row)
        
        # Activity Chart
        chart_widget = self.create_activity_chart()
        layout.addWidget(chart_widget)
        
        # Recent Activity Table
        recent_activity = DataTable()
        recent_activity.setColumnCount(4)
        recent_activity.setHorizontalHeaderLabels([
            self.translator.get("time"),
            self.translator.get("uid"),
            self.translator.get("action"),
            self.translator.get("status")
        ])
        layout.addWidget(recent_activity)
        
        return dashboard
        
    def create_activity_chart(self) -> QWidget:
        """
        رسم بياني للنشاط اليومي/الأسبوعي
        
        استخدم PyQtGraph أو matplotlib
        - خط زمني لعدد القراءات
        - ألوان تتبع theme mode
        - تفاعلي (hover لعرض التفاصيل)
        """
        
    def create_custom_titlebar(self):
        """
        شريط عنوان مخصص (بدون إطار Windows الافتراضي)
        
        يحتوي على:
        - أيقونة التطبيق + العنوان
        - أزرار: Settings, Theme Toggle, Minimize, Maximize, Close
        - إمكانية سحب النافذة
        """
        
    def setup_shortcuts(self):
        """
        اختصارات لوحة المفاتيح
        
        - Ctrl+R: قراءة سريعة
        - Ctrl+W: كتابة سريعة
        - Ctrl+D: فتح Dashboard
        - Ctrl+, : فتح Settings
        - Ctrl+T: تبديل Theme
        - Ctrl+L: تبديل اللغة
        - Ctrl+Q: خروج
        - F5: إعادة فحص القارئات
        - Esc: إلغاء العملية الحالية
        """
        
        QShortcut(QKeySequence("Ctrl+R"), self, self.quick_read)
        QShortcut(QKeySequence("Ctrl+W"), self, self.quick_write)
        QShortcut(QKeySequence("F5"), self, self.rescan_readers)
        # ... etc


class SideNavigation(QWidget):
    """
    شريط تنقل جانبي حديث
    
    Features:
    - أيقونات جميلة لكل صفحة
    - تسليط ضوء على الصفحة النشطة
    - tooltips للعناوين
    - قابل للطي (collapsible) لإظهار الأيقونات فقط
    - انتقالات سلسة
    """
    
    page_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.current_index = 0
        self.is_collapsed = False
        self.setup_ui()
        
    def setup_ui(self):
        """
        Layout:
        ┌────────────┐
        │ 📊 Dashboard│
        │ 📖 Read    │  ← active (highlighted)
        │ ✏️ Write   │
        │ 🔐 Security│
        │ ⚙️ Settings│
        │            │
        │ [Collapse] │
        └────────────┘
        """


class NotificationBar(QFrame):
    """
    شريط إشعارات في أعلى النافذة
    
    يظهر عند:
    - فقدان الاتصال بالقارئ
    - تحديث متاح
    - رسائل مهمة من النظام
    
    Features:
    - ظهور/اختفاء سلس من الأعلى
    - ألوان حسب نوع الرسالة
    - زر إغلاق
    - زر إجراء (action button) اختياري
    """
```

---

## 📊 ميزات جديدة مطلوبة

### 1. نظام قاعدة بيانات محلية

```python
# ملف جديد: database.py

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class CardRecord(Base):
    """
    سجل قراءة/كتابة بطاقة
    
    الحقول:
    - id (PK)
    - uid (string, unique index)
    - first_seen (datetime)
    - last_seen (datetime)
    - read_count (int)
    - write_count (int)
    - nickname (string, nullable) - اسم مخصص للبطاقة
    - notes (text, nullable)
    - data_snapshots (JSON) - لقطات للبيانات عبر الزمن
    - tags (string) - وسوم مفصولة بفواصل
    """
    __tablename__ = 'card_records'
    
    id = Column(Integer, primary_key=True)
    uid = Column(String(32), unique=True, index=True, nullable=False)
    first_seen = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    read_count = Column(Integer, default=0)
    write_count = Column(Integer, default=0)
    nickname = Column(String(100))
    notes = Column(Text)
    data_snapshots = Column(Text)  # JSON string
    tags = Column(String(500))


class ActivityLog(Base):
    """
    سجل كل الأنشطة
    
    الحقول:
    - id (PK)
    - timestamp (datetime)
    - action_type (read/write/error)
    - card_uid (string, FK)
    - block_number (int, nullable)
    - data (text, nullable)
    - status (success/failure)
    - error_message (text, nullable)
    """
    __tablename__ = 'activity_logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    action_type = Column(String(20), nullable=False)
    card_uid = Column(String(32), index=True)
    block_number = Column(Integer)
    data = Column(Text)
    status = Column(String(20))
    error_message = Column(Text)


class DatabaseManager:
    """
    مدير قاعدة البيانات
    
    الوظائف:
    - initialize_db(): إنشاء الجداول
    - add_card_record(uid, ...): إضافة/تحديث سجل بطاقة
    - log_activity(action, ...): تسجيل نشاط
    - get_card_history(uid): سجل بطاقة معينة
    - get_recent_activities(limit=50): آخر الأنشطة
    - get_statistics(date_from, date_to): إحصائيات
    - search_cards(query): بحث في البطاقات
    - export_to_csv(filename): تصدير البيانات
    """
    
    def __init__(self, db_path='nfc_reader.db'):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
    def add_card_record(self, uid, nickname=None, notes=None):
        """إضافة أو تحديث سجل بطاقة"""
        
    def log_activity(self, action_type, card_uid, status, **kwargs):
        """تسجيل نشاط"""
        
    def get_statistics(self, date_from=None, date_to=None):
        """
        إحصائيات شاملة
        
        Returns:
        {
            'total_cards': int,
            'total_reads': int,
            'total_writes': int,
            'success_rate': float,
            'activity_by_day': {date: count},
            'top_cards': [(uid, count)],
            'recent_errors': [error_msgs]
        }
        """
```

### 2. نظام التصدير والاستيراد

```python
# ملف جديد: import_export.py

class DataExporter:
    """
    تصدير البيانات بصيغ متعددة
    
    الصيغات المدعومة:
    - CSV (للبطاقات والأنشطة)
    - Excel (XLSX) مع أوراق متعددة
    - JSON (لنسخ احتياطي كامل)
    - PDF (تقرير منسق)
    """
    
    def export_cards_to_csv(self, filename, filters=None):
        """تصدير قائمة البطاقات"""
        
    def export_activity_to_excel(self, filename, date_from, date_to):
        """تصدير الأنشطة مع إحصائيات"""
        
    def generate_pdf_report(self, filename, date_from, date_to):
        """
        تقرير PDF احترافي
        
        يتضمن:
        - ملخص إحصائي
        - رسوم بيانية
        - جدول التفاصيل
        - header/footer مخصص
        """
        
    def backup_database(self, filename):
        """نسخة احتياطية كاملة JSON"""


class DataImporter:
    """
    استيراد البيانات
    
    يدعم:
    - CSV (البطاقات)
    - JSON (استعادة نسخة احتياطية)
    - Excel (XLSX)
    """
    
    def import_from_csv(self, filename):
        """استيراد بطاقات من CSV"""
        
    def restore_from_backup(self, filename):
        """استعادة من JSON"""
```

### 3. نظام المهام المجدولة

```python
# ملف جديد: scheduler.py

class AutomationScheduler:
    """
    مهام تلقائية ومجدولة
    
    أمثلة:
    - قراءة تلقائية عند اكتشاف بطاقة
    - حفظ نسخة احتياطية يومياً
    - مسح السجلات القديمة (> 90 يوم)
    - إرسال إشعارات لبطاقات معينة
    """
    
    def __init__(self):
        self.tasks = []
        self.is_running = False
        
    def add_task(self, task_type, interval, callback):
        """إضافة مهمة مجدولة"""
        
    def auto_backup_daily(self, backup_dir):
        """نسخ احتياطي تلقائي"""
        
    def auto_cleanup_logs(self, days_to_keep=90):
        """تنظيف السجلات القديمة"""
```

### 4. نظام البحث المتقدم

```python
# ملف جديد: search.py

class AdvancedSearch:
    """
    بحث متقدم مع فلاتر
    
    معايير البحث:
    - UID (كامل أو جزئي)
    - Nickname
    - Tags
    - Date range
    - Action type
    - Status (success/failure)
    - Block number
    - Data content (hex search)
    
    Features:
    - بحث حي (live search)
    - حفظ استعلامات البحث المفضلة
    - تصدير نتائج البحث
    """
    
    def search(self, query, filters):
        """
        Returns:
        {
            'cards': [CardRecord],
            'activities': [ActivityLog],
            'count': int,
            'took_ms': int
        }
        """
```

### 5. نظام الإشعارات

```python
# ملف جديد: notifications.py

class NotificationSystem:
    """
    نظام إشعارات شامل
    
    Types:
    - System tray notifications (عند قراءة بطاقة مهمة)
    - In-app toasts (رسائل نجاح/فشل)
    - Sound alerts (اختياري)
    - Email notifications (للأحداث المهمة)
    
    Settings:
    - تفعيل/تعطيل حسب النوع
    - اختيار الأصوات
    - إعدادات Email SMTP
    """
    
    def __init__(self):
        self.settings = NotificationSettings.load()
        
    def show_card_detected(self, uid, nickname=None):
        """إشعار باكتشاف بطاقة"""
        
    def show_system_tray(self, title, message, icon='info'):
        """إشعار في system tray"""
        
    def play_sound(self, sound_type):
        """تشغيل صوت تنبيه"""
```

### 6. تحليل البيانات المرئي

```python
# ملف جديد: analytics.py

class AnalyticsDashboard:
    """
    لوحة تحليلات مرئية
    
    الرسوم البيانية:
    1. Line Chart: نشاط القراءة عبر الزمن
    2. Bar Chart: أكثر البطاقات استخداماً
    3. Pie Chart: نسب نجاح/فشل العمليات
    4. Heatmap: نشاط حسب ساعة اليوم
    5. Timeline: تاريخ بطاقة معينة
    
    استخدم: matplotlib أو PyQtGraph
    """
    
    def create_activity_timeline(self, date_from, date_to):
        """رسم بياني خطي للنشاط"""
        
    def create_top_cards_chart(self, limit=10):
        """أكثر البطاقات قراءة"""
        
    def create_success_rate_pie(self):
        """نسبة النجاح/الفشل"""
        
    def create_hourly_heatmap(self):
        """Heatmap النشاط حسب الساعة"""
```

---

## 🔧 تحسينات تقنية متقدمة

### 1. Multi-threading المحسن

```python
# تحديث: reader.py

class NFCReaderManager(QObject):
    """
    IMPROVEMENTS:
    
    1. استخدم QThreadPool بدلاً من threading.Thread
    2. أضف priority queue للعمليات
    3. أضف rate limiting لتجنب إرهاق القارئ
    4. أضف connection pooling
    5. أضف retry logic ذكي مع exponential backoff
    """
    
    def __init__(self):
        super().__init__()
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(3)
        
        # Priority queue للعمليات
        self.operation_queue = PriorityQueue()
        
        # Rate limiter
        self.rate_limiter = RateLimiter(max_ops_per_second=10)
        
        # Retry strategy
        self.retry_strategy = ExponentialBackoff(
            max_retries=3,
            base_delay=0.5,
            max_delay=5.0
        )
        
    def read_block_async(self, block_num, priority=1, callback=None):
        """قراءة غير متزامنة مع priority"""
        worker = ReadWorker(self, block_num)
        worker.signals.result.connect(callback)
        self.thread_pool.start(worker, priority)


class ReadWorker(QRunnable):
    """Worker للقراءة في خيط منفصل"""
    
    class Signals(QObject):
        result = pyqtSignal(object)
        error = pyqtSignal(str)
        progress = pyqtSignal(int)
        
    def __init__(self, manager, block_num):
        super().__init__()
        self.manager = manager
        self.block_num = block_num
        self.signals = self.Signals()
        
    def run(self):
        try:
            data = self.manager.read_block(self.block_num)
            self.signals.result.emit(data)
        except Exception as e:
            self.signals.error.emit(str(e))
```

### 2. Caching System

```python
# ملف جديد: cache.py

class DataCache:
    """
    نظام تخزين مؤقت للبيانات
    
    يخزن:
    - آخر البيانات المقروءة من كل block
    - معلومات البطاقات المكتشفة
    - نتائج البحث
    - إعدادات المستخدم
    
    Features:
    - TTL (Time To Live) لكل entry
    - حجم محدود (LRU eviction)
    - تخزين على القرص للاستمرارية
    """
    
    def __init__(self, max_size=1000, default_ttl=300):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.expiry = {}
        
    def get(self, key, default=None):
        """الحصول على قيمة من الكاش"""
        
    def set(self, key, value, ttl=None):
        """تخزين قيمة في الكاش"""
        
    def invalidate(self, key):
        """إبطال entry"""
        
    def clear_expired(self):
        """مسح العناصر منتهية الصلاحية"""
```

### 3. Configuration Management

```python
# ملف جديد: config.py

class AppConfig:
    """
    إدارة إعدادات التطبيق
    
    الإعدادات:
    - theme (light/dark)
    - language (ar/en)
    - auto_read (bool)
    - auto_backup (bool)
    - backup_interval (days)
    - notification_enabled (bool)
    - sound_enabled (bool)
    - window_geometry (x, y, w, h)
    - reader_preference (string)
    - custom_sounds (dict)
    - smtp_settings (dict)
    """
    
    DEFAULT_CONFIG = {
        'theme': 'light',
        'language': 'ar',
        'auto_read': False,
        'auto_backup': True,
        'backup_interval': 7,
        'notification_enabled': True,
        'sound_enabled': True,
        'window_geometry': None,
        'reader_preference': None,
    }
    
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load()
        
    def load(self):
        """تحميل الإعدادات من ملف"""
        
    def save(self):
        """حفظ الإعدادات"""
        
    def get(self, key, default=None):
        """الحصول على إعداد"""
        
    def set(self, key, value):
        """تعيين إعداد"""
        
    def reset_to_defaults(self):
        """إعادة تعيين للافتراضيات"""
```

### 4. Error Handling & Logging

```python
# ملف جديد: error_handler.py

class ErrorHandler:
    """
    معالج أخطاء مركزي
    
    Features:
    - تسجيل الأخطاء في ملف
    - إرسال تقارير الأخطاء (اختياري)
    - عرض رسائل خطأ واضحة للمستخدم
    - اقتراح حلول تلقائية
    """
    
    ERROR_SOLUTIONS = {
        'NO_READERS_FOUND': [
            'Check if PC/SC service is running',
            'Reconnect the USB cable',
            'Try a different USB port',
            'Install/update drivers'
        ],
        'CARD_CONNECTION_FAILED': [
            'Clean the card surface',
            'Try placing the card closer',
            'Remove any metal objects nearby'
        ],
        'WRITE_FAILED': [
            'Card may be write-protected',
            'Check block number',
            'Verify data format'
        ]
    }
    
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """معالج عام للاستثناءات"""
        
    def log_error(self, error_code, details):
        """تسجيل خطأ مع التفاصيل"""
        
    def suggest_solution(self, error_code):
        """اقتراح حلول للخطأ"""


# Setup global exception handler
import sys
sys.excepthook = ErrorHandler().handle_exception
```

### 5. Security & Encryption

```python
# ملف جديد: security.py

class DataEncryption:
    """
    تشفير البيانات الحساسة
    
    استخدم:
    - cryptography library
    - Fernet (symmetric encryption)
    - Password-based key derivation (PBKDF2)
    
    يشفر:
    - SMTP passwords
    - API keys
    - Sensitive card data (اختياري)
    """
    
    def __init__(self, master_password=None):
        self.master_password = master_password
        self.fernet = None
        
        if master_password:
            self.derive_key(master_password)
            
    def derive_key(self, password):
        """اشتقاق مفتاح من كلمة المرور"""
        
    def encrypt(self, data):
        """تشفير بيانات"""
        
    def decrypt(self, encrypted_data):
        """فك تشفير"""


class AccessControl:
    """
    التحكم بالوصول (اختياري للنسخ المؤسسية)
    
    Features:
    - مستويات صلاحيات (Admin, User, Viewer)
    - قيود على العمليات حسب الصلاحية
    - سجل audit للعمليات الحساسة
    """
```

---

## 📱 تحسينات تجربة المستخدم (UX)

### 1. Onboarding & Tutorials

```python
# ملف جديد: onboarding.py

class OnboardingWizard(QWizard):
    """
    معالج الإعداد الأولي
    
    الخطوات:
    1. Welcome screen
    2. Language selection
    3. Theme selection
    4. Reader detection & test
    5. Quick tutorial
    6. Finish & open app
    
    يظهر فقط في:
    - أول تشغيل
    - بعد إعادة التعيين
    - عند طلب المستخدم (Help > Tutorial)
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to NFC Manager")
        self.add_pages()
        
    def add_pages(self):
        self.addPage(WelcomePage())
        self.addPage(LanguagePage())
        self.addPage(ThemePage())
        self.addPage(ReaderTestPage())
        self.addPage(TutorialPage())
        self.addPage(FinishPage())


class InteractiveTutorial(QWidget):
    """
    دروس تفاعلية داخل التطبيق
    
    Features:
    - Tooltips تفاعلية تظهر عند التحويم
    - Highlight للعناصر المهمة
    - خطوات مرقمة
    - إمكانية التخطي
    - تقدم قابل للحفظ
    """
    
    def start_tutorial(self, tutorial_name):
        """بدء درس معين"""
```

### 2. Context Menus & Quick Actions

```python
# تحديث: جميع المكونات

class EnhancedReadTab(ReadTab):
    """
    تبويب قراءة محسن
    
    NEW FEATURES:
    - Context menu على كل بطاقة:
        • Copy UID
        • Add to favorites
        • Set nickname
        • View history
        • Export data
        
    - Quick actions bar:
        • Read all blocks (dump)
        • Compare with saved
        • Auto-read on detect (toggle)
        
    - Drag & drop support:
        • سحب UID لتطبيقات أخرى
    """
    
    def create_context_menu(self):
        menu = QMenu(self)
        
        copy_action = QAction("Copy UID", self)
        copy_action.triggered.connect(self.copy_uid)
        menu.addAction(copy_action)
        
        favorite_action = QAction("Add to Favorites", self)
        menu.addAction(favorite_action)
        
        # ... more actions
        
        return menu
```

### 3. Keyboard Shortcuts Guide

```python
# ملف جديد: shortcuts.py

class ShortcutsGuide(QDialog):
    """
    نافذة عرض جميع الاختصارات
    
    التنسيق:
    ┌────────────────────────────────────┐
    │  Keyboard Shortcuts                │
    ├────────────────────────────────────┤
    │                                    │
    │  General:                          │
    │    Ctrl+R ........ Quick Read      │
    │    Ctrl+W ........ Quick Write     │
    │    F5 ............ Refresh         │
    │                                    │
    │  Navigation:                       │
    │    Ctrl+1 ........ Dashboard       │
    │    Ctrl+2 ........ Read            │
    │    ...                             │
    │                                    │
    │  [Print] [Close]                   │
    └────────────────────────────────────┘
    """
    
    SHORTCUTS = {
        'General': {
            'Ctrl+R': 'Quick Read',
            'Ctrl+W': 'Quick Write',
            'F5': 'Refresh Readers',
            'Ctrl+,': 'Settings',
        },
        'Navigation': {
            'Ctrl+1': 'Dashboard',
            'Ctrl+2': 'Read Tab',
            'Ctrl+3': 'Write Tab',
            'Ctrl+4': 'Security Tab',
            'Ctrl+5': 'Settings Tab',
        },
        'Editing': {
            'Ctrl+C': 'Copy',
            'Ctrl+V': 'Paste',
            'Ctrl+A': 'Select All',
            'Delete': 'Clear',
        }
    }
```

### 4. Help System

```python
# ملف جديد: help_system.py

class HelpSystem:
    """
    نظام مساعدة متكامل
    
    يتضمن:
    - Documentation viewer (HTML/Markdown)
    - FAQ section
    - Troubleshooting guide
    - Video tutorials (روابط)
    - Contact support
    - Check for updates
    """
    
    def show_documentation(self, topic=None):
        """عرض التوثيق"""
        
    def show_faq(self):
        """الأسئلة الشائعة"""
        
    def show_troubleshooting(self):
        """دليل حل المشاكل"""
        
    def check_for_updates(self):
        """فحص التحديثات"""
```

---

## 🧪 Testing & Quality Assurance

### 1. Unit Tests التوسع

```python
# في tests/

class TestNFCReaderManager(unittest.TestCase):
    """
    اختبارات شاملة لـ NFCReaderManager
    
    يجب أن تغطي:
    - اكتشاف القارئات
    - الاتصال بالبطاقات
    - قراءة/كتابة البيانات
    - معالجة الأخطاء
    - Multi-threading safety
    - Memory leaks
    """
    
    def setUp(self):
        self.manager = NFCReaderManager()
        
    def test_reader_detection(self):
        """اختبار اكتشاف القارئات"""
        
    def test_card_read(self):
        """اختبار قراءة بطاقة"""
        
    def test_card_write(self):
        """اختبار كتابة على بطاقة"""
        
    def test_error_handling(self):
        """اختبار معالجة الأخطاء"""


class TestUI(unittest.TestCase):
    """
    اختبارات الواجهة
    
    استخدم pytest-qt
    """
    
    def test_theme_switching(self, qtbot):
        """اختبار تبديل Theme"""
        
    def test_language_switching(self, qtbot):
        """اختبار تبديل اللغة"""
        
    def test_shortcuts(self, qtbot):
        """اختبار الاختصارات"""
```

### 2. Integration Tests

```python
# tests/test_integration.py

class TestFullWorkflow(unittest.TestCase):
    """
    اختبار سيناريوهات كاملة
    
    Scenarios:
    1. تشغيل التطبيق → اكتشاف قارئ → قراءة بطاقة → حفظ
    2. كتابة بيانات → التحقق → التصدير
    3. استيراد بيانات → الكتابة → التحقق
    """
```

### 3. Performance Tests

```python
# tests/test_performance.py

class TestPerformance(unittest.TestCase):
    """
    اختبارات الأداء
    
    Benchmarks:
    - زمن بدء التطبيق (< 2 seconds)
    - زمن قراءة بطاقة (< 100ms)
    - زمن كتابة block (< 200ms)
    - استهلاك الذاكرة (< 100MB)
    - CPU usage في الوضع الخامل (< 5%)
    """
    
    def test_startup_time(self):
        """قياس زمن البدء"""
        
    def test_read_speed(self):
        """قياس سرعة القراءة"""
```

---

## 📦 Packaging & Distribution

### 1. Installer Creation

```python
# ملف جديد: build_installer.py

"""
إنشاء installer احترافي

Linux:
- .deb package (Debian/Ubuntu)
- .rpm package (Fedora/RHEL)
- AppImage (portable)

Windows:
- NSIS installer
- MSI package
- Portable .exe (PyInstaller)

Features:
- Auto-detect dependencies
- Desktop shortcut
- Start menu entry
- Auto-update mechanism
- Uninstaller
"""

from setuptools import setup

setup(
    name='ACR122U-Manager',
    version='2.0.0',
    description='Professional NFC Reader Management Tool',
    author='Your Name',
    packages=['acr122u_app'],
    install_requires=[
        'PyQt6>=6.4.0',
        'pyscard>=2.0.0',
        'pynput>=1.7.6',
        'sqlalchemy>=2.0.0',
        'cryptography>=41.0.0',
        'matplotlib>=3.7.0',
        'openpyxl>=3.1.0',
        'reportlab>=4.0.0',
    ],
    entry_points={
        'console_scripts': [
            'acr122u-manager=acr122u_app.main:main',
        ],
    },
)
```

### 2. Auto-Update System

```python
# ملف جديد: updater.py

class AutoUpdater:
    """
    نظام تحديث تلقائي
    
    Features:
    - فحص التحديثات عند البدء
    - تنزيل وتثبيت تلقائي (اختياري)
    - Changelog viewer
    - Rollback للإصدار السابق
    
    يستخدم:
    - GitHub Releases API
    - أو خادم تحديثات خاص
    """
    
    def check_for_updates(self):
        """فحص وجود تحديثات"""
        
    def download_update(self, version):
        """تنزيل تحديث"""
        
    def install_update(self):
        """تثبيت التحديث"""
        
    def show_changelog(self, version):
        """عرض التغييرات"""
```

---

## 🎯 الأولويات والخطة الزمنية

### المرحلة 1 (أسبوع 1-2): إصلاح المشاكل الحرجة
✅ **CRITICAL**:
1. إصلاح مشكلة اكتشاف القارئ
2. تحسين آلية البحث التلقائي
3. إضافة نظام تشخيص شامل
4. تحسين رسائل الأخطاء

### المرحلة 2 (أسبوع 3-4): تطوير الواجهة
🎨 **HIGH PRIORITY**:
1. تطبيق نظام التصميم الحديث (Theme System)
2. إنشاء المكونات الحديثة (ModernCard, StatusIndicator, etc.)
3. بناء النافذة الرئيسية الجديدة
4. إضافة Dark Mode
5. تحسين التجاوب مع RTL/LTR

### المرحلة 3 (أسبوع 5-6): الميزات الأساسية
⚙️ **MEDIUM PRIORITY**:
1. نظام قاعدة البيانات
2. Dashboard مع الإحصائيات
3. نظام البحث المتقدم
4. التصدير/الاستيراد
5. نظام الإشعارات

### المرحلة 4 (أسبوع 7-8): الميزات المتقدمة
🚀 **NICE TO HAVE**:
1. Analytics & Charts
2. المهام المجدولة
3. نظام التشفير
4. Onboarding wizard
5. Help system

### المرحلة 5 (أسبوع 9-10): Testing & Polish
✨ **FINAL TOUCHES**:
1. Unit & Integration tests
2. Performance optimization
3. Bug fixes
4. Documentation
5. Packaging & Distribution

---

## 📋 Checklist التنفيذ

عند تنفيذ كل ميزة، تأكد من:

✅ الكود نظيف ومعلق بشكل جيد
✅ يتبع PEP 8 style guide
✅ Type hints لجميع الدوال
✅ Docstrings شاملة
✅ معالجة جميع الأخطاء المحتملة
✅ Logging مناسب
✅ Unit tests (coverage > 80%)
✅ دعم RTL/LTR
✅ دعم Dark/Light mode
✅ Responsive design
✅ Accessibility (keyboard navigation)
✅ Translations (AR/EN)
✅ Documentation محدثة

---

## 🎓 أفضل الممارسات

### الكود:
```python
# استخدم Type Hints
def read_block(self, block_num: int) -> List[int]:
    """
    Read a block from the card.
    
    Args:
        block_num: Block number to read (0-255)
        
    Returns:
        List of 16 bytes
        
    Raises:
        NoCardException: If no card is present
        CardConnectionException: If connection fails
    """
    
# استخدم Context Managers
with self.db_session() as session:
    session.add(record)
    session.commit()
    
# استخدم Enums
from enum import Enum

class CardType(Enum):
    MIFARE_CLASSIC = "MIFARE Classic"
    MIFARE_ULTRALIGHT = "MIFARE Ultralight"
    NTAG = "NTAG"
    
# استخدم dataclasses
from dataclasses import dataclass

@dataclass
class CardInfo:
    uid: str
    card_type: CardType
    capacity: int
    writable: bool
```

### الواجهة:
```python
# فصل المنطق عن العرض (MVC)
class CardViewModel:
    """View Model للبطاقة"""
    
class CardView(QWidget):
    """View للبطاقة"""
    
# استخدم Signals للتواصل
class DataChanged(QObject):
    data_updated = pyqtSignal(dict)
    
# استخدم Resource files للأيقونات
from PyQt6 import QtCore
QtCore.QDir.addSearchPath('icons', 'resources/icons')
```

---

## 🚀 ابدأ الآن!

هذا البرومبت شامل لكل ما تحتاجه لتحويل المشروع إلى تطبيق احترافي عالمي المستوى.

**الخطوة التالية**: ابدأ بالمرحلة 1 - إصلاح المشاكل الحرجة!

```bash
# 1. إنشاء نسخة احتياطية
git add .
git commit -m "Backup before major refactoring"

# 2. إنشاء فرع جديد للتطوير
git checkout -b feature/modern-ui-v2

# 3. ابدأ التطوير!
# ابدأ بـ:
# - diagnostics.py (نظام التشخيص)
# - ui_components/theme.py (نظام التصميم)
# - تحديث reader.py (إصلاح الاكتشاف)
```

**Good luck! 🎉**
