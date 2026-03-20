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
