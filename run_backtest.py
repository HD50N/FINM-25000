"""Print backtest metrics (charts are shown in the UI)."""

import argparse

from backtest.runner import run_all


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="AAPL", help="Ticker symbol")
    args = parser.parse_args()

    data = run_all(args.symbol)
    print(f"Backtest complete for {data['symbol']}")
    print(data["metrics_table"])
    print("Open python main.py and use the Backtesting tab to view charts.")


if __name__ == "__main__":
    main()
