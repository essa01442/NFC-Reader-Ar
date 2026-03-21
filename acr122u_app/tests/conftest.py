"""
Provide stub modules for pyscard (smartcard) so that tests can run without the
native pcsclite library installed. The test fixtures in test_reader.py patch
the specific classes they need; these stubs only need to satisfy the module-level
imports in reader.py.
"""
import sys
from unittest.mock import MagicMock

_SMARTCARD_MODS = [
    "smartcard",
    "smartcard.System",
    "smartcard.CardMonitoring",
    "smartcard.ReaderMonitoring",
    "smartcard.Exceptions",
    "smartcard.util",
]

for _mod in _SMARTCARD_MODS:
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

# Expose the specific names that reader.py imports at module level.
sys.modules["smartcard.System"].readers = MagicMock(return_value=[])
sys.modules["smartcard.util"].toHexString = lambda data: " ".join(f"{b:02X}" for b in data)

_exc_mod = sys.modules["smartcard.Exceptions"]
_exc_mod.CardConnectionException = type("CardConnectionException", (Exception,), {})
_exc_mod.NoCardException = type("NoCardException", (Exception,), {})
_exc_mod.ListReadersException = type("ListReadersException", (Exception,), {})

_card_mon = sys.modules["smartcard.CardMonitoring"]
_card_mon.CardMonitor = MagicMock()
_card_mon.CardObserver = object  # base class used by NFCCardObserver

_reader_mon = sys.modules["smartcard.ReaderMonitoring"]
_reader_mon.ReaderMonitor = MagicMock()
_reader_mon.ReaderObserver = object  # base class used by NFCReaderObserver

# Stub PyQt6 so reader.py (which imports QObject/QThread/pyqtSignal) can be
# imported in unit tests without a full Qt installation.
try:
    import PyQt6  # noqa: F401  - real Qt available; no stub needed
except ModuleNotFoundError:
    _pyqt6 = MagicMock()

    # QThread must be a real class so NFCReaderManager (which inherits from
    # QObject) and other classes can use it as a base.
    class _QThread:
        def __init__(self, *a, **kw):
            pass
        def start(self): pass
        def quit(self): pass
        def wait(self, *a): pass

    class _QObject:
        def __init__(self, *a, **kw):
            pass

    def _pyqtSignal(*args, **kwargs):
        return MagicMock()

    _pyqt6_core = MagicMock()
    _pyqt6_core.QObject = _QObject
    _pyqt6_core.QThread = _QThread
    _pyqt6_core.pyqtSignal = _pyqtSignal

    sys.modules["PyQt6"] = _pyqt6
    sys.modules["PyQt6.QtCore"] = _pyqt6_core
