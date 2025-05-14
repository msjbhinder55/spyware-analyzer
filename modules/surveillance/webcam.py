import cv2
import time
import threading
from pathlib import Path
from datetime import datetime

class WebcamCapture:
    def __init__(self, interval=600):
        self.interval = interval
        self.running = False
        self.webcam_dir = Path('data/webcam/')
        self.webcam_dir.mkdir(parents=True, exist_ok=True)

    def capture(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.webcam_dir / f"webcam_{timestamp}.jpg"
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(str(filename), frame)
            cap.release()
        except Exception as e:
            print(f"Webcam capture failed: {e}")

    def start(self):
        """Start periodic webcam capture"""
        self.running = True
        while self.running:
            self.capture()
            time.sleep(self.interval)