async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 1200},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            print(f"🚀 前往 M平方 目標頁面...")
            
            # 修改點 1：將 wait_until 改為 "domcontentloaded" (只要 HTML 下載完就開始下一步)
            # 這是繞過 Timeout 的關鍵，不強求所有廣告或追蹤腳本載入完畢
            await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            
            print("⏳ 頁面基礎結構已加載，等待圖表渲染...")
            # 修改點 2：手動強制等待 20 秒，給予 Highcharts 圖表足夠的繪製時間
            await asyncio.sleep(20) 

            # 修改點 3：嘗試移除可能擋在最上層的透明遮罩或彈窗
            await page.evaluate("""
                () => {
                    const selectors = ['.stat-close', '.modal-backdrop', '.modal'];
                    selectors.forEach(s => document.querySelector(s)?.remove());
                }
            """)

            print("📸 執行截圖...")
            # 針對特定的圖表 ID 截圖，M平方這張圖通常在 #chart-canvas 或類似容器
            chart = await page.query_selector("#chart-wrapper") or await page.query_selector(".chart-container")
            if chart:
                await chart.screenshot(path=IMAGE_PATH)
            else:
                await page.screenshot(path=IMAGE_PATH)
                
            print(f"✅ 截圖完成 -> {IMAGE_PATH}")

        except Exception as e:
            print(f"❌ 執行過程發生錯誤: {e}")
            # 報錯時也強行截一張圖，方便我們從 Telegram 看到到底卡在哪個畫面
            await page.screenshot(path="error_debug.png")
            send_to_telegram("error_debug.png", caption="⚠️ 報錯時的畫面截圖")
        finally:
            await browser.close()
