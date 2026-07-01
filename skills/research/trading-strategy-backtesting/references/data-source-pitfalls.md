# Data Source Pitfalls (CCXT + yfinance)

Empirical findings from multi-exchange data fetching.

## CCXT Hyperliquid Quirks

### `since` parameter ignored for sub-4h timeframes

```python
exchange = ccxt.hyperliquid({"enableRateLimit": True})

# BROKEN: Always returns most recent candles, ignores since
ohlcv = exchange.fetch_ohlcv("BTC/USDC:USDC", "1h", since=1700000000000, limit=500)
# Result: candles from last 24h regardless of since

# WORKS: 4H timeframe respects since
ohlcv = exchange.fetch_ohlcv("BTC/USDC:USDC", "4h", since=1700000000000, limit=500)
# Result: proper historical pagination
```

**Pagination pattern that works (4H only):**
```python
data = []
since = exchange.parse8601("2024-01-01T00:00:00Z")
while True:
    batch = exchange.fetch_ohlcv("BTC/USDC:USDC", "4h", since=since, limit=500)
    if not batch: break
    data.extend(batch)
    since = batch[-1][0] + 1
    if len(batch) < 500: break
```

### Slow `load_markets()`

- Loads all 751 markets → timeouts on slow connections
- **Fix**: Don't call `load_markets()`. Use `fetch_ohlcv()` directly with known symbol strings.
- Known symbols: `BTC/USDC:USDC`, `ETH/USDC:USDC`, `SOL/USDC:USDC`, `SPX/USDC:USDC`

### NASDAQ/Index Symbols

- `NASDAQ/USDC` — exists but returns empty OHLCV data
- `SPX/USDC:USDC` — works, has data from ~Jan 2025, but prices are tokenized ($0.2-$2 range, not real SPX)
- `SPH/USDC` and `SPX/USDC` — spot versions, mostly illiquid

## yfinance (Yahoo Finance) Quirks

### 730-day intraday limit

- 1h / 15m / 30m data limited to **last 730 days from CURRENT date**
- If today is 2026-06-30, max intraday range is 2024-07-01 → present
- Daily (1d) data is not subject to this limit
- **Fix**: Calculate start date dynamically: `pd.Timestamp.now() - pd.Timedelta(days=720)`

### MultiIndex columns on ETF symbols

```python
df = yf.download("QQQ", start="2024-07-01", interval="1h")
# df.columns = MultiIndex: [('Close', 'QQQ'), ('High', 'QQQ'), ...]

# Flatten:
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
```

### "possibly delisted" errors

- `^IXIC` (NASDAQ Composite) often returns "possibly delisted" for intraday — use `QQQ` (NASDAQ-100 ETF) or `SPY` instead
- Always check `len(df) == 0` after download before processing

## CCXT Binance (Cryptocurrency)

- Full historical data, proper `since` pagination
- Any timeframe works (1m, 5m, 15m, 1h, 4h, 1d, etc.)
- Symbols use standard notation: `BTC/USDT`, `ETH/USDT`
- Rate limit is generous (~1200 requests/min)
- Preferred for historical backtesting when price action is fungible across exchanges

## Strategy Script Structure

Minimal viable backtest pattern:

```python
import pandas as pd, numpy as np, ccxt

def fetch(symbol, timeframe, start, end):
    ex = ccxt.binance({"enableRateLimit": True})
    since = ex.parse8601(start)
    data = []
    while True:
        batch = ex.fetch_ohlcv(symbol, timeframe, since=since, limit=500)
        if not batch: break
        data.extend(batch)
        since = batch[-1][0] + 1
        if len(batch) < 500: break
    df = pd.DataFrame(data, columns=["ts","o","h","l","c","v"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms")
    df = df[df["ts"] <= pd.Timestamp(end)]
    # Add indicators
    df["ema20"] = df["c"].ewm(span=20).mean()
    df["atr"] = df["c"].diff().abs().rolling(14).mean()
    return df

def detect(df): ...   # strategy-specific
def backtest(df): ... # simulate with capital * risk%
```

For trading strategies that need 1H data for filtering: use Binance (crypto) or yfinance (equties). Avoid Hyperliquid for 1H backtesting data.
