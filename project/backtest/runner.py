"""Run the portfolio backtest and build the metrics table."""

import pandas as pd

from project.backtest.engine import run_portfolio_backtest
from project.backtest.metrics import compute_metrics, make_metrics_table
from project.config import BACKTEST_YEARS, INITIAL_CAPITAL, UNIVERSE
from project.data_connector.historical import fetch_daily_bars_for_universe


def run_equal_weight_benchmark(closes: pd.DataFrame, initial_capital: float) -> dict:
    """Buy-and-hold benchmark: equal weight across the universe."""
    daily_returns = closes.pct_change().fillna(0).mean(axis=1)
    equity_curve = initial_capital * (1 + daily_returns).cumprod()
    equity_curve.name = "equity"
    return {"equity_curve": equity_curve, "daily_returns": daily_returns, "trades": []}


def run_backtest(universe: list[str] | None = None) -> dict:
    symbols = [s.upper() for s in (universe or UNIVERSE)]
    bars = fetch_daily_bars_for_universe(symbols, days=BACKTEST_YEARS * 252)
    if not bars:
        raise ValueError("No data returned for the universe")

    strategy_result = run_portfolio_backtest(bars, INITIAL_CAPITAL)
    benchmark_result = run_equal_weight_benchmark(strategy_result["closes"], INITIAL_CAPITAL)

    metrics = {
        "Trend Following": compute_metrics(strategy_result, INITIAL_CAPITAL),
        "Equal Weight B&H": compute_metrics(benchmark_result, INITIAL_CAPITAL),
    }

    return {
        "bars": bars,
        "strategy_result": strategy_result,
        "benchmark_result": benchmark_result,
        "metrics": metrics,
        "metrics_table": make_metrics_table(metrics),
    }
