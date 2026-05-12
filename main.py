import os
import yfinance as yf
import requests
import pandas as pd
import pandas_ta as ta

# 2026/01/22
# Strategy: check MA20 and RSI, if price close to MA20 and RSI~50 --> Buy signal; if price<MA20 and RSI>75 --> Sell

# 1. 設定你的 TOKEN
LINE_ACCESS_TOKEN = os.getenv('LINE_ACCESS_TOKEN')

# 2. 你的類 ETF 名單
stocks = ["LEU", "NVT", "GEV", "BWXT", "POWL", "VICR", "OKLO", "CCJ","VRT","CRDO","ALAB","ASTS"]

tickers = ["LEU","OKLO","GEV","BWXT","UUUU","ASTS","HIMX"]

def get_signals():
    buy_list = []
    sell_list = []
    macd_details = [] # 建立儲存 MACD 狀態的清單
    
    for symbol in stocks:
        try:
            # 抓取最近 60 天的資料
            df = yf.download(symbol, period="60d", progress=False)
            if df.empty: continue
            
            # --- 修正 1：處理 yfinance 的多層索引 ---
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            close = df['Close']
            ma20 = close.rolling(window=20).mean() # 20日均線
            
            # 計算 RSI (14天)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # --- 修正 2：使用 .item() 獲取純數字，解決 TypeError ---
            curr_p = float(close.iloc[-1].item())
            curr_ma20 = float(ma20.iloc[-1].item())
            curr_rsi = float(rsi.iloc[-1].item())
            
            # 設定判斷邏輯
            if curr_p <= curr_ma20 * 1.02 and curr_rsi < 50:
                buy_list.append(f"🟢 {symbol} 回檔至月線(RSI:{curr_rsi:.1f})")
            elif curr_p < curr_ma20:
                sell_list.append(f"🔴 {symbol} 跌破月線(趨勢轉弱)")
            elif curr_rsi > 75:
                sell_list.append(f"🟡 {symbol} RSI過熱({curr_rsi:.1f}) 建議分批獲利")
                
            # --- MACD 計算邏輯 ---
            exp1 = close.ewm(span=12, adjust=False).mean()
            exp2 = close.ewm(span=26, adjust=False).mean()
            macd_line = exp1 - exp2
            signal_line = macd_line.ewm(span=9, adjust=False).mean()
            
            # --- 修正 3：MACD 取值也要補上 .item() ---
            last_macd = float(macd_line.iloc[-1].item())
            last_signal = float(signal_line.iloc[-1].item())
            prev_macd = float(macd_line.iloc[-2].item())
            prev_signal = float(signal_line.iloc[-2].item())
            
            if prev_macd < prev_signal and last_macd > last_signal:
                macd_status = "🚀 金叉 (趨勢轉強)"
            elif prev_macd > prev_signal and last_macd < last_signal:
                macd_status = "⚠️ 死叉 (趨勢轉弱)"
            else:
                macd_status = "多頭排列" if last_macd > last_signal else "空頭排列"
            
            macd_details.append(f"• {symbol}: {macd_status}")
            
        except Exception as e:
            print(f"處理 {symbol} 時發生錯誤: {e}")
            continue
            
    return buy_list, sell_list, macd_details




# ------------------------------------------------------------------------------------------------------
def get_stock_analysis_report(tickers):
    report = "\n📊 每日技術追蹤\n"
    
    for ticker in tickers:
        try:
            # 抓取資料
            df = yf.download(ticker, period="6mo", interval="1d", progress=False)
            if df.empty: continue
            
            # 修正 1：處理 yfinance 的多層索引 (Multi-Index)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            close_price = df['Close'].dropna()
            rsi_series = ta.rsi(close_price, length=14)
            macd_df = ta.macd(close_price, fast=12, slow=26, signal=9)
            # macd_df is a Dataframe, like
            # Date (索引)	MACD_12_26_9 (快線)	MACDs_12_26_9 (訊號線)	MACDh_12_26_9 (柱狀圖)
            # 2026-01-21	10.55	9.80	0.75
            # 2026-01-22	10.68	9.95	0.73
            # 2026-01-23	10.74	10.10	0.64
            
            # 修正 2：使用 .iloc[-1].item() 確保提取的是「純純的數字」
            # 這能解決 image_4597cc.png 中顯示的 TypeError
            latest_p = float(close_price.iloc[-1].item())
            latest_rsi = float(rsi_series.iloc[-1].item())
            
            # 獲取 MACD 柱狀圖 (通常是第三個欄位)
            h_now = float(macd_df.iloc[-1, 2].item())
            h_prev = float(macd_df.iloc[-2, 2].item())
            
            # 判斷趨勢燈號, histogram >0
            if h_now > 0:
                trend = "🟢強勢" if h_now > h_prev else "🟡衰竭"
            else:
                trend = "⚪反彈" if h_now > h_prev else "🔴殺盤"
            
            report += f"\n【{ticker}】 ${latest_p:.2f}\n"
            report += f"指標: RSI {latest_rsi:.1f} | MACD {trend}\n"
            
            # 交叉訊號判定 (同樣使用 .item())
            m_now, s_now = macd_df.iloc[-1, 0].item(), macd_df.iloc[-1, 1].item()
            m_prev, s_prev = macd_df.iloc[-2, 0].item(), macd_df.iloc[-2, 1].item()
            
            if m_now > s_now and m_prev < s_prev:
                report += "🚀 訊號: 出現黃金交叉！\n"
            elif m_now < s_now and m_prev > s_prev:
                report += "⚠️ 警示: 出現死亡交叉！\n"
                
        except Exception as e:
            report += f"\n【{ticker}】 分析失敗: {str(e)}\n"
            
    return report
# ------------------------------------------------------------------------------------------------------
def send_line(msg):
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'}
    payload = {'messages': [{'type': 'text', 'text': msg}]}
    requests.post(url, json=payload, headers=headers)

# 執行監控
buy, sell, macd_list = get_signals()
if buy or sell:
    report = "【⚡電力核能監控報告】\n\n"
    if buy: report += "📈 潛在加碼點：\n" + "\n".join(buy) + "\n\n"
    if sell: report += "📉 建議減碼點：\n" + "\n".join(sell)
    send_line(report)
    print("報告已傳送！")
else:
    print("今日盤勢穩健，無觸發訊號。")
    
# 第二個通知：MACD 趨勢報告 (無論有無買賣點都發送)
macd_report = "📊 MACD 全球趨勢追蹤：\n\n" + "\n".join(macd_list)
send_line(macd_report)
print("MACD 趨勢報告已傳送！")

# 第三個通知：VOL/MACD/RSI 相關資訊
msg = get_stock_analysis_report(tickers)
send_line(msg)

