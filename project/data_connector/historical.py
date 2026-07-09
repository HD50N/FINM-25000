"""Download daily OHLCV bars from Alpaca for the whole universe."""

from datetime import datetime, timedelta

import pandas as pd
from alpaca.data.enums import DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from hw1.data_connector.config import get_alpaca_credentials


def fetch_daily_bars_for_universe(
    symbols: list[str], days: int = 120
) -> dict[str, pd.DataFrame]:
    """Return a dict of symbol -> daily OHLCV DataFrame."""
    api_key, secret_key = get_alpaca_credentials()
    client = StockHistoricalDataClient(api_key, secret_key)

    end = datetime.now()
    start = end - timedelta(days=days * 2 + 30)

    request = StockBarsRequest(
        symbol_or_symbols=[s.upper() for s in symbols],
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
        feed=DataFeed.IEX,
    )

    df = client.get_stock_bars(request).df
    if df.empty:
        return {}

    bars = {}
    for symbol in symbols:
        symbol = symbol.upper()
        if symbol not in df.index.get_level_values("symbol"):
            continue
        symbol_df = df.xs(symbol, level="symbol")
        symbol_df.index = pd.to_datetime(symbol_df.index)
        bars[symbol] = symbol_df.sort_index().tail(days)

    return bars
