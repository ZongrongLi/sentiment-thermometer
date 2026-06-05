# Promo Kit · 推广物料包

This file is the source of truth for how this project is promoted.
本文件是这个项目对外推广的统一物料包。

Demo: https://zongrongli.github.io/sentiment-thermometer/
Repo: https://github.com/ZongrongLi/sentiment-thermometer

---

## Channels · 投放渠道

### English
- **Hacker News** — Show HN, Tue/Wed 08:00–10:00 PT, title prefix `Show HN:`
- **Reddit** — `r/algotrading`, `r/SideProject`, `r/opensource`, `r/dataisbeautiful`, `r/macroeconomics`, `r/quantfinance` (respect 9:1 self-promo rule)
- **Product Hunt** — Launch Tue 00:01 PT, need a hunter, be on-thread for 12+ hours
- **Indie Hackers** — Write a build log, organic traffic
- **Lobste.rs** — Invite-only, higher quality
- **Twitter / X** — `#opensource #fintech #polymarket #macro`
- **dev.to / Medium** — "How I built" article linking to repo
- **LinkedIn** — Personal post, better reach for finance circle
- **StockTwits / Bogleheads / QuantConnect community** — Finance verticals

### 中文
- **V2EX** — `分享创造` 节点，工作日 9–11 点
- **即刻 (jike)** — 独立开发者圈
- **少数派** — 工具介绍长文
- **知乎** — "美股" / "宏观经济" / "开源" 话题
- **雪球** — 工作日 16:00 后发，精准金融用户
- **掘金 / SegmentFault / OSCHINA** — 技术向
- **微博** — @ 财经向博主
- **抖音 Simon 林原视频评论区** — 灵感来源致谢 + demo 链接
- **东方财富股吧** — 注意水军环境，谨慎

---

## Posting discipline · 发帖纪律

- Hacker News 只发一次，标题不要 hype
- Reddit 不要同一时段刷多个 sub，每个 sub 间隔几天
- Product Hunt 当天必须全程互动 12 小时以上
- V2EX 不要小号互捧，会被全站 ban
- 雪球 / 微博先发干货再挂链接
- 每一处都加 **不构成投资建议** 免责声明
- 抖音评论先夸原作者，再附 demo 链接

---

## Disclaimer · 免责声明

This project is for educational and informational use only. It is not financial advice and not a trading signal.
本项目仅供学习与信息聚合使用，不构成任何投资建议、不是任何交易信号。

---

## Copy: Hacker News (Show HN) · 英文

**Title:** Show HN: Global Sentiment Thermometer – open-source US macro mood dashboard

Hi HN — I built an open-source US market sentiment dashboard that aggregates 12 weighted indicators into a single 0–100 "temperature":

VIX · Put/Call · AAII · CNN Fear & Greed · 10Y-2Y · HY OAS · DXY · Gold · TED · S&P vs 200MA · BTC Fear & Greed · Polymarket macro heat.

- Demo: https://zongrongli.github.io/sentiment-thermometer/
- Code: https://github.com/ZongrongLi/sentiment-thermometer

Stack: FastAPI backend (5-min refresh) + a single self-contained HTML frontend, GitHub Pages static snapshot mode refreshed via GitHub Actions every 6 hours. Bilingual UI (EN / 中文).

All data sources are free (yfinance, CNN F&G, alternative.me, AAII, Polymarket Gamma API). A few indicators (Put/Call, HY OAS, TED, S&P vs 200MA) are proxy-derived from VIX/SPX for now — that is explicitly documented in the README, and the design is meant to be replaceable with real FRED/CBOE series.

For educational / informational use only and not financial advice. Happy to take feedback on indicator design, weights, or additional macro signals worth integrating (FRED, more Polymarket markets, oil, recession odds).

---

## Copy: Reddit · 英文

**Title:** I built an open-source US market sentiment thermometer (12 weighted signals + Polymarket) [EN/中文]

I open-sourced a US market macro sentiment dashboard. It aggregates 12 weighted indicators into a single 0–100 sentiment number, with a bilingual UI.

- Demo: https://zongrongli.github.io/sentiment-thermometer/
- Code: https://github.com/ZongrongLi/sentiment-thermometer

Indicators: VIX, Put/Call, AAII bull-bear, CNN Fear & Greed, 10Y-2Y, HY OAS, DXY, Gold, TED, S&P vs 200MA, Bitcoin Fear & Greed, Polymarket macro heat (Fed decisions, rate cuts, geopolitics, crypto).

Stack: FastAPI + plain HTML/JS + SQLite. GitHub Pages serves a static snapshot refreshed every 6 hours by GitHub Actions.

All data is from free public APIs. Some indicators are proxy-derived right now (clearly documented), can be replaced with real FRED / CBOE data.

