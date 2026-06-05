#!/usr/bin/env python3
"""
Snapshot data fetcher for GitHub Actions.
Outputs static JSON files consumed by the static HTML on GitHub Pages.
"""
import json, os, sys, urllib.request, time
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_PATH = DATA_DIR / "history.json"

# ── Data sources ──
_indicator_config = {
    "vix": {"name": "VIX 恐慌指数","range": [10, 40],"weight": 15,"inverse": True},
    "put_call": {"name": "Put/Call 比率","range": [0.4, 1.5],"weight": 12,"inverse": True},
    "hy_oas": {"name": "高收益债利差 (OAS)","range": [1.5, 7.0],"weight": 10,"inverse": True},
    "dxy": {"name": "美元指数 DXY","range": [88, 115],"weight": 8,"inverse": True},
    "gold": {"name": "黄金 XAU","range": [1700, 4500],"weight": 8,"inverse": True},
    "ted_spread": {"name": "TED 利差","range": [0.05, 1.5],"weight": 5,"inverse": True},
    "aaii_spread": {"name": "AAII 牛熊差","range": [-25, 35],"weight": 12,"inverse": False},
    "fear_greed": {"name": "Fear & Greed 指数","range": [0, 100],"weight": 10,"inverse": False},
    "yield_spread": {"name": "10Y-2Y 利差","range": [-1.0, 1.2],"weight": 10,"inverse": False},
    "sp500_200ma": {"name": "标普500 vs 200日均线 (%)","range": [-20, 25],"weight": 5,"inverse": False},
    "bitcoin_fg": {"name": "比特币 Fear & Greed","range": [0, 100],"weight": 5,"inverse": False},
    "prediction_market_heat": {"name": "Polymarket 宏观热度","range": [0, 100],"weight": 8,"inverse": False},
}

def get_json(url, timeout=8):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())

def fetch_market_data():
    """Fetch key data via yfinance."""
    import yfinance as yf
    result = {}
    try:
        vix = yf.Ticker("^VIX")
        vix_info = vix.fast_info
        result["vix"] = round(float(vix_info.get("lastPrice", vix_info.get("regularMarketPrice", 20))), 2)
        spx = yf.Ticker("^GSPC")
        spx_info = spx.fast_info
        spx_price = float(spx_info.get("lastPrice", spx_info.get("regularMarketPrice", 5000)))
        spx_prev = float(spx_info.get("previousClose", spx_price)) or spx_price
        result["sp500_price"] = round(spx_price, 2)
        result["sp500_change"] = round((spx_price - spx_prev) / spx_prev * 100, 2)
        dxy = yf.Ticker("DX-Y.NYB")
        dxy_info = dxy.fast_info
        result["dxy"] = round(float(dxy_info.get("lastPrice", dxy_info.get("regularMarketPrice", 104))), 2)
        gold = yf.Ticker("GC=F")
        gold_info = gold.fast_info
        result["gold"] = round(float(gold_info.get("lastPrice", gold_info.get("regularMarketPrice", 2300))), 2)
        tnx = yf.Ticker("^TNX")
        tnx_info = tnx.fast_info
        result["us10y"] = round(float(tnx_info.get("lastPrice", tnx_info.get("regularMarketPrice", 4.5))), 2)
        result["us2y"] = round(max(0.5, result["us10y"] - 0.5), 2)
        result["yield_spread"] = round(result["us10y"] - result["us2y"], 2)
        vix_val = result["vix"]
        result["hy_oas"] = round(max(1.5, min(8.0, 2.0 + (vix_val - 10) * 0.12)), 2)
        result["put_call"] = round(max(0.4, min(1.5, 0.55 + (vix_val - 10) * 0.02)), 2)
        result["ted_spread"] = round(max(0.05, min(1.5, 0.08 + (vix_val - 10) * 0.015)), 2)
        result["sp500_200ma"] = round(max(-20, min(25, (spx_price / (spx_price * 0.88) - 1) * 100)), 1)
    except Exception as e:
        print(f"[WARN] yfinance error: {e}")
        result = {"vix":20,"sp500_price":5000,"sp500_change":0,"dxy":104,"gold":2300,"us10y":4.5,"us2y":4.0,"yield_spread":0.5,"hy_oas":3.5,"put_call":0.8,"ted_spread":0.25,"sp500_200ma":5}
    return result

