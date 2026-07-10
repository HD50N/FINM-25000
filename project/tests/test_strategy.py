"""Strategy tests using synthetic price data (no network)."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project.strategies.momentum import generate_signals, latest_signal


def make_price_df(prices: list[float]) -> pd.DataFrame:
    index = pd.bdate_range("2024-01-01", periods=len(prices))
    return pd.DataFrame({"close": prices}, index=index)


def test_uptrend_produces_long_signal() -> None:
    df = make_price_df(list(np.linspace(100, 200, 120)))
    signals = generate_signals(df)
    assert signals.iloc[-1] == 1
    assert latest_signal(df) == 1


def test_downtrend_produces_flat_signal() -> None:
    df = make_price_df(list(np.linspace(200, 100, 120)))
    signals = generate_signals(df)
    assert signals.iloc[-1] == 0
    assert latest_signal(df) == 0


def test_signals_are_shifted_no_lookahead() -> None:
    df = make_price_df(list(np.linspace(100, 200, 120)))
    signals = generate_signals(df)
    fast = df["close"].rolling(20).mean()
    slow = df["close"].rolling(50).mean()
    unshifted = (fast > slow).astype(int)
    assert signals.equals(unshifted.shift(1).fillna(0).astype(int))


def test_short_history_returns_flat() -> None:
    df = make_price_df(list(np.linspace(100, 110, 30)))
    assert latest_signal(df) == 0
