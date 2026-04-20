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
            viewport={"width": 1680, "height": 1200},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("🌐 正在開啟 wantgoo 微台指散戶多空比頁面...")
        
        # 使用最寬鬆的載入方式
        await page.goto(URL, wait_until="domcontentloaded", timeout=120000)
        await page.wait_for_load_state("load", timeout=90000)
        
        print("⏳ 等待頁面完全穩定與圖表繪製...")
        # 給予足夠時間讓 Highcharts 動態繪製柱狀圖與藍線
        await asyncio.sleep(12)
        
        # === 最可靠的截圖方式：只截取中間主要內容區域（避開 header/footer）===
        print("📸 開始截取圖表...")
        
        # 方式1：截取整個可視視窗（最穩，圖表會在中央）
        await page.screenshot(path=IMAGE_PATH, full_page=False)
        
        # 如果你想更乾淨，可以試下面這行（取消註解取代上面一行）：
        # await page.locator('main, .container, article').first.screenshot(path=IMAGE_PATH)  # 視情況
        
        print(f"✅ 截圖完成 → {IMAGE_PATH}")
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
            print(f"❌ LINE 發送失敗: {response.status_code}")
    except Exception as e:
        print(f"發送錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    if os.path.exists(IMAGE_PATH):
        send_to_line(IMAGE_PATH)
