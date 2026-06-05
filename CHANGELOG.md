# Changelog · 更新日志

All notable changes to this project will be documented in this file.
所有重要的改动会记录在这里。

This project adheres to a simple chronological changelog.

---

## [Unreleased]

- placeholder for next release

---

## [1.1.0] - 2026-06-05

### Added
- Bilingual UI: language switcher (EN / 中文) with `?lang=` URL support
- Bilingual README, English first
- Social preview image `assets/og-image.png`
- SEO metadata: description, keywords, canonical, hreflang, Open Graph, Twitter, schema.org JSON-LD
- GitHub topics for global discoverability
- `LICENSE` (MIT), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`

### Changed
- Static snapshot now persists a `history` array for Pages-only trend rendering
- Improved README structure: demo, preview, features, architecture, quick start
- README badges include live demo and data workflow status

### Fixed
- Removed leftover error banner code path on GitHub Pages
- Hard split between Pages static mode and local API mode

---

## [1.0.0] - 2026-06-05

### Added
- Initial public release of Global Sentiment Thermometer
- 12 weighted indicators including VIX, Put/Call, AAII, Fear & Greed, 10Y-2Y, HY OAS, DXY, Gold, TED, S&P vs 200MA, Bitcoin Fear & Greed, Polymarket macro heat
- FastAPI backend on port 8866 with SQLite history
- Static HTML frontend with dark theme and trend chart
- GitHub Pages static snapshot mode
- GitHub Actions workflow that refreshes the snapshot every 6 hours
