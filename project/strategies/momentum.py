"""Trend-following strategy: fast/slow moving average crossover.

Intuition: prices trend because information diffuses gradually and investors
herd. When the fast moving average is above the slow one the trend is up and
we hold the asset; otherwise we stay in cash. Long-only, no leverage.
"""

import pandas as pd

from project.config import FAST_WINDOW_DAYS, SLOW_WINDOW_DAYS


def generate_signals(
    df: pd.DataFrame,
    fast_window: int = FAST_WINDOW_DAYS,
    slow_window: int = SLOW_WINDOW_DAYS,
) -> pd.Series:
    """Return a 0/1 series: 1 while the fast SMA is above the slow SMA.

    Signals are shifted one bar so a crossover observed at the close of day t
    is traded on day t+1 (no look-ahead).
    """
    fast_sma = df["close"].rolling(fast_window).mean()
    slow_sma = df["close"].rolling(slow_window).mean()
    signals = (fast_sma > slow_sma).astype(int)
    return signals.shift(1).fillna(0).astype(int)


def latest_signal(df: pd.DataFrame) -> int:
    """Return the current signal (0 or 1) using the most recent closed bars."""
    if len(df) < SLOW_WINDOW_DAYS:
        return 0
    fast_sma = df["close"].rolling(FAST_WINDOW_DAYS).mean().iloc[-1]
    slow_sma = df["close"].rolling(SLOW_WINDOW_DAYS).mean().iloc[-1]
    return int(fast_sma > slow_sma)
