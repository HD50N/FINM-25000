"""Order routing through the Alpaca paper trading API."""

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

from hw1.data_connector.config import get_alpaca_credentials


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

    def submit_market_order(self, symbol: str, qty: int, side: str) -> dict:
        """Submit a market order and return its id, status, and details."""
        order_request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        )
        order = self._client.submit_order(order_request)
        return {
            "id": str(order.id),
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "status": str(order.status.value),
        }

    def get_order_status(self, order_id: str) -> str:
        return str(self._client.get_order_by_id(order_id).status.value)
