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
            viewport={"width": 1600, "height": 1200},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("🌐 正在開啟 wantgoo 微台指散戶多空比頁面...")
        
        # 1. 先用較寬鬆的方式載入頁面
        await page.goto(URL, wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_load_state("load", timeout=60000)
        
        print("📊 等待圖表區域載入...")
        
        # 2. 多種 selector 嘗試（依優先順序）
        selectors = [
            '.highcharts-container',           # 最常見的 Highcharts
            'canvas',                          # 如果是 canvas 繪製
            'svg',                             # 如果是 SVG
            '[id*="chart"]',                   # 包含 chart 的元素
            'text=微台指散戶多空比',           # 文字定位
        ]
        
        chart_locator = None
        for sel in selectors:
            try:
                print(f"嘗試 selector: {sel}")
                await page.wait_for_selector(sel, timeout=15000)
                chart_locator = page.locator(sel).first
                if await chart_locator.is_visible():
                    print(f"✅ 找到圖表：{sel}")
                    break
            except:
                continue
        
        # 3. 如果還是沒找到，就用比較大的區域（包含標題）
        if not chart_locator or not await chart_locator.is_visible():
            print("⚠️ 無法精準找到圖表容器，改用較大區域截圖...")
            chart_locator = page.locator('body').locator('div:has-text("微台指散戶多空比")').first
        
        # 4. 額外等待讓柱狀圖與藍線完全繪製
        await asyncio.sleep(10)
        
        # 截圖
        await chart_locator.screenshot(path=IMAGE_PATH)
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
            print(f"❌ LINE 發送失敗: {response.status_code}")
    except Exception as e:
        print(f"發送錯誤: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    if os.path.exists(IMAGE_PATH):
        send_to_line(IMAGE_PATH)
