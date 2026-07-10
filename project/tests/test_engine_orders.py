"""Offline tests for order snapshot merging in the live engine."""

from project.engine.live_engine import LiveTradingEngine


def test_merge_orders_updates_existing_id():
    existing = [
        {"id": "abc", "symbol": "SPY", "status": "partially_filled", "filled_qty": 6, "qty": 18},
    ]
    updates = [
        {"id": "abc", "symbol": "SPY", "status": "filled", "filled_qty": 18, "qty": 18},
    ]
    merged = LiveTradingEngine._merge_orders(existing, updates)
    assert len(merged) == 1
    assert merged[0]["status"] == "filled"
    assert merged[0]["filled_qty"] == 18


def test_merge_orders_appends_new_ids():
    existing = [{"id": "abc", "symbol": "SPY", "status": "filled", "filled_qty": 18, "qty": 18}]
    updates = [{"id": "def", "symbol": "JPM", "status": "filled", "filled_qty": 44, "qty": 44}]
    merged = LiveTradingEngine._merge_orders(existing, updates)
    assert [order["id"] for order in merged] == ["abc", "def"]
