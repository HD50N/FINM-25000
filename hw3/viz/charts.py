"""Assignment-required charts."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def make_equity_curve_chart(equity_curves: dict[str, pd.Series]) -> plt.Figure:
    figure, axis = plt.subplots(figsize=(10, 5))
    for strategy_name, equity_curve in equity_curves.items():
        axis.plot(equity_curve.index, equity_curve, label=strategy_name)
    axis.set_title("Equity Curve Comparison")
    axis.legend()
    axis.grid(True, alpha=0.3)
    figure.tight_layout()
    return figure


def make_drawdown_chart(drawdown_series_by_strategy: dict[str, pd.Series]) -> plt.Figure:
    figure, axis = plt.subplots(figsize=(10, 5))
    for strategy_name, drawdown_series in drawdown_series_by_strategy.items():
        axis.plot(drawdown_series.index, drawdown_series * 100, label=strategy_name)
    axis.set_title("Drawdown Comparison (%)")
    axis.legend()
    axis.grid(True, alpha=0.3)
    figure.tight_layout()
    return figure


def make_pca_variance_chart(
    explained_variance_ratio: pd.Series,
    cumulative_variance_ratio: pd.Series,
) -> plt.Figure:
    figure, axis = plt.subplots(figsize=(10, 5))
    component_numbers = range(1, len(explained_variance_ratio) + 1)
    axis.bar(component_numbers, explained_variance_ratio, alpha=0.7, label="Explained variance")
    axis.plot(
        component_numbers,
        cumulative_variance_ratio,
        color="red",
        marker="o",
        label="Cumulative variance",
    )
    axis.axhline(0.80, color="gray", linestyle="--", label="80% threshold")
    axis.set_xlabel("PCA component")
    axis.set_ylabel("Variance ratio")
    axis.set_title("PCA Explained Variance")
    axis.legend()
    axis.grid(True, alpha=0.3)
    figure.tight_layout()
    return figure


def save_equity_curve_chart(
    equity_curves: dict[str, pd.Series],
    output_path: Path,
) -> None:
    figure = make_equity_curve_chart(equity_curves)
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def save_drawdown_chart(
    drawdown_series_by_strategy: dict[str, pd.Series],
    output_path: Path,
) -> None:
    figure = make_drawdown_chart(drawdown_series_by_strategy)
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def save_pca_variance_chart(
    explained_variance_ratio: pd.Series,
    cumulative_variance_ratio: pd.Series,
    output_path: Path,
) -> None:
    figure = make_pca_variance_chart(explained_variance_ratio, cumulative_variance_ratio)
    figure.savefig(output_path, dpi=150)
    plt.close(figure)
