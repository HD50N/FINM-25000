"""Run backtests for assignment strategies."""

import argparse
from pathlib import Path

import pandas as pd

from backtest.engine import run_backtest
from backtest.metrics import compute_metrics
from data_connector.historical import fetch_daily_bars
from indicators.technical import add_indicators
from strategies.custom import generate_signals as custom_signals
from strategies.mean_reversion import generate_signals as mean_reversion_signals
from strategies.trend_following import generate_signals as trend_signals
from viz.charts import plot_drawdown, plot_equity_curve, plot_price_chart

INITIAL_CAPITAL = 100_000
CHARTS_DIR = Path("charts")


def buy_and_hold_signals(df: pd.DataFrame) -> pd.Series:
    return pd.Series(1, index=df.index)


def format_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def format_num(value: float) -> str:
    return f"{value:.2f}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="AAPL", help="Ticker symbol")
    args = parser.parse_args()
    symbol = args.symbol.upper()

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

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    plot_price_chart(
        df,
        strategy_map["Trend Following"],
        symbol,
        CHARTS_DIR / "price_chart.png",
    )
    plot_equity_curve(
        {name: r["equity_curve"] for name, r in results.items()},
        CHARTS_DIR / "equity_curve.png",
    )
    plot_drawdown(
        {name: m["drawdown"] for name, m in metrics.items()},
        CHARTS_DIR / "drawdown_chart.png",
    )

    print(f"Backtest complete for {symbol}")
    print(metrics_table)
    print(f"Charts saved to {CHARTS_DIR}/")
    print("Write your final report manually in reports/backtest_report.pdf")


if __name__ == "__main__":
    main()
