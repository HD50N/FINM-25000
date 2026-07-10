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
ORDER_POLL_TIMEOUT_SECONDS = 15  # how long to wait for an order to leave pending_new
ORDER_POLL_INTERVAL_SECONDS = 0.5

# Backtest.
BACKTEST_YEARS = 5
INITIAL_CAPITAL = 100_000

LOGS_DIRECTORY = "project/logs"
CHARTS_DIRECTORY = "project/charts"


def validate_config() -> None:
    """Raise ValueError if any setting is invalid (bad types, ranges, or relations)."""
    errors: list[str] = []

    if not isinstance(UNIVERSE, list) or not UNIVERSE:
        errors.append("UNIVERSE must be a non-empty list of ticker symbols")
    else:
        if not (5 <= len(UNIVERSE) <= 20):
            errors.append(f"UNIVERSE must have 5–20 tickers (got {len(UNIVERSE)})")
        if len(set(s.upper() for s in UNIVERSE)) != len(UNIVERSE):
            errors.append("UNIVERSE contains duplicate tickers")
        if any(not isinstance(s, str) or not s.strip() for s in UNIVERSE):
            errors.append("UNIVERSE tickers must be non-empty strings")

    if not isinstance(FAST_WINDOW_DAYS, int) or FAST_WINDOW_DAYS < 1:
        errors.append("FAST_WINDOW_DAYS must be a positive integer")
    if not isinstance(SLOW_WINDOW_DAYS, int) or SLOW_WINDOW_DAYS < 1:
        errors.append("SLOW_WINDOW_DAYS must be a positive integer")
    if (
        isinstance(FAST_WINDOW_DAYS, int)
        and isinstance(SLOW_WINDOW_DAYS, int)
        and FAST_WINDOW_DAYS >= SLOW_WINDOW_DAYS
    ):
        errors.append("FAST_WINDOW_DAYS must be strictly less than SLOW_WINDOW_DAYS")

    for name, value in [
        ("MAX_POSITION_FRACTION", MAX_POSITION_FRACTION),
        ("MAX_GROSS_EXPOSURE", MAX_GROSS_EXPOSURE),
        ("STOP_LOSS_FRACTION", STOP_LOSS_FRACTION),
        ("MAX_DAILY_LOSS_FRACTION", MAX_DAILY_LOSS_FRACTION),
    ]:
        if not isinstance(value, (int, float)) or not (0 < value <= 1):
            errors.append(f"{name} must be a number in (0, 1]")

    if (
        isinstance(MAX_POSITION_FRACTION, (int, float))
        and isinstance(MAX_GROSS_EXPOSURE, (int, float))
        and MAX_POSITION_FRACTION > MAX_GROSS_EXPOSURE
    ):
        errors.append("MAX_POSITION_FRACTION cannot exceed MAX_GROSS_EXPOSURE")

    for name, value in [
        ("CYCLE_SECONDS", CYCLE_SECONDS),
        ("BAR_HISTORY_DAYS", BAR_HISTORY_DAYS),
        ("BACKTEST_YEARS", BACKTEST_YEARS),
        ("INITIAL_CAPITAL", INITIAL_CAPITAL),
        ("ORDER_POLL_TIMEOUT_SECONDS", ORDER_POLL_TIMEOUT_SECONDS),
        ("ORDER_POLL_INTERVAL_SECONDS", ORDER_POLL_INTERVAL_SECONDS),
    ]:
        if not isinstance(value, (int, float)) or value <= 0:
            errors.append(f"{name} must be a positive number")

    if (
        isinstance(BAR_HISTORY_DAYS, int)
        and isinstance(SLOW_WINDOW_DAYS, int)
        and BAR_HISTORY_DAYS < SLOW_WINDOW_DAYS
    ):
        errors.append("BAR_HISTORY_DAYS must be at least SLOW_WINDOW_DAYS")

    if not isinstance(LOGS_DIRECTORY, str) or not LOGS_DIRECTORY.strip():
        errors.append("LOGS_DIRECTORY must be a non-empty string")
    if not isinstance(CHARTS_DIRECTORY, str) or not CHARTS_DIRECTORY.strip():
        errors.append("CHARTS_DIRECTORY must be a non-empty string")

    if errors:
        raise ValueError("Invalid project config:\n- " + "\n- ".join(errors))


validate_config()
