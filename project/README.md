# Final Project — Alpaca Systematic Trading System

A complete, end-to-end systematic trading system built on Alpaca's **paper
trading** environment. A live data pipeline pulls quotes and bars from Alpaca,
a trend-following strategy generates signals, a risk module sizes and limits
positions, a trading engine turns targets into paper orders, and a Tkinter UI
monitors and controls the whole system.

**Paper trading only.** Every order goes through
`TradingClient(api_key, secret_key, paper=True)`. No real-money account, no
credit card, no live capital is ever touched.

This README covers the system as a whole: how it maps to the assignment, the
architecture, the design decisions and their justifications, and how to run
it. Each subpackage has its own README with module-level detail:

| Module | README | Responsibility |
|--------|--------|----------------|
| `data_connector/` | [README](data_connector/README.md) | Quotes and bars from Alpaca, quote logging |
| `strategies/` | [README](strategies/README.md) | Signal generation (trend following) |
| `risk/` | [README](risk/README.md) | Position sizing, stop-losses, daily loss halt |
| `execution/` | [README](execution/README.md) | Order routing via Alpaca paper API |
| `engine/` | [README](engine/README.md) | Live trading loop tying it all together |
| `backtest/` | [README](backtest/README.md) | Historical simulation and metrics |
| `ui/` | [README](ui/README.md) | Paper Trading and Project Backtest tabs |
| `tests/` | [README](tests/README.md) | Offline unit tests for strategy and risk |

---

## How this maps to the assignment

| Assignment requirement | Where it is implemented |
|---|---|
| Systematic strategy (rule-based, no discretion) | `strategies/momentum.py` — deterministic SMA crossover rules |
| Live data pipeline collecting quotes from Alpaca | `data_connector/quotes.py` — fetched every cycle, logged to CSV with timestamps/prices/volumes |
| Trading engine turning signals into orders | `engine/live_engine.py` + `execution/broker.py` |
| UI to monitor and control the system | `ui/dashboard.py`, embedded as two tabs in `app/terminal.py` |
| Paper trading only | `execution/broker.py` hard-codes `paper=True`; there is no code path to a live account |
| Universe of 5–20 tickers | `config.py` `UNIVERSE` — 10 liquid large-caps plus SPY |
| Secure API key handling | Keys come from `.env` via `hw1/data_connector/config.py`; `.env` is gitignored, `.env.example` has placeholders |
| Structured data storage | pandas DataFrames in memory; quotes appended to daily CSVs in `logs/` |
| Position sizing and risk limits | `risk/limits.py` — per-asset cap, gross exposure cap, stop-loss, daily loss halt |
| Order states and error handling | Engine logs submitted → polls to filled / partially_filled / canceled; rejects invalid qty/side; catches API errors per order |
| Backtest mode and paper trading mode | `run_backtest.py` / `run_live.py` (or the two UI tabs) |
| Config for tickers, parameters, limits | `config.py` — flat settings file with `validate_config()` on import |
| Logging of data, signals, orders, P&L | `logs/quotes_YYYYMMDD.csv` (data) and `logs/engine.log` (events) |
| Performance metrics (P&L, drawdown, trades, hit rate) | Live UI: P&L, drawdown from peak, trades, hit rate. Backtest: `backtest/metrics.py` |
| Tests | `tests/` — 11 offline unit tests |
| Video walkthrough | Recorded separately by the group (see repo root for prior HW video placement, `hw3/Video/`) |

## Architecture

```
                  ┌────────────────────────────────────────────┐
                  │        app/terminal.py (Tkinter UI)        │
                  │  Paper Trading tab      Project Backtest   │
                  └───────────┬───────────────────┬────────────┘
                              │ start/stop         │ run
                              ▼                    ▼
                  ┌───────────────────┐  ┌───────────────────┐
                  │ engine/           │  │ backtest/         │
                  │ LiveTradingEngine │  │ engine + metrics  │
                  └──┬──────┬──────┬──┘  └───────┬───────────┘
                     │      │      │             │
        ┌────────────┘      │      └──────────┐  │
        ▼                   ▼                 ▼  ▼
┌───────────────┐  ┌───────────────┐  ┌────────────────────────┐
│ data_connector│  │ risk/limits   │  │ strategies/momentum    │
│ quotes + bars │  │ sizing, stops │  │ SMA crossover signals  │
└───────┬───────┘  └───────────────┘  └────────────────────────┘
        │                  ▲
        ▼                  │ orders
┌───────────────┐  ┌───────┴───────┐
│  Alpaca data  │  │ execution/    │
│  API (IEX)    │  │ AlpacaBroker  │──► Alpaca paper trading API
└───────────────┘  └───────────────┘
```

