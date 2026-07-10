"""Config validation tests (no network)."""

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import project.config as config


def test_default_config_is_valid() -> None:
    config.validate_config()  # should not raise


def test_invalid_fast_slow_windows_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "FAST_WINDOW_DAYS", 50)
    monkeypatch.setattr(config, "SLOW_WINDOW_DAYS", 20)
    with pytest.raises(ValueError, match="FAST_WINDOW_DAYS"):
        config.validate_config()


def test_invalid_position_fraction_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "MAX_POSITION_FRACTION", 1.5)
    with pytest.raises(ValueError, match="MAX_POSITION_FRACTION"):
        config.validate_config()


def test_universe_too_small_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "UNIVERSE", ["AAPL", "MSFT"])
    with pytest.raises(ValueError, match="5–20"):
        config.validate_config()


def test_module_reimport_still_valid() -> None:
    importlib.reload(config)
    config.validate_config()
