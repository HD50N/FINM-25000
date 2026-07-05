"""Performance metrics."""

import numpy as np

from hw3.config import INITIAL_CAPITAL


def compute_metrics(backtest_result: dict) -> dict:
    equity_curve = backtest_result["equity_curve"]
    daily_returns = backtest_result["daily_returns"]
    trades = backtest_result["trades"]

    total_return = equity_curve.iloc[-1] / INITIAL_CAPITAL - 1
    trading_day_count = len(equity_curve)
    compound_annual_growth_rate = (
        (equity_curve.iloc[-1] / INITIAL_CAPITAL) ** (252 / trading_day_count) - 1
    )
    volatility = daily_returns.std() * np.sqrt(252)
    sharpe_ratio = (
        daily_returns.mean() / daily_returns.std() * np.sqrt(252)
        if daily_returns.std() > 0
        else 0.0
    )

    negative_returns = daily_returns[daily_returns < 0]
    downside_volatility = negative_returns.std()
    sortino_ratio = (
        daily_returns.mean() / downside_volatility * np.sqrt(252)
        if downside_volatility > 0
        else 0.0
    )

    rolling_peak = equity_curve.cummax()
    drawdown_series = equity_curve / rolling_peak - 1
    maximum_drawdown = drawdown_series.min()

    winning_trades = 0
    closed_trades = 0
    for trade_index in range(1, len(trades)):
        if trades[trade_index]["side"] == "sell" and trades[trade_index - 1]["side"] == "buy":
            closed_trades += 1
            if trades[trade_index]["profit_loss"] > 0:
                winning_trades += 1
    win_rate = winning_trades / closed_trades if closed_trades > 0 else 0.0

    return {
        "total_return": total_return,
        "cagr": compound_annual_growth_rate,
        "volatility": volatility,
        "sharpe": sharpe_ratio,
        "sortino": sortino_ratio,
        "max_drawdown": maximum_drawdown,
        "win_rate": win_rate,
        "drawdown": drawdown_series,
    }
