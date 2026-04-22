import asyncio
import os
import requests
from datetime import datetime
from playwright.async_api import async_playwright

# --- 設定區 ---
URL = "https://www.wantgoo.com/futures/retail-indicator/wtm"
IMAGE_PATH = "micro_futures_retail_ratio.png"

async def main():
    async with async_playwright() as p:
        # 啟動瀏覽器
        browser = await p.chromium.launch(headless=True)
        
        # 深度偽裝 Context
        context = await browser.new_context(
            viewport={"width": 1280, "height": 1000},
            # 使用更現代、更像真人的 User-Agent
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="zh-TW",
            timezone_id="Asia/Taipei"
        )
        
        page = await context.new_page()

        try:
            print("🌐 正在執行真人偽裝存取策略...")
            # 策略：先去首頁，模擬一般人的進站流程，有助於通過 Cloudflare 檢查
            await page.goto("https://www.wantgoo.com", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(3) 

            print(f"🚀 前往目標頁面: {URL}")
            # 前往目標頁面並等待網路活動停止
            await page.goto(URL, wait_until="networkidle", timeout=120000)
            
            # 檢查是否不幸還是撞到驗證牆
            content = await page.content()
            if "Performing security verification" in content or "Cloudflare" in content:
                print("⚠️ 偵測到驗證牆，嘗試強制等待 20 秒...")
                await asyncio.sleep(20)
            else:
                # 正常情況下，多等 10 秒讓 TradingView 圖表完全渲染
                print("⏳ 圖表繪製中，請稍候...")
                await asyncio.sleep(12)

            print("📸 執行截圖...")
            # 針對圖表區域截圖，若不確定位置可用全頁截圖或維持現狀
            await page.screenshot(path=IMAGE_PATH)
            print(f"✅ 截圖完成 -> {IMAGE_PATH}")

        except Exception as e:
            print(f"❌ 執行過程發生錯誤: {e}")
        finally:
            await browser.close()

def send_to_telegram(image_path: str):
    # 從 GitHub Actions Secrets 讀取
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("❌ 錯誤：找不到 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID 環境變數")
        return

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    # 準備發送時間
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    caption = f"📊 <b>每日微台指散戶多空比</b>\n⏰ 時間：{now_str}"

    try:
        with open(image_path, "rb") as f:
            files = {"photo": f}
            data = {
                "chat_id": chat_id,
                "caption": caption,
                "parse_mode": "HTML" # 使用 HTML 格式讓標題變粗體
            }
            response = requests.post(url, data=data, files=files)

        if response.status_code == 200:
            print("✅ 已成功發送到 Telegram！")
        else:
            print(f"❌ Telegram 發送失敗：{response.status_code}")
            print(f"🔍 原始錯誤訊息：{response.text}")
            
    except Exception as e:
        print(f"❌ 發送過程發生異常：{e}")

if __name__ == "__main__":
    # 執行主程式
    asyncio.run(main())
    
    # 檢查截圖檔案是否存在，存在才發送
    if os.path.exists(IMAGE_PATH):
        send_to_telegram(IMAGE_PATH)
    else:
        print("❌ 找不到截圖檔案，無法發送通知。")
