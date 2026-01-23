import yaml
import requests
import time
from datetime import datetime
import os
import sys
import random
import argparse
import re
from dotenv import load_dotenv

# โหลดค่าจาก .env file
load_dotenv()

try:
    from uploader import FacebookReelsBot
    from report import save_report
    from daily_scheduler import (
        get_schedule_for_today, get_next_task, mark_task_done,
        apply_backoff, get_remaining_tasks, get_next_task_time,
        check_checkpoint_error, stop_schedule, print_schedule_table,
        CONSECUTIVE_FAIL_THRESHOLD
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit()

# ==========================================
# 📝 โซนแก้ไขแคปชั่น & แฮชแท็ก (Safe Mode Edition 🛡️)
# ==========================================
MY_CAPTION_TEMPLATE = """
{กราบสวัสดี|ทักทาย|สวัสดี}ครับ {กัลยาณมิตร|สายมู|พี่น้อง} 🙏
.
วันนี้มี {แนวทางรัฐบาล|ตัวเลขมงคล|พิกัดขอพร|เลขธูป} มาแบ่งปัน {งวดนี้|ประจำวัน}
เป็น {ความเชื่อส่วนบุคคล|แนวทางเสี่ยงโชค|เรื่องราวดีๆ} โปรดใช้วิจารณญาณ 🔮
.
{ใครผ่านมาเห็น|ท่านที่พบโพสต์นี้} ขอบารมี {สิ่งศักดิ์สิทธิ์|ปู่พญานาค|ท้าวเวสสุวรรณ}
ดลบันดาลให้ท่าน {มีโชคลาภ|รับทรัพย์ก้อนโต|สุขสมหวัง|การงานราบรื่น} 💸✨
.
{คอมเมนต์|พิมพ์} คำว่า "{สาธุ|รับโชค|999}" เพื่อ {เป็นสิริมงคล|เปิดทางรวย|เสริมกำลังใจ} 👇
.
#แนวทางรัฐบาลไทย #สลากกินแบ่งรัฐบาล #{ตัวเลข|เลขมงคล|เลขนำโชค}
#{ดูดวง|เช็คดวง|ดวงรายวัน|ราศี}
#{สายมู|มูเตลู|ขอพร|ไหว้พระ|ทำบุญ|เสริมบารมี}
#{Reels|Shorts|ReelsTH|เปิดการมองเห็น}
#อาจารย์ภูมิ #{ปาฏิหาริย์|พญานาค|ท้าวเวสสุวรรณ}
"""
# ==========================================

# 🌀 ฟังก์ชัน Spintax (สุ่มคำ)
def spintax(text):
    if not text: return ""
    pattern = r'\{([^{}]+)\}'
    while True:
        match = re.search(pattern, text)
        if not match:
            break
        choices = match.group(1).split('|')
        replacement = random.choice(choices)
        text = text[:match.start()] + replacement + text[match.end():]
    return text

# ===========================
# ⚙️ PAGE & FOLDER CONFIG
# ===========================
PAGE_MAPPINGS = [
    # [0] เพจที่ 1
    {
        "name": "ปาฏิหาริย์ตัวเลข",
        "url": "https://www.facebook.com/profile.php?id=61584846901511", 
        "folder": "MyReels",
        "mode": "sequence"
    },
    # [1] เพจที่ 2
    {
        "name": "Add.ภูมิV.4",
        "url": "https://www.facebook.com/profile.php?id=61585373284011", 
        "folder": "MyReels2",
        "mode": "random"
    },
    # [2] เพจที่ 3
    {
        "name": "ขุมทรัพย์ตัวเลข",
        "url": "https://www.facebook.com/profile.php?id=61585926308020", 
        "folder": "MyReels3",
        "mode": "random"
    },
    # [3-9] ใส่เพิ่มได้ตามปกติ...
    {"name": "ชื่อเพจที่_4", "url": "ใส่_URL_เพจ_4", "folder": "MyReels4", "mode": "random"},
    {"name": "ชื่อเพจที่_5", "url": "ใส่_URL_เพจ_5", "folder": "MyReels5", "mode": "random"},
    {"name": "ชื่อเพจที่_6", "url": "ใส่_URL_เพจ_6", "folder": "MyReels6", "mode": "random"},
    {"name": "ชื่อเพจที่_7", "url": "ใส่_URL_เพจ_7", "folder": "MyReels7", "mode": "random"},
    {"name": "ชื่อเพจที่_8", "url": "ใส่_URL_เพจ_8", "folder": "MyReels8", "mode": "random"},
    {"name": "ชื่อเพจที่_9", "url": "ใส่_URL_เพจ_9", "folder": "MyReels9", "mode": "random"},
    {"name": "ชื่อเพจที่_10", "url": "ใส่_URL_เพจ_10", "folder": "MyReels10", "mode": "random"},
]

# ===========================
# 📱 TELEGRAM CONFIG (from .env)
# ===========================
def send_telegram_msg(message):
    """ส่งข้อความไปยัง Telegram - ข้ามถ้าไม่มี config"""
    token = os.getenv("TELEGRAM_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    
    if not token or not chat_id:
        return  # ข้ามถ้าไม่มี config
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {"chat_id": chat_id, "text": message}
        requests.post(url, data=data, timeout=10)
    except:
        pass  # ล้มเหลวก็ข้ามไป

def load_config():
    try:
        if os.path.exists("config.yaml"):
            with open("config.yaml", "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
    except: pass
    return {}

def get_video(folder_path, mode="random"):
    if not os.path.exists(folder_path): return None
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
    if not files: return None
    
    if mode == "sequence":
        files.sort()
        selected = files[0]
        print(f"🎬 [Mode: Sequence] ถึงคิวของ: {selected}")
        return os.path.join(folder_path, selected)
    else:
        selected = random.choice(files)
        print(f"🎲 [Mode: Random] สุ่มได้คลิป: {selected}")
        return os.path.join(folder_path, selected)

def execute_job(bot, category="Lottery", selected_indices=None):
    if selected_indices is None:
        work_list = PAGE_MAPPINGS
    else:
        work_list = []
        for i in selected_indices:
            if 0 <= i < len(PAGE_MAPPINGS):
                work_list.append(PAGE_MAPPINGS[i])
        
        if not work_list: 
            print("⚠️ ไม่พบเพจที่เลือก... รันทั้งหมดแทนครับ")
            work_list = PAGE_MAPPINGS

    print(f"🎬 เริ่มภารกิจวนลูป... (จำนวน {len(work_list)} เพจ)")
    
    for page_data in work_list:
        target_url = page_data["url"]
        current_folder = page_data["folder"]
        page_name = page_data.get("name", "Unknown Page")
        mode = page_data.get("mode", "random")
        
        print(f"\n🚀 กำลังเริ่มงานเพจ: {page_name}")
        
        if "ใส่_URL" in target_url:
            continue

        print(f"📂 ดึงคลิปจาก: {current_folder}")
        
        try:
            bot.handle_page_switch(target_url)
        except Exception as e:
            print(f"⚠️ สลับเพจมีปัญหา: {e}")
            continue
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        full_folder_path = os.path.join(base_path, current_folder)
        video_path = get_video(full_folder_path, mode)
        
        if not video_path:
             print(f"⚠️ โฟลเดอร์ {current_folder} คลิปหมด! ข้าม...")
             continue

        print(f"🎥 ไฟล์: {os.path.basename(video_path)}")
        
        # ✅ ใช้แคปชั่นจากด้านบนสุดที่เราตั้งค่าไว้
        used_caption = spintax(MY_CAPTION_TEMPLATE)
        print(f"📝 แคปชั่นที่ใช้: {used_caption}")

        success, reason, _ = bot.run_post_task(video_path, used_caption)
        
        video_name = os.path.basename(video_path)
        status_text = "Success" if success else f"Failed: {reason}"
        save_report(f"{video_name} @ {page_name}", status_text, used_caption)

        if success:
             print("✅ โพสต์สำเร็จ! ย้ายเข้ากรุ...")
             bot.move_to_posted(video_path, full_folder_path)
             send_telegram_msg(f"✅ โพสต์สำเร็จ!\nเพจ: {page_name}\nไฟล์: {video_name}")
        else:
             print("❌ โพสต์ไม่ผ่าน")
        
        sleep_time = random.randint(60, 180)
        print(f"💤 พัก {sleep_time} วินาที...")
        time.sleep(sleep_time)
    
    print("🏁 จบรอบการทำงานแล้ว!")

def execute_single_page(bot, page_index, page_data):
    """โพสต์ 1 ครั้งสำหรับเพจที่ระบุ"""
    page_name = page_data.get("name", "Unknown")
    page_url = page_data["url"]
    folder = page_data["folder"]
    mode = page_data.get("mode", "random")
    
    print(f"\n[START] Page: {page_name}")
    
    try:
        bot.handle_page_switch(page_url)
    except Exception as e:
        print(f"[ERROR] Page switch failed: {e}")
        return False, str(e)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_folder_path = os.path.join(base_path, folder)
    video_path = get_video(full_folder_path, mode)
    
    if not video_path:
        print(f"[SKIP] Folder {folder} has no videos!")
        return False, "No video"
    
    video_name = os.path.basename(video_path)
    post_time = datetime.now().strftime("%H:%M:%S")
    print(f"[VIDEO] {video_name}")
    
    used_caption = spintax(MY_CAPTION_TEMPLATE)
    success, reason, _ = bot.run_post_task(video_path, used_caption)
    
    status_text = "Success" if success else f"Failed: {reason}"
    save_report(f"{video_name} @ {page_name}", status_text, used_caption)
    
    if success:
        # Enhanced logging: page, video, time, move status
        print(f"[SUCCESS] page={page_name} | video={video_name} | time={post_time}")
        
        # Move file and log status
        try:
            bot.move_to_posted(video_path, full_folder_path)
            print(f"[MOVE] OK -> posted/")
        except Exception as e:
            print(f"[MOVE] FAILED: {e}")
        
        print(f"[REPORT] Saved to daily_report.csv")
        send_telegram_msg(f"[OK] {page_name}\n{video_name}\n{post_time}")
    else:
        print(f"[FAILED] reason={reason}")
    
    return success, reason


def run_quota_mode(bot, dry_run=False, max_tasks=None):
    """โหมด Variable Daily Quota - สุ่ม 8-10 โพสต์/เพจ/วัน"""
    print("\n" + "="*50)
    print("VARIABLE DAILY QUOTA MODE")
    print("   Quota: 8-10 posts/page/day")
    print("   Time window: 09:30 - 21:30")
    print("   Min-gap: 55-95 min (based on quota)")
    if max_tasks:
        print(f"   [TEST] Max tasks: {max_tasks}")
    print("="*50 + "\n")
    
    # โหลด/สร้างตารางวันนี้
    schedule = get_schedule_for_today(PAGE_MAPPINGS)
    
    # Dry-run mode: แสดงตารางแล้วออก
    if dry_run:
        print("\n[DRY-RUN MODE] - No posting, just showing schedule")
        print_schedule_table(schedule)
        return
    
    remaining = get_remaining_tasks(schedule)
    print(f"Remaining Tasks: {remaining}")
    
    if schedule.get("stopped"):
        print(f"\n[STOPPED] Schedule was stopped: {schedule.get('stop_reason')}")
        print("Delete daily_schedule.json to reset.")
        return
    
    tasks_completed = 0  # Counter for max_tasks limit
    
    while True:
        # Check max_tasks limit
        if max_tasks and tasks_completed >= max_tasks:
            print(f"\n[TEST] Reached max_tasks limit ({max_tasks}). Stopping.")
            break
        
        # หา task ถัดไป
        task, task_idx = get_next_task(schedule)
        
        if task:
            page_idx = task["page_index"]
            page_data = PAGE_MAPPINGS[page_idx]
            
            print(f"\n[{task['time']}] Task: {task['page_name']} (#{task.get('quota_number', '?')})")
            
            success, reason = execute_single_page(bot, page_idx, page_data)
            consecutive_fails = mark_task_done(schedule, task_idx, success, reason)
            
            # ตรวจสอบ checkpoint/login error
            if not success and check_checkpoint_error(reason):
                print("\n[CRITICAL] Checkpoint/Login detected!")
                stop_schedule(schedule, f"Checkpoint/Login: {reason}")
                send_telegram_msg(f"[CRITICAL] Bot stopped!\nReason: {reason}")
                break
            
            if not success:
                backoff = apply_backoff(schedule, task_idx, consecutive_fails)
                
                # ถ้า fail มากเกินไป
                if consecutive_fails >= CONSECUTIVE_FAIL_THRESHOLD:
                    print(f"\n[WARNING] {consecutive_fails} consecutive fails!")
                    send_telegram_msg(f"[WARNING] {consecutive_fails} fails! Backoff: {backoff}min")
            
            # พักหลังโพสต์
            tasks_completed += 1
            sleep_time = random.randint(60, 180)
            remaining = get_remaining_tasks(schedule)
            print(f"Rest: {sleep_time}s... (completed: {tasks_completed}, remaining: {remaining})")
            time.sleep(sleep_time)
        else:
            # ไม่มี task ที่ต้องทำตอนนี้
            remaining = get_remaining_tasks(schedule)
            
            if remaining == 0:
                print("\n[DONE] All tasks completed for today!")
                send_telegram_msg(f"[DONE] Daily quota completed! Done: {schedule.get('total_done', 0)}")
                break
            
            next_time = get_next_task_time(schedule)
            if next_time:
                print(f"\rWaiting for {next_time} (remaining: {remaining} tasks) ...", end="")
            time.sleep(30)


def main():
    print("[BOT] Loading config...")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--now", action="store_true", help="Run immediately")
    parser.add_argument("--quota", action="store_true", help="Variable daily quota mode (8-10/page/day)")
    parser.add_argument("--dry-run", action="store_true", help="Generate schedule without posting (use with --quota)")
    parser.add_argument("--max-tasks", type=int, default=None, help="Limit max tasks for testing (e.g., --max-tasks 1)")
    parser.add_argument("--pages", type=str, default="all", help="Selected pages e.g. 0,2")
    parser.add_argument("--times", type=str, default=None, help="Custom schedule times e.g. 08:00,12:00")
    args = parser.parse_args()

    config = load_config()
    if not config: config = {}
    if "profile_path" not in config: config["profile_path"] = os.getcwd()

    # โหมด Dry-Run: ไม่เปิด browser
    if getattr(args, 'dry_run', False) and args.quota:
        print("\n[DRY-RUN] Generating schedule only (no browser)...")
        from daily_scheduler import get_schedule_for_today, print_schedule_table
        schedule = get_schedule_for_today(PAGE_MAPPINGS, force_regenerate=True)
        print_schedule_table(schedule)
        print("Schedule saved to: daily_schedule.json")
        return

    bot = FacebookReelsBot(config)
    bot.setup_driver()

    print("Waiting for Facebook login (60s)...")

    selected_indices = None
    if args.pages and args.pages != "all":
        try:
            selected_indices = [int(x) for x in args.pages.split(",")]
        except: pass

    # โหมด 1: Run Now
    if args.now:
        execute_job(bot, category="Lottery", selected_indices=selected_indices)
        bot.driver.quit()
        return
    
    # โหมด 2: Variable Daily Quota
    if args.quota:
        try:
            run_quota_mode(bot, max_tasks=getattr(args, 'max_tasks', None))
        except KeyboardInterrupt:
            print("\n[STOPPED] User cancelled")
        finally:
            bot.driver.quit()
        return

    # โหมด 3: Scheduler ตามเวลา
    print("⏰ เข้าสู่โหมดตั้งเวลา (Scheduler)...")
    
    if args.times:
        schedule_times = [t.strip() for t in args.times.split(",") if t.strip()]
    else:
        schedule_times = config.get('schedule_times', ["08:00", "12:00", "18:00"])
    
    while True:
        current_time = datetime.now().strftime("%H:%M")
        if current_time in schedule_times:
            print(f"\n🔔 ถึงเวลา {current_time} แล้ว!")
            execute_job(bot, category="Lottery", selected_indices=selected_indices)
            time.sleep(61)
        else:
            print(f"\r⏳ รอเวลา {current_time} ... (เป้าหมาย: {schedule_times})", end="")
            time.sleep(10)


if __name__ == "__main__":
    main()