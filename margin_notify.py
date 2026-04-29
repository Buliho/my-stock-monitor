import requests
from bs4 import BeautifulSoup
import os

def get_margin_data(stock_no):
    print(f"正在抓取股票代碼: {stock_no}...")
    url = f"https://histock.tw/stock/chips.aspx?no={stock_no}&m=mg"
    
    # 模擬更真實的瀏覽器標頭，加入 Referer 避開簡單的擋爬
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://histock.tw/"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找尋包含 '日期' 與 '融資' 字眼的表格，這種方法比找 Class 更穩健
        target_table = None
        tables = soup.find_all('table')
        for t in tables:
            if '融資' in t.text and '日期' in t.text:
                target_table = t
                break

        if not target_table:
            print("無法透過內容定位表格，嘗試直接抓取第一個數據表...")
            target_table = soup.find('table', class_='gvSummary')

        if not target_table:
            print("錯誤：完全找不到數據表格。")
            return None

        rows = target_table.find_all('tr')
        # 尋找第一行含有數字的數據列 (跳過表頭)
        data_row = None
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4 and cols[0].text.strip().replace('/', '').isdigit():
                data_row = cols
                break

        if not data_row:
            print("錯誤：找不到有效的數據行。")
            return None

        date = data_row[0].text.strip()
        margin_add = data_row[1].text.strip()
        margin_balance = data_row[2].text.strip()
        margin_usage = data_row[3].text.strip()

        msg = f"\n【{stock_no} 融資監控】\n"
        msg += f"日期：{date}\n"
        msg += f"融資增加：{margin_add} 張\n"
        msg += f"融資餘額：{margin_balance} 張\n"
        msg += f"使用率：{margin_usage}%"
        
        return msg

    except Exception as e:
        print(f"解析過程出錯: {str(e)}")
        return None

def send_line(msg):
    token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '').strip()
    if not token:
        print("未偵測到 LINE_CHANNEL_ACCESS_TOKEN")
        return
    
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = {'messages': [{'type': 'text', 'text': msg}]}
    
    res = requests.post(url, json=payload, headers=headers)
    print(f"LINE 回應狀態碼: {res.status_code}")

if __name__ == "__main__":
    content = get_margin_data("2344")
    if content:
        print(content)
        send_line(content)
    else:
        print("失敗，未發送訊息。")
