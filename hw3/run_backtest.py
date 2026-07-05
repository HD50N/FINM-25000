"""Run ML backtest and save charts."""

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hw3.backtest.runner import train_ml_pipeline
from hw3.config import CHARTS_DIRECTORY, DEFAULT_SYMBOL
from hw3.viz.charts import (
    save_drawdown_chart,
    save_equity_curve_chart,
    save_pca_variance_chart,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL, help="Ticker symbol")
    args = parser.parse_args()

    results = train_ml_pipeline(args.symbol)
    charts_directory = Path(CHARTS_DIRECTORY)
    charts_directory.mkdir(parents=True, exist_ok=True)

    save_equity_curve_chart(
        {
            "Buy & Hold": results["buy_and_hold_result"]["equity_curve"],
            "ML Signal": results["machine_learning_result"]["equity_curve"],
        },
        charts_directory / "equity_curve.png",
    )
    save_drawdown_chart(
        {
            "Buy & Hold": results["buy_and_hold_metrics"]["drawdown"],
            "ML Signal": results["machine_learning_metrics"]["drawdown"],
        },
        charts_directory / "drawdown_chart.png",
    )
    save_pca_variance_chart(
        pd.Series(results["pca_bundle"]["explained_variance_ratio"]),
        pd.Series(results["pca_bundle"]["cumulative_variance_ratio"]),
        charts_directory / "pca_variance.png",
    )

    print(f"Backtest complete for {results['symbol']}")
    print(results["metrics_table"])
    print(f"PCA components kept: {results['pca_bundle']['component_count']}")
    print(f"Charts saved to {charts_directory}/")


if __name__ == "__main__":
    main()