The dependency direction is strictly one-way: the UI knows about the engine,
the engine knows about data/strategy/risk/execution, and those leaf modules
know nothing about each other (risk and strategy are pure functions over
plain data). This is what makes each piece independently testable and lets
backtest and live trading share code.

### One live cycle (every `CYCLE_SECONDS`, default 60s)

1. **Data** — fetch the latest quote and trade for every symbol in the
   universe and append them to `logs/quotes_YYYYMMDD.csv`; fetch recent daily
   bars for signal computation.
2. **Signals** — compute the 0/1 trend signal per symbol from the daily bars.
3. **Risk** — check the daily loss halt (liquidate everything and stop
   trading for the day if breached), then apply per-position stop-losses,
   then size the surviving signals into dollar targets under the exposure
   caps.
4. **Execution** — diff target quantities against actual Alpaca positions
   and submit market orders only for the difference (idempotent: if nothing
   changed, nothing is sent).
5. **Monitoring** — update a thread-safe snapshot (equity, cash, cumulative
   P&L, trade count, hit rate, positions, signals, orders, events) that the
   UI polls once per second.

## Design decisions and justification

**Why a new `project/` package instead of spreading code around.** The
assignment explicitly asks for a clear folder structure with separate
modules for data, strategy, execution, risk, and UI. The repo already
follows a one-folder-per-assignment layout (`hw1/`, `hw2/`, `hw3/`), so the
final project gets the same treatment, with the assignment's suggested
subfolder names.

**Why the strategy is a daily SMA crossover.** The assignment allows any
rule-based strategy and asks for documented intuition. A 20/50-day crossover
is (a) genuinely systematic — zero discretion, two parameters, (b) directly
in the lineage of HW2's trend-following work, so it fits the course arc, and
(c) simple enough that the interesting engineering (pipeline, risk, engine,
UI) stays in focus. The signal is shifted one bar to eliminate look-ahead —
the same convention `hw2/strategies/trend_following.py` uses. See
[strategies/README.md](strategies/README.md) for the market intuition.

**Why REST polling instead of the WebSocket stream for the live loop.** The
strategy trades off *daily* bars, so decisions change at most once a day; a
60-second polling loop is far more data than the strategy needs. Polling
also makes the engine loop deterministic and easy to reason about (one
cycle = one function call), avoids managing a long-lived socket across
market hours, and sidesteps Alpaca's one-connection-per-account WebSocket
limit — the existing Live Quotes tab (HW1) already owns a `StockDataStream`,
and running a second one in the same process would conflict. The HW1
streaming code remains in the UI for real-time quote display.

