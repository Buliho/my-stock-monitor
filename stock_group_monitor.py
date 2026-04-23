import yfinance as yf
import requests
import os

# --- 設定區 ---
LINE_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
# 定義族群與名單
GROUPS = {
    "類比IC車用": ["TXN", "STM", "ON"]
}

def send_line(msg):
    if not LINE_TOKEN: return
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": "Bearer " + LINE_TOKEN}
    requests.post(url, headers=headers, data={"message": msg})

def monitor():
    for group_name, tickers in GROUPS.items():
        # 抓取近期數據 (為了算5天漲幅，抓7天比較保險)
        data = yf.download(tickers, period="7d", interval="1d")['Close']
        
        # --- 邏輯 A: 五天內集體大漲 (盤後監控) ---
        # 計算 5 天前的漲幅 (這裡用最後一筆跟五天前那一筆比)
        lookback = 5
        pct_change_5d = (data.iloc[-1] / data.iloc[-lookback]) - 1
        
        all_hit_15pct = all(pct_change_5d >= 0.08)
        if all_hit_15pct:
            msg = f"\n🔥 族群爆發預警：{group_name}\n"
            msg += f"名單：{', '.join(tickers)}\n"
            msg += f"五日內集體漲幅超過 15%！"
            send_line(msg)

        # --- 邏輯 B: 盤中集體大漲 (即時監控) ---
        # 抓取今日即時數據
        live_data = yf.download(tickers, period="1d", interval="1m")
        if not live_data.empty:
            current_prices = live_data['Close'].iloc[-1]
            prev_closes = data.iloc[-2] # 昨日收盤
            pct_change_live = (current_prices / prev_closes) - 1
            
            all_hit_5pct = all(pct_change_live >= 0.05)
            if all_hit_5pct:
                msg = f"\n⚡ 盤中集體異動：{group_name}\n"
                msg += f"目前成員皆漲超過 5%！\n"
                for t in tickers:
                    msg += f"{t}: {pct_change_live[t]:.2%}\n"
                send_line(msg)

if __name__ == "__main__":
    monitor()
