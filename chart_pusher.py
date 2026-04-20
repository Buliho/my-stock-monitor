import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def send_to_line(image_path):
    token = os.getenv('LINE_ACCESS_TOKEN')
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"message": "\n📊 微台指散戶多空比即時測試"}
    
    # 建立重試機制，對抗暫時性的 DNS 錯誤
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    try:
        with open(image_path, "rb") as f:
            files = {"imageFile": f}
            # 增加 timeout 並執行發送
            r = session.post(url, headers=headers, params=payload, files=files, timeout=30)
        
        if r.status_code == 200:
            print("✅ LINE 傳送成功！")
        else:
            print(f"❌ LINE 傳送失敗，狀態碼: {r.status_code}, 內容: {r.text}")
    except Exception as e:
        print(f"🔥 連線失敗: {e}")
