import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_retail_chart():
    print("🚀 啟動截圖流程...")
    chrome_options = Options()
    # 這裡是最關鍵的四行參數，沒加這幾行 GitHub Actions 會跑不動
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    try:
        # 自動下載並安裝對應版本的 Chrome Driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        url = "https://www.wantgoo.com/futures/retail-indicator/wtm&"
        print(f"🌐 正在存取網頁: {url}")
        driver.get(url)
        
        # 增加等待時間，確保圖表加載完成 (玩股網圖表較重)
        time.sleep(15) 
        
        driver.save_screenshot("retail_chart.png")
        print("📸 截圖已儲存")
        driver.quit()

        # 傳送 LINE
        token = os.getenv('LINE_ACCESS_TOKEN')
        if not token:
            print("❌ 錯誤：找不到 LINE_ACCESS_TOKEN")
            return

        print("📤 傳送至 LINE Notify...")
        notify_url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"message": "\n📊 微台指散戶多空比即時測試"}
        files = {"imageFile": open("retail_chart.png", "rb")}
        
        r = requests.post(notify_url, headers=headers, params=payload, files=files)
        print(f"✅ LINE 回報狀態: {r.status_code}")

    except Exception as e:
        print(f"🔥 發生錯誤: {str(e)}")

if __name__ == "__main__":
    get_retail_chart()
