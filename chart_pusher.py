import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def get_retail_chart():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080') # 設定大視窗好定位

    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 1. 前往網頁
        driver.get("https://www.wantgoo.com/futures/retail-indicator/wtm&")
        time.sleep(5) # 等待 JavaScript 渲染圖表

        # 2. 定位圖表區塊 (這部分根據玩股網結構微調)
        # 我們直接對整頁截圖，或是針對特定的 canvas/div
        element = driver.find_element(By.ID, "chart-canvas") # 這是常見的圖表 ID
        element.screenshot("retail_chart.png")
        
        # 3. 傳送至 LINE
        token = os.getenv('LINE_ACCESS_TOKEN')
        url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"message": "\n📊 今日微台指散戶多空比圖表"}
        files = {"imageFile": open("retail_chart.png", "rb")}
        
        r = requests.post(url, headers=headers, params=payload, files=files)
        print("LINE Notify Status:", r.status_code)

    except Exception as e:
        print(f"發生錯誤: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    get_retail_chart()
