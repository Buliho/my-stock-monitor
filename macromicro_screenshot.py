import asyncio
import os
import requests
from datetime import datetime
from playwright.async_api import async_playwright

# --- 設定區 ---
URL = "https://www.macromicro.me/charts/110457/tw-tmf-long-to-short-ratio-of-individual-player"
IMAGE_PATH = "macromicro_retail_ratio.png"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # 模擬真人瀏覽器環境
        context = await browser.new_context(
            viewport={"width": 1280, "height": 1200}, # M平方圖表較長，高度設大一點
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="zh-TW"
        )
        
        page = await context.new_page()

        try:
            print(f"🚀 正在前往 M平方 頁面: {URL}")
            # M平方有時候會偵測 referrer，先去首頁轉跳
            await page.goto("https://www.macromicro.me", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(2)
            
            # 前往目標圖表
            await page.goto(URL, wait_until="networkidle", timeout=120000)
            
            print("⏳ 等待圖表動畫與數據載入...")
            # M平方的圖表是用 Highcharts 繪製，有進場動畫，建議多等一下
            await asyncio.sleep(15) 
            
            # 嘗試移除可能擋住圖表的彈出視窗（如廣告或 Cookie 聲明）
            try:
                await page.evaluate("document.querySelector('.stat-close')?.click()")
            except:
                pass

            print("📸 執行截圖...")
            # 針對主要圖表區域截圖，或是全頁截圖後手動調整
            # M平方的圖表容器通常是 .chart-container 或 #chart-wrapper
            chart_element = await page.query_selector(".chart-container")
            if chart_element:
                await chart_element.screenshot(path=IMAGE_PATH)
            else:
                await page.screenshot(path=IMAGE_PATH)
                
            print(f"✅ 截圖完成 -> {IMAGE_PATH}")

        except Exception as e:
            print(f"❌ 執行過程發生錯誤: {e}")
        finally:
            await browser.close()

def send_to_telegram(image_path: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("❌ 錯誤：找不到 Telegram 環境變數")
        return

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    caption = f"📊 <b>微台指散戶多空比 (財經M平方)</b>\n⏰ 時間：{now_str}"

    try:
        with open(image_path, "rb") as f:
            files = {"photo": f}
            data = {
                "chat_id": chat_id,
                "caption": caption,
                "parse_mode": "HTML"
            }
            response = requests.post(url, data=data, files=files)

        if response.status_code == 200:
            print("✅ 已成功發送到 Telegram！")
        else:
            print(f"❌ Telegram 發送失敗：{response.text}")
            
    except Exception as e:
        print(f"❌ 發送過程發生異常：{e}")

if __name__ == "__main__":
    asyncio.run(main())
    if os.path.exists(IMAGE_PATH):
        send_to_telegram(IMAGE_PATH)
    else:
        print("❌ 找不到截圖檔案，無法發送通知。")
