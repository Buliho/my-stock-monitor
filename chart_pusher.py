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
    # 必須加入的參數，否則 GitHub Actions 會無法啟動 Chrome
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    try:
        # 自動管理 Chrome Driver 版本
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        url = "https://www.wantgoo.com/futures/retail-indicator/wtm&"
        print(f"🌐 正在存取網頁: {url}")
        driver.get(url)
        
        # 增加等待時間，確保玩股網的圖表渲染完全
        time.sleep(20) 
        
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
        
        # 讀取圖片並發送，加入 timeout 避免連線卡死
        with open("retail_chart.png", "rb") as f:
            files = {"imageFile": f}
            r = requests.post(notify_url, headers=headers, params=payload, files=files, timeout=30)
        
        if r.status_code == 200:
            print("✅ LINE 傳送成功！")
        else:
            print(f"❌ LINE 傳送失敗，狀態碼: {r.status_code}")

    except Exception as e:
        print(f"🔥 發生錯誤: {str(e)}")

if __name__ == "__main__":
    get_retail_chart()
