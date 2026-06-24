"""Download historical OHLCV bars from Alpaca."""

from datetime import datetime, timedelta

import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

from .config import get_alpaca_credentials


def fetch_historical_bars(symbol: str, days: int = 30) -> pd.DataFrame:
    api_key, secret_key = get_alpaca_credentials()
    client = StockHistoricalDataClient(api_key, secret_key)

    request = StockBarsRequest(
        symbol_or_symbols=symbol.upper(),
        timeframe=TimeFrame(5, TimeFrameUnit.Minute),
        start=datetime.now() - timedelta(days=days),
        end=datetime.now(),
    )

    df = client.get_stock_bars(request).df
    if df.empty:
        return df

    if isinstance(df.index, pd.MultiIndex):
        df = df.xs(symbol.upper(), level="symbol")

    return df.sort_index()
