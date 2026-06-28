"""Download historical OHLCV bars from Alpaca."""

from datetime import datetime, timedelta

import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.data.enums import DataFeed

from .config import get_alpaca_credentials


def fetch_historical_bars(symbol: str, days: int = 30) -> pd.DataFrame:
    api_key, secret_key = get_alpaca_credentials()
    client = StockHistoricalDataClient(api_key, secret_key)

    end = datetime.now()

    request = StockBarsRequest(
        symbol_or_symbols=symbol.upper(),
        timeframe=TimeFrame(5, TimeFrameUnit.Minute),
        start=end - timedelta(days=days * 2 + 10),
        end=end,
        feed=DataFeed.IEX,
    )

    df = client.get_stock_bars(request).df
    if df.empty:
        return df

    if isinstance(df.index, pd.MultiIndex):
        df = df.xs(symbol.upper(), level="symbol")

    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    trading_dates = pd.Index(df.index.normalize().unique()).sort_values()
    keep_dates = trading_dates[-days:]
    df = df[df.index.normalize().isin(keep_dates)]

    return df


def fetch_daily_bars(symbol: str, years: int = 5) -> pd.DataFrame:
    api_key, secret_key = get_alpaca_credentials()
    client = StockHistoricalDataClient(api_key, secret_key)

    end = datetime.now()
    start = end - timedelta(days=years * 365 + 30)

    request = StockBarsRequest(
        symbol_or_symbols=symbol.upper(),
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
        feed=DataFeed.IEX,
    )

    df = client.get_stock_bars(request).df
    if df.empty:
        return df

    if isinstance(df.index, pd.MultiIndex):
        df = df.xs(symbol.upper(), level="symbol")

    df.index = pd.to_datetime(df.index)
    return df.sort_index()
