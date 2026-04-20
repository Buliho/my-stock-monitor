import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright
import requests

# === 你的設定 ===
LINE_TOKEN = os.getenv("LINE_ACCESS_TOKEN")          # 你原本 GitHub Secrets 裡面的名稱
URL = "https://www.wantgoo.com/futures/retail-indicator/wtm"
IMAGE_PATH = "micro_futures_retail_ratio.png"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1600, "height": 1100},   # 讓圖表完整顯示
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("🌐 正在開啟 wantgoo 微台指散戶多空比頁面...")
        await page.goto(URL, wait_until="networkidle", timeout=60000)
        
        # 等待圖表完全載入（Highcharts 是動態繪製）
        await page.wait_for_selector('.highcharts-container', timeout=15000)
        await asyncio.sleep(6)   # 再等 6 秒確保柱狀圖與線完全畫好
        
        # 🔥 只截「微台指散戶多空比」這張圖表（不是整頁）
        chart = page.locator('.highcharts-container').first
        await chart.screenshot(path=IMAGE_PATH)
        print(f"✅ 圖表截取完成 → {IMAGE_PATH}")
        
        await browser.close()

def send_to_line(image_path: str):
    if not LINE_TOKEN:
        print("❌ 找不到 LINE_ACCESS_TOKEN")
        return
    
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    message = f"📊 每日微台指散戶多空比\n時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}"

    with open(image_path, "rb") as f:
        files = {"imageFile": f}
        data = {"message": message}
        response = requests.post(url, headers=headers, data=data, files=files)
    
    if response.status_code == 200:
        print("✅ 已成功發送到 LINE")
    else:
        print(f"❌ LINE 發送失敗: {response.text}")

if __name__ == "__main__":
    asyncio.run(main())
    if os.path.exists(IMAGE_PATH):
        send_to_line(IMAGE_PATH)
        # os.remove(IMAGE_PATH)   # 發完可選擇刪除
