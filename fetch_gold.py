import json, urllib.request, datetime

URL = "https://api.gold-api.com/price/XAU"   # free, no key: gold price in USD per troy ounce
AED_PER_USD = 3.6725                          # AED is pegged to USD
GRAMS_PER_OZ = 31.1035

with urllib.request.urlopen(URL, timeout=30) as r:
    usd_oz = json.load(r)["price"]

g24 = usd_oz * AED_PER_USD / GRAMS_PER_OZ
entry = {
    "date": datetime.date.today().isoformat(),
    "usd_oz": round(usd_oz, 2),
    "k24": round(g24, 2),
    "k22": round(g24 * 22 / 24, 2),
    "k21": round(g24 * 21 / 24, 2),
    "k18": round(g24 * 18 / 24, 2),
}

with open("data.json") as f:
    data = json.load(f)
data = [d for d in data if d["date"] != entry["date"]] + [entry]
with open("data.json", "w") as f:
    json.dump(data[-365:], f, indent=1)
print(entry)
