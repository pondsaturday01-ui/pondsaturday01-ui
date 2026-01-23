# โค้ดสำหรับ bot.py (ระบบตั้งเวลา)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import random
import shutil
import pyperclip
import config
from datetime import datetime

def run_post_task():
    print("🚀 ถึงเวลาแล้ว! เริ่มภารกิจโพสต์ Reels...")
    posted_folder = os.path.join(config.VIDEO_FOLDER, "Posted")
    if not os.path.exists(posted_folder): os.makedirs(posted_folder)

    try:
        all_clips = [f for f in os.listdir(config.VIDEO_FOLDER) if f.endswith(".mp4")]
    except:
        print("❌ หาโฟลเดอร์ไม่เจอ ตรวจสอบ config นะครับ")
        return

    if len(all_clips) == 0:
        print("⚠️ ไม่มีคลิปเหลือแล้ว! (ข้ามรอบนี้ไป)")
        return

    selected_clip = random.choice(all_clips)
    video_path = os.path.join(config.VIDEO_FOLDER, selected_clip)
    my_caption = random.choice(config.CAPTIONS)

    print(f"🎬 คลิป: {selected_clip}")
    print(f"📝 แคปชั่น: {my_caption}")

    print(">>> กำลังเปิด Chrome...")
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={os.getcwd()}\\bot_brain")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    try:
        driver.get(config.PAGE_URL)
        wait = WebDriverWait(driver, 30)

        # ด่าน 1: กด Reels
        print("⏳ หาปุ่ม Reels...")
        try:
            # ลองหาคำว่า "Reels" หรือ "คลิป Reels"
            # หา element ที่มี text ว่า "คลิป Reels" แบบเป๊ะๆ หรืออยู่ใน span/div
            reels_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='คลิป Reels' or text()='Reels']")))
            reels_btn.click()
        except:
             # ถ้าไม่เจอ ลองหาผ่าน URL หรือกดลิงก์ตรงๆ
            print("⚠️ หาปุ่มไม่เจอ! กำลังพยายามเข้าหน้า Reels โดยตรง...")
            driver.get(config.PAGE_URL + "/reels")
            time.sleep(3)

        # ด่าน 1.5: หาปุ่ม "สร้างคลิป" (Create)
        print("⏳ กำลังหาปุ่ม 'สร้างคลิป'...")
        try:
             # หาปุ่มที่มีคำว่า "สร้าง" หรือ "Create"
            create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='button']//*[contains(text(), 'สร้าง') or contains(text(), 'Create')]")))
            create_btn.click()
            time.sleep(2)
        except:
            print("⚠️ หาปุ่มสร้างไม่เจอ? ลองข้ามไปขั้นตอนอัปโหลดเลย...")

        # ด่าน 2: อัปโหลด
        print("⏳ อัปโหลดไฟล์...")
        # รอให้ Dialog เด้งขึ้นมา (หาคำว่า "สร้าง" หรือ "Create")
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']//*[contains(text(), 'สร้าง') or contains(text(), 'Create')]")))
        upload_input = driver.find_element(By.XPATH, "//div[@role='dialog']//input[@type='file']")
        upload_input.send_keys(video_path)

        # ด่าน 3 & 4: กดถัดไป
        print("⏳ กดถัดไป...")
        for _ in range(2):
            time.sleep(5)
            driver.find_element(By.XPATH, "//div[@role='dialog']//span[contains(text(), 'ถัดไป')]").click()

        # ด่าน 5: แคปชั่น + โพสต์
        time.sleep(5)
        caption_box = driver.find_element(By.XPATH, "//div[@role='dialog']//div[@contenteditable='true']")
        caption_box.click()
        pyperclip.copy(my_caption)
        caption_box.send_keys(Keys.CONTROL, 'v')
        time.sleep(2)

        driver.find_element(By.XPATH, "//div[@role='dialog']//div[@role='button']//span[text()='โพสต์']").click()
        print("🎉 กดโพสต์สำเร็จ!")

        time.sleep(10)
        driver.quit()
        shutil.move(video_path, os.path.join(posted_folder, selected_clip))
        print("✅ เก็บกวาดไฟล์เรียบร้อย")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        try: driver.quit()
        except: pass

# Loop ทดสอบ (3 รอบ)
print("⏰ บอทเริ่มทำงาน (โหมดทดสอบ 3 รอบ ทุก 1 นาที)...")
for i in range(3):
    print(f"\n🔔 รอบที่ {i+1}/3 เริ่มแล้ว! (จากทั้งหมด 3 รอบ)")
    run_post_task()
    
    if i < 2: # ถ้ายังไม่ครบรอบสุดท้าย ให้รอ
        print("💤 พัก 60 วินาที ก่อนเริ่มรอบต่อไป...")
        time.sleep(60)

print("\n✅ ครบ 3 รอบแล้ว! จบการทำงานครับ")