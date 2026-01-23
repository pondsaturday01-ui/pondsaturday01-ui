import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def manual_login():
    print("--- 🔑 MANUAL LOGIN TOOL ---")
    
    # ตั้งค่าให้ใช้ Profile เดียวกับบอท (สำคัญมาก!)
    current_folder = os.getcwd()
    profile_path = os.path.join(current_folder, "bot_brain")
    
    options = Options()
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument("--disable-notifications")
    
    print(f"📂 Loading Profile from: {profile_path}")
    print("🚀 Opening Facebook... Please wait.")
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.facebook.com")
        
        print("\n" + "="*40)
        print("🛑  เจ้านายครับ! ตอนนี้หน้าเว็บเปิดอยู่")
        print("👉  กรุณา 'กรอกรหัสผ่าน' และกดล็อกอินให้เรียบร้อย")
        print("👉  ถ้ามีให้กด Save Browser / จดจำฉันไว้ ให้กดด้วยนะครับ")
        print("✅  พอล็อกอินเสร็จ จนเห็นหน้าฟีดข่าวแล้ว... ให้กลับมาที่จอดำนี้แล้วกด Enter")
        print("="*40 + "\n")
        
        input("⌨️ กด Enter ตรงนี้ เพื่อบันทึกและปิดโปรแกรม...")
        
        driver.quit()
        print("✅ บันทึกการล็อกอินเรียบร้อย! พร้อมรันบอทแล้วครับ!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    manual_login()