from pynput.keyboard import Controller, Key
import time

class KeyboardEmulator:
    def __init__(self):
        self.keyboard = Controller()
        self.enabled = False
        self.suffix = "none" # "none", "enter", "tab"

    def set_enabled(self, enabled):
        self.enabled = enabled

    def set_suffix(self, suffix):
        self.suffix = suffix

    def type_string(self, text):
        if not self.enabled:
            return

        # Give a small delay to ensure focus is correct
        time.sleep(0.1)
        self.keyboard.type(text)

        if self.suffix == "enter":
            self.keyboard.press(Key.enter)
            self.keyboard.release(Key.enter)
        elif self.suffix == "tab":
            self.keyboard.press(Key.tab)
            self.keyboard.release(Key.tab)
