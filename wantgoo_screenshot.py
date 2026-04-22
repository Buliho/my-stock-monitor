import asyncio
import os
from datetime import datetime
from playwright.async_api import async_playwright
import requests

# --- 你的設定 ---
URL = "https://www.wantgoo.com/futures/retail-indicator/wtm"
IMAGE_PATH = "micro_futures_retail_ratio.png"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1600, "height": 1200},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("🌐 正在開啟 Wantgoo 微台指散戶多空比頁面...")
        try:
            await page.goto(URL, wait_until="domcontentloaded", timeout=120000)
            await page.wait_for_load_state("load", timeout=90000)
            
            print("⏳ 等待圖表完全繪製...")
            await asyncio.sleep(12)  # 給予足夠時間讓圖表 Render
            
            print("📸 開始截取圖表...")
            await page.screenshot(path=IMAGE_PATH, full_page=False)
            print(f"✅ 截圖完成 -> {IMAGE_PATH}")
        except Exception as e:
            print(f"❌ 截圖過程發生錯誤: {e}")
        finally:
            await browser.close()

def send_to_telegram(image_path: str):
    # 建議直接在函式內獲取環境變數，確保抓取成功
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("❌ 未設定 Telegram Token 或 Chat ID")
        return

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    # 格式化時間，移除可能導致 Telegram API 解析錯誤的特殊字元
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    caption = f"📊 每日微台指散戶多空比\n⏰ 時間：{now_str}"

    try:
        with open(image_path, "rb") as f:
            files = {"photo": f}
            data = {
                "chat_id": chat_id, 
                "caption": caption
            }
            response = requests.post(url, data=data, files=files)

        if response.status_code == 200:
            print("✅ 已成功發送到 Telegram")
        else:
            print(f"❌ Telegram 發送失敗: {response.status_code}")
            # 強烈建議印出這行，這樣 400 錯誤時你才知道具體是哪裡不對（例如：Chat not found）
            print(f"🔍 錯誤原因: {response.text}")
            
    except Exception as e:
        print(f"❌ 發生異常: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    if os.path.exists(IMAGE_PATH):
        send_to_telegram(IMAGE_PATH)
