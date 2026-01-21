import yfinance as yf
import requests
import pandas as pd

# 1. 設定你的 TOKEN
LINE_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')

# 2. 你的類 ETF 名單
stocks = ["LEU", "NVT", "GEV", "BWXT", "POWL", "VICR", "OKLO", "CCJ"]

def get_signals():
    buy_list = []
    sell_list = []
    
    for symbol in stocks:
        # 抓取最近 60 天的資料
        df = yf.download(symbol, period="60d", progress=False)
        if df.empty: continue
        
        # 計算技術指標
        close = df['Close']
        ma20 = close.rolling(window=20).mean() # 20日均線 (月線)
        
        # 計算 RSI (14天)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        curr_p = float(close.iloc[-1])
        curr_ma20 = float(ma20.iloc[-1])
        curr_rsi = float(rsi.iloc[-1])
        
        # --- 設定判斷邏輯 ---
        # 買進條件：回測到月線附近 且 RSI 不過高
        if curr_p <= curr_ma20 * 1.02 and curr_rsi < 50:
            buy_list.append(f"🟢 {symbol} 回檔至月線(RSI:{curr_rsi:.1f})")
            
        # 賣出/減碼條件：跌破月線 或 RSI 過熱(>75)
        elif curr_p < curr_ma20:
            sell_list.append(f"🔴 {symbol} 跌破月線(趨勢轉弱)")
        elif curr_rsi > 75:
            sell_list.append(f"🟡 {symbol} RSI過熱({curr_rsi:.1f}) 建議分批獲利")

    return buy_list, sell_list

def send_line(msg):
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'}
    payload = {'messages': [{'type': 'text', 'text': msg}]}
    requests.post(url, json=payload, headers=headers)

# 執行監控
buy, sell = get_signals()
if buy or sell:
    report = "【⚡電力核能監控報告】\n\n"
    if buy: report += "📈 潛在加碼點：\n" + "\n".join(buy) + "\n\n"
    if sell: report += "📉 建議減碼點：\n" + "\n".join(sell)
    send_line(report)
    print("報告已傳送！")
else:
    print("今日盤勢穩健，無觸發訊號。")
