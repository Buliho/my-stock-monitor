import requests
from bs4 import BeautifulSoup
import os
import sys

def get_margin_data(stock_no):
    print(f"正在抓取股票代碼: {stock_no}...")
    url = f"https://histock.tw/stock/chips.aspx?no={stock_no}&m=mg"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"網頁回應狀態碼: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # 嘗試尋找表格
        table = soup.find('table', class_='gvSummary')
        if not table:
            print("警告：找不到 class 為 gvSummary 的表格")
            return None

        rows = table.find_all('tr')
        print(f"找到表格行數: {len(rows)}")

        if len(rows) < 2:
            print("警告：表格中沒有足夠的數據行")
            return None

        # 抓取第一行數據
        cols = rows[1].find_all('td')
        if len(cols) < 4:
            print(f"警告：資料列欄位不足 (僅有 {len(cols)} 欄)")
            return None
        
        date = cols[0].text.strip()
        margin_add = cols[1].text.strip()
        margin_balance = cols[2].text.strip()
        margin_usage = cols[3].text.strip()

        msg = f"\n【{stock_no} 融資監控】\n"
        msg += f"日期：{date}\n"
        msg += f"融資增加：{margin_add} 張\n"
        msg += f"融資餘額：{margin_balance} 張\n"
        msg += f"使用率：{margin_usage}%"
        
        print("成功解析數據內容！")
        return msg

    except Exception as e:
        print(f"發生異常錯誤: {str(e)}")
        return None

def send_line(msg):
    token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '').strip()
    if not token:
        print("錯誤：找不到 LINE_CHANNEL_ACCESS_TOKEN 密鑰")
        return
    
    print(f"準備發送 LINE 訊息，Token 長度: {len(token)}")
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = {
        'messages': [{'type': 'text', 'text': msg}]
    }
    
    res = requests.post(url, json=payload, headers=headers)
    print(f"LINE API 回應狀態碼: {res.status_code}")
    print(f"回應內容: {res.text}")

if __name__ == "__main__":
    result = get_margin_data("2344")
    if result:
        print(result)
        send_line(result)
    else:
        print("最終結果為空，不執行發送。")
