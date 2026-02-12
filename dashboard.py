import customtkinter as ctk
import subprocess
import threading
import signal
import sys
import os
import time
import json  # ✅ พระเอกของเรา: เอาไว้จดบันทึกความจำ
from datetime import datetime, timedelta

# 🎨 ตั้งค่าธีม
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BotDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🤖 Facebook Reels Bot (V.Final God Mode)")
        self.geometry("900x900")
        self.process = None

        # ===========================
        # 1. ส่วนหัว + นาฬิกา
        # ===========================
        self.header_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=15)
        self.header_frame.pack(pady=15, padx=20, fill="x")

        self.label_title = ctk.CTkLabel(self.header_frame, text="Reels Auto-Pilot Dashboard", font=("Segoe UI", 26, "bold"))
        self.label_title.pack(pady=(15, 0))

        self.lbl_clock = ctk.CTkLabel(self.header_frame, text="00:00:00", 
                                      font=("Consolas", 64, "bold"), 
                                      text_color="#00E676") 
        self.lbl_clock.pack(pady=5)
        self.update_clock()

        self.status_label = ctk.CTkLabel(self.header_frame, text="สถานะ: พร้อมทำงาน ✅", text_color="silver", font=("Segoe UI", 16))
        self.status_label.pack(pady=(0, 15))

        # ===========================
        # 2. โซนเลือกเพจ
        # ===========================
        self.chk_frame = ctk.CTkFrame(self, fg_color="#252525", corner_radius=15)
        self.chk_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.chk_frame, text="🎯 เลือกเพจที่จะโพสต์:", font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(15,5))

        self.grid_box = ctk.CTkFrame(self.chk_frame, fg_color="transparent")
        self.grid_box.pack(padx=10, pady=5)

        self.checkboxes = []
        self.page_names = [
            "1. ปาฏิหาริย์ตัวเลข", "2. Add.ภูมิV.4", "3. ขุมทรัพย์ตัวเลข",
            "4. ชื่อเพจที่ 4",     "5. ชื่อเพจที่ 5",    "6. ชื่อเพจที่ 6",
            "7. ชื่อเพจที่ 7",     "8. ชื่อเพจที่ 8",    "9. ชื่อเพจที่ 9", 
            "10. ชื่อเพจที่ 10"
        ]

        for i, name in enumerate(self.page_names):
            chk = ctk.CTkCheckBox(self.grid_box, text=name, font=("Segoe UI", 14), corner_radius=20, hover_color="#00B0FF")
            chk.select()
            chk.grid(row=i//5, column=i%5, padx=15, pady=10, sticky="w")
            self.checkboxes.append(chk)

        # ===========================
        # 3. โซนคำนวณเวลา
        # ===========================
        self.calc_frame = ctk.CTkFrame(self, fg_color="#2E2E2E", corner_radius=15, border_width=2, border_color="#F57C00")
        self.calc_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(self.calc_frame, text="⚡ เครื่องสร้างเวลาอัตโนมัติ (Auto-Generator):", font=("Segoe UI", 18, "bold")).pack(pady=(15,5))
        
        self.input_box = ctk.CTkFrame(self.calc_frame, fg_color="transparent")
        self.input_box.pack(pady=10)

        ctk.CTkLabel(self.input_box, text="เริ่ม (HH:MM):", font=("Segoe UI", 14)).grid(row=0, column=0, padx=5)
        self.entry_start = ctk.CTkEntry(self.input_box, width=90, placeholder_text="09:00", corner_radius=10)
        self.entry_start.insert(0, "09:00")
        self.entry_start.grid(row=0, column=1, padx=5)

        ctk.CTkLabel(self.input_box, text="ถึง (HH:MM):", font=("Segoe UI", 14)).grid(row=0, column=2, padx=5)
        self.entry_end = ctk.CTkEntry(self.input_box, width=90, placeholder_text="21:00", corner_radius=10)
        self.entry_end.insert(0, "21:00")
        self.entry_end.grid(row=0, column=3, padx=5)

        ctk.CTkLabel(self.input_box, text="ห่าง (นาที):", font=("Segoe UI", 14)).grid(row=0, column=4, padx=5)
        self.entry_interval = ctk.CTkEntry(self.input_box, width=70, placeholder_text="60", corner_radius=10)
        self.entry_interval.insert(0, "60")
        self.entry_interval.grid(row=0, column=5, padx=5)

        self.btn_calc = ctk.CTkButton(self.input_box, text="🔨 สร้างตารางเวลา", 
                                      command=self.generate_schedule_list,
                                      fg_color="#F57C00", hover_color="#E65100", width=160, height=35, corner_radius=15, font=("Segoe UI", 14, "bold"))
        self.btn_calc.grid(row=0, column=6, padx=15)

        # ===========================
        # 4. ช่องแสดงผลเวลา
        # ===========================
        self.time_frame = ctk.CTkFrame(self, fg_color="#252525", corner_radius=15)
        self.time_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(self.time_frame, text="⏰ รายการเวลาที่จะโพสต์ (แก้ไขเองได้):", font=("Segoe UI", 16)).pack(anchor="w", padx=20, pady=(15,5))
        
        self.entry_box_frame = ctk.CTkFrame(self.time_frame, fg_color="transparent")
        self.entry_box_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.entry_time = ctk.CTkEntry(self.entry_box_frame, font=("Segoe UI", 14), corner_radius=10, height=35)
        self.entry_time.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_time.insert(0, "08:00, 12:00, 18:00") 

        self.btn_clear = ctk.CTkButton(self.entry_box_frame, text="❌ ล้างค่า", width=100, height=35, corner_radius=15,
                                         command=self.clear_time_input,
                                         fg_color="#D32F2F", hover_color="#B71C1C", font=("Segoe UI", 14, "bold"))
        self.btn_clear.pack(side="left")

        # ===========================
        # 5. ปุ่มควบคุมหลัก
        # ===========================
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        self.btn_run_now = ctk.CTkButton(self.btn_frame, text="🚀 โพสต์ทันที (Run Now)", 
                                         command=self.start_manual_run, 
                                         fg_color="#2E7D32", hover_color="#1B5E20", width=220, height=50, corner_radius=25, font=("Segoe UI", 18, "bold"))
        self.btn_run_now.grid(row=0, column=0, padx=10)

        self.btn_schedule = ctk.CTkButton(self.btn_frame, text="⏳ เริ่มรันตามเวลาด้านบน", 
                                          command=self.start_schedule_mode,
                                          fg_color="#1565C0", hover_color="#0D47A1", width=220, height=50, corner_radius=25, font=("Segoe UI", 18, "bold"))
        self.btn_schedule.grid(row=0, column=1, padx=10)

        self.btn_stop = ctk.CTkButton(self.btn_frame, text="🛑 หยุดบอท", 
                                      command=self.stop_bot, 
                                      fg_color="#C62828", hover_color="#B71C1C", width=160, height=50, corner_radius=25, font=("Segoe UI", 18, "bold"))
        self.btn_stop.grid(row=0, column=2, padx=10)
        self.btn_stop.configure(state="disabled")

        # ===========================
        # 6. จอแสดงผล
        # ===========================
        self.log_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=15)
        self.log_frame.pack(pady=15, padx=20, fill="both", expand=True)

        self.log_label = ctk.CTkLabel(self.log_frame, text="📝 รายงานผล (Real-Time Logs):", anchor="w", font=("Segoe UI", 16, "bold"))
        self.log_label.pack(fill="x", padx=20, pady=(15,0))

        self.log_box = ctk.CTkTextbox(self.log_frame, font=("Consolas", 14), text_color="#E0E0E0", fg_color="#2b2b2b", corner_radius=10)
        self.log_box.pack(fill="both", expand=True, padx=15, pady=15)
        self.log_box.insert("0.0", ">>> ยินดีต้อนรับสู่ Dashboard โฉมใหม่! (พร้อมระบบจำค่าอัตโนมัติ) ✨ \n")
        self.log_box.configure(state="disabled")

        # ✅ โหลดค่าเดิมที่เคยบันทึกไว้ (ถ้ามี)
        self.load_settings()

    # ===========================
    # 💾 โซนสมองความจำ (Save/Load)
    # ===========================
    def save_settings(self):
        # รวบรวมข้อมูลที่จะบันทึก
        selected_pages = []
        for i, chk in enumerate(self.checkboxes):
            if chk.get() == 1:
                selected_pages.append(i)

        data = {
            "time_input": self.entry_time.get(),
            "selected_pages": selected_pages,
            "gen_start": self.entry_start.get(),
            "gen_end": self.entry_end.get(),
            "gen_interval": self.entry_interval.get()
        }

        try:
            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print("💾 บันทึกการตั้งค่าเรียบร้อย!")
        except Exception as e:
            print(f"❌ บันทึกไม่สำเร็จ: {e}")

    def load_settings(self):
        if not os.path.exists("settings.json"):
            return # ถ้าไม่มีไฟล์ (ครั้งแรก) ก็ไม่ต้องทำอะไร

        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                data = json.load(f)

            # 1. คืนค่าเวลา
            if "time_input" in data:
                self.entry_time.delete(0, "end")
                self.entry_time.insert(0, data["time_input"])

            # 2. คืนค่าติ๊กถูกเพจ
            if "selected_pages" in data:
                saved_indices = data["selected_pages"]
                for i, chk in enumerate(self.checkboxes):
                    if i in saved_indices:
                        chk.select()
                    else:
                        chk.deselect()

            # 3. คืนค่าเครื่องสร้างเวลา
            if "gen_start" in data:
                self.entry_start.delete(0, "end")
                self.entry_start.insert(0, data["gen_start"])
            if "gen_end" in data:
                self.entry_end.delete(0, "end")
                self.entry_end.insert(0, data["gen_end"])
            if "gen_interval" in data:
                self.entry_interval.delete(0, "end")
                self.entry_interval.insert(0, data["gen_interval"])
            
            self.log_message("📂 โหลดค่าเดิมกลับมาให้แล้วครับเจ้านาย!")

        except Exception as e:
            self.log_message(f"⚠️ โหลดค่าเดิมผิดพลาด: {e}")

    # ===========================
    # ⚙️ ฟังก์ชันทำงานต่างๆ
    # ===========================
    def update_clock(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.lbl_clock.configure(text=current_time)
        self.after(1000, self.update_clock)

    def log_message(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def clear_time_input(self):
        self.entry_time.delete(0, "end")
        self.log_message("🧹 ล้างช่องเวลาเรียบร้อย!")

    def generate_schedule_list(self):
        try:
            start_str = self.entry_start.get().strip()
            end_str = self.entry_end.get().strip()
            interval_str = self.entry_interval.get().strip()

            t_start = datetime.strptime(start_str, "%H:%M")
            t_end = datetime.strptime(end_str, "%H:%M")
            interval = int(interval_str)

            if interval <= 0:
                self.log_message("❌ ระยะห่างต้องมากกว่า 0 นาทีครับ")
                return
            
            generated_times = []
            current = t_start
            
            while current <= t_end:
                generated_times.append(current.strftime("%H:%M"))
                current += timedelta(minutes=interval)

            result_str = ", ".join(generated_times)
            
            self.entry_time.delete(0, "end")
            self.entry_time.insert(0, result_str)
            
            self.log_message(f"✅ คำนวณเสร็จแล้ว! ได้ทั้งหมด {len(generated_times)} รอบครับ")
            
            # ✅ บันทึกค่าทันทีที่กดคำนวณ
            self.save_settings()
            
        except ValueError:
            self.log_message("❌ รูปแบบเวลาผิด! โปรดใส่เป็น HH:MM (เช่น 09:00)")
        except Exception as e:
            self.log_message(f"❌ เกิดข้อผิดพลาด: {e}")

    def run_process(self, command_list):
        def task():
            try:
                env_config = os.environ.copy()
                env_config["PYTHONIOENCODING"] = "utf-8"
                env_config["PYTHONUNBUFFERED"] = "1"

                popen_kwargs = dict(
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    env=env_config,
                    bufsize=0,
                )
                if sys.platform == 'win32':
                    popen_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
                else:
                    # Linux/macOS: สร้าง process group เพื่อให้ stop_bot kill ได้ทั้ง tree
                    popen_kwargs["preexec_fn"] = os.setsid

                self.process = subprocess.Popen(command_list, **popen_kwargs)

                for line in iter(self.process.stdout.readline, ''):
                    if line:
                        self.log_message(line.strip())
                
                self.process.stdout.close()
                self.process.wait()
                self.process = None
                self.finish_running()
                
            except Exception as e:
                self.log_message(f"❌ Error: {e}")
                self.finish_running()

        threading.Thread(target=task, daemon=True).start()

    def start_running_ui(self, mode_name):
        self.btn_run_now.configure(state="disabled")
        self.btn_schedule.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.status_label.configure(text=f"สถานะ: 🔥 กำลังรัน ({mode_name})...", text_color="#FFA000")
        self.log_message(f"----------------------------------------")
        self.log_message(f"🚀 เริ่มต้นการทำงานโหมด: {mode_name}")

    def finish_running(self):
        self.btn_run_now.configure(state="normal")
        self.btn_schedule.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.status_label.configure(text="สถานะ: พักผ่อน 💤", text_color="silver")
        self.log_message("🏁 จบการทำงาน")

    def start_manual_run(self):
        selected_pages_indices = []
        for i, chk in enumerate(self.checkboxes):
            if chk.get() == 1:
                selected_pages_indices.append(str(i))
        
        if not selected_pages_indices:
            self.log_message("❌ กรุณาเลือกอย่างน้อย 1 เพจนะครับ!")
            return

        pages_arg = ",".join(selected_pages_indices)
        
        # ✅ บันทึกค่าก่อนเริ่มรัน
        self.save_settings()
        
        self.start_running_ui("Manual Run")
        self.run_process([sys.executable, '-u', 'bot.py', '--now', '--pages', pages_arg])

    def start_schedule_mode(self):
        times_input = self.entry_time.get()
        if not times_input:
            self.log_message("❌ ไม่พบเวลาในช่อง! ลองกดปุ่ม 'สร้างตารางเวลา' ดูก่อนครับ")
            return

        selected_pages_indices = []
        selected_pages_names = []
        for i, chk in enumerate(self.checkboxes):
            if chk.get() == 1:
                selected_pages_indices.append(str(i))
                selected_pages_names.append(self.page_names[i])
        
        if not selected_pages_indices:
            self.log_message("❌ กรุณาเลือกอย่างน้อย 1 เพจนะครับ!")
            return

        self.log_message(f"⏰ ตั้งเวลาทำงาน: {times_input}")
        self.log_message(f"🎯 เพจที่จะทำ: {', '.join(selected_pages_names)}")
        
        pages_arg = ",".join(selected_pages_indices)
        
        # ✅ บันทึกค่าก่อนเริ่มรัน
        self.save_settings()
        
        self.start_running_ui("Schedule Mode")
        self.run_process([sys.executable, '-u', 'bot.py', '--times', times_input, '--pages', pages_arg])

    def stop_bot(self):
        if self.process:
            self.log_message("🛑 สั่งหยุดบอททันที!!!")
            try:
                if sys.platform == "win32":
                    # Windows: ใช้ taskkill เพื่อ kill process tree ทั้งหมด
                    subprocess.call(f"taskkill /F /T /PID {self.process.pid}", shell=True)
                else:
                    # Linux/macOS: ส่ง signal SIGTERM แล้วรอ แล้วค่อย SIGKILL
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            except (ProcessLookupError, OSError) as e:
                self.log_message(f"⚠️ Process อาจจบไปแล้ว: {e}")
            finally:
                self.process = None
                self.finish_running()

if __name__ == "__main__":
    app = BotDashboard()
    app.mainloop()