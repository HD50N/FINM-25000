"""Risk checks: position sizing, stop-losses, and a daily loss halt."""

from dataclasses import dataclass, field

from project.config import (
    MAX_DAILY_LOSS_FRACTION,
    MAX_GROSS_EXPOSURE,
    MAX_POSITION_FRACTION,
    STOP_LOSS_FRACTION,
)


@dataclass
class RiskState:
    """Mutable risk bookkeeping carried across live trading cycles."""

    day_start_equity: float
    entry_prices: dict[str, float] = field(default_factory=dict)
    halted: bool = False


def size_positions(signals: dict[str, int], equity: float) -> dict[str, float]:
    """Turn 0/1 signals into target dollar notionals per symbol.

    Long symbols split the equity equally, capped at MAX_POSITION_FRACTION
    per asset and MAX_GROSS_EXPOSURE in total. No leverage, no shorts.
    """
    long_symbols = [symbol for symbol, signal in signals.items() if signal == 1]
    if not long_symbols:
        return {symbol: 0.0 for symbol in signals}

    per_asset_fraction = min(MAX_GROSS_EXPOSURE / len(long_symbols), MAX_POSITION_FRACTION)
    notional = equity * per_asset_fraction

    return {symbol: notional if signal == 1 else 0.0 for symbol, signal in signals.items()}


def apply_stop_losses(
    signals: dict[str, int], prices: dict[str, float], risk_state: RiskState
) -> dict[str, int]:
    """Force a symbol's signal to 0 if it has fallen past the stop-loss."""
    adjusted = dict(signals)
    for symbol, entry_price in risk_state.entry_prices.items():
        price = prices.get(symbol)
        if price is None or entry_price <= 0:
            continue
        if price <= entry_price * (1 - STOP_LOSS_FRACTION):
            adjusted[symbol] = 0
    return adjusted


def check_daily_loss(equity: float, risk_state: RiskState) -> bool:
    """Return True (and set halted) if the daily loss limit has been breached."""
    if risk_state.day_start_equity <= 0:
        return risk_state.halted
    daily_loss = 1 - equity / risk_state.day_start_equity
    if daily_loss >= MAX_DAILY_LOSS_FRACTION:
        risk_state.halted = True
    return risk_state.halted
