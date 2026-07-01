# FINM-25000 — Market Data Terminal & Backtesting

Acknowledgements: with the permission of the professor, AI was used to assist with the assignment, help debug the code, and provide conceptual explanations.

## Project layout

```
├── app/          # Shared Tkinter UI
├── hw1/          # HW1 source code
├── hw2/          # HW2 source code
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
