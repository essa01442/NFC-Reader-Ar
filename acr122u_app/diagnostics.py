import os
import platform
import subprocess

# Known NFC/Smart Card USB vendor:product IDs (ACR122U and common readers)
_NFC_USB_IDS = [
    ("072f", "2200"),  # ACS ACR122U
    ("072f", "2224"),  # ACS ACR122U (alternate firmware)
    ("072f", "220f"),  # ACS ACR1281U
    ("072f", "0901"),  # ACS ACR38U
    ("04e6", "5790"),  # SCM SCR3310
    ("04e6", "5116"),  # SCM SCR331
    ("08e6", "3437"),  # Gemplus USB Smart Card Reader
    ("04e6", "511d"),  # SCM SCR335
]

# udev rule template for ACR122U (and generic NFC readers)
_UDEV_RULE_CONTENT = """\
# ACR122U NFC Reader
SUBSYSTEMS=="usb", ATTRS{{idVendor}}=="072f", ATTRS{{idProduct}}=="2200", GROUP="plugdev", MODE="0660"
SUBSYSTEMS=="usb", ATTRS{{idVendor}}=="072f", ATTRS{{idProduct}}=="2224", GROUP="plugdev", MODE="0660"
# Generic PC/SC readers – ensure plugdev members can access them
SUBSYSTEM=="usb", ATTRS{{bDeviceClass}}=="0b", GROUP="plugdev", MODE="0660"
"""

_UDEV_RULE_PATH = "/etc/udev/rules.d/99-nfc-readers.rules"

