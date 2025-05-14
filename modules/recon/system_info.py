import platform
import socket
import subprocess
import psutil
import json
from pathlib import Path

class SystemInfo:
    def __init__(self):
        self.info_file = Path('data/logs/system_info.txt')
        self.info_file.parent.mkdir(parents=True, exist_ok=True)

    def gather_info(self):
        info = {
            "system": {
                "os": platform.system(),
                "hostname": socket.gethostname(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "cpu": {
                "cores": psutil.cpu_count(logical=False),
                "threads": psutil.cpu_count(logical=True),
                "usage": psutil.cpu_percent(interval=1)
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "used": psutil.virtual_memory().used,
                "percent": psutil.virtual_memory().percent
            },
            "disk": [],
            "network": [],
            "users": [],
            "processes": []
        }

        # Disk information
        for part in psutil.disk_partitions(all=False):
            usage = psutil.disk_usage(part.mountpoint)
            info["disk"].append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent
            })

        # Network information
        for name, addrs in psutil.net_if_addrs().items():
            info["network"].append({
                "interface": name,
                "addresses": [str(addr.address) for addr in addrs]
            })

        # User information
        for user in psutil.users():
            info["users"].append({
                "name": user.name,
                "terminal": user.terminal,
                "host": user.host,
                "started": user.started
            })

        # Process information (top 10 by CPU)
        procs = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent']):
            procs.append(proc.info)
        info["processes"] = sorted(procs, key=lambda p: p['cpu_percent'], reverse=True)[:10]

        return info

    def start(self):
        """Gather and save system information"""
        info = self.gather_info()
        with self.info_file.open('w') as f:
            json.dump(info, f, indent=2)