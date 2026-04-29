import requests
from bs4 import BeautifulSoup
import os

def get_margin_data(stock_no):
    url = f"https://histock.tw/stock/chips.aspx?no={stock_no}&m=mg"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 找到表格中第一行數據 (排除表頭)
        table = soup.find('table', class_='gvSummary')
        if not table:
            return "找不到數據表格"

        rows = table.find_all('tr')
        if len(rows) < 2:
            return "數據尚未更新"

        # 第一列通常是最新日期
        cols = rows[1].find_all('td')
        
        date = cols[0].text.strip()           # 日期
        margin_add = cols[1].text.strip()      # 融資增加
        margin_balance = cols[2].text.strip()  # 融資餘額
        margin_usage = cols[3].text.strip()    # 融資使用率%

        msg = f"\n【{stock_no} 融資監控】\n"
        msg += f"日期：{date}\n"
        msg += f"融資增加：{margin_add} 張\n"
        msg += f"融資餘額：{margin_balance} 張\n"
        msg += f"使用率：{margin_usage}%"
        
        return msg

    except Exception as e:
        return f"爬取失敗: {str(e)}"

#--------------------------------------------------------------------

def send_line(msg):
    # 讀取原本的 Secrets 名稱
    token = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '').strip()
    if not token:
        print("Error: LINE_CHANNEL_ACCESS_TOKEN not found")
        return
    
    # 使用 Messaging API 的 Broadcast 網址
    url = 'https://api.line.me/v2/bot/message/broadcast'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    # 符合 Messaging API 規範的 JSON 格式
    payload = {
        'messages': [
            {
                'type': 'text',
                'text': msg
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("LINE 訊息發送成功")
        else:
            print(f"LINE 發送失敗，狀態碼：{response.status_code}, 原因：{response.text}")
        return response
    except Exception as e:
        print(f"發送過程發生錯誤: {e}")
