import zipfile
import os
from pathlib import Path
from datetime import datetime

def compress_data():
    """Compress collected data into a zip file"""
    data_dir = Path('data/')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = data_dir.parent / f"collected_data_{timestamp}.zip"
    
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, data_dir.parent)
                zipf.write(file_path, arcname)
                
    return archive_path