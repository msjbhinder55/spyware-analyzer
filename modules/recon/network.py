import subprocess
import re
import json
from pathlib import Path
import time

class NetworkScanner:
    def __init__(self, interval=600):
        self.interval = interval  # Scan interval in seconds
        self.output_file = Path("data/logs/network_info.json")
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.running = False

    def scan_network(self):
        """Gather network information and connected devices"""
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "interfaces": self._get_network_interfaces(),
            "connections": self._get_active_connections(),
            "arp_table": self._get_arp_table(),
            "wifi_info": self._get_wifi_info(),
        }

        with self.output_file.open("w") as f:
            json.dump(results, f, indent=2)

        return results

    def _get_network_interfaces(self):
        """Get list of network interfaces and their configurations"""
        try:
            output = subprocess.check_output(["ip", "a"], stderr=subprocess.STDOUT).decode()
            interfaces = []
            current_iface = None
            
            for line in output.split("\n"):
                if not line.strip():
                    continue
                
                # New interface
                if line[0].isdigit():
                    if current_iface:
                        interfaces.append(current_iface)
                    parts = line.split(": ")
                    current_iface = {
                        "name": parts[1].strip(),
                        "state": "UP" if "UP" in line else "DOWN",
                        "ip": [],
                        "mac": None
                    }
                else:
                    # MAC address
                    if "link/ether" in line:
                        current_iface["mac"] = line.strip().split()[1]
                    # IP address
                    elif "inet " in line:
                        ip_info = line.strip().split()
                        current_iface["ip"].append({
                            "address": ip_info[1].split("/")[0],
                            "netmask": ip_info[1].split("/")[1] if "/" in ip_info[1] else None
                        })

            if current_iface:
                interfaces.append(current_iface)

            return interfaces
        except Exception as e:
            return {"error": str(e)}

    def _get_arp_table(self):
        """Get the system ARP table"""
        try:
            output = subprocess.check_output(["ip", "neigh"], stderr=subprocess.STDOUT).decode()
            arp_entries = []

            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 5:
                    arp_entries.append({
                        "ip": parts[0],
                        "mac": parts[4] if len(parts) >= 5 else None,
                        "device": parts[2],
                        "state": parts[3]
                    })

            return arp_entries
        except Exception as e:
            return {"error": str(e)}

    def _get_active_connections(self):
        """Get active network connections"""
        try:
            output = subprocess.check_output(["ss", "-tulnp"], stderr=subprocess.STDOUT).decode()
            connections = []
            
            # Parse ss output
            lines = output.split("\n")[1:]  # Skip header
            for line in lines:
                if not line.strip():
                    continue
                parts = re.split(r"\s+", line.strip())
                if len(parts) >= 6:
                    connections.append({
                        "state": parts[0],
                        "local": parts[4],
                        "peer": parts[5],
                        "process": parts[6] if len(parts) > 6 else None
                    })

            return connections
        except Exception as e:
            return {"error": str(e)}

    def _get_wifi_info(self):
        """Get WiFi network information"""
        try:
            output = subprocess.check_output(["iwconfig"], stderr=subprocess.STDOUT).decode()
            wifi_info = {}
            
            for line in output.split("\n"):
                if "ESSID" in line:
                    wifi_info["essid"] = line.split('"')[1] if '"' in line else None
                elif "Frequency" in line:
                    wifi_info["frequency"] = line.split(":")[1].split()[0] if ":" in line else None
                elif "Bit Rate" in line:
                    wifi_info["bitrate"] = line.split("=")[1].split()[0] if "=" in line else None
                elif "Access Point" in line:
                    wifi_info["ap"] = line.split()[-1] if len(line.split()) > 0 else None

            return wifi_info if wifi_info else {"error": "No WiFi information found"}
        except Exception as e:
            return {"error": str(e)}

    def start(self):
        """Start periodic network scanning"""
        self.running = True
        while self.running:
            try:
                self.scan_network()
                time.sleep(self.interval)
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                print(f"Network scan error: {e}")
                time.sleep(10)  # Wait before retrying