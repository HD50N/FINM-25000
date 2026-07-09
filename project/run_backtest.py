"""Run the final project backtest, print metrics, and save charts."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project.backtest.runner import run_backtest
from project.config import CHARTS_DIRECTORY
from project.viz.charts import (
    make_drawdown_chart,
    make_equity_curve_chart,
    make_exposure_chart,
)


def main() -> None:
    results = run_backtest()

    print("\nBacktest metrics:\n")
    print(results["metrics_table"].to_string())

    charts_directory = Path(CHARTS_DIRECTORY)
    charts_directory.mkdir(parents=True, exist_ok=True)

    figures = {
        "equity_curve": make_equity_curve_chart(
            {
                "Trend Following": results["strategy_result"]["equity_curve"],
                "Equal Weight B&H": results["benchmark_result"]["equity_curve"],
            }
        ),
        "drawdown": make_drawdown_chart(
            {
                "Trend Following": results["metrics"]["Trend Following"]["drawdown"],
                "Equal Weight B&H": results["metrics"]["Equal Weight B&H"]["drawdown"],
            }
        ),
        "exposure": make_exposure_chart(results["strategy_result"]["signals"]),
    }

    for name, figure in figures.items():
        chart_path = charts_directory / f"{name}.png"
        figure.savefig(chart_path, dpi=150)
        print(f"Saved {chart_path}")


if __name__ == "__main__":
    main()
