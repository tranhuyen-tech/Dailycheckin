import os
import time
from datetime import datetime, timedelta
import subprocess
from curl_cffi import requests

LOG_FILE = "last_claim_success.txt"
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
        print(f"⚠️ Không thể Git Commit: {e}")

def do_unlucid_checkin():
    # URL API chuẩn xác từ tên tiến trình claim_free_gems của bạn
    url = "https://unlucid.ai"  
    cookie = os.getenv("UNLUCID_COOKIE")
    
    headers = {
        "Cookie": cookie,
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Referer": "https://unlucid.ai",
        "Origin": "https://unlucid.ai",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    # Payload mặc định dạng đối tượng trống
    payload_data = {} 
    
    print("📡 Đang gửi yêu cầu nhận Gem chính thức bằng phương thức POST...")
    try:
        response = requests.post(url, headers=headers, json=payload_data, impersonate="chrome", allow_redirects=False, timeout=30)
        print(f"👉 Kết quả phản hồi từ Web - Mã trạng thái: {response.status_code}")
        print(f"Nội dung phản hồi từ máy chủ: {response.text[:200]}")
        
        # Chấp nhận mã thành công 200 từ lệnh POST hệ thống
        if response.status_code == 200:
            print("🎉 Điểm danh Unlucid AI thành công! Hệ thống đã ghi nhận.")
            save_and_commit_time()
            return True
        else:
            print("❌ Máy chủ từ chối lệnh POST. Có thể cần kiểm tra lại chuỗi chữ trong View source.")
            return False
    except Exception as e:
        print(f"💥 Lỗi kết nối gửi lệnh POST: {e}")
        return False

def main():
    last_time = get_last_checkin()
    now = datetime.now()
    
    if last_time and (now - last_time) < REQUIRED_DELAY:
        time_left = REQUIRED_DELAY - (now - last_time)
        print(f"⏳ Cảnh báo bảo vệ: Chưa đủ chu kỳ an toàn. Cần chờ thêm: {time_left}. Hủy lượt chạy ngầm!")
        return

    print("🚀 Đã đủ thời gian an toàn. Tiến hành gửi lệnh điểm danh chính thức...")
    do_unlucid_checkin()

if __name__ == "__main__":
    main()
