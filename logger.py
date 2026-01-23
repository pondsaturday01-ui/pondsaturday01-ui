import os
import time
from datetime import datetime

class BotLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def log(self, message):
        """Prints message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def log_error(self, message, driver=None):
        """
        Logs error message and takes a screenshot if driver is provided.
        Returns screenshot path if saved, else None.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[ERROR] [{timestamp}] {message}")
        
        screenshot_path = None

        if driver:
            try:
                filename = f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                screenshot_path = os.path.join(self.log_dir, filename)
                driver.save_screenshot(screenshot_path)
                print(f"[SCREENSHOT] {screenshot_path}")
            except Exception as e:
                print(f"[SCREENSHOT FAILED] {e}")
                screenshot_path = None
        
        return screenshot_path

