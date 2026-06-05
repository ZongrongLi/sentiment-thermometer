<h1 align="center">🌡️ 全球情绪温度计 · Global Sentiment Thermometer</h1>

<p align="center">
  <em>实时美股宏观情绪看板 — 综合 VIX、利率、地缘、Polymarket 等 12 项指标</em>
  <br/>
  <em>US Market Macro Sentiment Dashboard — 12 weighted indicators in real time</em>
</p>

<p align="center">
  <a href="https://github.com/topics/market-sentiment"><img src="https://img.shields.io/badge/topic-market--sentiment-blue?style=flat-square" alt="Topic: Market Sentiment"/></a>
  <a href="https://github.com/topics/trading-tools"><img src="https://img.shields.io/badge/topic-trading--tools-green?style=flat-square" alt="Topic: Trading Tools"/></a>
  <a href="https://github.com/topics/polymarket"><img src="https://img.shields.io/badge/topic-polymarket-orange?style=flat-square" alt="Topic: Polymarket"/></a>
  <a href="#license"><img src="https://img.shields.io/badge/license-MIT-lightgrey?style=flat-square" alt="License"/></a>
</p>

---

## 🔥 实时 Demo

| 版本 | 链接 | 说明 |
|---|---|---|
| **GitHub Pages (静态快照)** | [sentiment-thermometer.pages.dev](https://zongrongli.github.io/sentiment-thermometer/) | 无需后端，数据每6小时自动更新 |
| **本地运行 (完整版)** | `http://localhost:8866` | 实时数据，5分钟刷新频率 |

> ⚠️ GitHub Pages 版本展示的是最近一次数据快照，完整实时版需启动本地后端。

---

## 📸 预览

<p align="center">
  <img src="assets/screenshot.svg" alt="Global Sentiment Thermometer Screenshot" width="90%"/>
</p>

---

## ✨ 功能特性

| 功能 | 说明 |
|---|---|
| 🌡️ **综合温度计** | 0–100° 颜色渐变，从"极度恐慌"到"极度贪婪" |
| 📊 **12 项加权指标** | VIX · Put/Call · AAII · Fear & Greed · 10Y-2Y · HY OAS · DXY · 黄金 · TED · S&P vs 200MA · 比特币 F&G · Polymarket 宏观热度 |
| 🎯 **Polymarket 宏观盘** | 接入预测市场的 Fed 利率决议、降息预期、美伊和平概率、加密投机热度 |
| 🏭 **板块热度** | 11 个标普行业 ETF (XLK/XLF/XLE...) 实时涨跌 |
| 📈 **温度趋势** | 1月 / 3月 / 1年 历史温度曲线 |
| 🔄 **自动刷新** | 每 5 分钟自动更新，也可手动刷新 |
| 🌙 **暗色主题** | 夜间友好，低光环境舒适 |

---

## 🏗️ 架构

```
                             ┌──────────────────┐
                             │   GitHub Pages    │
                             │  (静态快照)        │
                             └────────┬─────────┘
                                      │ data/snapshot.json
                                      │ (每6小时GH Action更新)
┌──────────┐    fetch()     ┌─────────┴──────────┐    ┌──────────────────┐
│ Browser  │ ────────────→  │   FastAPI Server   │ ──→│  Yahoo Finance   │
│ (HTML5)  │ ←────────────  │   (port 8866)      │    │  (yfinance)      │
└──────────┘    JSON API    └─────────┬──────────┘    ├──────────────────┤
                                      │                │  CNN Fear/Greed  │
                                      │                ├──────────────────┤
                                      │                │  Polymarket API  │
                                      │                ├──────────────────┤
                                      │                │  alternative.me   │
                                      │                │  (BTC F&G)        │
                                      │                └──────────────────┘
                                      │
                                 ┌────┴────┐
                                 │ SQLite  │
                                 │ (历史)   │
                                 └─────────┘
```

---

## 🚀 快速开始

### 本地运行 (完整版)

```bash
# 1. 克隆仓库
git clone https://github.com/ZongrongLi/sentiment-thermometer.git
cd sentiment-thermometer

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python3 server.py

# 4. 打开浏览器
open http://localhost:8866
```

### 静态部署 (GitHub Pages)

1. Fork 本仓库
2. 进入 Settings → Pages → 选择 **Deploy from branch: `gh-pages`**
3. 等待 GitHub Actions 自动执行（每 6 小时更新数据快照）
4. 访问 `https://zongrongli.github.io/sentiment-thermometer/`

> 第一次部署后，需要手动触发一次 GitHub Actions（Actions → Update Market Data Snapshot → Run workflow）来生成数据快照。

---

## 📡 数据源

| 指标 | 来源 | 类型 | API Key |
|---|---|---|---|
| VIX 恐慌指数 | Yahoo Finance (yfinance) | 股票数据 | 免费，无需 Key |
| S&P 500 / DXY / 黄金 / 10Y | Yahoo Finance | 股票数据 | 免费，无需 Key |
| Put/Call 比率 | VIX 派生估算 | 代理值 | — |
| AAII 牛熊差 | aaii.com (HTML) | 情绪调查 | 免费，无需 Key |
| Fear & Greed | CNN Business | 综合情绪 | 免费，无需 Key |
| 10Y-2Y 利差 | Yahoo Finance / 估算 | 收益率曲线 | 免费，无需 Key |
| HY OAS | VIX 派生估算 | 信用利差 | — |
| TED 利差 | VIX 派生估算 | 银行间风险 | — |
| S&P vs 200MA | 价格估算 | 技术指标 | — |
| 比特币 Fear & Greed | alternative.me | 加密情绪 | 免费，无需 Key |
| **Polymarket 宏观盘** | **Gamma API (polymarket.com)** | **预测市场** | **免费，无需 Key** |
| 板块 ETF (11 个) | Yahoo Finance | 股票数据 | 免费，无需 Key |

> ⚠️ 标注"代理值"的指标基于 VIX 等真实数据的推算，如需精确值建议接入 FRED API（免费）。

---

## ⚙️ 指标权重

```
VIX 恐慌指数           ███████████████░  w15
Put/Call 比率         ████████████░░░░  w12
AAII 牛熊差           ████████████░░░░  w12
Fear & Greed         ██████████░░░░░░  w10
10Y-2Y 利差           ██████████░░░░░░  w10
HY OAS               ██████████░░░░░░  w10
Polymarket 宏观热度    ████████░░░░░░░░  w8
美元指数 DXY           ████████░░░░░░░░  w8
黄金 XAU              ████████░░░░░░░░  w8
S&P vs 200MA         █████░░░░░░░░░░░  w5
TED 利差              █████░░░░░░░░░░░  w5
比特币 F&G            █████░░░░░░░░░░░  w5
```

---

## 🔄 更新频率

| 层级 | 频率 |
|---|---|
| 前端轮询 | 每 5 分钟 |
| 后端缓存 TTL | 5 分钟 |
| 历史 K 线 (S&P, VIX) | 24 小时 |
| GitHub Pages 快照 | 每 6 小时 (通过 GitHub Actions) |

---

## 🧩 依赖

- **Python 3.9+**
- `yfinance` — Yahoo Finance 数据
- `fastapi` + `uvicorn` — HTTP 服务
- `pydantic` — 数据验证

---

## 🔍 搜索关键词

`市场情绪温度计` `美股宏观` `恐惧贪婪指数` `VIX` `Polymarket` `预测市场` `宏观指标看板` `market sentiment thermometer` `stock market indicators` `fear and greed index` `US market macro dashboard` `prediction markets`

---

## 📜 License

MIT

---

## ⚠️ 免责声明

**这不是投资建议。** 本工具仅供教育和研究目的。市场情绪指标具有滞后性，不应作为唯一决策依据。数据源可能存在 15 分钟以上的延迟。
