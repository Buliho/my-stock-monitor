
import os
import requests
from datetime import datetime, timezone

# ============================================================
# CNN Fear & Greed Index
# GitHub Actions -> CNN -> LINE
# ============================================================

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")

CNN_URL = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"


def get_cnn_fear_greed():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0 Safari/537.36"
        ),
        "Referer": "https://edition.cnn.com/markets/fear-and-greed",
        "Accept": "application/json",
    }

    response = requests.get(
        CNN_URL,
        headers=headers,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    fg = data["fear_and_greed"]

    score = float(fg["score"])
    rating = fg["rating"]

    previous_close = float(fg["previous_close"])
    previous_week = float(fg["previous_1_week"])
    previous_month = float(fg["previous_1_month"])
    previous_year = float(fg["previous_1_year"])

    return {
        "score": score,
        "rating": rating,
        "previous_close": previous_close,
        "previous_week": previous_week,
        "previous_month": previous_month,
        "previous_year": previous_year,
        "timestamp": fg.get("timestamp", "")
    }


def get_signal(score):

    if score < 25:
        return "🟢 極度恐慌 → 歷史上偏向長線加碼區"
    elif score < 45:
        return "🟢 恐慌 → 可留意逢低機會"
    elif score < 55:
        return "⚪ 中性 → 市場情緒平衡"
    elif score < 75:
        return "🟡 貪婪 → 持股為主，避免追高"
    else:
        return "🔴 極度貪婪 → 注意過熱與回檔風險"


def get_emoji(score):

    if score < 25:
        return "😱"
    elif score < 45:
        return "😨"
    elif score < 55:
        return "😐"
    elif score < 75:
        return "🤑"
    else:
        return "🔥"


def send_line(message):

    if not LINE_ACCESS_TOKEN:
        raise ValueError("找不到 LINE_ACCESS_TOKEN")

    url = "https://api.line.me/v2/bot/message/broadcast"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }

    payload = {
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=15
    )

    response.raise_for_status()


# ============================================================
# Main
# ============================================================

try:

    fg = get_cnn_fear_greed()

    score = fg["score"]
    rating = fg["rating"]

    previous_close = fg["previous_close"]
    previous_week = fg["previous_week"]
    previous_month = fg["previous_month"]
    previous_year = fg["previous_year"]

    # 與上一交易日相比
    change_day = score - previous_close

    # 與一週前相比
    change_week = score - previous_week

    # 與一個月前相比
    change_month = score - previous_month

    emoji = get_emoji(score)
    signal = get_signal(score)

    today = datetime.now().strftime("%Y/%m/%d")

    message = f"""
{emoji} CNN Fear & Greed Index

📅 {today}

━━━━━━━━━━━━━━━━
📊 今日指數
━━━━━━━━━━━━━━━━

{score:.1f} / 100
{rating.upper()}

{signal}

━━━━━━━━━━━━━━━━
📈 與過去比較
━━━━━━━━━━━━━━━━

昨日：
{previous_close:.1f}  →  {change_day:+.1f}

一週前：
{previous_week:.1f}  →  {change_week:+.1f}

一個月前：
{previous_month:.1f}  →  {change_month:+.1f}

一年前：
{previous_year:.1f}

━━━━━━━━━━━━━━━━
📌 CNN 情緒區間
━━━━━━━━━━━━━━━━

0–24    😱 Extreme Fear
25–44   😨 Fear
45–55   😐 Neutral
56–75   🤑 Greed
76–100  🔥 Extreme Greed
"""

    print(message)

    send_line(message)

    print("CNN Fear & Greed 已成功傳送 LINE！")


except Exception as e:

    error_message = f"""
❌ CNN Fear & Greed 更新失敗

錯誤：
{str(e)}
"""

    print(error_message)

    # 發送錯誤通知
    try:
        send_line(error_message)
    except Exception as line_error:
        print("LINE 錯誤通知也失敗:", line_error)

