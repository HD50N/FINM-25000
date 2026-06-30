"""Assignment-required charts."""

import matplotlib.pyplot as plt
import pandas as pd


def make_price_chart(df: pd.DataFrame, signals: pd.Series, symbol: str) -> plt.Figure:
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    axes[0].plot(df.index, df["close"], label="Close", color="black", linewidth=1)
    axes[0].plot(df.index, df["sma_20"], label="SMA 20", alpha=0.7)
    buys = df.index[signals.diff() == 1]
    sells = df.index[signals.diff() == -1]
    axes[0].scatter(buys, df.loc[buys, "close"], marker="^", color="green", label="Buy", s=40)
    axes[0].scatter(sells, df.loc[sells, "close"], marker="v", color="red", label="Sell", s=40)
    axes[0].set_title(f"{symbol} Price, Indicators, and Trend Following Signals")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(df.index, df["macd"], label="MACD", linewidth=1)
    axes[1].plot(df.index, df["macd_signal"], label="Signal", linewidth=1)
    axes[1].axhline(0, color="gray", linewidth=0.5)
    axes[1].set_ylabel("MACD")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(df.index, df["adx"], label="ADX", color="purple", linewidth=1)
    axes[2].axhline(25, color="gray", linestyle="--", linewidth=0.8, label="ADX 25")
    axes[2].set_ylabel("ADX")
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    fig.tight_layout()
    return fig


def make_equity_curve(equity_curves: dict[str, pd.Series]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 5))
    for name, equity in equity_curves.items():
        ax.plot(equity.index, equity, label=name)
    ax.set_title("Equity Curve Comparison")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def make_drawdown(drawdowns: dict[str, pd.Series]) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 5))
    for name, dd in drawdowns.items():
        ax.plot(dd.index, dd * 100, label=name)
    ax.set_title("Drawdown Comparison (%)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig
