"""Performance metrics."""

import numpy as np
import pandas as pd


def compute_metrics(result: dict, initial_capital: float = 100_000) -> dict:
    equity = result["equity_curve"]
    returns = result["daily_returns"]
    trades = result["trades"]

    total_return = equity.iloc[-1] / initial_capital - 1
    n_days = len(equity)
    cagr = (equity.iloc[-1] / initial_capital) ** (252 / n_days) - 1
    volatility = returns.std() * np.sqrt(252)
    sharpe = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0.0

    downside = returns[returns < 0]
    downside_std = downside.std()
    sortino = (
        returns.mean() / downside_std * np.sqrt(252) if downside_std > 0 else 0.0
    )

    rolling_max = equity.cummax()
    drawdown = equity / rolling_max - 1
    max_drawdown = drawdown.min()

    wins = 0
    closed = 0
    for i in range(1, len(trades)):
        if trades[i]["side"] == "sell" and trades[i - 1]["side"] == "buy":
            closed += 1
            if trades[i]["price"] > trades[i - 1]["price"]:
                wins += 1
    win_rate = wins / closed if closed > 0 else 0.0

    return {
        "total_return": total_return,
        "cagr": cagr,
        "volatility": volatility,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "drawdown": drawdown,
    }
