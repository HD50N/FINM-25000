"""Risk module tests (no network)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project.config import (
    MAX_DAILY_LOSS_FRACTION,
    MAX_GROSS_EXPOSURE,
    MAX_POSITION_FRACTION,
    STOP_LOSS_FRACTION,
)
from project.risk.limits import (
    RiskState,
    apply_stop_losses,
    check_daily_loss,
    size_positions,
)


def test_single_long_capped_at_max_position() -> None:
    targets = size_positions({"AAPL": 1, "MSFT": 0}, equity=100_000)
    assert targets["AAPL"] == 100_000 * MAX_POSITION_FRACTION
    assert targets["MSFT"] == 0.0


def test_many_longs_capped_at_gross_exposure() -> None:
    signals = {f"SYM{i}": 1 for i in range(10)}
    targets = size_positions(signals, equity=100_000)
    total = sum(targets.values())
    assert total <= 100_000 * MAX_GROSS_EXPOSURE + 1e-6
    for notional in targets.values():
        assert notional <= 100_000 * MAX_POSITION_FRACTION + 1e-6


def test_no_longs_means_all_cash() -> None:
    targets = size_positions({"AAPL": 0, "MSFT": 0}, equity=100_000)
    assert all(notional == 0.0 for notional in targets.values())


def test_stop_loss_forces_exit() -> None:
    risk_state = RiskState(day_start_equity=100_000, entry_prices={"AAPL": 100.0})
    stop_price = 100.0 * (1 - STOP_LOSS_FRACTION)
    adjusted = apply_stop_losses({"AAPL": 1}, {"AAPL": stop_price}, risk_state)
    assert adjusted["AAPL"] == 0


def test_stop_loss_keeps_position_above_stop() -> None:
    risk_state = RiskState(day_start_equity=100_000, entry_prices={"AAPL": 100.0})
    adjusted = apply_stop_losses({"AAPL": 1}, {"AAPL": 99.0}, risk_state)
    assert adjusted["AAPL"] == 1


def test_daily_loss_halts_trading() -> None:
    risk_state = RiskState(day_start_equity=100_000)
    breach_equity = 100_000 * (1 - MAX_DAILY_LOSS_FRACTION)
    assert check_daily_loss(breach_equity, risk_state) is True
    assert risk_state.halted is True


def test_small_loss_does_not_halt() -> None:
    risk_state = RiskState(day_start_equity=100_000)
    assert check_daily_loss(99_500, risk_state) is False
    assert risk_state.halted is False
