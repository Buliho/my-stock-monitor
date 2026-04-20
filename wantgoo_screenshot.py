import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright
import requests

# === 設定 ===
LINE_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
URL = "https://www.wantgoo.com/futures/retail-indicator/wtm"
IMAGE_PATH = "micro_futures_retail_ratio.png"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1600, "height": 1100},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("🌐 正在開啟 wantgoo 微台指散戶多空比頁面...")
        
        # 改用較寬鬆的等待策略
        await page.goto(URL, wait_until="domcontentloaded", timeout=90000)  # 先等基本結構載入
        
        print("📊 等待圖表載入...")
        # 等待 Highcharts 圖表容器出現
        await page.wait_for_selector('.highcharts-container', timeout=30000)
        
        # 額外等待，讓柱狀圖和藍線完全繪製
        await asyncio.sleep(8)
        
        # 只截取主要圖表（微台指散戶多空比）
        chart = page.locator('.highcharts-container').first
        await chart.screenshot(path=IMAGE_PATH)
        
        print(f"✅ 圖表截取完成 → {IMAGE_PATH}")
        await browser.close()

def send_to_line(image_path: str):
    if not LINE_TOKEN:
        print("❌ 未設定 LINE_ACCESS_TOKEN")
        return
    
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    message = f"📊 每日微台指散戶多空比\n時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}"

    try:
        with open(image_path, "rb") as f:
            files = {"imageFile": f}
            data = {"message": message}
            response = requests.post(url, headers=headers, data=data, files=files)
        
        if response.status_code == 200:
            print("✅ 已成功發送到 LINE")
        else:
            print(f"❌ LINE 發送失敗: {response.status_code} {response.text}")
    except Exception as e:
        print(f"發送錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    if os.path.exists(IMAGE_PATH):
        send_to_line(IMAGE_PATH)
