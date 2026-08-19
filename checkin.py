import os
import time
from datetime import datetime, timedelta
import subprocess
from curl_cffi import requests

LOG_FILE = "last_claim_success.txt"
REQUIRED_DELAY = timedelta(hours=24, minutes=5)

def get_last_checkin():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                return datetime.fromisoformat(f.read().strip())
            except:
                return None
    return None

def save_and_commit_time():
    current_time = datetime.now().isoformat()
    with open(LOG_FILE, "w") as f:
        f.write(current_time)
    
    try:
        subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@://github.com"], check=True)
        subprocess.run(["git", "add", LOG_FILE], check=True)
        subprocess.run(["git", "commit", "-m", f" Update checkin history: {current_time}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print(" Đã lưu lịch sử và đồng bộ lên GitHub thành công.")
    except Exception as e:
        print(f" Không thể Git Commit (Có thể dữ liệu không đổi): {e}")

def do_unlucid_checkin():
    url = "https://unlucid.ai"  
    cookie = os.getenv("UNLUCID_COOKIE")
    
    headers = {
        "Cookie": cookie,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Referer": "https://unlucid.ai",
        "Origin": "https://unlucid.ai",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    try:
        response = requests.post(url, headers=headers, json={}, impersonate="safari_15_3", timeout=30)
        print(f" Trạng thái phản hồi từ Web: {response.status_code}")
        
        if response.status_code == 200:
            print(" Điểm danh Unlucid AI thành công! Nhận 5 Gems.")
            save_and_commit_time()
            return True
        elif response.status_code == 401:
            print(" Cookie đã hết hạn hoặc sai thông tin. Vui lòng lấy lại Cookie mới.")
            return False
        else:
            print(f" Điểm danh thất bại. Chi tiết phản hồi: {response.text}")
            return False
    except Exception as e:
        print(f" Lỗi kết nối vượt tường lửa đến Unlucid AI: {e}")
        return False

def main():
    last_time = get_last_checkin()
    now = datetime.now()
    
    if last_time and (now - last_time) < REQUIRED_DELAY:
        time_left = REQUIRED_DELAY - (now - last_time)
        print(f" Chưa đủ 24 giờ kể từ lần nhận trước. Cần chờ thêm: {time_left}. Hủy lượt này.")
        return

    print(" Đã đủ chu kỳ thời gian. Đang gửi lệnh nhận Gem...")
    do_unlucid_checkin()

if __name__ == "__main__":
    main()
