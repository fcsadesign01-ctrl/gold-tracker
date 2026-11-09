import json, os, sys, time, urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

SYMBOLS = ["VOO", "VXUS"]
OUT = "etf.json"
URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}?range=1mo&interval=1d"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
}


def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.load(r)
        except Exception as e:
            print(f"  attempt {i + 1} failed: {e}")
            time.sleep(3 * (i + 1))
    return None


def parse(data):
    res = data["chart"]["result"][0]
    meta = res["meta"]
    tz = ZoneInfo(meta.get("exchangeTimezoneName") or "America/New_York")
    closes = res["indicators"]["quote"][0]["close"]
    by_date = {}
    for ts, c in zip(res["timestamp"], closes):
        if c is None:
            continue
        d = datetime.fromtimestamp(ts, tz).strftime("%Y-%m-%d")
        by_date[d] = round(c, 4)
    rows = [{"date": d, "c": c} for d, c in sorted(by_date.items())]
    if len(rows) < 2:
        raise ValueError("not enough price history")
    price = meta.get("regularMarketPrice") or rows[-1]["c"]
    mtime = meta.get("regularMarketTime")
    if mtime:
        if datetime.fromtimestamp(mtime, tz).strftime("%Y-%m-%d") == rows[-1]["date"]:
            rows[-1]["c"] = round(price, 4)
    return {
        "price": round(price, 4),
        "prev": rows[-2]["c"],
        "market_time": datetime.fromtimestamp(mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if mtime else None,
        "history": rows[-10:],
    }


def main():
    old = {}
    if os.path.exists(OUT):
        try:
            old = json.load(open(OUT)).get("symbols", {})
        except Exception:
            pass
    out, ok = dict(old), 0
    for s in SYMBOLS:
        print("Fetching", s)
        data = get(URL.format(s))
        try:
            out[s] = parse(data)
            ok += 1
            print(f"  {s}: {out[s]['price']}")
        except Exception as e:
            print(f"  {s} FAILED: {e} (keeping previous data)")
    if ok == 0:
        print("All symbols failed")
        sys.exit(1)
    with open(OUT, "w") as f:
        json.dump({"symbols": out}, f, indent=1)


if __name__ == "__main__":
    main()
