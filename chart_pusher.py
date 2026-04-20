import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def get_retail_chart():
    print("🚀 啟動截圖程式...")
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1200,1000')

    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        url = "https://www.wantgoo.com/futures/retail-indicator/wtm&"
        print(f"🌐 正在打開網頁: {url}")
        driver.get(url)
        time.sleep(10) # 增加等待時間，確保圖表跑出來

        print("📸 正在進行全螢幕截圖...")
        driver.save_screenshot("debug_full.png") # 先存一張全圖備查
        
        # 3. 傳送至 LINE
        token = os.getenv('LINE_ACCESS_TOKEN')
        if not token:
            print("❌ 錯誤: 找不到 LINE_ACCESS_TOKEN，請檢查 GitHub Secrets 設定")
            return

        print("📤 正在傳送至 LINE Notify...")
        notify_url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"message": "\n📊 微台指多空比測試"}
        files = {"imageFile": open("debug_full.png", "rb")}
        
        r = requests.post(notify_url, headers=headers, params=payload, files=files)
        print(f"✅ LINE 回傳狀態碼: {r.status_code}")
        if r.status_code != 200:
            print(f"❌ LINE 傳送失敗，原因: {r.text}")

    except Exception as e:
        print(f"🔥 發生嚴重錯誤: {e}")
    finally:
        driver.quit()
        print("🏁 程式結束")

if __name__ == "__main__":
    get_retail_chart()
