"""Offline tests for order settlement logic."""

from project.execution.broker import is_order_settled


def test_partially_filled_is_not_settled_until_full_qty():
    order = {"status": "partially_filled", "qty": 18, "filled_qty": 6.0}
    assert not is_order_settled(order)


def test_partially_filled_settled_when_filled_qty_reaches_order_qty():
    order = {"status": "partially_filled", "qty": 18, "filled_qty": 18.0}
    assert is_order_settled(order)


def test_filled_is_settled():
    order = {"status": "filled", "qty": 18, "filled_qty": 18.0}
    assert is_order_settled(order)


def test_accepted_is_not_settled():
    order = {"status": "accepted", "qty": 18, "filled_qty": 0.0}
    assert not is_order_settled(order)


def test_canceled_is_settled():
    order = {"status": "canceled", "qty": 18, "filled_qty": 6.0}
    assert is_order_settled(order)
