# Contributing · 贡献指南

Thanks for your interest in **Global Sentiment Thermometer**.
感谢你愿意参与 **全球情绪温度计** 的建设。

---

## English

### Ways to contribute

- File an issue for bugs, missing data sources, or UX problems
- Open a pull request for fixes or new indicators
- Suggest new Polymarket markets to integrate
- Improve i18n (EN / 中文 / other languages)

### Development setup

```bash
git clone https://github.com/ZongrongLi/sentiment-thermometer.git
cd sentiment-thermometer
pip install -r requirements.txt
python3 server.py
open http://localhost:8866
```

### Branch and commit conventions

- Branch from `main`
- Use clear commit messages, e.g. `feat:`, `fix:`, `docs:`, `refactor:`
- Keep PRs focused and small

### Adding a new indicator

1. Add fetch logic in `scripts/fetch_data.py` and `server.py`
2. Register it in `_indicator_config` with weight, range, and direction
3. Add localized name in `index.html` (both EN and 中文)
4. Make sure it can be served from both the local backend and the static snapshot

### Code style

- Python: format with `black` if available, keep functions small
- Frontend: keep `index.html` self-contained, no extra build step
- Avoid pulling in heavy dependencies unless necessary

### Disclaimer

This project is for educational and informational use only.
It is not financial advice and not a trading signal.

---

## 中文

### 你可以怎么参与

- 提 issue 反馈 bug、缺失的数据源、体验问题
- 提 PR 修复问题或增加新指标
- 推荐新的 Polymarket 合约接入
- 帮助多语言（中文 / English / 其他语言）

### 本地开发

```bash
git clone https://github.com/ZongrongLi/sentiment-thermometer.git
cd sentiment-thermometer
pip install -r requirements.txt
python3 server.py
open http://localhost:8866
```

### 分支和提交规范

- 从 `main` 拉分支
- 提交信息写清楚，例如 `feat:` / `fix:` / `docs:` / `refactor:`
- 一个 PR 只做一件事，越小越好 review

### 增加新指标的步骤

1. 在 `scripts/fetch_data.py` 和 `server.py` 增加抓取逻辑
2. 在 `_indicator_config` 注册它，写好权重、区间、方向
3. 在 `index.html` 里加上中英文名字
4. 确保本地后端和 Pages 静态快照都能用

### 代码风格

- Python：能用 `black` 就格式化，函数尽量小
- 前端：`index.html` 保持单文件，不要引入复杂构建
- 不要随便加重依赖

### 免责声明

本项目仅作学习和信息聚合用途，不构成任何投资建议、不是任何交易信号。
