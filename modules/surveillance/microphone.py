import sounddevice as sd
import numpy as np
import time
import threading
from pathlib import Path
from datetime import datetime
from scipy.io.wavfile import write

class MicrophoneRecorder:
    def __init__(self, duration=30):
        self.duration = duration
        self.running = False
        self.audio_dir = Path('data/audio/')
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.fs = 44100  # Sample rate

    def record(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.audio_dir / f"audio_{timestamp}.wav"
        try:
            recording = sd.rec(int(self.duration * self.fs), 
                             samplerate=self.fs, channels=2)
            sd.wait()  # Wait until recording is finished
            write(filename, self.fs, recording)
        except Exception as e:
            print(f"Audio recording failed: {e}")

    def start(self):
        """Start periodic audio recording"""
        self.running = True
        while self.running:
            self.record()
            time.sleep(self.duration * 2)  # Wait between recordings