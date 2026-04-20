import os
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# ---- 設定目標網址與截圖路徑 ----
TARGET_URL = "https://www.wantgoo.com/futures/retail-indicator/wtm&"   # <-- 改成你的目標網址
SCREENSHOT_PATH = "/tmp/chart_screenshot.png"

def capture_screenshot(url, save_path):
    """使用 Selenium headless Chrome 截圖"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,900")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        driver.get(url)
        time.sleep(5)  # 等待頁面載入，可依需要調整
        driver.save_screenshot(save_path)
        print(f"截圖成功，儲存至：{save_path}")
    finally:
        driver.quit()

def send_to_line(image_path):
    """將截圖傳送到 LINE Notify"""
    token = os.getenv('LINE_ACCESS_TOKEN')
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"message": "\n微台指數戶多空比即時測試"}

    # 建立重試機制，對抗暫時性的 DNS 錯誤
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        with open(image_path, "rb") as f:
            files = {"imageFile": f}
            r = session.post(url, headers=headers, params=payload, files=files, timeout=30)

        if r.status_code == 200:
            print("LINE 傳送成功！")
        else:
            print(f"LINE 傳送失敗，狀態碼：{r.status_code}，內容：{r.text}")
    except Exception as e:
        print(f"連線失敗：{e}")

# ---- 主程式入口 ----
if __name__ == "__main__":
    capture_screenshot(TARGET_URL, SCREENSHOT_PATH)
    send_to_line(SCREENSHOT_PATH)
