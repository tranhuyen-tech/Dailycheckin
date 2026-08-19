import os
import time
from datetime import datetime, timedelta
import subprocess
from curl_cffi import requests

LOG_FILE = "last_claim_success.txt"
# Chu kỳ an toàn (24 giờ 15 phút) bù đắp sai số hệ thống
REQUIRED_DELAY = timedelta(hours=24, minutes=15)

def get_last_checkin():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                return datetime.strptime(f.read().strip(), "%d/%m/%Y %H:%M:%S")
            except:
                return None
    return None

def save_and_commit_time():
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    with open(LOG_FILE, "w") as f:
        f.write(current_time)
    
    try:
        subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@://github.com"], check=True)
        subprocess.run(["git", "add", LOG_FILE], check=True)
        subprocess.run(["git", "commit", "-m", f"🔄 Update checkin history: {current_time} (ICT)"], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"💾 Đã lưu lịch sử điểm danh lúc {current_time} về GitHub thành công.")
    except Exception as e:
        print(f"⚠️ Không thể Git Commit (Có thể dữ liệu không đổi): {e}")

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
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        # Gửi lệnh POST bypass Cloudflare
        response = requests.post(url, headers=headers, json={}, impersonate="chrome", allow_redirects=False, timeout=30)
        print(f"📡 Trạng thái phản hồi thực tế từ Web: {response.status_code}")
        
        if response.status_code == 200 and "<!doctype html>" not in response.text:
            print(f"Chi tiết phản hồi nhận quà: {response.text}")
            print("🎉 Điểm danh Unlucid AI thành công! Nhận 5 Gems.")
            save_and_commit_time()
            return True
        else:
            print(f"❌ Web từ chối hoặc bắt xác thực lại (Mã: {response.status_code}).")
            print("Vui lòng đợi đến đúng chu kỳ 24h15m để hệ thống tự quét lại.")
            return False
    except Exception as e:
        print(f"💥 Lỗi kết nối vượt tường lửa đến Unlucid AI: {e}")
        return False

def main():
    last_time = get_last_checkin()
    now = datetime.now()
    
    if last_time and (now - last_time) < REQUIRED_DELAY:
        time_left = REQUIRED_DELAY - (now - last_time)
        print(f"⏳ Cảnh báo bảo vệ: Chưa đủ chu kỳ an toàn. Cần chờ thêm: {time_left}. Hủy lượt chạy ngầm!")
        return

    print("🚀 Đã qua chu kỳ an toàn. Đang gửi lệnh nhận Gem...")
    do_unlucid_checkin()

if __name__ == "__main__":
    main()
