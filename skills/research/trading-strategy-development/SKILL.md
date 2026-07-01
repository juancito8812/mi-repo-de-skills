---
name: trading-strategy-development
description: "Build, backtest, and optimize trading strategies for crypto perps and indices. Covers data sourcing, signal detection, parameter sweeps, risk rules, and live-bot templates."
platforms: [linux, macos, windows]
---

# Trading Strategy Development

## When to use

Use when the user asks you to:
- Analyze a trading video or strategy concept
- Build a backtest from scratch
- Optimize strategy parameters via grid search
- Create a live trading bot for Hyperliquid, Binance, or similar
- Port a strategy from one asset class (e.g. NASDAQ futures) to another (e.g. crypto perps)

## Workflow

### Phase 1: Understand the Strategy

1. **Extract rules** from any provided video/description
   - Load `youtube-content` skill for YouTube videos
   - Identify: entry, stop-loss, take-profit, timeframe, session/clock filter, filters/indicators
   - Name the strategy so you can refer to it clearly

2. **Research origins**:
   - Search for original author/source (e.g. Linda Raschke, ICT, WH/Will Street)
   - Understand the *why* — what market edge does it exploit?
   - Note the *original* asset and conditions (e.g. NASDAQ futures 9-10 AM NY session)

### Phase 2: Data Sourcing

| Data Source | Best For | Limits |
|---|---|---|
| **ccxt** (exchange SDK) | Crypto perps on Binance, Hyperliquid | Hyperliquid ignores `since` for <4h timeframes |
| **yfinance** | NASDAQ, ETFs, indices | 1h max 730 days, 15m/5m max ~60 days from current date |
| **youtube-transcript-api** | Video analysis (strategy explanations) | Requires `uv pip install` |

**Windows note**: Use `source .venv/Scripts/activate && python script.py` instead of `python3`.
**Pagination pattern** for large data:
```python
data = []
since = exchange.parse8601("2024-01-01T00:00:00Z")
while True:
    batch = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=500)
    if not batch: break
    data.extend(batch)
    since = batch[-1][0] + 1
    if len(batch) < 500: break
```

### Phase 3: Build the Backtest

**Structure:**
```
strategies/<strategy-name>/
├── 00_STRATEGY_GUIDE.md        # Rules, rationale, expected metrics
├── 01_backtest.py              # Core backtest
├── 02_bot_template.py          # Live bot template
└── README.md
```

**Backtest skeleton:**
1. `detect_signals(df, params)` — pure signal detection
2. `apply_filters(signals, df, params)` — trend, volatility, RR filters
3. `run_backtest(signals, df, params)` — simulate entries → exits → P&L
4. `generate_report(trades)` — win rate, profit factor, Sharpe, max DD

**Critical rules:**
- Always validate data alignment (4H vs 1H timestamps must overlap)
- Always debug filter rejections with counters (`debug = {"trend": 0, "rr": 0, "ok": 0}`)
- Always test with NO filter first to see raw signal quality

### Phase 4: Parameter Optimization

**Grid sweep pattern:**
```python
from itertools import product

param_grid = list(product(
    [20, 30, 40],           # lookback
    [1.5, 2.0, 3.0, 5.0],  # atr_mult (TP width)
    [1.0, 1.2],             # rr_min
    [2.0, 3.0],             # risk_max %
    [72, 144],              # hold_bars
))

# Cache signal detection by lookback to avoid recomputation
for lb in set(g[0] for g in param_grid):
    cache[lb] = detect_signals(df, lookback=lb)
```

**Ranking metrics** (prefer ≥10 trades minimum):
```python
score = pf * 2 + wr/100 - dd/100 + be_rate/100
```

### Phase 5: Key Findings (from Turtle Soup session)

#### What works
- **No trend filter** (EMA20/50) on NASDAQ — it kills 60%+ of signals and drops WR
- **LONG trades** outperform SHORTs in bullish markets (57% WR vs 33%)
- **ATR × 3.0** for TP (wider target gives the move room to breathe)
- **Lookback 20** on 1h outperforms tighter lookbacks
- **Mecha ratio 0.5** (wick must be ≥50% of body) filters low-quality sweeps

#### What doesn't
- **EMA20/50 trend filter** on crypto or NASDAQ — destructive
- **ATR × 1.0–2.0** for TP — too tight, get stopped before move completes
- **15m/30m timeframes on NASDAQ** — too much noise
- **SPX/USDC:USDC token** on Hyperliquid — synthetic micro-price, no structural edge

#### Data pitfalls
- Yahoo Finance 1h: max 730 days back from today
- Yahoo Finance 15m/5m: max ~60 days back from today
- Hyperliquid CCXT: 1h+ data ignores `since` param (returns most recent)
- Hyperliquid SPX/USDC:USDC 5m: only ~17 days of history available

## User Preferences
- Usuario habla español, prefiere mensajes compactos (estado + resultado, sin logs largos)
- Entregar artefactos en `C:/Users/JRCPU/Desktop/administracion Velas/ADMINISTRACIÒN/Juan/`
- Prefiere backtests funcionales antes que descripciones teóricas

## References

See `references/turtle-soup-winning-config.md` for the optimized parameter set.
