"""
Daily Scheduler - ระบบจัดตารางโพสต์รายวัน
สุ่มโควต้า 8-10 โพสต์/เพจ/วัน ภายในช่วง 09:30-21:30

Features:
- Variable min-gap based on quota (10=>55-75, 9=>65-85, 8=>75-95 min)
- Cross-page buffer: 5-12 min
- Smart backoff: 2 consecutive fails => 60-180 min rest
- Checkpoint/login detection => stop immediately
- Resume support with per-page quota and status tracking
"""

import json
import os
import random
import sys
from datetime import datetime, timedelta

# ===========================
# CONFIG
# ===========================
SCHEDULE_FILE = "daily_schedule.json"
MIN_QUOTA = 8
MAX_QUOTA = 10
START_HOUR = 9
START_MINUTE = 30
END_HOUR = 21
END_MINUTE = 30

# Min gap ตามโควต้า (minutes)
GAP_BY_QUOTA = {
    10: (55, 75),  # quota 10 => 55-75 นาที
    9: (65, 85),   # quota 9 => 65-85 นาที
    8: (75, 95),   # quota 8 => 75-95 นาที
}

# Cross-page buffer (minutes)
CROSS_PAGE_BUFFER_MIN = 5
CROSS_PAGE_BUFFER_MAX = 12

# Backoff settings
NORMAL_BACKOFF_MINUTES = 15
HEAVY_BACKOFF_MIN = 60
HEAVY_BACKOFF_MAX = 180
CONSECUTIVE_FAIL_THRESHOLD = 2

# Checkpoint/Login keywords to detect
CHECKPOINT_KEYWORDS = [
    "checkpoint", "login", "confirm your identity", "secure your account",
    "ยืนยันตัวตน", "เข้าสู่ระบบ", "บัญชีถูกจำกัด", "ถูกระงับ"
]


def safe_print(msg):
    """Print with encoding error handling for Windows Thai console"""
    try:
        print(msg)
    except UnicodeEncodeError:
        import re
        clean_msg = re.sub(r'[^\x00-\x7F\u0E00-\u0E7F]+', '', msg)
        print(clean_msg)


def get_today_str():
    """วันที่ปัจจุบันในรูปแบบ YYYY-MM-DD"""
    return datetime.now().strftime("%Y-%m-%d")


def load_schedule():
    """โหลดตารางจากไฟล์ JSON"""
    if os.path.exists(SCHEDULE_FILE):
        try:
            with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            safe_print(f"[WARNING] อ่าน {SCHEDULE_FILE} ไม่ได้: {e} — จะสร้างใหม่")
    return {}


def save_schedule(schedule):
    """บันทึกตารางลงไฟล์ JSON อย่างปลอดภัย (เขียน tmp ก่อนแล้ว rename)"""
    tmp_file = SCHEDULE_FILE + ".tmp"
    try:
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(schedule, f, ensure_ascii=False, indent=2)
        # atomic rename — ป้องกันไฟล์เสียถ้า crash ระหว่างเขียน
        if os.path.exists(SCHEDULE_FILE):
            os.replace(tmp_file, SCHEDULE_FILE)
        else:
            os.rename(tmp_file, SCHEDULE_FILE)
    except Exception as e:
        safe_print(f"[ERROR] บันทึก schedule ไม่สำเร็จ: {e}")


def validate_schedule(schedule):
    """ตรวจสอบความถูกต้องของ schedule ที่โหลดมา"""
    required_keys = ["date", "tasks"]
    for key in required_keys:
        if key not in schedule:
            return False
    if not isinstance(schedule.get("tasks"), list):
        return False
    return True


def get_min_gap_for_quota(quota):
    """คำนวณ min gap ตามโควต้า"""
    gap_range = GAP_BY_QUOTA.get(quota, GAP_BY_QUOTA[8])
    return random.randint(gap_range[0], gap_range[1])


