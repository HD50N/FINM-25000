"""Real-time bid/ask quote and trade streaming via Alpaca WebSocket."""

import threading
from collections.abc import Callable
from typing import Any

from alpaca.data.enums import DataFeed
from alpaca.data.live import StockDataStream

from .config import get_alpaca_credentials


class QuoteStreamer:
    def __init__(
        self,
        on_quote: Callable[[Any], None],
        on_trade: Callable[[Any], None] | None = None,
        on_error: Callable[[str], None] | None = None,
    ) -> None:
        self._on_quote = on_quote
        self._on_trade = on_trade
        self._on_error = on_error
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
        try:
            if self._stream is not None:
                self._stream.run()
        except Exception as exc:
            if self._on_error:
                self._on_error(str(exc))

    def _cleanup(self) -> tuple[StockDataStream | None, threading.Thread | None]:
        """Stop the current stream. Caller must not hold _lock."""
        with self._lock:
            stream = self._stream
            thread = self._thread
            self._stream = None
            self._thread = None
            self._symbol = None

        if stream is not None:
            try:
                stream.stop()
            except Exception:
                pass

        if thread is not None and thread.is_alive():
            thread.join(timeout=5)

        return stream, thread

    def subscribe(self, symbol: str) -> None:
        symbol = symbol.upper().strip()

        with self._lock:
            if symbol == self._symbol and self._thread and self._thread.is_alive():
                return
            old_stream = self._stream
            old_thread = self._thread
            self._stream = None
            self._thread = None
            self._symbol = None

        if old_stream is not None:
            try:
                old_stream.stop()
            except Exception:
                pass
        if old_thread is not None and old_thread.is_alive():
            old_thread.join(timeout=5)

        api_key, secret_key = get_alpaca_credentials()
        stream = StockDataStream(api_key, secret_key, feed=DataFeed.IEX)
        stream.subscribe_quotes(self._quote_handler, symbol)
        stream.subscribe_trades(self._trade_handler, symbol)

        with self._lock:
            self._stream = stream
            self._symbol = symbol
            self._thread = threading.Thread(target=self._run_stream, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._cleanup()
