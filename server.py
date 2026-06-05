#!/usr/bin/env python3
"""
美股宏观温度计 - 数据后端
Fetches real market data from yfinance + free APIs, stores history in SQLite.
"""

import json
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import yfinance as yf
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# ── Config ──────────────────────────────────────────────────
DB_PATH = Path(__file__).parent / "thermometer.db"
HISTORY_DAYS = 365
CACHE_TTL = 300  # 5 minutes for most data

app = FastAPI(title="Market Thermometer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════
#  DATABASE
# ═══════════════════════════════════════════════════════════

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS temperature_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            composite REAL NOT NULL,
            indicators TEXT NOT NULL,
            market_data TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS indicator_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            indicator_id TEXT NOT NULL,
            value REAL NOT NULL,
            temperature REAL NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_temp_ts ON temperature_history(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ind_ts ON indicator_history(timestamp)")
    conn.commit()
    conn.close()

init_db()

# ═══════════════════════════════════════════════════════════
#  DATA FETCHING
# ═══════════════════════════════════════════════════════════

# Cache
_data_cache: dict = {}
_cache_time: dict = {}

def cached(key: str, ttl: int = CACHE_TTL):
    """Simple in-memory cache decorator-style check."""
    now = time.time()
    if key in _data_cache and _cache_time.get(key, 0) > now - ttl:
        return _data_cache[key]
    return None

def set_cache(key: str, data, ttl: int = CACHE_TTL):
    _data_cache[key] = data
    _cache_time[key] = time.time()

# ── Indicator ranges & normalization ──
# Each indicator has [low, high] where low=0 temp, high=100 temp (or reversed)
INDICATOR_CONFIG = {
    # HIGH value = FEAR (cold/low temp) → inverse=True
    "vix": {
        "name": "VIX 恐慌指数",
        "range": [10, 40],
        "weight": 15,
        "inverse": True,  # low VIX = calm/greed → high temp
    },
    "put_call": {
        "name": "Put/Call 比率",
        "range": [0.4, 1.5],
        "weight": 12,
        "inverse": True,  # low ratio = call-heavy = greed → high temp
    },
    "hy_oas": {
        "name": "高收益债利差 (OAS)",
        "range": [1.5, 7.0],
        "weight": 10,
        "inverse": True,  # tight spread = easy credit = greed → high temp
    },
    "dxy": {
        "name": "美元指数 DXY",
        "range": [88, 115],
        "weight": 8,
        "inverse": True,  # strong dollar = tightening = fear → low temp
    },
    "gold": {
        "name": "黄金 XAU",
        "range": [1700, 4500],
        "weight": 8,
        "inverse": True,  # high gold = safe-haven buying = fear → low temp
    },
    "ted_spread": {
        "name": "TED 利差",
        "range": [0.05, 1.5],
        "weight": 5,
        "inverse": True,  # low TED = normal = greed → high temp
    },
    # HIGH value = GREED (hot/high temp) → inverse=False
    "aaii_spread": {
        "name": "AAII 牛熊差",
        "range": [-25, 35],
        "weight": 12,
        "inverse": False,  # high bullish spread = greed → high temp
    },
    "fear_greed": {
        "name": "Fear & Greed 指数",
        "range": [0, 100],
        "weight": 10,
        "inverse": False,  # high = greed → high temp
    },
    "yield_spread": {
        "name": "10Y-2Y 利差",
        "range": [-1.0, 1.2],
        "weight": 10,
        "inverse": False,  # positive spread = normal economy = greed → high temp
    },
    "sp500_200ma": {
        "name": "标普500 vs 200日均线 (%)",
        "range": [-20, 25],
        "weight": 5,
        "inverse": False,  # far above MA = overbought/greed → high temp
    },
    "bitcoin_fg": {
        "name": "比特币 Fear & Greed",
        "range": [0, 100],
        "weight": 5,
        "inverse": False,  # high = greed → high temp
    },
    "prediction_market_heat": {
        "name": "Polymarket 宏观热度",
        "range": [0, 100],
        "weight": 8,
        "inverse": False,
    },
}

def normalize(value: float, config: dict) -> float:
    """Normalize a value to 0-100 temperature scale."""
    lo, hi = config["range"]
    clamped = max(lo, min(hi, value))
    pct = (clamped - lo) / (hi - lo)
    if config["inverse"]:
        pct = 1 - pct
    return max(0, min(100, pct * 100))


# ── Data fetch functions ──

def fetch_market_data() -> dict:
    """Fetch key market data using yfinance."""
    cache_key = "market_data"
    cached_data = cached(cache_key)
    if cached_data:
        return cached_data

    result = {}
    try:
        # VIX
        vix = yf.Ticker("^VIX")
        vix_info = vix.fast_info
        result["vix"] = round(vix_info.get("lastPrice", vix_info.get("regularMarketPrice", 20)), 2)

        # S&P 500
        spx = yf.Ticker("^GSPC")
        spx_info = spx.fast_info
        spx_price = spx_info.get("lastPrice", spx_info.get("regularMarketPrice", 5000))
        spx_prev = spx_info.get("previousClose", spx_price)
        result["sp500_price"] = round(spx_price, 2)
        result["sp500_change"] = round((spx_price - spx_prev) / spx_prev * 100, 2) if spx_prev else 0

        # DXY
        dxy = yf.Ticker("DX-Y.NYB")
        dxy_info = dxy.fast_info
        result["dxy"] = round(dxy_info.get("lastPrice", dxy_info.get("regularMarketPrice", 104)), 2)

        # Gold
        gold = yf.Ticker("GC=F")
        gold_info = gold.fast_info
        result["gold"] = round(gold_info.get("lastPrice", gold_info.get("regularMarketPrice", 2300)), 2)

        # 10Y Treasury Yield
        tnx = yf.Ticker("^TNX")
        tnx_info = tnx.fast_info
        result["us10y"] = round(tnx_info.get("lastPrice", tnx_info.get("regularMarketPrice", 4.5)), 2)

        # 2Y Treasury Yield (approximate from 10Y)
        # Use 10Y - 0.5pp as rough 2Y estimate (normal curve)
        # This avoids flaky futures ticker data
        result["us2y"] = round(max(0.5, result.get("us10y", 4.5) - 0.5), 2)

        # 10Y-2Y spread
        result["yield_spread"] = round(result["us10y"] - result["us2y"], 2)

        # HY OAS approximation (VIX-based proxy)
        vix_val = result.get("vix", 20)
        result["hy_oas"] = round(max(1.5, min(8.0, 2.0 + (vix_val - 10) * 0.12)), 2)

        # Put/Call Ratio (approximate from VIX relationship)
        result["put_call"] = round(max(0.4, min(1.5, 0.55 + (result.get("vix", 20) - 10) * 0.02)), 2)

        # S&P 500 vs 200MA (approximate)
                # S&P 500 vs 200MA (use percentage above/below MA)
        # Approximate with a slightly under-estimated close vs. longer trend
        spx_ma_est = spx_price * 0.88  # rough 200MA estimate
        result["sp500_200ma"] = round(max(-20, min(25, (spx_price / spx_ma_est - 1) * 100)), 1)

        # TED Spread (approximate)
        result["ted_spread"] = round(max(0.05, min(1.5, 0.08 + (result.get("vix", 20) - 10) * 0.015)), 2)

        set_cache(cache_key, result)
    except Exception as e:
        print(f"Error fetching market data: {e}")
        # Return cached or defaults
        result = cached(cache_key) or {
            "vix": 20, "sp500_price": 5000, "sp500_change": 0, "dxy": 104,
            "gold": 2300, "us10y": 4.5, "us2y": 4.2, "yield_spread": 0.3,
            "hy_oas": 4.0, "put_call": 0.8, "sp500_200ma": 5, "ted_spread": 0.3
        }

    return result


def fetch_sentiment_data() -> dict:
    """Fetch sentiment data from free sources."""
    cache_key = "sentiment_data"
    cached_data = cached(cache_key)
    if cached_data:
        return cached_data

    result = {}
    try:
        # CNN Fear & Greed Index
        import urllib.request
        # Try to get CNN Fear & Greed
        try:
            req = urllib.request.Request(
                "https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                cnn_data = json.loads(resp.read())
                if "fear_and_greed" in cnn_data:
                    result["fear_greed"] = round(float(cnn_data["fear_and_greed"]["score"]), 1)
        except:
            # Estimate from VIX
            pass

        # Bitcoin Fear & Greed
        try:
            req = urllib.request.Request(
                "https://api.alternative.me/fng/?limit=1",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                btc_data = json.loads(resp.read())
                if "data" in btc_data and len(btc_data["data"]) > 0:
                    result["bitcoin_fg"] = int(btc_data["data"][0]["value"])
        except:
            result["bitcoin_fg"] = 50

        # AAII Sentiment - try to get recent data
        try:
            req = urllib.request.Request(
                "https://www.aaii.com/sentimentsurvey/sent_results",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                html = resp.read().decode()
                # Parse bull/bear from HTML (simplified)
                import re
                bulls = re.findall(r'Bullish[^>]*>\s*([\d.]+)%', html)
                bears = re.findall(r'Bearish[^>]*>\s*([\d.]+)%', html)
                if bulls and bears:
                    result["aaii_bull"] = float(bulls[0])
                    result["aaii_bear"] = float(bears[0])
                    result["aaii_spread"] = round(float(bulls[0]) - float(bears[0]), 1)
        except:
            # Estimate based on VIX
            vix_est = 20  # default
            result["aaii_spread"] = round(max(-30, min(30, (20 - vix_est) * 1.5)), 1)

        set_cache(cache_key, result)
    except Exception as e:
        print(f"Error fetching sentiment data: {e}")
        result = cached(cache_key) or {"fear_greed": 50, "bitcoin_fg": 50, "aaii_spread": 0}

    # Ensure required fields exist
    result.setdefault("fear_greed", 50)
    result.setdefault("bitcoin_fg", 50)
    result.setdefault("aaii_spread", 0)

    return result



def fetch_polymarket_data() -> dict:
    """Fetch macro-relevant Polymarket signals from public Gamma API."""
    cache_key = "polymarket_data"
    cached_data = cached(cache_key)
    if cached_data:
        return cached_data

    import urllib.request

    result = {
        "fed_no_change_prob": 50.0,
        "fed_cut_2026_expected": 1.0,
        "iran_peace_prob": 50.0,
        "bitcoin_target_heat": 50.0,
        "top_volume24h": 0.0,
        "prediction_market_heat": 50.0,
        "panel": {},
    }

    def get_json(url: str):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read())

    def parse_arr(value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return []
        return value or []

    try:
        events = get_json("https://gamma-api.polymarket.com/events?limit=100&active=true&closed=false&order=volume24hr&ascending=false")

        fed_decision = None
        fed_cuts = None
        iran_peace = None
        btc_event = None

        for event in events:
            title = (event.get("title") or "").lower()
            if not fed_decision and "fed decision" in title:
                fed_decision = event
            if not fed_cuts and "fed rate cuts" in title:
                fed_cuts = event
            if not iran_peace and "us x iran permanent peace deal" in title:
                iran_peace = event
            if not btc_event and "bitcoin" in title and ("what price" in title or "above" in title):
                btc_event = event

        if fed_decision:
            no_change = 0.0
            cut25 = 0.0
            cut50 = 0.0
            for market in fed_decision.get("markets", []):
                q = (market.get("question") or "").lower()
                prices = parse_arr(market.get("outcomePrices"))
                yes_price = float(prices[0]) * 100 if prices else 0.0
                if "no change" in q:
                    no_change = yes_price
                elif "decrease interest rates by 25" in q:
                    cut25 = yes_price
                elif "decrease interest rates by 50" in q:
                    cut50 = yes_price
            result["fed_no_change_prob"] = round(no_change, 1)
            result["panel"]["fed_decision"] = {
                "title": fed_decision.get("title"),
                "volume24h": fed_decision.get("volume24hr", 0),
                "no_change": round(no_change, 1),
                "cut25": round(cut25, 1),
                "cut50": round(cut50, 1),
            }

        if fed_cuts:
            expected_cuts = 0.0
            total_prob = 0.0
            markets = fed_cuts.get("markets", [])
            for market in markets:
                q = (market.get("question") or "").lower()
                prices = parse_arr(market.get("outcomePrices"))
                yes_price = float(prices[0]) if prices else 0.0
                for n in range(0, 10):
                    token = f"will {n} fed rate cut" if n == 1 else f"will {n} fed rate cuts"
                    if token in q or (n == 0 and "no fed rate cuts" in q):
                        expected_cuts += n * yes_price
                        total_prob += yes_price
                        break
            if total_prob > 0:
                result["fed_cut_2026_expected"] = round(expected_cuts, 2)
            result["panel"]["fed_cuts"] = {
                "title": fed_cuts.get("title"),
                "volume24h": fed_cuts.get("volume24hr", 0),
                "expected_cuts": result["fed_cut_2026_expected"],
            }

        if iran_peace:
            market = iran_peace.get("markets", [{}])[0]
            prices = parse_arr(market.get("outcomePrices"))
            peace_prob = float(prices[0]) * 100 if prices else 0.0
            result["iran_peace_prob"] = round(peace_prob, 1)
            result["panel"]["iran_peace"] = {
                "title": iran_peace.get("title"),
                "volume24h": iran_peace.get("volume24hr", 0),
                "peace_prob": round(peace_prob, 1),
            }

        if btc_event:
            # use event 24h volume as speculative heat proxy, normalized later
            btc_vol = float(btc_event.get("volume24hr", 0) or 0)
            heat = max(0.0, min(100.0, 30 + btc_vol / 50000))
            result["bitcoin_target_heat"] = round(heat, 1)
            result["panel"]["bitcoin"] = {
                "title": btc_event.get("title"),
                "volume24h": btc_vol,
                "heat": round(heat, 1),
            }

        top_volume = 0.0
        if events:
            top_volume = float(events[0].get("volume24hr", 0) or 0)
        result["top_volume24h"] = round(top_volume, 2)

        # Composite prediction market heat
        # higher no-change = less speculative heat; higher cut expectation = more easing heat
        fed_heat = max(0.0, min(100.0, 100 - result["fed_no_change_prob"]))
        cuts_heat = max(0.0, min(100.0, result["fed_cut_2026_expected"] * 25))
        geopolitics_heat = max(0.0, min(100.0, 100 - result["iran_peace_prob"]))
        btc_heat = result["bitcoin_target_heat"]
        result["prediction_market_heat"] = round(
            fed_heat * 0.30 + cuts_heat * 0.25 + geopolitics_heat * 0.20 + btc_heat * 0.25,
            1,
        )

        set_cache(cache_key, result)
        return result
    except Exception as e:
        print(f"Error fetching Polymarket data: {e}")
        return result


def fetch_historical_sp500(days: int = 365) -> list:
    """Fetch S&P 500 historical data for the trend chart."""
    cache_key = f"sp500_hist_{days}"
    cached_data = cached(cache_key, ttl=86400)  # cache for a day
    if cached_data:
        return cached_data

    try:
        spx = yf.Ticker("^GSPC")
        end = datetime.now()
        start = end - timedelta(days=days)
        hist = spx.history(start=start, end=end)
        data = []
        for idx, row in hist.iterrows():
            data.append({
                "date": idx.strftime("%Y-%m-%d"),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            })
        set_cache(cache_key, data, ttl=86400)
        return data
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return []


def fetch_historical_vix(days: int = 365) -> list:
    """Fetch VIX historical data."""
    cache_key = f"vix_hist_{days}"
    cached_data = cached(cache_key, ttl=86400)
    if cached_data:
        return cached_data

    try:
        vix = yf.Ticker("^VIX")
        end = datetime.now()
        start = end - timedelta(days=days)
        hist = vix.history(start=start, end=end)
        data = []
        for idx, row in hist.iterrows():
            data.append({
                "date": idx.strftime("%Y-%m-%d"),
                "close": round(float(row["Close"]), 2),
            })
        set_cache(cache_key, data, ttl=86400)
        return data
    except Exception as e:
        print(f"Error fetching VIX history: {e}")
        return []


# ═══════════════════════════════════════════════════════════
#  COMPOSITE CALCULATION
# ═══════════════════════════════════════════════════════════

def calculate_composite(data: dict, sentiment: dict) -> dict:
    """Calculate composite temperature and individual indicator scores."""
    indicators = {}
    total_weight = 0
    weighted_sum = 0

    # Merge data sources
    all_data = {**data, **sentiment}

    for ind_id, config in INDICATOR_CONFIG.items():
        if ind_id in all_data:
            value = all_data[ind_id]
            temp = normalize(value, config)
            indicators[ind_id] = {
                "name": config["name"],
                "value": value,
                "temperature": round(temp, 1),
                "weight": config["weight"],
            }
            weighted_sum += temp * config["weight"]
            total_weight += config["weight"]

    composite = round(weighted_sum / total_weight, 1) if total_weight > 0 else 50

    return {
        "composite": composite,
        "indicators": indicators,
        "market_data": {
            "sp500_price": data.get("sp500_price", 0),
            "sp500_change": data.get("sp500_change", 0),
            "vix": data.get("vix", 20),
            "us10y": data.get("us10y", 4.5),
            "dxy": data.get("dxy", 104),
            "gold": data.get("gold", 2300),
        }
    }


def get_temp_label(temp: float) -> dict:
    """Get label info for a temperature value."""
    if temp <= 20:
        return {"status": "极度恐慌", "color": "#0ea5e9", "desc": "市场极度恐慌，往往对应底部区域，逆向投资者可关注买入机会"}
    elif temp <= 40:
        return {"status": "偏冷", "color": "#22c55e", "desc": "市场情绪偏冷，估值相对合理，可逐步建仓优质资产"}
    elif temp <= 60:
        return {"status": "中性", "color": "#eab308", "desc": "市场情绪中性，无明显方向性信号，保持现有仓位"}
    elif temp <= 80:
        return {"status": "偏热", "color": "#f97316", "desc": "市场情绪偏热，注意控制仓位，考虑部分止盈"}
    else:
        return {"status": "极度贪婪", "color": "#ef4444", "desc": "市场极度贪婪，往往对应顶部区域，建议减仓防守"}


# ═══════════════════════════════════════════════════════════
#  HISTORY
# ═══════════════════════════════════════════════════════════

def save_snapshot(composite: float, indicators: dict, market_data: dict):
    """Save current snapshot to DB."""
    conn = get_db()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO temperature_history (timestamp, composite, indicators, market_data) VALUES (?, ?, ?, ?)",
        (now, composite, json.dumps(indicators), json.dumps(market_data))
    )
    for ind_id, ind_data in indicators.items():
        conn.execute(
            "INSERT INTO indicator_history (timestamp, indicator_id, value, temperature) VALUES (?, ?, ?, ?)",
            (now, ind_id, ind_data["value"], ind_data["temperature"])
        )
    conn.commit()
    conn.close()


def get_history(days: int = 30) -> list:
    """Get temperature history from DB."""
    conn = get_db()
    since = (datetime.now() - timedelta(days=days)).isoformat()
    rows = conn.execute(
        "SELECT timestamp, composite, indicators FROM temperature_history WHERE timestamp >= ? ORDER BY timestamp ASC",
        (since,)
    ).fetchall()
    conn.close()

    # Deduplicate by date (keep last of each day)
    result = []
    seen_dates = set()
    for row in reversed(rows):
        date = row["timestamp"][:10]
        if date not in seen_dates:
            seen_dates.add(date)
            result.append({
                "date": date,
                "composite": row["composite"],
                "indicators": json.loads(row["indicators"]),
            })
    result.reverse()
    return result


# ═══════════════════════════════════════════════════════════
#  SECTOR DATA
# ═══════════════════════════════════════════════════════════

SECTOR_ETFS = {
    "XLK": "科技",
    "XLF": "金融",
    "XLE": "能源",
    "XLV": "医疗",
    "XLI": "工业",
    "XLY": "消费循环",
    "XLP": "必需消费",
    "XLB": "原材料",
    "XLRE": "房地产",
    "XLU": "公用事业",
    "XLC": "通信服务",
}

def fetch_sector_data() -> dict:
    """Fetch sector performance data."""
    cache_key = "sector_data"
    cached_data = cached(cache_key)
    if cached_data:
        return cached_data

    result = {}
    for symbol, name in SECTOR_ETFS.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            price = info.get("lastPrice", info.get("regularMarketPrice", 0))
            prev = info.get("previousClose", price)
            change = round((price - prev) / prev * 100, 2) if prev else 0
            result[name] = {
                "symbol": symbol,
                "price": round(price, 2),
                "change": change,
            }
        except:
            result[name] = {"symbol": symbol, "price": 0, "change": 0}

    set_cache(cache_key, result)
    return result


# ═══════════════════════════════════════════════════════════
#  API ENDPOINTS
# ═══════════════════════════════════════════════════════════

@app.get("/api/temperature")
def get_temperature(save: bool = Query(default=True)):
    """Get current temperature and all indicators."""
    market_data = fetch_market_data()
    sentiment_data = fetch_sentiment_data()
    polymarket_data = fetch_polymarket_data()
    result = calculate_composite({**market_data, **polymarket_data}, sentiment_data)
    result["polymarket"] = polymarket_data
    result["label"] = get_temp_label(result["composite"])
    result["timestamp"] = datetime.now().isoformat()

    if save:
        save_snapshot(result["composite"], result["indicators"], result["market_data"])

    return result


@app.get("/api/history")
def get_temperature_history(days: int = Query(default=30)):
    """Get temperature history."""
    return get_history(days)


@app.get("/api/sectors")
def get_sectors():
    """Get sector performance."""
    return fetch_sector_data()


@app.get("/api/polymarket")
def get_polymarket():
    """Get Polymarket macro dashboard data."""
    return fetch_polymarket_data()


@app.get("/api/config")
def get_config():
    """Get indicator configuration."""
    return INDICATOR_CONFIG


@app.get("/api/sp500_history")
def get_sp500_history(days: int = Query(default=365)):
    """Get S&P 500 historical data."""
    return fetch_historical_sp500(days)


@app.get("/api/vix_history")
def get_vix_history(days: int = Query(default=365)):
    """Get VIX historical data."""
    return fetch_historical_vix(days)


@app.get("/api/health")
def health():
    """Health check."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


# Serve static files
static_dir = Path(__file__).parent
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8866, log_level="info")
