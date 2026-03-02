import requests
from datetime import datetime

BASE = "https://api.binance.com/api/v3/klines"

# Binance: max 1000 candles per request, paginate via startTime/endTime
# Check earliest available 1m data for each pair
for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
    # get the very first candle
    r = requests.get(BASE, params={
        "symbol": sym, "interval": "1m", "limit": 1, "startTime": 0,
    }, timeout=15)
    data = r.json()
    if isinstance(data, list) and len(data) > 0:
        first_ts = data[0][0]
        print(f"{sym}: earliest 1m candle = {datetime.utcfromtimestamp(first_ts / 1000)}")
    else:
        print(f"{sym}: {data}")

    # get the latest
    r = requests.get(BASE, params={
        "symbol": sym, "interval": "1m", "limit": 1,
    }, timeout=15)
    data = r.json()
    if isinstance(data, list) and len(data) > 0:
        last_ts = data[0][0]
        print(f"  latest = {datetime.utcfromtimestamp(last_ts / 1000)}")

    # estimate total bars from 2018-01-01
    from_ts = int(datetime(2018, 1, 1).timestamp() * 1000)
    now_ts = int(datetime.utcnow().timestamp() * 1000)
    total_min = (now_ts - max(first_ts, from_ts)) / 60000
    reqs_needed = total_min / 1000
    print(f"  ~{total_min:,.0f} minute bars from 2018 ({reqs_needed:,.0f} API calls needed)")
    print()
