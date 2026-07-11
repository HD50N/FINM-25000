# FINM-25000 — Assignments and Project Overview

Acknowledgements: with the permission of the professor, AI was used to assist with the assignments and project, help debug the code, and provide conceptual explanations.

## Project layout

```
├── app/          # Shared Tkinter UI
├── hw1/          # HW1 source code
├── hw2/          # HW2 source code
├── hw3/          # HW3 source code
├── project/      # Final project: systematic trading system
├── main.py       # Run the UI
├── requirements.txt
└── .env          # Alpaca API keys (shared)
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your Alpaca paper API keys
```

Get paper API keys from https://app.alpaca.markets/paper/dashboard/overview

## Run

```bash
python main.py
```

| Tab | Assignment | Description |
|-----|------------|-------------|
| Live Quotes | HW1 | Stream bid/ask/last trade |
| Historical Chart | HW1 | 30 days of 5-minute OHLCV |
| Backtesting | HW2 | Run 3 strategies, view charts and metrics |
| ML Backtest | HW3 | Run ML pipeline, view charts and metrics |
| Paper Trading | Final Project | Start/stop the live trading engine, monitor positions, P&L, orders |
| Project Backtest | Final Project | Backtest the project strategy over the universe |

---

## HW1 — Mini Market Data Terminal

Connect to Alpaca, stream live bid/ask quotes, and chart 30 days of 5-minute OHLCV data.

### Source code

- `hw1/data_connector/` — Alpaca auth, live quote streaming, 5-minute historical bars

### UI tabs

| Tab | Description |
|-----|-------------|
| Live Quotes | Enter a ticker, click Subscribe, see bid/ask/last trade update automatically |
| Historical Chart | Enter a ticker, click Load Chart, see 30 days of 5-minute OHLCV |

### Submission

- Screenshot: `hw1/screenshots/UI_Screenshot.png`

---

## HW2 — Technical Indicators & Strategy Backtesting

Download 5 years of daily OHLCV data, compute technical indicators, backtest 3 strategies, and compare performance.

### Source code

- `hw2/data_connector/` — 5-year daily OHLCV fetch
- `hw2/indicators/` — SMA, EMA, MACD, ADX, RSI, Bollinger Bands, OBV
- `hw2/strategies/` — Trend Following, Mean Reversion, Custom
- `hw2/backtest/` — Engine, metrics, runner
- `hw2/viz/` — Chart builders for the UI

### Run

```bash
python main.py
```

Open the **Backtesting** tab to view charts and metrics in the UI.

Or print metrics to the terminal (for your report):

```bash
python hw2/run_backtest.py --symbol AAPL
```

---

## HW3 — Machine Learning Trading Signal (Paper Trading Only)

Download 5 years of daily data, engineer features, apply PCA, train an ML model, backtest, and submit **paper trades only**.

### Source code

- `hw3/data_connector/` — 5-year daily OHLCV fetch
- `hw3/features/` — indicators, log returns, rolling mean/std
- `hw3/pca/` — standardize features and PCA (≥80% variance)
- `hw3/model/` — ML model and signal generation
- `hw3/backtest/` — engine, metrics, runner
- `hw3/viz/` — equity curve, drawdown, PCA variance charts
- `hw3/paper_trade.py` — Alpaca **paper** trading demo

### Run

```bash
python main.py
```

Open the **ML Backtest** tab, enter a ticker, and click **Run ML Backtest**.

Or save charts to disk and print metrics:

```bash
python hw3/run_backtest.py --symbol AAPL
```

Charts are saved to `hw3/charts/`.

### Run paper trading demo

```bash
python hw3/paper_trade.py --symbol AAPL
```


---

## Final Project — Alpaca Systematic Trading System (Paper Trading Only)

An end-to-end systematic trading system: a live data pipeline pulls quotes from
Alpaca, a trend-following strategy generates signals, a risk module sizes and
limits positions, and a trading engine turns targets into paper orders. The
Tkinter UI monitors and controls the whole system.

Video link: https://youtu.be/lDtsqweuH74

**Paper trading only — no real money is ever used** (`TradingClient(..., paper=True)`).

