"""Convert model probabilities into long/flat signals."""

import numpy as np
import pandas as pd

from hw3.config import LONG_PROBABILITY_THRESHOLD


def probabilities_to_signals(
    probabilities: np.ndarray,
    index: pd.Index,
    probability_threshold: float = LONG_PROBABILITY_THRESHOLD,
) -> pd.Series:
    long_signals = (probabilities > probability_threshold).astype(int)
    return pd.Series(long_signals, index=index)
