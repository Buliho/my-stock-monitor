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
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        url = "https://www.wantgoo.com/futures/retail-indicator/wtm&"
        driver.get(url)
        time.sleep(25) # 確保圖表完整渲染
        
        driver.save_screenshot("retail_chart.png")
        print("📸 截圖已儲存")
        driver.quit()

        # --- 強化傳送區塊 ---
        token = os.getenv('LINE_ACCESS_TOKEN')
        notify_url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"message": "\n📊 微台指散戶多空比即時測試"}

        # 嘗試 5 次發送，應對 DNS 解析失敗
        for attempt in range(5):
            try:
                print(f"📤 正在嘗試發送至 LINE (第 {attempt + 1} 次)...")
                with open("retail_chart.png", "rb") as f:
                    r = requests.post(notify_url, headers=headers, data=payload, files={"imageFile": f}, timeout=30)
                if r.status_code == 200:
                    print("✅ LINE 傳送成功！")
                    return
                else:
                    print(f"⚠️ 伺服器回應錯誤: {r.status_code}")
            except Exception as e:
                print(f"⚠️ 連線異常: {e}")
                time.sleep(10) # 等待 10 秒後重試
        
        print("❌ 經過多次嘗試後仍失敗。")

    except Exception as e:
        print(f"🔥 發生錯誤: {e}")

if __name__ == "__main__":
    get_retail_chart()
