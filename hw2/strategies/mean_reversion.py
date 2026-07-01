"""Strategy 2: Mean Reversion."""

import pandas as pd


def generate_signals(df: pd.DataFrame) -> pd.Series:
    position = 0
    signals = []

    for _, row in df.iterrows():
        if position == 0:
            if row["rsi"] < 30 and row["close"] < row["bb_lower"]:
                position = 1
        elif row["rsi"] > 70 and row["close"] > row["bb_upper"]:
            position = 0
        signals.append(position)

    return pd.Series(signals, index=df.index).shift(1).fillna(0).astype(int)
