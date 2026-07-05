"""Long-only backtest engine with trade profit and loss."""

import pandas as pd

from hw3.config import INITIAL_CAPITAL


def run_backtest(price_data: pd.DataFrame, signals: pd.Series) -> dict:
    cash_balance = INITIAL_CAPITAL
    share_count = 0.0
    portfolio_values = []
    trades = []
    last_buy_price = None

    for trade_date, price_row in price_data.iterrows():
        close_price = price_row["close"]
        signal_value = int(signals.loc[trade_date])

        if signal_value == 1 and share_count == 0:
            share_count = cash_balance / close_price
            cash_balance = 0.0
            last_buy_price = close_price
            trades.append(
                {
                    "date": trade_date,
                    "side": "buy",
                    "price": close_price,
                    "shares": share_count,
                    "profit_loss": 0.0,
                }
            )
        elif signal_value == 0 and share_count > 0:
            cash_balance = share_count * close_price
            trade_profit_loss = (close_price - last_buy_price) * share_count
            trades.append(
                {
                    "date": trade_date,
                    "side": "sell",
                    "price": close_price,
                    "shares": share_count,
                    "profit_loss": trade_profit_loss,
                }
            )
            share_count = 0.0
            last_buy_price = None

        portfolio_values.append(cash_balance + share_count * close_price)

    equity_curve = pd.Series(portfolio_values, index=price_data.index, name="equity")
    daily_returns = equity_curve.pct_change().fillna(0)

    return {
        "equity_curve": equity_curve,
        "daily_returns": daily_returns,
        "trades": trades,
    }
