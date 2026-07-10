"""Charts for the final project backtest."""

import matplotlib.pyplot as plt
import pandas as pd


def make_equity_curve_chart(equity_curves: dict[str, pd.Series]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 5))
    for name, equity in equity_curves.items():
        ax.plot(equity.index, equity, label=name)
    ax.set_title("Portfolio Equity Curve")
    ax.set_ylabel("Equity ($)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def make_drawdown_chart(drawdowns: dict[str, pd.Series]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 5))
    for name, drawdown in drawdowns.items():
        ax.plot(drawdown.index, drawdown * 100, label=name)
    ax.set_title("Portfolio Drawdown (%)")
    ax.set_ylabel("Drawdown (%)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def make_exposure_chart(signals: pd.DataFrame) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 5))
    long_count = signals.sum(axis=1)
    ax.fill_between(long_count.index, long_count, step="mid", alpha=0.4)
    ax.set_title("Number of Long Positions Over Time")
    ax.set_ylabel("Long positions")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig
