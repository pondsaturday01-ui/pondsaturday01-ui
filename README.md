# Facebook Reels Bot

บอทอัตโนมัติสำหรับโพสต์ Reels ไปยังหลายเพจ Facebook พร้อมระบบแยก Chrome Profile และแคปชั่นแต่ละเพจ

## Features

- ✅ **แยก Chrome Profile แต่ละเพจ** - แต่ละเพจใช้ profile แยกกัน (bot_brain_page0, bot_brain_page1, ...)
- ✅ **แยกแคปชั่นแต่ละเพจ** - กำหนดแคปชั่นต่างกันสำหรับแต่ละเพจ
- ✅ **Sequential Execution** - เปิด-ปิด Chrome ทีละเพจ (ประหยัด RAM)
- ✅ **Spintax Support** - สุ่มแคปชั่นแบบอัตโนมัติ
- ✅ **Telegram Notifications** - แจ้งเตือนเมื่อโพสต์สำเร็จ
- ✅ **Daily Report** - บันทึกรายงานการโพสต์
- ✅ **Multi-mode** - รองรับโหมด Random/Sequential สำหรับการเลือกคลิป

## Requirements

- Python 3.8+
- Google Chrome
- ChromeDriver
- Facebook account

## Installation

1. Clone repository:
```bash
git clone https://github.com/pondsaturday01-ui/facebook-reels-bot.git
cd facebook-reels-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. สร้างไฟล์ `.env` จาก `.env.example`:
```bash
cp .env.example .env
```

4. แก้ไขไฟล์ `.env` ใส่ Telegram Token และ Chat ID (ถ้าต้องการแจ้งเตือน)

## Setup

### 1. Login แต่ละ Profile

ต้อง login แยกแต่ละ Chrome profile ก่อนใช้งาน (ใช้ Facebook account **เดียวกัน** ทุก profile):

```bash
# Login สำหรับเพจ 0
python login_fix.py bot_brain_page0

# Login สำหรับเพจ 1
python login_fix.py bot_brain_page1

# Login สำหรับเพจ 2
python login_fix.py bot_brain_page2
```

### 2. ตั้งค่าเพจใน bot.py

แก้ไข `PAGE_MAPPINGS` ในไฟล์ bot.py ใส่ URL เพจและแคปชั่น

## Usage

### โพสต์ทันที (Run Now)

```bash
# โพสต์ทุกเพจ
python bot.py --now

# โพสต์เฉพาะเพจที่ 0, 1, 2
python bot.py --now --pages 0,1,2
```

### โหมดตั้งเวลา (Scheduler)

```bash
# ใช้เวลาจาก config
python bot.py

# กำหนดเวลาเอง
python bot.py --times 08:00,12:00,18:00
```

### โหมด Quota (8-10 โพสต์/เพจ/วัน)

```bash
# Dry-run (ดูตารางเวลาก่อน)
python bot.py --quota --dry-run

# รันจริง
python bot.py --quota
```

## Project Structure

```
MyBot/
├── bot.py              # โค้ดหลัก
├── uploader.py         # ระบบอัปโหลดและโพสต์
├── login_fix.py        # เครื่องมือ login
├── organizer.py        # จัดระเบียบไฟล์
├── dashboard.py        # Dashboard
├── logger.py           # ระบบ logging
├── .env               # ตั้งค่า (ห้ามอัปโหลด!)
├── requirements.txt    # Dependencies
└── MyReels*/          # โฟลเดอร์คลิป

bot_brain_page*/       # Chrome profiles (ห้ามอัปโหลด!)
logs/                  # Log files
```

## Important Notes

⚠️ **ความปลอดภัย:**
- ไม่ควรอัปโหลดไฟล์ `.env` หรือ `bot_brain*` ขึ้น GitHub
- ตรวจสอบ `.gitignore` ให้ครบถ้วน
- ใช้ repository แบบ Private

⚠️ **Resource Usage:**
- แต่ละ Chrome profile กิน ~100-200 MB disk space
- RAM usage: ~500MB-1GB ต่อ Chrome instance
- เปิดทีละตัว = ประหยัดทรัพยากร

⚠️ **Facebook Policy:**
- ใช้ในทางที่ถูกต้อง
- ไม่ spam หรือโพสต์เนื้อหาที่ผิดกฎหมาย
- ปฏิบัติตามข้อกำหนดของ Facebook

## License

MIT License - ใช้งานได้ตามต้องการ

## Credits

Built with Selenium WebDriver, Python, and Claude Code

---

**หมายเหตุ:** บอทนี้พัฒนาเพื่อการศึกษาและใช้งานส่วนตัว โปรดใช้อย่างรับผิดชอบ