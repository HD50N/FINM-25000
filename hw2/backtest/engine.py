"""Reusable long-only backtesting engine."""

import pandas as pd


def run_backtest(
    df: pd.DataFrame, signals: pd.Series, initial_capital: float = 100_000
) -> dict:
    cash = initial_capital
    shares = 0.0
    equity = []
    trades = []

    for date, row in df.iterrows():
        price = row["close"]
        signal = int(signals.loc[date])

        if signal == 1 and shares == 0:
            shares = cash / price
            cash = 0.0
            trades.append({"date": date, "side": "buy", "price": price, "shares": shares})
        elif signal == 0 and shares > 0:
            cash = shares * price
            trades.append({"date": date, "side": "sell", "price": price, "shares": shares})
            shares = 0.0

        equity.append(cash + shares * price)

    equity_series = pd.Series(equity, index=df.index, name="equity")
    daily_returns = equity_series.pct_change().fillna(0)

    return {
        "equity_curve": equity_series,
        "daily_returns": daily_returns,
        "trades": trades,
    }
