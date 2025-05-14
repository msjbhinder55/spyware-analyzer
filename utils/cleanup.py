import os
import time
from pathlib import Path
import random
import string

class Cleanup:
    def __init__(self):
        self.data_dir = Path('data/')

    def secure_delete(self, path, passes=3):
        """Overwrite file before deletion"""
        try:
            with open(path, 'ba+') as f:
                length = f.tell()
                for _ in range(passes):
                    f.seek(0)
                    f.write(os.urandom(length))
            os.remove(path)
            return True
        except Exception:
            return False

    def cleanup_evidence(self):
        """Remove all collected data"""
        # Overwrite and delete files
        for root, _, files in os.walk(self.data_dir):
            for file in files:
                file_path = os.path.join(root, file)
                self.secure_delete(file_path)
        
        # Remove empty directories
        for root, dirs, _ in os.walk(self.data_dir, topdown=False):
            for dir in dirs:
                try:
                    os.rmdir(os.path.join(root, dir))
                except OSError:
                    pass

    def random_traces(self):
        """Create random files to obscure traces"""
        for _ in range(10):
            rand_name = ''.join(random.choices(string.ascii_lowercase, k=8))
            rand_ext = random.choice(['.log', '.txt', '.tmp', '.dat'])
            rand_path = self.data_dir / f"{rand_name}{rand_ext}"
            
            with rand_path.open('w') as f:
                f.write(''.join(random.choices(
                    string.ascii_letters + string.digits + ' \n',
                    k=random.randint(100, 1000)
                )))

    def execute(self):
        """Run full cleanup procedure"""
        self.cleanup_evidence()
        self.random_traces()