# مدير قارئ ACR122U NFC

تطبيق احترافي بواجهة رسومية لإدارة قارئ ACR122U والبطاقات الذكية على نظام Linux.
يدعم اللغتين العربية والإنجليزية.

## المتطلبات
- Python 3.x
- PyQt6
- pyscard
- pynput
- حزمة pcscd (على نظام Linux)

## التثبيت على Linux
```bash
sudo apt-get update
sudo apt-get install pcscd libpcsclite-dev pcsc-tools
```

ثم تثبيت متطلبات بايثون:
```bash
python3 -m venv venv
source venv/bin/activate
pip install PyQt6 pyscard pynput
```

## التشغيل
```bash
python acr122u_app/main.py
```

## الميزات
- اكتشاف القارئ والبطاقة بشكل تلقائي
- قراءة البيانات (الـ UID ومحتوى الذاكرة)
- الكتابة على البطاقة مع التحذيرات اللازمة
- محاكاة لوحة المفاتيح لإدخال بيانات البطاقة تلقائيا
- سجل كامل للعمليات واللغة العربية مدعومة بالكامل
