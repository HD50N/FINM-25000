"""Long-only portfolio backtest across the universe."""

import pandas as pd

from project.risk.limits import size_positions
from project.strategies.momentum import generate_signals


def run_portfolio_backtest(
    bars: dict[str, pd.DataFrame], initial_capital: float = 100_000
) -> dict:
    """Backtest the strategy over the whole universe with daily rebalancing.

    Position sizing reuses the same risk module as live trading, so backtest
    and paper trading follow identical rules.
    """
    closes = pd.DataFrame({symbol: df["close"] for symbol, df in bars.items()}).dropna()
    signals = pd.DataFrame(
        {symbol: generate_signals(df) for symbol, df in bars.items()}
    ).reindex(closes.index).fillna(0).astype(int)
    returns = closes.pct_change().fillna(0)

    weights = pd.DataFrame(0.0, index=closes.index, columns=closes.columns)
    for date, signal_row in signals.iterrows():
        fractions = size_positions(signal_row.to_dict(), equity=1.0)
        weights.loc[date] = pd.Series(fractions)

    daily_returns = (weights * returns).sum(axis=1)
    equity_curve = initial_capital * (1 + daily_returns).cumprod()
    equity_curve.name = "equity"

    trades = []
    for symbol in signals.columns:
        changes = signals[symbol].diff().fillna(signals[symbol])
        for date in signals.index[changes != 0]:
            side = "buy" if changes.loc[date] > 0 else "sell"
            trades.append(
                {"date": date, "symbol": symbol, "side": side, "price": closes.loc[date, symbol]}
            )
    trades.sort(key=lambda trade: trade["date"])

    return {
        "equity_curve": equity_curve,
        "daily_returns": daily_returns,
        "trades": trades,
        "signals": signals,
        "closes": closes,
    }
