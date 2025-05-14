import pyautogui
import time
import threading
from pathlib import Path
from datetime import datetime

class ScreenshotCapture:
    def __init__(self, interval=300):
        self.interval = interval
        self.running = False
        self.screenshot_dir = Path('data/screenshots/')
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def capture(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.screenshot_dir / f"screenshot_{timestamp}.png"
        try:
            pyautogui.screenshot(str(filename))
        except Exception as e:
            print(f"Screenshot failed: {e}")

    def start(self):
        """Start periodic screenshot capture"""
        self.running = True
        while self.running:
            self.capture()
            time.sleep(self.interval)