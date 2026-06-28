"""Strategy 3: Custom (trend + momentum + volume)."""

import pandas as pd


def generate_signals(df: pd.DataFrame) -> pd.Series:
    obv_sma = df["obv"].rolling(20).mean()
    long = (
        (df["close"] > df["sma_20"])
        & (df["rsi"] > 50)
        & (df["obv"] > obv_sma)
    )
    signals = long.astype(int)
    return signals.shift(1).fillna(0).astype(int)
