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

def send_line(msg):
    token = os.getenv('LINE_TOKEN') # 從 Github Secrets 讀取
    if not token:
        print("Error: LINE_TOKEN not found")
        return
    
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": msg}
    requests.post(url, headers=headers, data=data)

if __name__ == "__main__":
    # 預設抓取華邦電 2344
    target_msg = get_margin_data("2344")
    print(target_msg)
    send_line(target_msg)
