import platform
import traceback
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.ReaderMonitoring import ReaderMonitor, ReaderObserver
from smartcard.Exceptions import CardConnectionException, NoCardException, ListReadersException
from PyQt6.QtCore import QObject, QThread, pyqtSignal


class _WatchdogThread(QThread):
    """Background thread that periodically checks whether pcscd is still running.

    Emits ``pcscd_status(bool)`` every *interval_ms* milliseconds so that the
    main manager can react when the service goes down or comes back up.
    """

    pcscd_status = pyqtSignal(bool)

    def __init__(self, interval_ms: int = 5000):
        super().__init__()
        self._interval_ms = interval_ms
        self._stop_flag = False

    def run(self):
        from diagnostics import SystemDiagnostics
        while not self._stop_flag:
            try:
                is_running, _ = SystemDiagnostics.check_pcscd_status()
                self.pcscd_status.emit(is_running)
            except Exception:
                pass
            # Sleep in small increments so stop_flag is checked quickly.
            elapsed = 0
            while elapsed < self._interval_ms and not self._stop_flag:
                self.msleep(200)
                elapsed += 200

    def stop(self):
        self._stop_flag = True


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
        self._pcscd_last_known = None  # None=unknown, True=running, False=down

        self._init_monitors()

        # Watchdog: detects pcscd going down / coming back and auto-recovers.
        self._watchdog = _WatchdogThread()
        self._watchdog.pcscd_status.connect(self._on_pcscd_status)
        self._watchdog.start()

    def _init_monitors(self):
        try:
            if not self.reader_monitor:
                self.reader_monitor = ReaderMonitor()
                self.reader_monitor.addObserver(self.reader_observer)

            if not self.card_monitor:
                self.card_monitor = CardMonitor()
                self.card_monitor.addObserver(self.card_observer)
        except Exception as e:
            # Reset any partially initialised monitor to None so the next call
            # to _init_monitors() (from the watchdog) can try again cleanly.
            if self.reader_monitor is not None:
                try:
                    self.reader_monitor.deleteObserver(self.reader_observer)
                except Exception:
                    pass
                self.reader_monitor = None
            if self.card_monitor is not None:
                try:
                    self.card_monitor.deleteObserver(self.card_observer)
                except Exception:
                    pass
                self.card_monitor = None
            hint = self._get_pcsc_error_hint(e)
            self.pcsc_error_occurred.emit(f"{hint} | Details: {repr(e)}")

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

    # ── Watchdog / recovery helpers ───────────────────────────────────────────

    def _on_pcscd_status(self, is_running: bool):
        """Slot called by the watchdog thread with the current pcscd health.

        Handles three transitions:
        * running → down  : clean up dead monitors, notify UI
        * down → running  : re-initialise monitors and rescan readers
        * running, no reader : try to rescan / re-init monitors
        """
        was_running = self._pcscd_last_known
        self._pcscd_last_known = is_running

        if is_running:
            if was_running is False:
                # pcscd just came back – rebuild the PC/SC stack.
                self._restart_monitors()
            elif not self.all_readers:
                # pcscd is running but we have no reader yet; try again.
                if self.card_monitor is None or self.reader_monitor is None:
                    self._init_monitors()
                self.update_readers_list()
        else:
            if was_running is True:
                # pcscd just went down – clean up stale monitors.
                self._cleanup_monitors()
                if self.reader is not None:
                    self.reader = None
                    self.connection = None
                    self.reader_disconnected.emit()

    def _cleanup_monitors(self):
        """Remove observers from monitors and reset references to None."""
        if self.card_monitor is not None:
            try:
                self.card_monitor.deleteObserver(self.card_observer)
            except Exception:
                pass
            self.card_monitor = None
        if self.reader_monitor is not None:
            try:
                self.reader_monitor.deleteObserver(self.reader_observer)
            except Exception:
                pass
            self.reader_monitor = None

    def _restart_monitors(self):
        """Tear down existing monitors and create fresh ones.

        Called automatically by the watchdog after pcscd restarts so that the
        app reconnects without requiring a manual rescan by the user.
        """
        self._cleanup_monitors()
        self._init_monitors()
        self.update_readers_list()

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
        # Stop the watchdog thread first to prevent it emitting signals while
        # we tear down monitors.
        if hasattr(self, '_watchdog') and self._watchdog is not None:
            self._watchdog.stop()
            # Allow up to 2 s for the thread to exit its current 200 ms sleep
            # increment and observe the stop flag.
            self._watchdog.wait(2000)
        self._cleanup_monitors()
