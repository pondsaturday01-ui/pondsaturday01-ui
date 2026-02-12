import os
import glob
from datetime import datetime

# จำนวนไฟล์ log สูงสุดที่เก็บไว้ (เก่าสุดจะถูกลบ)
MAX_LOG_FILES = 30

class BotLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        self._cleanup_old_logs()

    def _get_log_filepath(self):
        """สร้าง path ไฟล์ log ของวันนี้"""
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"bot_{today}.log")

    def _write_to_file(self, line):
        """เขียน 1 บรรทัดลงไฟล์ log ของวันนี้"""
        try:
            with open(self._get_log_filepath(), "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception as e:
            print(f"[LOG FILE ERROR] เขียน log ไม่ได้: {e}")

    def _cleanup_old_logs(self):
        """ลบไฟล์ log เก่าที่เกิน MAX_LOG_FILES ไฟล์"""
        try:
            log_files = sorted(glob.glob(os.path.join(self.log_dir, "bot_*.log")))
            if len(log_files) > MAX_LOG_FILES:
                for old_file in log_files[:len(log_files) - MAX_LOG_FILES]:
                    os.remove(old_file)
        except Exception as e:
            print(f"[LOG CLEANUP] ลบ log เก่าไม่ได้: {e}")

    def log(self, message):
        """Prints message with timestamp + เขียนลงไฟล์"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"
        print(line)
        self._write_to_file(line)

    def log_error(self, message, driver=None):
        """
        Logs error message + เขียนลงไฟล์ + ถ่าย screenshot ถ้ามี driver
        Returns screenshot path if saved, else None.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[ERROR] [{timestamp}] {message}"
        print(line)
        self._write_to_file(line)

        screenshot_path = None

        if driver:
            try:
                filename = f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                screenshot_path = os.path.join(self.log_dir, filename)
                driver.save_screenshot(screenshot_path)
                ss_msg = f"[SCREENSHOT] {screenshot_path}"
                print(ss_msg)
                self._write_to_file(ss_msg)
            except Exception as e:
                err_msg = f"[SCREENSHOT FAILED] {e}"
                print(err_msg)
                self._write_to_file(err_msg)
                screenshot_path = None

        return screenshot_path
