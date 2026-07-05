"""Train ML pipeline and run backtests."""

import pandas as pd

from hw3.backtest.engine import run_backtest
from hw3.backtest.metrics import compute_metrics
from hw3.config import (
    DATA_YEARS,
    LONG_PROBABILITY_THRESHOLD,
    ML_MODEL_NAME,
    TRAIN_FRACTION,
)
from hw3.data_connector.historical import fetch_daily_bars
from hw3.features.engineering import (
    FEATURE_COLUMNS,
    build_feature_dataframe,
    create_next_day_positive_return_target,
)
from hw3.model.signals import probabilities_to_signals
from hw3.model.trainer import predict_long_probabilities, train_model
from hw3.pca.transform import fit_pca_on_training_features, transform_features_with_pca


def buy_and_hold_signals(price_data: pd.DataFrame) -> pd.Series:
    return pd.Series(1, index=price_data.index)


def format_percentage(value: float) -> str:
    return f"{value * 100:.2f}%"


def format_number(value: float) -> str:
    return f"{value:.2f}"


def train_ml_pipeline(symbol: str) -> dict:
    symbol = symbol.upper()
    price_data = fetch_daily_bars(symbol, years=DATA_YEARS)
    if price_data.empty:
        raise ValueError(f"No data returned for {symbol}")

    feature_data = build_feature_dataframe(price_data)
    target_labels = create_next_day_positive_return_target(price_data)

    model_table = feature_data[FEATURE_COLUMNS].copy()
    model_table["target"] = target_labels
    model_table = model_table.dropna()
    target_labels = model_table["target"]
    feature_matrix = model_table[FEATURE_COLUMNS]

    split_index = int(len(model_table) * TRAIN_FRACTION)
    training_features = feature_matrix.iloc[:split_index]
    testing_features = feature_matrix.iloc[split_index:]
    training_targets = target_labels.iloc[:split_index]
    testing_index = testing_features.index

    pca_bundle = fit_pca_on_training_features(training_features)
    pca_training_components = pca_bundle["pca_training_components"]
    pca_testing_components = transform_features_with_pca(testing_features, pca_bundle)

    machine_learning_model = train_model(
        pca_training_components,
        training_targets.to_numpy(),
        model_name=ML_MODEL_NAME,
    )
    long_probabilities = predict_long_probabilities(
        machine_learning_model,
        pca_testing_components,
    )
    machine_learning_signals = probabilities_to_signals(long_probabilities, testing_index)

    testing_price_data = price_data.loc[testing_index]
    buy_and_hold_result = run_backtest(
        testing_price_data,
        buy_and_hold_signals(testing_price_data),
    )
    machine_learning_result = run_backtest(testing_price_data, machine_learning_signals)

    buy_and_hold_metrics = compute_metrics(buy_and_hold_result)
    machine_learning_metrics = compute_metrics(machine_learning_result)

    metrics_table = pd.DataFrame(
        {
            "Buy & Hold": {
                "Return": format_percentage(buy_and_hold_metrics["total_return"]),
                "CAGR": format_percentage(buy_and_hold_metrics["cagr"]),
                "Volatility": format_percentage(buy_and_hold_metrics["volatility"]),
                "Sharpe": format_number(buy_and_hold_metrics["sharpe"]),
                "Sortino": format_number(buy_and_hold_metrics["sortino"]),
                "Max Drawdown": format_percentage(buy_and_hold_metrics["max_drawdown"]),
                "Win Rate": format_percentage(buy_and_hold_metrics["win_rate"]),
            },
            "ML Signal": {
                "Return": format_percentage(machine_learning_metrics["total_return"]),
                "CAGR": format_percentage(machine_learning_metrics["cagr"]),
                "Volatility": format_percentage(machine_learning_metrics["volatility"]),
                "Sharpe": format_number(machine_learning_metrics["sharpe"]),
                "Sortino": format_number(machine_learning_metrics["sortino"]),
                "Max Drawdown": format_percentage(machine_learning_metrics["max_drawdown"]),
                "Win Rate": format_percentage(machine_learning_metrics["win_rate"]),
            },
        }
    ).T

    return {
        "symbol": symbol,
        "pca_bundle": pca_bundle,
        "machine_learning_model": machine_learning_model,
        "training_features": training_features,
        "testing_price_data": testing_price_data,
        "machine_learning_signals": machine_learning_signals,
        "long_probabilities": long_probabilities,
        "buy_and_hold_result": buy_and_hold_result,
        "machine_learning_result": machine_learning_result,
        "buy_and_hold_metrics": buy_and_hold_metrics,
        "machine_learning_metrics": machine_learning_metrics,
        "metrics_table": metrics_table,
    }


def train_ml_pipeline_for_paper_trading(symbol: str) -> dict:
    """Train on all available history and return a signal for the latest bar."""
    symbol = symbol.upper()
    price_data = fetch_daily_bars(symbol, years=DATA_YEARS)
    if price_data.empty:
        raise ValueError(f"No data returned for {symbol}")

    feature_data = build_feature_dataframe(price_data)
    target_labels = create_next_day_positive_return_target(price_data)

    model_table = feature_data[FEATURE_COLUMNS].copy()
    model_table["target"] = target_labels
    model_table = model_table.dropna()
    if len(model_table) < 2:
        raise ValueError("Not enough rows after feature engineering.")

    training_rows = model_table.iloc[:-1]
    latest_feature_row = model_table.iloc[[-1]]

    training_features = training_rows[FEATURE_COLUMNS]
    training_targets = training_rows["target"]

    pca_bundle = fit_pca_on_training_features(training_features)
    pca_training_components = pca_bundle["pca_training_components"]
    latest_pca_components = transform_features_with_pca(latest_feature_row[FEATURE_COLUMNS], pca_bundle)

    machine_learning_model = train_model(
        pca_training_components,
        training_targets.to_numpy(),
        model_name=ML_MODEL_NAME,
    )
    latest_long_probability = predict_long_probabilities(
        machine_learning_model,
        latest_pca_components,
    )[0]
    latest_signal = int(latest_long_probability > LONG_PROBABILITY_THRESHOLD)
    latest_close_price = float(price_data.loc[latest_feature_row.index[0], "close"])

    return {
        "symbol": symbol,
        "latest_bar_date": latest_feature_row.index[0],
        "latest_close_price": latest_close_price,
        "latest_long_probability": latest_long_probability,
        "latest_signal": latest_signal,
        "machine_learning_model": machine_learning_model,
        "pca_bundle": pca_bundle,
    }