class SystemDiagnostics:
    @staticmethod
    def check_pcscd_status():
        """
        Check if PC/SC service is running.
        Returns (is_running: bool, message: str)
        """
        sys_os = platform.system().lower()
        if "linux" in sys_os:
            try:
                # Check systemctl status for pcscd
                result = subprocess.run(
                    ['systemctl', 'is-active', 'pcscd'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.stdout.strip() == 'active':
                    return True, "خدمة pcscd تعمل بشكل سليم."

                # pcscd.service is not active – check whether socket activation is
                # the culprit (pcscd stops automatically when no client is connected).
                socket_result = subprocess.run(
                    ['systemctl', 'is-active', 'pcscd.socket'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if socket_result.stdout.strip() == 'active':
                    return False, (
                        "خدمة pcscd غير مفعلة (تشغيل عبر المقبس يوقفها تلقائيًا عند عدم الاستخدام). "
                        "لإصلاح التوقف التلقائي يرجى تنفيذ: "
                        "sudo systemctl disable pcscd.socket && "
                        "sudo systemctl enable pcscd && sudo systemctl start pcscd"
                    )

                return False, "خدمة pcscd غير مفعلة. يرجى تنفيذ: sudo systemctl start pcscd"
            except Exception as e:
                return False, f"تعذر التحقق من حالة pcscd: {str(e)}"

        elif "windows" in sys_os:
            try:
                # Check sc query SCardSvr on Windows
                result = subprocess.run(
                    ['sc', 'query', 'SCardSvr'],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                if "RUNNING" in result.stdout:
                    return True, "خدمة Smart Card تعمل بشكل سليم."
                else:
                    return False, "خدمة Smart Card متوقفة. يرجى تفعيلها من services.msc."
            except Exception as e:
                return False, f"تعذر التحقق من خدمة Smart Card: {str(e)}"

        elif "darwin" in sys_os:
            return True, "نظام macOS يدعم PC/SC بشكل مدمج، يُفترض أن الخدمة تعمل."

        return False, "نظام تشغيل غير معروف لتشخيص خدمة البطاقات الذكية."

    @staticmethod
    def check_user_permissions():
        """
        Check if the current user is in the required groups (plugdev, pcscd) on Linux.
        Returns (ok: bool, groups_found: list, message: str)
        """
        sys_os = platform.system().lower()
        if "linux" not in sys_os:
            return True, [], "فحص المجموعات متاح على Linux فقط."

        required_groups = ["plugdev", "pcscd"]
        found_groups = []

        try:
            import grp
            user_name = os.environ.get("USER") or os.environ.get("LOGNAME") or ""
            # Get all groups the current process belongs to
            current_gids = os.getgroups()
            current_gids.append(os.getgid())

            for group_name in required_groups:
                try:
                    grp_info = grp.getgrnam(group_name)
                    if grp_info.gr_gid in current_gids or (user_name and user_name in grp_info.gr_mem):
                        found_groups.append(group_name)
                except KeyError:
                    pass  # Group does not exist on this system

            if found_groups:
                return True, found_groups, f"المستخدم ضمن المجموعات: {', '.join(found_groups)}"
            else:
                missing = [g for g in required_groups if g not in found_groups]
                return False, found_groups, (
                    f"المستخدم ليس ضمن المجموعات المطلوبة ({', '.join(missing)}). "
                    "يرجى تنفيذ أوامر الإصلاح أدناه."
                )
        except Exception as e:
            return False, [], f"تعذر فحص مجموعات المستخدم: {str(e)}"

    @staticmethod
    def check_usb_devices():
        """
        Detect connected NFC/Smart Card USB devices using lsusb (Linux/macOS) or
        system device enumeration (Windows).
        Returns (devices_found: list[dict], message: str)
          Each dict has keys: vendor_id, product_id, description
        """
        sys_os = platform.system().lower()
        devices = []

        if "linux" in sys_os or "darwin" in sys_os:
            try:
                result = subprocess.run(
                    ['lsusb'],
                    capture_output=True, text=True, timeout=5
                )
                for line in result.stdout.splitlines():
                    line_lower = line.lower()
                    # Match known NFC USB IDs
                    for vendor, product in _NFC_USB_IDS:
                        if f"{vendor}:{product}" in line_lower:
                            devices.append({
                                "vendor_id": vendor,
                                "product_id": product,
                                "description": line.strip()
                            })
                            break
                    else:
                        # Also match by keyword
                        if any(kw in line_lower for kw in ("acr122", "nfc", "smart card", "smartcard", "072f")):
                            devices.append({
                                "vendor_id": "",
                                "product_id": "",
                                "description": line.strip()
                            })
            except FileNotFoundError:
                pass  # lsusb not available
            except Exception:
                pass

        elif "windows" in sys_os:
            try:
                result = subprocess.run(
                    ['powershell', '-Command',
                     'Get-PnpDevice -Class SmartCardReader | Select-Object Status,FriendlyName | Format-List'],
                    capture_output=True, text=True, timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                if result.stdout.strip():
                    for line in result.stdout.splitlines():
                        if "FriendlyName" in line:
                            name = line.split(":", 1)[-1].strip()
                            if name:
                                devices.append({
                                    "vendor_id": "",
                                    "product_id": "",
                                    "description": name
                                })
            except Exception:
                pass

        if devices:
            return devices, f"تم اكتشاف {len(devices)} جهاز قارئ NFC/بطاقة ذكية."
        return devices, "لم يتم اكتشاف أي جهاز قارئ NFC متصل."

    @staticmethod
    def get_fix_commands():
        """
        Return shell commands the user should run to fix device detection permissions on Linux.
        Returns list of (description: str, command: str)
        """
        sys_os = platform.system().lower()
        if "linux" not in sys_os:
            return []

        user = os.environ.get("USER") or os.environ.get("LOGNAME") or "$USER"
        return [
            ("تثبيت خدمة pcscd وأدوات البطاقات الذكية",
             "sudo apt-get install -y pcscd pcsc-tools libpcsclite-dev"),
            ("تعطيل تشغيل pcscd عبر المقبس (يسبب توقفها تلقائيًا بعد دقائق من الخمول)",
             "sudo systemctl disable pcscd.socket && sudo systemctl stop pcscd.socket"),
            ("تفعيل وتشغيل خدمة pcscd بشكل مستمر",
             "sudo systemctl enable pcscd && sudo systemctl start pcscd"),
            (f"إضافة المستخدم '{user}' إلى مجموعة plugdev",
             f"sudo usermod -aG plugdev {user}"),
            (f"إضافة المستخدم '{user}' إلى مجموعة pcscd (إن وُجدت)",
             f"sudo usermod -aG pcscd {user}"),
            (f"إنشاء قاعدة udev للسماح بالوصول إلى قارئ ACR122U\n  (احفظ في {_UDEV_RULE_PATH})",
             f"sudo tee {_UDEV_RULE_PATH} << 'EOF'\n{_UDEV_RULE_CONTENT.strip()}\nEOF"),
            ("إعادة تحميل قواعد udev",
             "sudo udevadm control --reload-rules && sudo udevadm trigger"),
            ("تسجيل الخروج وإعادة الدخول لتفعيل تغييرات المجموعات",
             "# يجب تسجيل الخروج وإعادة الدخول بعد الانتهاء"),
        ]

    @staticmethod
    def run_full_diagnostics():
        """
        Run all diagnostic checks and return a comprehensive report dict.
        """
        pcscd_ok, pcscd_msg = SystemDiagnostics.check_pcscd_status()
        perms_ok, groups, perms_msg = SystemDiagnostics.check_user_permissions()
        usb_devices, usb_msg = SystemDiagnostics.check_usb_devices()

        return {
            "pcscd": {"ok": pcscd_ok, "message": pcscd_msg},
            "permissions": {"ok": perms_ok, "groups": groups, "message": perms_msg},
            "usb_devices": {"devices": usb_devices, "message": usb_msg},
            "os": {"name": platform.system(), "version": platform.version()},
            "overall_ok": pcscd_ok and perms_ok,
        }
