"""Strategy 1: Trend Following."""

import pandas as pd


def generate_signals(df: pd.DataFrame) -> pd.Series:
    position = 0
    signals = []

    for _, row in df.iterrows():
        if position == 0:
            if row["macd"] > row["macd_signal"] and row["adx"] > 25:
                position = 1
        elif row["macd"] < row["macd_signal"]:
            position = 0
        signals.append(position)

    return pd.Series(signals, index=df.index).shift(1).fillna(0).astype(int)
