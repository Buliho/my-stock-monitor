import os
import time
import requests
import urllib3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 禁用因 IP 直連導致的 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_retail_chart():
    print("🚀 啟動截圖流程...")
    chrome_options = Options()
    # GitHub Actions 必要參數
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    try:
        # 1. 截圖部分
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        url = "https://www.wantgoo.com/futures/retail-indicator/wtm&"
        print(f"🌐 正在存取網頁: {url}")
        driver.get(url)
        
        # 玩股網圖表渲染較慢，給予充足時間
        time.sleep(25) 
        
        driver.save_screenshot("retail_chart.png")
        print("📸 截圖已儲存")
        driver.quit()

        # 2. 傳送部分 (加入 IP 直連避開 DNS 錯誤)
        token = os.getenv('LINE_ACCESS_TOKEN')
        if not token:
            print("❌ 錯誤：找不到 LINE_ACCESS_TOKEN")
            return

        payload = {"message": "\n📊 微台指散戶多空比即時測試"}
        
        # 嘗試方案 A: IP 直連 (繞過 DNS)
        # 嘗試方案 B: 標準網址 (正常連線)
        targets = [
            {"url": "https://203.104.146.131/api/notify", "use_ip": True},
            {"url": "https://notify-api.line.me/api/notify", "use_ip": False}
        ]

        for target in targets:
            try:
                mode = "IP 直連" if target["use_ip"] else "網址模式"
                print(f"📤 嘗試以 [{mode}] 傳送至 LINE...")
                
                headers = {"Authorization": f"Bearer {token}"}
                if target["use_ip"]:
                    headers["Host"] = "notify-api.line.me"

                with open("retail_chart.png", "rb") as f:
                    files = {"imageFile": f}
                    r = requests.post(
                        target["url"], 
                        headers=headers, 
                        params=payload, 
                        files=files, 
                        timeout=30, 
                        verify=False # IP 連線必須跳過 SSL 驗證
                    )
                
                if r.status_code == 200:
                    print(f"✅ LINE 傳送成功！({mode})")
                    return
                else:
                    print(f"⚠️ {mode} 回應代碼: {r.status_code}")
            except Exception as e:
                print(f"⚠️ {mode} 嘗試失敗: {str(e)}")
                continue

        print("❌ 所有連線方案均已失敗。")

    except Exception as e:
        print(f"🔥 腳本發生核心錯誤: {str(e)}")

if __name__ == "__main__":
    get_retail_chart()
