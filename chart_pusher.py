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
        
        # 存取目標網頁
        url = "https://www.wantgoo.com/futures/retail-indicator/wtm&"
        driver.get(url)
        time.sleep(20) # 給圖表一點渲染時間
        
        driver.save_screenshot("retail_chart.png")
        print("📸 截圖已儲存")
        driver.quit()

        # --- 傳送區塊：完全模仿 main.py 的成功經驗 ---
        token = os.getenv('LINE_ACCESS_TOKEN')
        notify_url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": f"Bearer {token}"}
        
        # 這次我們把參數放在 params，檔案放在 files
        payload = {"message": "\n📊 微台指散戶多空比即時測試"}
        
        print("📤 正在透過網址模式傳送圖片...")
        with open("retail_chart.png", "rb") as f:
            file_data = {"imageFile": f}
            # 這裡不加 verify=False，因為 main.py 沒加也能通
            r = requests.post(notify_url, headers=headers, params=payload, files=file_data, timeout=30)
        
        if r.status_code == 200:
            print("✅ 圖片傳送成功！")
        else:
            print(f"❌ 傳送失敗，狀態碼: {r.status_code}, 回應: {r.text}")

    except Exception as e:
        print(f"🔥 發生錯誤: {e}")

if __name__ == "__main__":
    get_retail_chart()
