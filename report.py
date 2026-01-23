import csv
import os
from datetime import datetime

def save_report(video_name, status, caption):
    """
    บันทึกข้อมูลการโพสต์ลงไฟล์ daily_report.csv
    """
    file_exists = os.path.isfile('daily_report.csv')
    
    try:
        with open('daily_report.csv', 'a', newline='', encoding='utf-8') as f:
            headers = ['Date', 'Time', 'Video Name', 'Status', 'Caption']
            writer = csv.DictWriter(f, fieldnames=headers)
            
            if not file_exists:
                writer.writeheader()
            
            now = datetime.now()
            writer.writerow({
                'Date': now.strftime('%Y-%m-%d'),
                'Time': now.strftime('%H:%M:%S'),
                'Video Name': video_name,
                'Status': status,
                'Caption': caption
            })
            print(f"📝 Saved report for: {video_name}")
            
    except Exception as e:
        print(f"❌ Failed to save report: {e}")
