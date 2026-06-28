# Mini Market Data Terminal

FINM-25000 assignment: connect to Alpaca, download historical OHLCV data, stream live bid/ask quotes, and display in a Tkinter UI.

Acknowledgements: with the permission of the professor, AI was used to assist with the assignment, help debug the code, and provide conceptual explanations.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your Alpaca paper API keys
python main.py
```

Get paper API keys from https://app.alpaca.markets/paper/dashboard/overview

## What it does

- **Live Quotes tab** — enter a ticker, click Subscribe, see bid/ask/last trade update automatically
- **Historical Chart tab** — enter a ticker, click Load Chart, see 30 days of 5-minute OHLCV

## Backtesting (Part 2)

```bash
python run_backtest.py --symbol AAPL
```

Downloads 5 years of daily OHLCV from Alpaca, runs 3 strategies plus buy & hold, saves charts to `charts/`, and prints the metrics table for your report.
