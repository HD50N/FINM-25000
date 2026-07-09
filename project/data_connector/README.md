# `data_connector/` — Market data pipeline

Fetches everything the system knows about the market from Alpaca's data API,
and logs incoming quotes so there is a durable record of what the system saw.

## Files

- `historical.py` — `fetch_daily_bars_for_universe(symbols, days)` returns
  `dict[symbol, DataFrame]` of daily OHLCV bars. One batched request for the
  whole universe (Alpaca accepts a symbol list), then the MultiIndex response
  is split per symbol, sorted, and trimmed to the requested length.
- `quotes.py` — `fetch_latest_quotes(symbols)` returns
  `dict[symbol, {bid, ask, last, volume}]` from the latest-quote and
  latest-trade endpoints; `log_quotes(snapshot, logs_directory)` appends the
  snapshot to `logs/quotes_YYYYMMDD.csv`.

## Design notes and justification

**Why REST snapshots instead of the WebSocket stream.** The strategy is
driven by daily bars; the live loop only needs a fresh price per symbol each
cycle for stop-loss checks, order sizing, and logging. A latest-quote request
per cycle delivers exactly that with no connection management. It also avoids
contending with HW1's `StockDataStream` (Alpaca allows one stream per
account), which the Live Quotes UI tab still uses.

**Why one batched request for bars.** One request for 10 symbols instead of
10 requests keeps the cycle fast and respectful of rate limits. The
per-symbol splitting of the MultiIndex response follows the same
`df.xs(symbol, level="symbol")` pattern as `hw1/data_connector/historical.py`
and `hw2/data_connector/historical.py`.

**Why the IEX feed.** The free tier used throughout this repo
(`DataFeed.IEX` everywhere since HW1). Sufficient for daily-bar signals on
liquid large caps.

**Why daily CSV files.** The assignment asks for structured storage and
logging of incoming data (timestamps, prices, volumes). Append-only CSVs
with a fixed header are structured, human-inspectable, loadable with
`pd.read_csv`, and need no extra dependency. One file per day keeps files
bounded and easy to archive. Generated files are gitignored
(`project/logs/*`).

**Credentials** come from `hw1/data_connector/config.py`, the single
credential loader for the whole repo — no key handling is duplicated here.
