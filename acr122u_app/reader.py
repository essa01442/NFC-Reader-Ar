import platform
import traceback
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.ReaderMonitoring import ReaderMonitor, ReaderObserver
from smartcard.Exceptions import CardConnectionException, NoCardException, ListReadersException
from PyQt6.QtCore import QObject, pyqtSignal

class NFCCardObserver(CardObserver):
    def __init__(self, manager):
        self.manager = manager

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            self.manager.card_inserted(card)
        for card in removedcards:
            self.manager.card_removed(card)

class NFCReaderObserver(ReaderObserver):
    def __init__(self, manager):
        self.manager = manager

    def update(self, observable, actions):
        (addedreaders, removedreaders) = actions
        if addedreaders or removedreaders:
            self.manager.update_readers_list()

class NFCReaderManager(QObject):
    # Signals for UI updates
    reader_connected = pyqtSignal(str)
    reader_disconnected = pyqtSignal()
    card_detected = pyqtSignal(str) # UID
    card_removed_signal = pyqtSignal()
    error_occurred = pyqtSignal(str)
    available_readers_changed = pyqtSignal(list)
    pcsc_error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.reader = None
        self.all_readers = []
        self.connection = None

        # Monitors
        self.card_monitor = None
        self.card_observer = NFCCardObserver(self)
        self.reader_monitor = None
        self.reader_observer = NFCReaderObserver(self)

        self.is_running = True

        self._init_monitors()

    def _init_monitors(self):
        try:
            if not self.reader_monitor:
                self.reader_monitor = ReaderMonitor()
                self.reader_monitor.addObserver(self.reader_observer)

            if not self.card_monitor:
                self.card_monitor = CardMonitor()
                self.card_monitor.addObserver(self.card_observer)
        except Exception as e:
            err_repr = repr(e)
            hint = self._get_pcsc_error_hint(e)
            self.pcsc_error_occurred.emit(f"{hint} | Details: {err_repr}")

    def update_readers_list(self):
        try:
            current_readers = readers()

            # Allow all readers without strict name filtering so any connected reader works
            self.all_readers = current_readers

            reader_names = [str(r) for r in self.all_readers]
            self.available_readers_changed.emit(reader_names)

            if self.all_readers:
                if self.reader not in self.all_readers:
                    # Select the first available reader if none is selected
                    self.reader = self.all_readers[0]
                    self.reader_connected.emit(str(self.reader))
            else:
                if self.reader is not None:
                    self.reader = None
                    self.connection = None
                    self.reader_disconnected.emit()

        except Exception as e:
            err_repr = repr(e)
            hint = self._get_pcsc_error_hint(e)
            self.pcsc_error_occurred.emit(f"{hint} | Details: {err_repr}")

    def rescan_readers(self):
        """Manually trigger a scan immediately."""
        self.update_readers_list()
        # Optionally re-init monitors if they failed previously
        if not self.reader_monitor or not self.card_monitor:
            self._init_monitors()

    def select_reader(self, reader_name):
        """Set the active reader from UI combo box."""
        if not reader_name:
            return

        selected = next((r for r in self.all_readers if str(r) == reader_name), None)
        if selected and selected != self.reader:
            self.reader = selected
            self.connection = None
            self.reader_connected.emit(str(self.reader))

    def _get_pcsc_error_hint(self, exc):
        from diagnostics import SystemDiagnostics
        is_running, pcscd_msg = SystemDiagnostics.check_pcscd_status()
        perms_ok, groups, perms_msg = SystemDiagnostics.check_user_permissions()

        if not is_running:
            return pcscd_msg
        if not perms_ok:
            return f"{perms_msg} — انتقل إلى تبويب 'الحماية والصلاحيات' لأوامر الإصلاح."
        return f"تأكد من توصيل القارئ أو صلاحيات الوصول. ({pcscd_msg})"

    def card_inserted(self, card):
        try:
            self.connection = card.createConnection()
            self.connection.connect()

            # Get UID (APDU for getting UID on ACR122U)
            # FF CA 00 00 00
            GET_UID_APDU = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, sw1, sw2 = self.connection.transmit(GET_UID_APDU)

            if sw1 == 0x90 and sw2 == 0x00:
                uid = toHexString(data).replace(" ", "")
                self.card_detected.emit(uid)
            else:
                self.error_occurred.emit(f"Failed to read UID: {sw1:02X} {sw2:02X}")

        except CardConnectionException as e:
            self.error_occurred.emit(f"Card connection error: {str(e)}")
        except Exception as e:
            self.error_occurred.emit(f"Unknown card error: {str(e)}")

    def card_removed(self, card):
        self.connection = None
        self.card_removed_signal.emit()

    def read_block(self, block_num):
        if not self.connection:
            raise Exception("No card connected")

        try:
            # Read Binary Block APDU for MIFARE/NTAG
            # FF B0 00 <block_num> 10
            READ_APDU = [0xFF, 0xB0, 0x00, int(block_num), 0x10]
            data, sw1, sw2 = self.connection.transmit(READ_APDU)

            if sw1 == 0x90 and sw2 == 0x00:
                return data
            else:
                raise Exception(f"Read error: SW1={sw1:02X}, SW2={sw2:02X}")
        except Exception as e:
            raise e

    def write_block(self, block_num, data_bytes):
        if not self.connection:
            raise Exception("No card connected")

        if len(data_bytes) != 16 and len(data_bytes) != 4:
            # NTAG pages are 4 bytes, MIFARE Classic blocks are 16 bytes.
            # Depending on card type, we pad or truncate, or just require exactly 4/16
            raise Exception("Data must be exactly 4 or 16 bytes depending on card type")

        try:
            # Update Binary Block APDU
            # FF D6 00 <block_num> <len> <data>
            WRITE_APDU = [0xFF, 0xD6, 0x00, int(block_num), len(data_bytes)] + list(data_bytes)
            data, sw1, sw2 = self.connection.transmit(WRITE_APDU)

            if sw1 == 0x90 and sw2 == 0x00:
                return True
            else:
                raise Exception(f"Write error: SW1={sw1:02X}, SW2={sw2:02X}")
        except Exception as e:
            raise e

    def cleanup(self):
        self.is_running = False
        if self.card_monitor and self.card_observer:
            try:
                self.card_monitor.deleteObserver(self.card_observer)
            except Exception:
                pass
        if self.reader_monitor and self.reader_observer:
            try:
                self.reader_monitor.deleteObserver(self.reader_observer)
            except Exception:
                pass
