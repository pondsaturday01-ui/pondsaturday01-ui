import os
import sys

# ตั้งค่าสีให้ดูง่ายๆ
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check_file(filename):
    if os.path.exists(filename):
        print(f"[{GREEN}✔{RESET}] เจอไฟล์: {filename}")
        return True
    else:
        print(f"[{RED}✘{RESET}] ไม่เจอไฟล์: {filename} (ระวังระบบพัง!)")
        return False

def check_folder(foldername, expected_count=0):
    if os.path.exists(foldername):
        files = [f for f in os.listdir(foldername) if f.lower().endswith(('.mp4', '.mov'))]
        count = len(files)
        status = GREEN if count > 0 else YELLOW
        print(f"[{status}✔{RESET}] เจอโฟลเดอร์: {foldername:<15} | มีคลิป: {count} ไฟล์")
        
        if count == 0:
            print(f"    {YELLOW}⚠️  เตือน: ไม่มีคลิปเตรียมไว้เลยนะ! บอทจะข้ามเพจนี้{RESET}")
        else:
            # เช็กชื่อไฟล์ตัวอย่าง
            example = files[0]
            if len(example) > 20:
                print(f"    {RED}❌ ชื่อไฟล์ยาวเกินไป ({example[:15]}...){RESET} -> รัน cleaner.py ด่วน!")
            else:
                print(f"    {GREEN}✨ ชื่อไฟล์สวยงาม ({example}){RESET}")
    else:
        print(f"[{RED}✘{RESET}] ไม่เจอโฟลเดอร์: {foldername} (สร้างด่วน!)")

def main():
    print(f"\n{GREEN}=== 🤓 น้องเนิร์ดตรวจการบ้าน (System Check) ==={RESET}\n")
    
    # 1. เช็กไฟล์สำคัญ
    print("📂 ตรวจสอบไฟล์ระบบ:")
    files_to_check = ["bot.py", "dashboard.py", "cleaner.py", "uploader.py"]
    score = 0
    for f in files_to_check:
        if check_file(f): score += 1
            
    # 2. เช็กโฟลเดอร์คลิป
    print("\n🎬 ตรวจสอบเสบียง (คลิปวิดีโอ):")
    check_folder("MyReels")
    check_folder("MyReels2")
    
    # 3. สรุปผล
    print("\n" + "="*30)
    if score == len(files_to_check):
        print(f"{GREEN}✅ ระบบพร้อมรัน 100%! ลุยเลยลูกพี่!{RESET}")
    else:
        print(f"{RED}❌ ไฟล์หายไปบางส่วน! เช็กดูดีๆ นะครับ{RESET}")
    print("="*30 + "\n")

if __name__ == "__main__":
    main()