from datetime import datetime, timedelta
import os
import subprocess
import time
from curl_cffi import requests

LOG_FILE = "last_claim_success.txt"
# Đặt khoảng thời gian chờ cố định: 23 giờ + 50 phút
REQUIRED_DELAY = timedelta(hours=23, minutes=50)


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

  # Tự động commit lưu lịch sử lên GitHub (nếu bạn chạy bằng GitHub Actions)
  try:
    subprocess.run(
        ["git", "config", "--global", "user.name", "github-actions[bot]"],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "config",
            "--global",
            "user.email",
            "github-actions[bot]@users.noreply.github.com",
        ],
        check=True,
    )
    subprocess.run(["git", "add", LOG_FILE], check=True)
    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            f" Update checkin history: {current_time} (ICT)",
        ],
        check=True,
    )
    subprocess.run(["git", "push"], check=True)
    print(f" Đã lưu lịch sử điểm danh lúc {current_time} thành công.")
  except Exception as e:
    print(f" Không thể Git Commit (có thể do đang chạy dưới máy cục bộ): {e}")


def do_unlucid_checkin():
  # Endpoint API chính xác trích xuất từ cURL
  url = "https://unlucid.ai/api/claim_free_gems"

  # Lấy cookie từ biến môi trường
  cookie = os.getenv("UNLUCID_COOKIE")

  headers = {
      "accept": "*/*",
      "accept-language": "vi,en-US;q=0.9,en;q=0.8",
      "content-type": "application/json",
      "origin": "https://unlucid.ai",
      "priority": "u=1, i",
      "referer": "https://unlucid.ai/gems",
      "sec-ch-ua": (
          '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"'
      ),
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": '"Windows"',
      "sec-fetch-dest": "empty",
      "sec-fetch-mode": "cors",
      "sec-fetch-site": "same-origin",
      "user-agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/150.0.0.0 Safari/537.36"
      ),
      "cookie": cookie,
  }

  print(" Đang gửi yêu cầu nhận Gem tới /api/claim_free_gems...")

  try:
    # Gửi request POST với payload json rỗng {}
    response = requests.post(
        url,
        headers=headers,
        json={},
        impersonate="chrome",
        timeout=30,
    )

    print(f" Mã trạng thái phản hồi: {response.status_code}")
    print(f" Nội dung trả về từ máy chủ: {response.text[:200]}")

    if response.status_code == 200:
      print(" Điểm danh Unlucid AI thành công!")
      save_and_commit_time()
      return True
    else:
      print(" Máy chủ từ chối request. Hãy kiểm tra lại UNLUCID_COOKIE.")
      return False

  except Exception as e:
    print(f" Lỗi kết nối: {e}")
    return False


def main():
  last_time = get_last_checkin()
  now = datetime.now()

  if last_time:
    next_allowed_time = last_time + REQUIRED_DELAY
    if now < next_allowed_time:
      wait_time = next_allowed_time - now
      print(f" Chưa đủ 24h5p kể từ lần điểm danh trước ({last_time}).")
      print(
          f" Cần chờ thêm {wait_time}. Hủy bỏ lượt chạy này để tránh bị quá"
          " sớm!"
      )
      return

  print(" Đã đủ điều kiện thời gian. Bắt đầu gửi lệnh điểm danh...")
  do_unlucid_checkin()


if __name__ == "__main__":
  main()
