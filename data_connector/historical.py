"""Historical OHLCV bar data from Alpaca Market Data API."""

from datetime import datetime, timedelta

import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

from .config import get_alpaca_credentials, get_market_data_url


def get_historical_client() -> StockHistoricalDataClient:
    """Create an authenticated historical data client."""
    api_key, secret_key = get_alpaca_credentials()
    return StockHistoricalDataClient(
        api_key,
        secret_key,
        url_override=get_market_data_url(),
    )


def _build_timeframe(minutes: int) -> TimeFrame:
    if minutes == 1:
        return TimeFrame.Minute
    return TimeFrame(minutes, TimeFrameUnit.Minute)


def fetch_historical_bars(
    symbol: str,
    days: int = 30,
    timeframe_minutes: int = 5,
) -> pd.DataFrame:
    """
    Download historical OHLCV bars for a symbol.

    Args:
        symbol: Stock ticker (e.g. AAPL).
        days: Number of calendar days of history (default 30).
        timeframe_minutes: Bar size in minutes (1 or 5 recommended).

    Returns:
        DataFrame indexed by timestamp with open, high, low, close, volume, trade_count, vwap.
    """
    client = get_historical_client()
    symbol = symbol.upper().strip()
    end = datetime.now()
    start = end - timedelta(days=days)

    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=_build_timeframe(timeframe_minutes),
        start=start,
        end=end,
    )

    bars = client.get_stock_bars(request)
    df = bars.df

    if df.empty:
        return pd.DataFrame()

    if isinstance(df.index, pd.MultiIndex):
        df = df.xs(symbol, level="symbol")

    df.index = pd.to_datetime(df.index)
    df.index.name = "timestamp"
    return df.sort_index()
