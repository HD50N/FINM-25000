"""Performance metrics for the portfolio backtest."""

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

    rolling_max = equity.cummax()
    drawdown = equity / rolling_max - 1
    max_drawdown = drawdown.min()

    wins = 0
    closed = 0
    open_entries: dict[str, float] = {}
    for trade in trades:
        if trade["side"] == "buy":
            open_entries[trade["symbol"]] = trade["price"]
        elif trade["symbol"] in open_entries:
            closed += 1
            if trade["price"] > open_entries.pop(trade["symbol"]):
                wins += 1
    win_rate = wins / closed if closed > 0 else 0.0

    return {
        "total_return": total_return,
        "cagr": cagr,
        "volatility": volatility,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
        "trade_count": len(trades),
        "win_rate": win_rate,
        "drawdown": drawdown,
    }


def make_metrics_table(metrics_by_name: dict[str, dict]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            name: {
                "Return": f"{m['total_return'] * 100:.2f}%",
                "CAGR": f"{m['cagr'] * 100:.2f}%",
                "Volatility": f"{m['volatility'] * 100:.2f}%",
                "Sharpe": f"{m['sharpe']:.2f}",
                "Max Drawdown": f"{m['max_drawdown'] * 100:.2f}%",
                "Trades": f"{m['trade_count']}",
                "Win Rate": f"{m['win_rate'] * 100:.2f}%",
            }
            for name, m in metrics_by_name.items()
        }
    ).T