def generate_daily_schedule(pages):
    """
    สร้างตารางโพสต์สำหรับวันนี้
    
    Args:
        pages: list ของ page dict (ต้องมี 'name', 'url', 'folder')
    
    Returns:
        dict: ตารางสำหรับวันนี้
    """
    today = get_today_str()
    
    # ช่วงเวลาที่โพสต์ได้
    now = datetime.now()
    start_time = now.replace(hour=START_HOUR, minute=START_MINUTE, second=0, microsecond=0)
    end_time = now.replace(hour=END_HOUR, minute=END_MINUTE, second=0, microsecond=0)
    
    # ถ้าสร้างหลัง start_time ให้เริ่มจากตอนนี้ + 5 นาที
    if now > start_time:
        start_time = now + timedelta(minutes=5)
    
    # สร้างโควต้าแต่ละเพจ
    all_tasks = []
    page_quotas = {}  # เก็บโควต้าแต่ละเพจ
    
    for page_idx, page in enumerate(pages):
        if "ใส่_URL" in page.get("url", ""):
            continue  # ข้ามเพจที่ยังไม่ได้ตั้งค่า
            
        quota = random.randint(MIN_QUOTA, MAX_QUOTA)
        page_name = page.get("name", f"Page_{page_idx}")
        min_gap = get_min_gap_for_quota(quota)
        
        # บันทึกโควต้า
        page_quotas[page_name] = {
            "quota": quota,
            "min_gap": min_gap,
            "completed": 0,
            "failed": 0,
            "status": "active"
        }
        
        # คำนวณช่วงเวลาสำหรับเพจนี้
        total_minutes = int((end_time - start_time).total_seconds() / 60)
        
        if total_minutes <= 0 or quota <= 0:
            continue
            
        # สุ่มเวลาภายในช่วง โดยรักษา min gap
        available_minutes = list(range(0, total_minutes, min_gap))
        random.shuffle(available_minutes)
        
        selected_minutes = sorted(available_minutes[:quota])
        
        for minute_offset in selected_minutes:
            task_time = start_time + timedelta(minutes=minute_offset)
            # เพิ่ม jitter ±5-10 นาที
            jitter = random.randint(-10, 10)
            task_time += timedelta(minutes=jitter)
            
            # ตรวจสอบให้อยู่ในช่วงที่กำหนด
            if task_time < start_time:
                task_time = start_time + timedelta(minutes=random.randint(1, 10))
            if task_time > end_time:
                task_time = end_time - timedelta(minutes=random.randint(1, 10))
            
            all_tasks.append({
                "time": task_time.strftime("%H:%M"),
                "page_index": page_idx,
                "page_name": page_name,
                "status": "pending",
                "quota_number": len([t for t in all_tasks if t["page_name"] == page_name]) + 1
            })
    
    # เรียงตามเวลา
    all_tasks.sort(key=lambda x: x["time"])
    
    # ใช้กฎ cross-page buffer: สุ่ม 5-12 นาที
    for i in range(1, len(all_tasks)):
        prev_time = datetime.strptime(all_tasks[i-1]["time"], "%H:%M")
        curr_time = datetime.strptime(all_tasks[i]["time"], "%H:%M")
        gap = (curr_time - prev_time).total_seconds() / 60
        
        buffer = random.randint(CROSS_PAGE_BUFFER_MIN, CROSS_PAGE_BUFFER_MAX)
        if gap < buffer:
            # ขยับงานปัจจุบันออกไป
            new_time = prev_time + timedelta(minutes=buffer)
            all_tasks[i]["time"] = new_time.strftime("%H:%M")
    
    schedule = {
        "date": today,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "page_quotas": page_quotas,
        "consecutive_fails": 0,
        "total_done": 0,
        "total_failed": 0,
        "stopped": False,
        "stop_reason": None,
        "tasks": all_tasks,
        "summary": {
            page_name: {"quota": info["quota"], "completed": 0, "status": "active"}
            for page_name, info in page_quotas.items()
        }
    }
    
    return schedule


def get_next_task(schedule):
    """
    หา task ถัดไปที่ต้องทำ
    
    Returns:
        tuple: (task_dict, task_index) หรือ (None, -1) ถ้าไม่มี
    """
    if schedule.get("stopped"):
        return None, -1
        
    now = datetime.now().strftime("%H:%M")
    
    for idx, task in enumerate(schedule.get("tasks", [])):
        if task["status"] == "pending" and task["time"] <= now:
            return task, idx
    
    return None, -1


def mark_task_done(schedule, task_index, success=True, reason=None):
    """อัปเดตสถานะ task และติดตาม consecutive fails"""
    if 0 <= task_index < len(schedule.get("tasks", [])):
        task = schedule["tasks"][task_index]
        task["status"] = "done" if success else "failed"
        task["completed_at"] = datetime.now().strftime("%H:%M:%S")
        if reason:
            task["reason"] = reason
        
        # อัปเดต summary
        page_name = task["page_name"]
        if page_name in schedule.get("summary", {}):
            if success:
                schedule["summary"][page_name]["completed"] += 1
                schedule["total_done"] = schedule.get("total_done", 0) + 1
                schedule["consecutive_fails"] = 0  # รีเซ็ต
            else:
                schedule["total_failed"] = schedule.get("total_failed", 0) + 1
                schedule["consecutive_fails"] = schedule.get("consecutive_fails", 0) + 1
        
        save_schedule(schedule)
        
        return schedule["consecutive_fails"]
    return 0


def check_checkpoint_error(error_message):
    """ตรวจสอบว่าเป็น checkpoint/login error หรือไม่"""
    if not error_message:
        return False
    error_lower = error_message.lower()
    return any(keyword.lower() in error_lower for keyword in CHECKPOINT_KEYWORDS)


