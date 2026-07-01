"""Run all backtests and build metrics table."""

import pandas as pd

from hw2.backtest.engine import run_backtest
from hw2.backtest.metrics import compute_metrics
from hw2.data_connector.historical import fetch_daily_bars
from hw2.indicators.technical import add_indicators
from hw2.strategies.custom import generate_signals as custom_signals
from hw2.strategies.mean_reversion import generate_signals as mean_reversion_signals
from hw2.strategies.trend_following import generate_signals as trend_signals

INITIAL_CAPITAL = 100_000


def buy_and_hold_signals(df: pd.DataFrame) -> pd.Series:
    return pd.Series(1, index=df.index)


def format_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def format_num(value: float) -> str:
    return f"{value:.2f}"


def run_all(symbol: str) -> dict:
    symbol = symbol.upper()
    df = fetch_daily_bars(symbol)
    if df.empty:
        raise ValueError(f"No data returned for {symbol}")

    df = add_indicators(df).dropna()

    strategy_map = {
        "Buy & Hold": buy_and_hold_signals(df),
        "Trend Following": trend_signals(df),
        "Mean Reversion": mean_reversion_signals(df),
        "Custom Strategy": custom_signals(df),
    }

    results = {}
    metrics = {}
    for name, signals in strategy_map.items():
        result = run_backtest(df, signals, INITIAL_CAPITAL)
        results[name] = result
        metrics[name] = compute_metrics(result, INITIAL_CAPITAL)

    metrics_table = pd.DataFrame(
        {
            name: {
                "Return": format_pct(m["total_return"]),
                "CAGR": format_pct(m["cagr"]),
                "Volatility": format_pct(m["volatility"]),
                "Sharpe": format_num(m["sharpe"]),
                "Sortino": format_num(m["sortino"]),
                "Max Drawdown": format_pct(m["max_drawdown"]),
                "Win Rate": format_pct(m["win_rate"]),
            }
            for name, m in metrics.items()
        }
    ).T

    return {
        "symbol": symbol,
        "df": df,
        "strategy_map": strategy_map,
        "results": results,
        "metrics": metrics,
        "metrics_table": metrics_table,
    }
