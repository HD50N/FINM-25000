"""Real-time bid/ask quote and trade streaming via Alpaca WebSocket."""

import threading
from collections.abc import Callable
from typing import Any

from alpaca.data.enums import DataFeed
from alpaca.data.live import StockDataStream

from .config import get_alpaca_credentials


class QuoteStreamer:
    """Manages a background WebSocket subscription for live quotes and trades."""

    def __init__(
        self,
        on_quote: Callable[[Any], None],
        on_trade: Callable[[Any], None] | None = None,
    ) -> None:
        self._on_quote = on_quote
        self._on_trade = on_trade
        self._thread: threading.Thread | None = None
        self._stream: StockDataStream | None = None
        self._symbol: str | None = None
        self._lock = threading.Lock()

    async def _quote_handler(self, data: Any) -> None:
        self._on_quote(data)

    async def _trade_handler(self, data: Any) -> None:
        if self._on_trade:
            self._on_trade(data)

    def _run_stream(self) -> None:
        if self._stream is not None:
            self._stream.run()

    def subscribe(self, symbol: str) -> None:
        """Subscribe to live quotes and trades for the given symbol."""
        symbol = symbol.upper().strip()
        with self._lock:
            if symbol == self._symbol and self._thread and self._thread.is_alive():
                return

            self.stop()

            api_key, secret_key = get_alpaca_credentials()
            self._stream = StockDataStream(api_key, secret_key, feed=DataFeed.IEX)
            self._stream.subscribe_quotes(self._quote_handler, symbol)
            self._stream.subscribe_trades(self._trade_handler, symbol)

            self._symbol = symbol
            self._thread = threading.Thread(target=self._run_stream, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        """Stop the current WebSocket stream."""
        with self._lock:
            if self._stream is not None:
                try:
                    self._stream.stop()
                except Exception:
                    pass
                self._stream = None

            if self._thread is not None and self._thread.is_alive():
                self._thread.join(timeout=5)
            self._thread = None
            self._symbol = None