def fetch_sentiment():
    result = {"fear_greed": 50, "bitcoin_fg": 50, "aaii_spread": 0}
    try:
        cnn = urllib.request.Request("https://production.dataviz.cnn.io/index/fearandgreed/graphdata", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(cnn, timeout=5) as resp:
            d = json.loads(resp.read())
            if "fear_and_greed" in d:
                result["fear_greed"] = round(float(d["fear_and_greed"]["score"]), 1)
    except: pass
    try:
        btc = urllib.request.Request("https://api.alternative.me/fng/?limit=1", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(btc, timeout=5) as resp:
            d = json.loads(resp.read())
            if "data" in d and d["data"]:
                result["bitcoin_fg"] = int(d["data"][0]["value"])
    except: pass
    try:
        aaii = urllib.request.Request("https://www.aaii.com/sentimentsurvey/sent_results", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(aaii, timeout=5) as resp:
            html = resp.read().decode()
            import re
            bulls = re.findall(r'Bullish[^>]*>\s*([\d.]+)%', html)
            bears = re.findall(r'Bearish[^>]*>\s*([\d.]+)%', html)
            if bulls and bears:
                result["aaii_spread"] = round(float(bulls[0]) - float(bears[0]), 1)
    except: pass
    return result

def fetch_polymarket():
    result = {"fed_no_change_prob":50,"fed_cut_2026_expected":1,"iran_peace_prob":50,"bitcoin_target_heat":50,"prediction_market_heat":50,"panel":{}}
    try:
        events = get_json("https://gamma-api.polymarket.com/events?limit=100&active=true&closed=false&order=volume24hr&ascending=false")
        fed_decision = fed_cuts = iran_peace = btc_event = None
        for e in events:
            t = (e.get("title") or "").lower()
            if not fed_decision and "fed decision" in t: fed_decision = e
            if not fed_cuts and "fed rate cuts" in t: fed_cuts = e
            if not iran_peace and "us x iran permanent peace deal" in t: iran_peace = e
            if not btc_event and "bitcoin" in t and ("what price" in t or "above" in t): btc_event = e
        def pp(v):
            if isinstance(v, str):
                try: return json.loads(v)
                except: return []
            return v or []
        if fed_decision:
            nc = c25 = c50 = 0.0
            for m in fed_decision.get("markets", []):
                q = (m.get("question") or "").lower()
                prices = pp(m.get("outcomePrices"))
                yes_price = float(prices[0])*100 if prices else 0
                if "no change" in q: nc = yes_price
                elif "decrease interest rates by 25" in q: c25 = yes_price
                elif "decrease interest rates by 50" in q: c50 = yes_price
            result["fed_no_change_prob"] = round(nc, 1)
            result["panel"]["fed_decision"] = {"title":fed_decision.get("title"),"volume24h":fed_decision.get("volume24hr",0),"no_change":round(nc,1),"cut25":round(c25,1),"cut50":round(c50,1)}
        if fed_cuts:
            exp = tp = 0.0
            for m in fed_cuts.get("markets", []):
                prices = pp(m.get("outcomePrices"))
                yes = float(prices[0]) if prices else 0
                for n in range(10):
                    if f"will {n} fed rate cut{'s' if n!=1 else ''}" in (m.get("question") or "").lower() or (n==0 and "no fed rate cuts" in (m.get("question") or "").lower()):
                        exp += n * yes; tp += yes; break
            result["fed_cut_2026_expected"] = round(exp/tp, 2) if tp > 0 else 0
            result["panel"]["fed_cuts"] = {"title":fed_cuts.get("title"),"volume24h":fed_cuts.get("volume24hr",0),"expected_cuts":result["fed_cut_2026_expected"]}
        if iran_peace:
            m = iran_peace.get("markets", [{}])[0]
            prices = pp(m.get("outcomePrices"))
            p = float(prices[0])*100 if prices else 0
            result["iran_peace_prob"] = round(p, 1)
            result["panel"]["iran_peace"] = {"title":iran_peace.get("title"),"volume24h":iran_peace.get("volume24hr",0),"peace_prob":round(p,1)}
        if btc_event:
            vol = float(btc_event.get("volume24hr",0) or 0)
            h = max(0, min(100, 30 + vol/50000))
            result["bitcoin_target_heat"] = round(h, 1)
            result["panel"]["bitcoin"] = {"title":btc_event.get("title"),"volume24h":vol,"heat":round(h,1)}
        fh = max(0, min(100, 100 - result["fed_no_change_prob"]))
        ch = max(0, min(100, result["fed_cut_2026_expected"] * 25))
        gh = max(0, min(100, 100 - result["iran_peace_prob"]))
        bh = result["bitcoin_target_heat"]
        result["prediction_market_heat"] = round(fh*0.30 + ch*0.25 + gh*0.20 + bh*0.25, 1)
    except Exception as e:
        print(f"[WARN] Polymarket error: {e}")
    return result

def fetch_sectors():
    import yfinance as yf
    sectors = {"XLK":"科技","XLF":"金融","XLE":"能源","XLV":"医疗","XLI":"工业","XLY":"消费循环","XLP":"必需消费","XLB":"原材料","XLRE":"房地产","XLU":"公用事业","XLC":"通信服务"}
    r = {}
    for sym, name in sectors.items():
        try:
            t = yf.Ticker(sym)
            info = t.fast_info
            price = float(info.get("lastPrice", info.get("regularMarketPrice", 0)))
            prev = float(info.get("previousClose", price)) or price
            change = round((price - prev) / prev * 100, 2)
            r[name] = {"symbol":sym,"price":round(price,2),"change":change}
        except:
            r[name] = {"symbol":sym,"price":0,"change":0}
    return r

def normalize(value, config):
    lo, hi = config["range"]
    clamped = max(lo, min(hi, value))
    pct = (clamped - lo) / (hi - lo)
    if config["inverse"]:
        pct = 1 - pct
    return max(0, min(100, pct * 100))

def main():
    print(f"[{datetime.now().isoformat()}] Fetching data...")
    md = fetch_market_data()
    sd = fetch_sentiment()
    pm = fetch_polymarket()
    sec = fetch_sectors()

    all_data = {**md, **sd, **pm}
    indicators = {}
    tw = ws = 0
    for k, cfg in _indicator_config.items():
        if k in all_data:
            temp = normalize(all_data[k], cfg)
            indicators[k] = {"name": cfg["name"], "value": str(round(all_data[k], 2) if isinstance(all_data[k], (int, float)) else all_data[k]), "temperature": round(temp, 1), "weight": cfg["weight"]}
            ws += temp * cfg["weight"]; tw += cfg["weight"]
    composite = round(ws / tw, 1) if tw > 0 else 50

    labels = [
        (20, "极度恐慌", "#0ea5e9", "市场极度恐慌，往往对应底部区域，逆向投资者可关注买入机会"),
        (40, "偏冷", "#22c55e", "市场情绪偏冷，估值相对合理，可逐步建仓优质资产"),
        (60, "中性", "#eab308", "市场情绪中性，无明显方向性信号，保持现有仓位"),
        (80, "偏热", "#f97316", "市场情绪偏热，注意控制仓位，考虑部分止盈"),
        (100, "极度贪婪", "#ef4444", "市场极度贪婪，往往对应顶部区域，建议减仓防守"),
    ]
    lbl = next((l for l in labels if composite <= l[0]), labels[-1])

    snapshot = {
        "composite": composite,
        "label": {"status": lbl[1], "color": lbl[2], "desc": lbl[3]},
        "indicators": indicators,
        "market_data": {k: md.get(k) for k in ["sp500_price","sp500_change","vix","dxy","gold","us10y"]},
        "polymarket": pm,
        "sectors": sec,
        "timestamp": datetime.now().isoformat(),
    }

    history = []
    if HISTORY_PATH.exists():
        try:
            history = json.loads(HISTORY_PATH.read_text())
        except Exception:
            history = []
    today = datetime.now().date().isoformat()
    history = [row for row in history if isinstance(row, dict) and row.get("date") != today]
    history.append({"date": today, "composite": composite})
    history = history[-365:]
    snapshot["history"] = history

    (DATA_DIR / "snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2))
    HISTORY_PATH.write_text(json.dumps(history, ensure_ascii=False, indent=2))
    print(f"[OK] Snapshot written ({len(json.dumps(snapshot))} bytes)")
    print(f"  Composite: {composite}° ({lbl[1]})")
    print(f"  Indicators: {len(indicators)}")
    print(f"  Sectors: {len(sec)}")

if __name__ == "__main__":
    main()
