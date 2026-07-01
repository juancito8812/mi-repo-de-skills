---
name: trading-strategy-backtesting
description: "Analyze, adapt, and backtest trading strategies across markets (crypto perps, futures, stocks). Extract strategy rules from videos or articles, adapt them to different instruments/exchanges, build backtests, and deliver production-ready code (bot templates, configs)."
platforms: [linux, macos, windows]
---

# Trading Strategy Backtesting

Analyze a trading strategy from a source (YouTube, article, community), adapt it for a target exchange/market, backtest it, and deliver a ready-to-use package.

## Workflow

### 1. Strategy Extraction

If the source is a **YouTube video**:
- Fetch the transcript using the `youtube-content` skill script
- On Windows (git-bash): use `python` directly (not `python3`). Install via `uv venv && source .venv/Scripts/activate && uv pip install youtube-transcript-api`. Then write a standalone Python script using `YouTubeTranscriptApi` instead of the bundled script (which expects `python3`).
- Extract: timeframe, entry rules, exit rules, stop loss logic, risk management, session/schedule filters, indicators used
- Look for specific naming conventions (e.g. "Turtle Soup", "Breaker", "ICT", "SMC", "Price Action")

If the source is an **article or document**: extract key rules and parameters.

### 2. Market Adaptation

When adapting a strategy from one market to another, document the differences:

| Aspect | Futures (e.g. NQ) | Spot / Crypto Perps |
|---|---|---|
| Hours | Session-based (9-17 ET) | 24/7 — no session close |
| Leverage | Fixed (10-20x) | Configurable (up to 50x) |
| Fees | Per-contract | Taker/maker % |
| Funding | N/A | Perpetual funding every 1h |
| Data | Centralized | Multi-exchange, fungible |

### 3. Data Sources — Selection Guide

| Source | Pros | Cons |
|---|---|---|
| **CCXT Binance** | Best historical depth, pagination works, any timeframe | Only crypto |
| **CCXT Hyperliquid** | Direct perp data, real prices | `since` ignored for <4h timeframes, slow market loading (751 markets), limited history |
| **Yahoo Finance (yfinance)** | Stocks, ETFs, indices, free | 730-day limit on intraday (1h/15m), MultiIndex columns, `^IXIC` lacks 1h |
| **Alpha Vantage / Twelve Data** | Indices, forex | API keys needed, rate-limited |

**CCXT Hyperliquid pitfalls** (from experience):
- `fetch_ohlcv(symbol, '1h', since=ts)` **ignores `since`** — always returns most recent candles regardless of `since` value. Pagination appends the same recent data.
- 4H data respects `since` and paginates correctly.
- To backtest on Hyperliquid prices, use 4H as the minimum timeframe and compute EMAs/ATR on the 4H data itself (no 1H needed).
- `load_markets()` fetches all 751 markets and times out easily. Use `fetch_ohlcv()` directly without pre-loading.
- For NASDAQ/indices on Hyperliquid: `SPX/USDC:USDC` but prices are tokenized (~$0.3-$2 range), not real SPX levels.

**Yahoo Finance (yfinance) pitfalls**:
- 1h/15m data limited to last 730 days from **current date** (not from requested end date).
- `^IXIC` (NASDAQ Composite) generally lacks intraday data; prefer `QQQ` (NASDAQ-100 ETF) or `SPY`.
- ETF symbols like QQQ return MultiIndex columns: `('Close', 'QQQ')`. Flatten with: `df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]`.
- When download fails (e.g. "possibly delisted"), the dataframe is empty — check `len(df)` before processing.

### 4. Building the Backtest

Pattern for a backtest script:

```python
# Core structure
def fetch_data(symbol, timeframe, start, end): ...
def detect_signals(df): ...       # Strategy-specific pattern detection
def apply_filters(signals, df): ...  # Trend, volatility, RR filters
def run_backtest(signals, df): ...   # Simulate trades with position sizing
def generate_report(trades): ...     # Win rate, PF, DD, trade list
```

**Risk management**: use `capital * RISK_PER_TRADE / dollar_risk` for position sizing. Default 2% per trade.

**Stop loss**: by structure (below/above the liquidity sweep), NOT fixed percentage.

**Take profit**: adaptive (ATR-based) or fixed (RR ratio). For reversal strategies, 1:1.5 to 1:2 target.

### 5. Delivering the Package

Structure for the deliverable:

```
strategy-folder/
├── 00_ESTRATEGIA_NOMBRE.md       # Full strategy guide (Spanish if user prefers)
├── 01_backtest_strategy.py        # Runnable backtest (self-contained)
├── 02_bot_exchange.py             # Bot template for target exchange
└── README.md                      # Quick start
```

### 6. Interpreting Results

