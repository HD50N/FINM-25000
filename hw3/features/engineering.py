"""Feature engineering: indicators, log returns, rolling stats."""

import numpy as np
import pandas as pd

from hw3.config import ROLLING_WINDOW_DAYS

FEATURE_COLUMNS = [
    "simple_moving_average_20",
    "exponential_moving_average_12",
    "macd_line",
    "macd_signal_line",
    "average_directional_index",
    "relative_strength_index",
    "bollinger_band_upper",
    "bollinger_band_lower",
    "average_true_range",
    "on_balance_volume",
    "log_return",
    "rolling_mean_close",
    "rolling_std_close",
]


def build_feature_dataframe(price_data: pd.DataFrame) -> pd.DataFrame:
    features = price_data.copy()
    close_prices = features["close"]
    high_prices = features["high"]
    low_prices = features["low"]
    volumes = features["volume"]

    features["simple_moving_average_20"] = close_prices.rolling(ROLLING_WINDOW_DAYS).mean()
    features["exponential_moving_average_12"] = close_prices.ewm(
        span=12, adjust=False
    ).mean()
    exponential_moving_average_26 = close_prices.ewm(span=26, adjust=False).mean()
    features["macd_line"] = (
        features["exponential_moving_average_12"] - exponential_moving_average_26
    )
    features["macd_signal_line"] = features["macd_line"].ewm(span=9, adjust=False).mean()

    price_change = close_prices.diff()
    average_gain = price_change.clip(lower=0).rolling(14).mean()
    average_loss = (-price_change.clip(upper=0)).rolling(14).mean()
    relative_strength = average_gain / average_loss
    features["relative_strength_index"] = 100 - (100 / (1 + relative_strength))

    bollinger_middle = close_prices.rolling(ROLLING_WINDOW_DAYS).mean()
    bollinger_std = close_prices.rolling(ROLLING_WINDOW_DAYS).std()
    features["bollinger_band_upper"] = bollinger_middle + 2 * bollinger_std
    features["bollinger_band_lower"] = bollinger_middle - 2 * bollinger_std

    true_range = pd.concat(
        [
            high_prices - low_prices,
            (high_prices - close_prices.shift()).abs(),
            (low_prices - close_prices.shift()).abs(),
        ],
        axis=1,
    ).max(axis=1)
    features["average_true_range"] = true_range.rolling(14).mean()

    plus_directional_move = high_prices.diff()
    minus_directional_move = -low_prices.diff()
    plus_directional_move = plus_directional_move.where(
        (plus_directional_move > minus_directional_move) & (plus_directional_move > 0),
        0.0,
    )
    minus_directional_move = minus_directional_move.where(
        (minus_directional_move > plus_directional_move) & (minus_directional_move > 0),
        0.0,
    )
    average_true_range_14 = true_range.rolling(14).mean()
    plus_directional_indicator = 100 * plus_directional_move.rolling(14).mean() / average_true_range_14
    minus_directional_indicator = (
        100 * minus_directional_move.rolling(14).mean() / average_true_range_14
    )
    directional_index = (
        (plus_directional_indicator - minus_directional_indicator).abs()
        / (plus_directional_indicator + minus_directional_indicator)
        * 100
    )
    features["average_directional_index"] = directional_index.rolling(14).mean()

    volume_direction = close_prices.diff().apply(
        lambda change: 1 if change > 0 else (-1 if change < 0 else 0)
    )
    features["on_balance_volume"] = (volume_direction * volumes).cumsum()

    features["log_return"] = np.log(close_prices / close_prices.shift(1))
    features["rolling_mean_close"] = close_prices.rolling(ROLLING_WINDOW_DAYS).mean()
    features["rolling_std_close"] = close_prices.rolling(ROLLING_WINDOW_DAYS).std()

    return features


def create_next_day_positive_return_target(price_data: pd.DataFrame) -> pd.Series:
    next_day_return = price_data["close"].pct_change().shift(-1)
    return (next_day_return > 0).astype(int)
