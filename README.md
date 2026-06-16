# Mini Market Data Terminal (Alpaca)

A Python application that connects to [Alpaca](https://alpaca.markets/) paper-trading market data, downloads historical OHLCV bars, streams real-time bid/ask quotes, and displays everything in a simple desktop UI.

## Features

- **Data connector module** — loads API keys from environment variables, fetches historical bars, and streams live quotes/trades over WebSocket
- **Historical chart** — 30 days of 5-minute OHLCV candlesticks with volume (matplotlib + mplfinance)
- **Live quote UI** — Tkinter terminal with ticker input, bid, ask, last trade, and automatic updates

## Project Structure

```
FINM-25000/
├── data_connector/          # Alpaca API integration
│   ├── config.py            # Environment-based authentication
│   ├── historical.py        # Historical OHLCV bar downloads
│   └── streaming.py         # Real-time quote/trade WebSocket stream
├── app/
│   └── terminal.py          # Tkinter UI (live quotes + historical chart)
├── screenshots/             # UI screenshot for submission
├── main.py                  # Application entry point
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd FINM-25000
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Alpaca API keys

1. Sign up for a free [Alpaca paper trading account](https://app.alpaca.markets/signup).
2. Copy your **Paper** API Key ID and Secret Key from the dashboard.
3. Create a `.env` file from the example:

```bash
cp .env.example .env
```

4. Edit `.env` and paste your keys:

```
ALPACA_API_KEY=PK...
ALPACA_SECRET_KEY=...
ALPACA_API_BASE_URL=https://paper-api.alpaca.markets/v2
```

The app authenticates against the **paper trading API** at `https://paper-api.alpaca.markets/v2`. Historical bars and live quotes are fetched from Alpaca's market data API (`https://data.alpaca.markets`) using the same paper API keys.

### 3. Run the terminal

```bash
python main.py
```

## Usage

### Live Quotes tab

1. Enter a ticker (e.g. `AAPL`, `TSLA`, `SPY`).
2. Click **Subscribe** to start streaming bid/ask quotes and last trade price.
3. Values update automatically as new market data arrives (during market hours).
4. Click **Stop** to end the stream.

### Historical Chart tab

1. Enter a ticker symbol.
2. Click **Load Chart** to download 30 days of 5-minute OHLCV bars.
3. Use the matplotlib toolbar to pan and zoom the candlestick chart.

## Demo Video Checklist

Record a 2–5 minute video showing:

1. The UI launching (`python main.py`)
2. Loading a historical chart for a symbol
3. Subscribing to live quotes and watching bid/ask/last trade update

## Screenshot

Add a screenshot of the running UI to `screenshots/ui_screenshot.png` before submitting.

## Grading Rubric Alignment

| Component | Implementation |
|-----------|----------------|
| Authentication | `data_connector/config.py` loads keys from `.env` |
| Historical data | `data_connector/historical.py` — 30 days, 5-min bars |
| Historical chart | Historical tab — candlestick + volume chart |
| Real-time streaming | `data_connector/streaming.py` — WebSocket quotes/trades |
| Live UI | Live Quotes tab — bid, ask, last trade, auto-update |
| Code organization | Separate `data_connector` and `app` modules |
| GitHub repo | README, requirements.txt, code, screenshot |

## Dependencies

- [alpaca-py](https://github.com/alpacahq/alpaca-py) — Alpaca Market Data API
- [python-dotenv](https://github.com/theskumar/python-dotenv) — Environment variable loading
- [pandas](https://pandas.pydata.org/) — Data handling
- [matplotlib](https://matplotlib.org/) / [mplfinance](https://github.com/matplotlib/mplfinance) — OHLCV charts
- **tkinter** — Included with standard Python installations

## License

Educational project for FINM-25000.