Looking for feedback on:
- Weighting design
- New indicators worth adding
- Additional Polymarket markets to integrate

Not financial advice, just a tool.

---

## Copy: V2EX / 雪球 / 知乎 · 中文

**标题：** 开源了一个美股宏观情绪温度计 · 12 项加权指标 + Polymarket

受抖音 Simon 林 Claude Code 手搓系列「全球情绪温度计」启发，我把这个东西完整复刻并开源了。

12 项加权指标：VIX、Put/Call、AAII 牛熊差、CNN Fear & Greed、10Y-2Y 利差、HY OAS、DXY、黄金、TED、S&P vs 200MA、比特币 F&G、Polymarket 宏观热度。

- 在线 Demo：https://zongrongli.github.io/sentiment-thermometer/
- 源码：https://github.com/ZongrongLi/sentiment-thermometer
- 支持中英文切换
- 数据源全部免费、公开 API（yfinance / CNN / Polymarket Gamma / alternative.me / aaii.com）
- GitHub Actions 每 6 小时自动更新 Pages 快照
- 本地后端每 5 分钟实时刷新

技术栈：FastAPI + 单文件 HTML + SQLite + GitHub Pages，依赖很轻，clone 下来就能跑。

仅供学习和信息聚合，不构成任何投资建议。欢迎提 issue 推荐你觉得值得接入的宏观信号或 Polymarket 合约。

---

## Copy: Twitter / X · 短文案

🌡️ Built an open-source US market sentiment thermometer.

12 weighted signals → one 0–100 number.

VIX · AAII · Fear & Greed · 10Y-2Y · HY OAS · DXY · Gold · Polymarket macro heat · BTC F&G · S&P vs 200MA

Demo: https://zongrongli.github.io/sentiment-thermometer/
Code: https://github.com/ZongrongLi/sentiment-thermometer

#opensource #fintech #polymarket #macro

---

## Copy: LinkedIn · 英文

Just open-sourced a small weekend project: **Global Sentiment Thermometer**.

It aggregates 12 weighted US macro indicators into a single 0–100 sentiment temperature, with a bilingual (EN / 中文) UI and free, public data sources only.

What's inside:
- VIX, AAII bull-bear, CNN Fear & Greed, 10Y-2Y, HY OAS, DXY, Gold, TED, S&P vs 200MA, BTC Fear & Greed
- Polymarket macro panel (Fed decisions, easing expectations, geopolitics, crypto speculation)
- FastAPI backend, single-file HTML frontend, GitHub Pages static deployment

Demo: https://zongrongli.github.io/sentiment-thermometer/
Code: https://github.com/ZongrongLi/sentiment-thermometer

Not financial advice — just a free, transparent tool for tracking market mood.

#opensource #fintech #macroeconomics #datavisualization

---

## Copy: 抖音评论 (留在 Simon 林原视频下)

第一条（克制版，推荐）：

> 谢 Simon 哥的思路，照着这期视频用 Claude Code 手搓了一个完整版，加了 Polymarket 宏观盘和中英文切换，已经开源在 GitHub。Demo：zongrongli.github.io/sentiment-thermometer  仓库搜 sentiment-thermometer。仅作学习，不构成投资建议。

第二条（备选，互动版）：

> 跟着这期视频学了一晚上，最后做出了一个全球情绪温度计，12 个加权指标，多了一个 Polymarket 宏观盘，做了中英文切换，托管在 GitHub Pages。Demo 直接打开就能看实时数据，欢迎拍砖：zongrongli.github.io/sentiment-thermometer 。再次谢谢 Simon 哥的灵感，仅作学习参考。

---

## Copy: 即刻 / 小红书 · 中文短

🌡️ 美股情绪温度计 · 开源版

把 12 个宏观信号（VIX、AAII、CNN F&G、10Y-2Y、HY OAS、DXY、Gold、Polymarket、BTC F&G、S&P vs 200MA、TED、Put/Call）加权汇总成一个 0–100 的温度。

- 中英文切换
- 数据源全部免费
- GitHub Pages 直接可看
- 每 6 小时自动更新

Demo：zongrongli.github.io/sentiment-thermometer
代码：github.com/ZongrongLi/sentiment-thermometer

仅供学习，不构成投资建议。

---

## Assets · 视觉物料

- `assets/og-image.png` — 1200×630，社交分享卡片（Twitter / LinkedIn / OG）
- `assets/og-image.svg` — 矢量版
- `assets/poster-portrait.png` — 1080×1920，竖版海报（Product Hunt / 小红书 / 朋友圈）
- `assets/poster-portrait.svg` — 矢量版
- `assets/screenshot.svg` — README 内嵌截图