**Why long-only with no leverage.** The repo's paper trading was deliberately
switched from buying power to cash (commit `7689df1`, "Switched paper trading
from Buying Power to Cash (no leverage)"). The project keeps that constraint:
sizing works from equity with a 95% gross cap, so the system never borrows.

**Why market orders.** Rebalances are small relative to the liquidity of the
chosen universe (mega-cap stocks and SPY), fills are immediate, and order
state handling stays simple (`accepted → filled`). This matches
`hw3/paper_trade.py`. Limit orders are listed as a known improvement.

**Why target-position rebalancing instead of buy/sell event streams.** The
engine computes *target* quantities each cycle and submits only the diff
versus actual Alpaca positions. This makes cycles idempotent and
self-healing: if an order is rejected, or the process restarts, the next
cycle re-derives the correct orders from broker state rather than from
fragile local bookkeeping.

**Why backtest and live share the risk module.** `backtest/engine.py` calls
the exact same `risk.limits.size_positions` as the live engine. A backtest
that sizes positions differently from production is not evidence about
production; sharing the code closes that gap.

**Why Tkinter for the UI.** The assignment allows any lightweight GUI
toolkit. The repo already has a shared Tkinter terminal (`app/terminal.py`)
with one tab per assignment, and every previous assignment integrated with
it. The project adds two tabs (Paper Trading, Project Backtest) rather than
introducing a second UI stack (Streamlit/Dash) that would fragment the
codebase. The tab widgets live in `project/ui/` so the UI remains a separate
module per the assignment, and `app/terminal.py` only instantiates them.

**Why a snapshot-polling UI rather than callbacks.** The engine thread
writes a snapshot dict under a lock; the Tk thread reads it on a 1-second
`after()` timer. This mirrors the queue-plus-`_poll()` pattern already in
`app/terminal.py` and keeps every Tk widget mutation on the main thread,
which Tkinter requires.

**Why plain CSVs and a text log for storage.** The assignment asks for
structured storage and basic logging; daily CSV files with a fixed header
(`timestamp, symbol, bid, ask, last, volume`) are structured, append-only,
inspectable with pandas, and require no database dependency. Engine events go
to `logs/engine.log` with the same `[YYYY-MM-DD HH:MM:SS] message` format as
`hw3/paper_trade.py`.

## Consistency with the existing codebase

The project deliberately reuses the repo's established conventions:

- **Credentials**: everything goes through
  `hw1/data_connector/config.py:get_alpaca_credentials()` — one `.env`, one
  loader, no duplicated key handling.
- **Module style**: small function-based modules with a one-line docstring
  header and type hints; classes only where state demands it
  (`AlpacaBroker`, `LiveTradingEngine`, the Tk frames — same as HW1's
  `QuoteStreamer` and the terminal).
- **Folder shape**: `data_connector/`, `strategies/`, `backtest/`, `viz/`
  mirror `hw2/` and `hw3/`; `risk/`, `execution/`, `engine/`, `ui/`,
  `tests/` are added per the assignment spec.
- **Config**: a flat `config.py` of UPPER_CASE constants, like `hw3/config.py`.
- **Entry points**: `run_backtest.py` / `run_live.py` insert the repo root
  into `sys.path`, exactly like `main.py` and `hw3/run_backtest.py`.
- **Backtest/metrics/runner split** and the formatted metrics table follow
  `hw2/backtest/` and `hw3/backtest/`.
- **Threading**: background worker with a `threading.Event`/lock and a
  polling UI, following `hw1/data_connector/streaming.py` and
  `app/terminal.py`.

## Configuration

All knobs live in `config.py`:

| Setting | Default | Meaning |
|---|---|---|
| `UNIVERSE` | 10 tickers | Assets the system trades |
| `FAST_WINDOW_DAYS` / `SLOW_WINDOW_DAYS` | 20 / 50 | SMA crossover windows |
| `MAX_POSITION_FRACTION` | 0.15 | Max fraction of equity per asset |
| `MAX_GROSS_EXPOSURE` | 0.95 | Max total invested fraction (no leverage) |
| `STOP_LOSS_FRACTION` | 0.05 | Per-position stop-loss from entry |
| `MAX_DAILY_LOSS_FRACTION` | 0.03 | Daily equity loss that halts trading |
| `CYCLE_SECONDS` | 60 | Live cycle interval |
| `BACKTEST_YEARS` | 5 | Backtest lookback |
| `INITIAL_CAPITAL` | 100,000 | Backtest starting equity |

API keys are **never** configured here — they come from `.env`
(`ALPACA_API_KEY`, `ALPACA_SECRET_KEY`), which is gitignored. Copy
`.env.example` and fill in paper keys from the Alpaca dashboard.

## Running the system

```bash
# from the repo root, with .venv active and .env populated
python main.py                    # UI: Paper Trading / Project Backtest tabs
python project/run_live.py        # headless paper trading loop (Ctrl-C to stop)
python project/run_backtest.py    # metrics to stdout, charts to project/charts/
python -m pytest project/tests    # offline unit tests
```

## Example backtest results

Five years of daily IEX bars over the default universe (run July 2026):

```
                  Return    CAGR Volatility Sharpe Max Drawdown Trades Win Rate
Trend Following   51.53%   8.68%     15.44%   0.62      -25.76%    275   42.65%
Equal Weight B&H  78.13%  12.26%     21.92%   0.64      -43.02%      0    0.00%
```

The pattern is the classic trend-following trade-off: the strategy gives up
absolute return versus buy-and-hold in a strong bull market but earns a
similar Sharpe with markedly lower volatility (15% vs 22%) and a much
shallower maximum drawdown (−26% vs −43%), because it steps into cash when
trends break. Charts are saved to `project/charts/`
(`equity_curve.png`, `drawdown.png`, `exposure.png`).

## Limitations and possible improvements

- **Market orders only.** Limit orders would control slippage on rebalances;
  order-state handling would then need to manage partial fills and timeouts.
- **Daily signals.** Intraday information only enters through the stop-loss
  check on live quotes; an intraday strategy would need the WebSocket stream.
- **Idealized backtest fills.** Trades fill at the daily close with no
  slippage or spread (Alpaca is commission-free, so no commissions is
  accurate).
- **IEX data feed.** The free feed covers a subset of consolidated volume;
  fine for signals on liquid names, not for microstructure work.
- **In-memory trade history.** Hit rate and trade counts reset when the
  engine restarts; a SQLite trade journal would persist them.
- **Single strategy.** The module layout supports multiple strategies
  (`strategies/` is a package); a next step is combining trend with
  mean-reversion sleeves.
