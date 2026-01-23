import os

def clean_folder_names(folder_name):
    # หา path ของโฟลเดอร์
    base_path = os.getcwd()
    target_folder = os.path.join(base_path, folder_name)
    
    print(f"🧹 Cleaning folder: {folder_name}...", flush=True)
    
    if not os.path.exists(target_folder):
        print(f"❌ Not found: {target_folder}")
        return

    # อ่านไฟล์ทั้งหมด (ไม่สนนามสกุล)
    files = [f for f in os.listdir(target_folder) if os.path.isfile(os.path.join(target_folder, f))]
    files.sort() # เรียงตามชื่อเดิมก่อน
    
    count = 0
    for i, filename in enumerate(files):
        # ข้ามไฟล์ที่เป็น Script หรือไฟล์ระบบ
        if filename.endswith(".py") or filename.endswith(".ds_store"):
            continue
            
        # สร้างชื่อใหม่ (Ep001.mp4, Ep002.mp4...)
        new_name = f"Ep{str(i+1).zfill(3)}.mp4"
        
        old_path = os.path.join(target_folder, filename)
        new_path = os.path.join(target_folder, new_name)
        
        # เปลี่ยนชื่อ
        try:
            os.rename(old_path, new_path)
            print(f"   ✨ Renamed: {filename[:15]}... -> {new_name}")
            count += 1
        except Exception as e:
            print(f"   ⚠️ Error renaming {filename}: {e}")
            
    print(f"✅ Finished! Renamed {count} videos in {folder_name}.\n")

# --- สั่งทำงาน ---
# ใส่ชื่อโฟลเดอร์ที่ต้องการล้างชื่อตรงนี้
clean_folder_names("MyReels")
clean_folder_names("MyReels2") 
clean_folder_names("MyReels3")
clean_folder_names("zxcv") # ถ้ามีก็เปิดใช้งานบรรทัดนี้