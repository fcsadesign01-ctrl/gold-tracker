import json, urllib.request, datetime

GOLD_URL = "https://api.gold-api.com/price/XAU"      # gold, USD per troy ounce (no key)
FX_URL = "https://open.er-api.com/v6/latest/AED"     # AED -> PHP and other currencies (no key)
AED_PER_USD = 3.6725                                  # AED is pegged to USD
GRAMS_PER_OZ = 31.1035

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "gold-tracker"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

usd_oz = get(GOLD_URL)["price"]
g24 = usd_oz * AED_PER_USD / GRAMS_PER_OZ
today = datetime.date.today().isoformat()
entry = {
    "date": today,
    "usd_oz": round(usd_oz, 2),
    "k24": round(g24, 2),
    "k22": round(g24 * 22 / 24, 2),
    "k21": round(g24 * 21 / 24, 2),
    "k18": round(g24 * 18 / 24, 2),
}

# AED -> PHP: optional, so a currency hiccup never stops the gold price from saving
try:
    entry["php"] = round(get(FX_URL)["rates"]["PHP"], 4)
except Exception as e:
    print("FX fetch failed:", e)

with open("data.json") as f:
    data = json.load(f)
old = next((d for d in data if d["date"] == today), {})
if "php" not in entry and "php" in old:
    entry["php"] = old["php"]
data = [d for d in data if d["date"] != today] + [entry]
with open("data.json", "w") as f:
    json.dump(data[-365:], f, indent=1)
print(entry)