def apply_backoff(schedule, task_index, consecutive_fails):
    """
    เลื่อนเวลา tasks ที่เหลือหลังจากล้มเหลว
    - ล้มเหลว 1 ครั้ง: backoff 15 นาที
    - ล้มเหลว 2 ครั้งติด: backoff 60-180 นาที
    """
    tasks = schedule.get("tasks", [])
    
    if consecutive_fails >= CONSECUTIVE_FAIL_THRESHOLD:
        backoff = random.randint(HEAVY_BACKOFF_MIN, HEAVY_BACKOFF_MAX)
        safe_print(f"[BACKOFF] HEAVY: {backoff} min (consecutive fails: {consecutive_fails})")
    else:
        backoff = NORMAL_BACKOFF_MINUTES
        safe_print(f"[BACKOFF] Normal: {backoff} min")
    
    for i in range(task_index + 1, len(tasks)):
        if tasks[i]["status"] == "pending":
            try:
                old_time = datetime.strptime(tasks[i]["time"], "%H:%M")
                new_time = old_time + timedelta(minutes=backoff)
                tasks[i]["time"] = new_time.strftime("%H:%M")
            except (ValueError, KeyError) as e:
                safe_print(f"[BACKOFF] เลื่อนเวลา task {i} ไม่ได้: {e}")
    
    save_schedule(schedule)
    return backoff


def stop_schedule(schedule, reason):
    """หยุดตารางทันที"""
    schedule["stopped"] = True
    schedule["stop_reason"] = reason
    schedule["stopped_at"] = datetime.now().strftime("%H:%M:%S")
    
    # Mark remaining tasks as skipped
    for task in schedule.get("tasks", []):
        if task["status"] == "pending":
            task["status"] = "skipped"
            task["reason"] = reason
    
    save_schedule(schedule)
    safe_print(f"[STOPPED] {reason}")


def get_schedule_for_today(pages, force_regenerate=False):
    """
    ดึงหรือสร้างตารางสำหรับวันนี้
    
    Args:
        pages: list ของ page mappings
        force_regenerate: บังคับสร้างใหม่
        
    Returns:
        dict: ตาราง schedule
    """
    schedule = load_schedule()
    today = get_today_str()

    # ตรวจสอบว่า schedule ที่โหลดมาถูกต้องไหม
    if schedule and not validate_schedule(schedule):
        safe_print(f"[WARNING] schedule file เสีย/ไม่ครบ — จะสร้างใหม่")
        schedule = {}

    # ถ้ายังไม่มีตารางวันนี้ หรือตารางเก่า -> สร้างใหม่
    if schedule.get("date") != today or force_regenerate:
        safe_print(f"[SCHEDULER] Creating new schedule for {today}")
        schedule = generate_daily_schedule(pages)
        save_schedule(schedule)
        
        # แสดงสรุป
        safe_print("[SCHEDULER] Quota Summary:")
        for page_name, info in schedule.get("page_quotas", {}).items():
            safe_print(f"   - {page_name}: quota={info['quota']}, gap={info['min_gap']}min")
    else:
        # Resume: แสดงสถานะ
        safe_print(f"[SCHEDULER] Resuming schedule for {today}")
        done = schedule.get("total_done", 0)
        remaining = get_remaining_tasks(schedule)
        safe_print(f"   Done: {done}, Remaining: {remaining}")
    
    return schedule


def get_remaining_tasks(schedule):
    """นับจำนวน tasks ที่ยังเหลือ"""
    return sum(1 for t in schedule.get("tasks", []) if t["status"] == "pending")


def get_next_task_time(schedule):
    """หาเวลาของ task ถัดไป"""
    for task in schedule.get("tasks", []):
        if task["status"] == "pending":
            return task["time"]
    return None


def print_schedule_table(schedule):
    """พิมพ์ตารางแบบอ่านง่าย (สำหรับ dry-run)"""
    safe_print("\n" + "="*60)
    safe_print(f"DAILY SCHEDULE: {schedule['date']}")
    safe_print("="*60)
    
    # Quota summary
    safe_print("\n[PAGE QUOTAS]")
    for page_name, info in schedule.get("page_quotas", {}).items():
        safe_print(f"  {page_name}: quota={info['quota']}, min_gap={info['min_gap']}min")
    
    # Task list
    safe_print(f"\n[TASKS] Total: {len(schedule['tasks'])}")
    safe_print("-"*60)
    safe_print(f"{'Time':<8} {'Page':<25} {'#':>3} {'Status':<10}")
    safe_print("-"*60)
    
    for task in schedule["tasks"]:
        safe_print(f"{task['time']:<8} {task['page_name']:<25} {task.get('quota_number', '?'):>3} {task['status']:<10}")
    
    safe_print("="*60 + "\n")


# ===========================
# TEST
# ===========================
if __name__ == "__main__":
    test_pages = [
        {"name": "Page A", "url": "https://fb.com/a", "folder": "FolderA"},
        {"name": "Page B", "url": "https://fb.com/b", "folder": "FolderB"},
        {"name": "Page C", "url": "https://fb.com/c", "folder": "FolderC"},
    ]
    
    # Force regenerate for testing
    schedule = get_schedule_for_today(test_pages, force_regenerate=True)
    print_schedule_table(schedule)
