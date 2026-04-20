# 修改 chart_pusher.py 傳送區塊
def get_retail_chart():
    # ... 前面的截圖代碼保持不變 ...
    
    token = os.getenv('LINE_ACCESS_TOKEN')
    if not token:
        print("❌ 錯誤：找不到 LINE_ACCESS_TOKEN")
        return

    print("📤 傳送至 LINE Notify...")
    notify_url = "https://notify-api.line.me/api/notify"
    
    # 確保 Token 前後的空格正確
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"message": "\n📊 微台指散戶多空比即時測試"}
    
    try:
        # 加入 timeout 避免無限等待，並讀取圖片
        with open("retail_chart.png", "rb") as f:
            files = {"imageFile": f}
            r = requests.post(notify_url, headers=headers, data=payload, files=files, timeout=30)
        
        if r.status_code == 200:
            print("✅ LINE 傳送成功！")
        else:
            print(f"❌ LINE 傳送失敗，狀態碼: {r.status_code}, 內容: {r.text}")
            
    except Exception as e:
        print(f"🔥 發送過程發生錯誤: {e}")