When a backtest shows poor results (common for strategies adapted across markets):

1. **Check raw signal count** — if <20 signals/year, the detection is too restrictive
2. **Check filter breakdown** — which filter kills the most signals?
   - Trend filter (EMA20/50) often kills 50-60% of signals
   - RR/ATR filter often kills remaining candidates
3. **Compare win rate vs. profit factor** — high WR + negative PF means losses are too large (RR targets too tight)
4. **Common fixes**:
   - Relax or remove the trend filter if the strategy is mean-reversion based
   - Use session-based filtering instead of EMA for strategies designed around specific market hours
   - Use dynamic trailing stops instead of fixed ATR targets
   - On 24/7 markets, identify high-probability windows (London open, NY open, rollover)

### 7. Systematic Multi-Asset Testing (Battery Method)

When a strategy needs validation across multiple instruments:

```python
# Pattern for autonomous battery testing
ASSETS = ["BTC/USDC:USDC", "ETH/USDC:USDC", "SOL/USDC:USDC", "SPX/USDC:USDC"]
TIMEFRAMES = ["1h", "4h"]

for market, name in ASSETS:
    for tf in TIMEFRAMES:
        data = fetch_hl(market, tf, exchange)
        sigs = detect(data, winning_params)
        ts = run_backtest(sigs, data)
        SUMMARY.append({...})
```

**Battery output**: a comparison table showing every asset × timeframe with the same config.

### 8. Parameter Optimization (Grid Search)

Pattern for systematic parameter sweeps:

```python
from itertools import product

grid = list(product(
    [10, 20, 30, 40],       # lookback
    [1.0, 2.0, 3.0, 5.0],   # ATR multiplier
    [1.0, 1.2],              # RR minimum
    [2.0, 3.0],              # risk max %
    [6, 12, 24],             # hold bars
))
```

**Performance optimizations**:
- **Cache signal detection**: detect signals once per lookback value, then iterate through other param combos without re-detecting
- **Early pruning**: skip combos with <3 or <5 trades (insufficient sample)
- **Scoring**: use composite score (PF*2 + WR/100 + BE/100) to rank combos
- **Minimum trade threshold**: require ≥5-10 trades before considering a combo valid

### 9. Diagnosis Framework: Why a Strategy Works on Market A but Not B

When the same strategy tests positive on one instrument but negative on another:

| Factor | Session-Based (QQQ/NASDAQ) | 24/7 Perpetual (BTC/ETH) |
|---|---|---|
| **Data gaps** | ~6.5h/day (market closes) | 24h continuous |
| **ATR behavior** | Larger ATR (overnight gaps) | Smooth ATR (~0.3-0.5% of price) |
| **Swing structure** | Defined opens/closes | Continuous flow |
| **RR calc** | ATR/distance ratio > 1.0 | ATR/distance ratio < 0.5 |
| **Conclusion** | Strategy exploits session gaps | Strategy loses edge without gaps |

**Key diagnostic**: remove ALL filters and run every raw signal. If WR stays ~25-27% on both but PF differs, TP placement is the issue. If WR drops fundamentally (<25%), the pattern doesn't replicate.

### 10. Data Source Selection Quick Reference

| Need | Use |
|---|---|
| NASDAQ/stock backtest | **QQQ** via yfinance (1h) |
| Crypto historical backtest | **Binance** via CCXT (any TF) |
| Hyperliquid live prices | **Hyperliquid** via CCXT (4H for history) |
| Multi-asset comparison | Battery method, same date range |

## Common Strategy Archetypes

### Turtle Soup + Breaker (WH / Will Street)
- **Original**: Linda Raschke / Will Street. NASDAQ futures, 3H timeframe, 9-10 AM NY session.
- **Pattern**: Price sweeps a multi-candle low/high (liquidity grab), closes back inside, then breaks the opposite side of the swing (breaker).
- **Entry**: Buy/Sell Stop at the breaker level. SL below/above the sweep point.
- **Target**: 1:1 → BE → 1:1.5. Time exit at session close.
- **Adaptation for crypto**: Use 4H instead of 3H. Replace session filter with key windows (London 08:00 UTC, NY 13:00 UTC). Without the session filter, win rate drops significantly.

### SMC / ICT Concepts
- Focus on liquidity, order blocks, fair value gaps (FVG), market structure shifts.
- Entry on breaker + FVG confluence.

## Error Handling

- **CCXT timeout on market load**: Don't call `load_markets()`. Use `fetch_ohlcv()` directly with known symbol strings.
- **Empty dataframe from yfinance**: Check with `if len(df) == 0` before processing. Try a shorter range or different symbol.
- **execute_code blocked**: This tool can't call subprocesses in cron contexts. Write a `.py` file to disk and run via `terminal()` instead.