This section is the overview; **[`project/README.md`](project/README.md)** has
the full documentation — the assignment-requirement mapping, every design
decision with its justification, configuration reference, and example results
— and each subpackage (`data_connector/`, `strategies/`, `risk/`,
`execution/`, `engine/`, `backtest/`, `ui/`, `tests/`) has its own README
with module-level detail.

### Architecture

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
└───────┬───────┘  └───────┬───────┘  └────────────────────────┘
        │                  │
        ▼                  ▼ orders
┌───────────────┐  ┌───────────────┐
│  Alpaca data  │  │ execution/    │
│  API (IEX)    │  │ AlpacaBroker  │──► Alpaca paper trading API
└───────────────┘  └───────────────┘
```

Each live cycle (every 60s): fetch latest quotes for the universe (logged to
`project/logs/quotes_YYYYMMDD.csv`) and daily bars → compute signals → apply
stop-losses and the daily loss halt → size target positions → submit market
orders for the difference between target and current holdings → update the UI
snapshot (positions, P&L, orders, events). All events are also appended to
`project/logs/engine.log`.

### Source code

- `project/config.py` — universe, strategy parameters, risk limits
- `project/data_connector/` — latest quotes (with CSV logging) and daily bars for the universe
- `project/strategies/` — trend-following SMA crossover signals
- `project/risk/` — position sizing, stop-losses, daily loss halt
- `project/execution/` — Alpaca paper order routing and order status
- `project/engine/` — live trading loop (data → signals → risk → orders)
- `project/backtest/` — portfolio backtest engine, metrics, runner
- `project/viz/` — equity curve, drawdown, exposure charts
- `project/ui/` — Paper Trading and Project Backtest tabs
- `project/tests/` — strategy and risk unit tests (no network)

### Strategy

Trend-following moving average crossover on a 10-stock universe: hold a stock
while its 20-day SMA is above its 50-day SMA, otherwise stay in cash. Signals
are shifted one bar so a crossover observed at today's close is traded
tomorrow (no look-ahead). The intuition: prices trend because information
diffuses gradually and investors herd, so recent strength tends to persist. The strategy should generate returns because it attempts to participate during sustained upward trends while moving to cash when the trend weakens. Although we made the signal simple, by integrating the risk control parameters below into the strategy, we believe we could capture the opportunities more safely, generating more consistent, disciplined revenue.

### Risk controls

- Long-only, no leverage, no shorts
- Max 15% of equity per asset (`MAX_POSITION_FRACTION`)
- Max 95% of equity invested in total (`MAX_GROSS_EXPOSURE`)
- 5% stop-loss from entry price per position (`STOP_LOSS_FRACTION`)
- 3% daily loss limit: the engine liquidates and halts for the day (`MAX_DAILY_LOSS_FRACTION`)

All limits live in `project/config.py`. The backtest reuses the same
`risk/limits.py` sizing code as live trading.

### Run

```bash
python main.py                    # UI: use the Paper Trading / Project Backtest tabs
python project/run_live.py        # headless paper trading loop (Ctrl-C to stop)
python project/run_backtest.py    # backtest: prints metrics, saves charts to project/charts/
python -m pytest project/tests    # unit tests
```

### Modes

- **Backtest** — 5 years of daily bars, daily-rebalanced portfolio vs. an
  equal-weight buy-and-hold benchmark (return, CAGR, volatility, Sharpe, max
  drawdown, trade count, win rate).
- **Paper trading** — live loop against the Alpaca paper account. The UI shows
  system status (running/stopped, connected/disconnected, halted), positions,
  cumulative P&L, trade count, hit rate, and an event log.

### Limitations and possible improvements

- The strategy itself is intentionally simple. It relies on a single moving-average crossover and therefore may underperform in sideways markets.
- The project is designed exclusively for Alpaca's paper trading environment and makes market orders only, increasing the likelihood of slippage.
- The backtesting system currently ignores commission and slippage (Alpaca is commission-free, but fills are idealized at the close), which makes returns misleading, especially for strategies that execute trades at higher frequency.
- Signals use daily bars, so intraday moves only matter through the stop-loss.

- Incorporating limit orders would reduce slippage on rebalances.
- We could also implement additional trading strategies, expand the risk management framework, support multiple brokers, and add larger universes of assets.
- Possible additional improvements: volatility-scaled position sizing, a short leg,
  persistent trade database
