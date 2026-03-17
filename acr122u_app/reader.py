import threading
import time
import platform
import traceback
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.Exceptions import CardConnectionException, NoCardException, ListReadersException
from PyQt6.QtCore import QObject, pyqtSignal

class NFCObserver(CardObserver):
    def __init__(self, manager):
        self.manager = manager

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            self.manager.card_inserted(card)
        for card in removedcards:
            self.manager.card_removed(card)

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
        self.monitor = CardMonitor()
        self.observer = NFCObserver(self)
        self.monitor.addObserver(self.observer)
        self.is_running = True
        self.force_scan_event = threading.Event()

        # Start a thread to keep looking for readers if not found
        self.search_thread = threading.Thread(target=self._search_for_reader, daemon=True)
        self.search_thread.start()

    def rescan_readers(self):
        """Manually trigger a scan immediately."""
        self.force_scan_event.set()

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
        is_running, msg = SystemDiagnostics.check_pcscd_status()
        if not is_running:
            return msg
        return f"تأكد من توصيل القارئ أو صلاحيات الوصول. ({msg})"

    def _search_for_reader(self):
        backoff = 1.0
        max_backoff = 5.0

        while self.is_running:
            try:
                available_readers = readers()
                # reset backoff on success
                backoff = 1.0

                # Match "acr" or "122" case-insensitive
                target_readers = [r for r in available_readers if "acr" in str(r).lower() or "122" in str(r).lower()]

                current_reader_names = [str(r) for r in target_readers]
                old_reader_names = [str(r) for r in self.all_readers]

                if current_reader_names != old_reader_names:
                    self.all_readers = target_readers
                    self.available_readers_changed.emit(current_reader_names)

                if target_readers:
                    # Auto-select the first one if we don't have an active reader, or if our active reader is lost
                    if self.reader not in target_readers:
                        self.reader = target_readers[0]
                        self.reader_connected.emit(str(self.reader))
                else:
                    if self.reader is not None:
                        self.reader = None
                        self.connection = None
                        self.reader_disconnected.emit()

            except Exception as e:
                err_repr = repr(e)
                hint = self._get_pcsc_error_hint(e)
                # Emit a specific PCSC error signal
                self.pcsc_error_occurred.emit(f"{hint} | Details: {err_repr}")
                # Backoff
                backoff = min(backoff * 1.5, max_backoff)

            # Wait either for backoff duration or until forced scan is requested
            self.force_scan_event.wait(timeout=backoff)
            self.force_scan_event.clear()

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
        self.monitor.deleteObserver(self.observer)
