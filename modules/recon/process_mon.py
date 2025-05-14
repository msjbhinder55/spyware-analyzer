import psutil
import time
import json
from pathlib import Path

class ProcessMonitor:
    def __init__(self, interval=300):
        self.interval = interval
        self.output_file = Path('data/logs/processes.json')
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def monitor_processes(self):
        """Monitor running processes and their resource usage"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "user": proc.info['username'],
                    "cpu": proc.info['cpu_percent'],
                    "memory": proc.info['memory_percent'],
                    "cmdline": proc.cmdline()
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage
        processes.sort(key=lambda p: p['cpu'], reverse=True)
        
        with self.output_file.open('w') as f:
            json.dump(processes, f, indent=2)
        
        return processes

    def start(self):
        """Start periodic process monitoring"""
        while True:
            self.monitor_processes()
            time.sleep(self.interval)