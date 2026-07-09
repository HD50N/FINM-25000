"""Final project settings. Change these to customize the trading system."""

# Universe of assets the system trades (5-20 tickers).
UNIVERSE = [
    "AAPL",
    "MSFT",
    "GOOGL",
    "AMZN",
    "NVDA",
    "META",
    "JPM",
    "XOM",
    "JNJ",
    "SPY",
]

# Strategy parameters (trend-following moving average crossover).
FAST_WINDOW_DAYS = 20
SLOW_WINDOW_DAYS = 50

# Risk limits.
MAX_POSITION_FRACTION = 0.15   # max fraction of equity in any single asset
MAX_GROSS_EXPOSURE = 0.95      # max fraction of equity invested across all assets
STOP_LOSS_FRACTION = 0.05      # exit a position after a 5% loss from entry
MAX_DAILY_LOSS_FRACTION = 0.03 # halt trading after a 3% equity loss in one day

# Live engine.
CYCLE_SECONDS = 60             # seconds between live trading cycles
BAR_HISTORY_DAYS = 120         # daily bars fetched per symbol for signals

# Backtest.
BACKTEST_YEARS = 5
INITIAL_CAPITAL = 100_000

LOGS_DIRECTORY = "project/logs"
CHARTS_DIRECTORY = "project/charts"
