import platform
import subprocess

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
                else:
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
