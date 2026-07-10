"""Order routing through the Alpaca paper trading API."""

import time

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, QueryOrderStatus, TimeInForce
from alpaca.trading.requests import GetOrdersRequest, MarketOrderRequest

from hw1.data_connector.config import get_alpaca_credentials
from project.config import ORDER_POLL_INTERVAL_SECONDS, ORDER_POLL_TIMEOUT_SECONDS

# Statuses where no further fills are expected. partially_filled is NOT terminal —
# the order may still be working toward a full fill.
SETTLED_ORDER_STATUSES = {
    "filled",
    "canceled",
    "cancelled",
    "rejected",
    "expired",
    "done_for_day",
}


def is_order_settled(order: dict) -> bool:
    """True when the order will not receive more fills (fully done or dead)."""
    status = order["status"]
    if status in SETTLED_ORDER_STATUSES:
        return True
    if status == "partially_filled":
        return order.get("filled_qty", 0.0) >= float(order.get("qty", 0))
    return False


class AlpacaBroker:
    """Thin wrapper around Alpaca's TradingClient. Paper trading only."""

    def __init__(self) -> None:
        api_key, secret_key = get_alpaca_credentials()
        self._client = TradingClient(api_key, secret_key, paper=True)

    def get_equity_and_cash(self) -> tuple[float, float]:
        account = self._client.get_account()
        return float(account.equity), float(account.cash)

    def get_positions(self) -> dict[str, dict]:
        """Return symbol -> {qty, avg_entry_price, market_value, unrealized_pl}."""
        positions = {}
        for position in self._client.get_all_positions():
            positions[position.symbol] = {
                "qty": float(position.qty),
                "avg_entry_price": float(position.avg_entry_price),
                "market_value": float(position.market_value),
                "unrealized_pl": float(position.unrealized_pl),
            }
        return positions

    def get_open_orders(self) -> list[dict]:
        """Return currently open orders (accepted / pending / new / …)."""
        request = GetOrdersRequest(status=QueryOrderStatus.OPEN, limit=100)
        return [self._order_to_dict(order) for order in self._client.get_orders(filter=request)]

    def submit_market_order(self, symbol: str, qty: int, side: str) -> dict:
        """Submit a market order and return its id, status, and details."""
        if qty <= 0:
            raise ValueError(f"Order qty must be positive (got {qty} for {symbol})")
        if side not in {"buy", "sell"}:
            raise ValueError(f"Order side must be 'buy' or 'sell' (got {side!r})")

        order_request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        )
        order = self._client.submit_order(order_request)
        return self._order_to_dict(order, symbol=symbol, side=side, qty=qty)

    def get_order(self, order_id: str) -> dict:
        """Return the current order snapshot (status, filled qty, etc.)."""
        order = self._client.get_order_by_id(order_id)
        return self._order_to_dict(order)

    def get_order_status(self, order_id: str) -> str:
        return self.get_order(order_id)["status"]

    def wait_for_order_update(
        self,
        order_id: str,
        timeout_seconds: float = ORDER_POLL_TIMEOUT_SECONDS,
        poll_interval: float = ORDER_POLL_INTERVAL_SECONDS,
    ) -> dict:
        """Poll until the order is fully settled (filled / canceled / …) or timeout."""
        deadline = time.monotonic() + timeout_seconds
        latest = self.get_order(order_id)
        while not is_order_settled(latest):
            if time.monotonic() >= deadline:
                break
            time.sleep(poll_interval)
            latest = self.get_order(order_id)
        return latest

    @staticmethod
    def _order_to_dict(order, symbol: str | None = None, side: str | None = None, qty: int | None = None) -> dict:
        status = order.status.value if hasattr(order.status, "value") else str(order.status)
        filled_qty = float(order.filled_qty) if order.filled_qty is not None else 0.0
        return {
            "id": str(order.id),
            "symbol": symbol or order.symbol,
            "side": side or str(order.side.value if hasattr(order.side, "value") else order.side),
            "qty": qty if qty is not None else int(float(order.qty)),
            "filled_qty": filled_qty,
            "status": status,
        }
