import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright
import requests

# === 你的設定（改成 Telegram）===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")      # GitHub Secrets 新增這個
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # GitHub Secrets 新增這個
URL = "https://www.wantgoo.com/futures/retail-indicator/wtm"
IMAGE_PATH = "micro_futures_retail_ratio.png"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1680, "height": 1200},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()
        
        print("🌐 正在開啟 wantgoo 微台指散戶多空比頁面...")
        await page.goto(URL, wait_until="domcontentloaded", timeout=120000)
        await page.wait_for_load_state("load", timeout=90000)
        
        print("⏳ 等待圖表完全繪製...")
        await asyncio.sleep(12)
        
        print("📸 開始截取圖表...")
        await page.screenshot(path=IMAGE_PATH, full_page=False)
        print(f"✅ 截圖完成 → {IMAGE_PATH}")
        
        await browser.close()

def send_to_telegram(image_path: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ 未設定 Telegram Token 或 Chat ID")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    caption = f"📊 每日微台指散戶多空比\n時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}"

    try:
        with open(image_path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": TELEGRAM_CHAT_ID, "caption": caption}
            response = requests.post(url, data=data, files=files)
        
        if response.status_code == 200:
            print("✅ 已成功發送到 Telegram")
        else:
            print(f"❌ Telegram 發送失敗: {response.status_code}")
    except Exception as e:
        print(f"發送錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    if os.path.exists(IMAGE_PATH):
        send_to_telegram(IMAGE_PATH)
