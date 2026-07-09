"""Live paper trading engine: data -> signals -> risk -> orders.

Runs one cycle every CYCLE_SECONDS in a background thread. Each cycle:

1. Fetch daily bars and the latest quotes for the universe (quotes are
   logged to a CSV in project/logs/).
2. Compute the strategy signal per symbol.
3. Apply risk checks: stop-losses and the daily loss halt.
4. Size target positions and submit market orders for the difference
   between target and current holdings.
"""

import threading
import traceback
from datetime import date, datetime
from pathlib import Path

from project.config import (
    BAR_HISTORY_DAYS,
    CYCLE_SECONDS,
    LOGS_DIRECTORY,
    UNIVERSE,
)
from project.data_connector.historical import fetch_daily_bars_for_universe
from project.data_connector.quotes import fetch_latest_quotes, log_quotes
from project.execution.broker import AlpacaBroker
from project.risk.limits import (
    RiskState,
    apply_stop_losses,
    check_daily_loss,
    size_positions,
)
from project.strategies.momentum import latest_signal

MAX_EVENTS_KEPT = 200


class LiveTradingEngine:
    """Threaded paper trading loop with a thread-safe snapshot for the UI."""

    def __init__(self, universe: list[str] | None = None) -> None:
        self._universe = [s.upper() for s in (universe or UNIVERSE)]
        self._broker: AlpacaBroker | None = None
        self._risk_state: RiskState | None = None
        self._risk_day: date | None = None
        self._initial_equity: float | None = None
        self._trade_count = 0
        self._closed_trades: list[float] = []

        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._snapshot: dict = {
            "running": False,
            "connected": False,
            "halted": False,
            "mode": "paper",
            "equity": None,
            "cash": None,
            "cumulative_pnl": None,
            "trade_count": 0,
            "hit_rate": None,
            "positions": {},
            "signals": {},
            "orders": [],
            "events": [],
        }

    # -- public API -------------------------------------------------------

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=10)
        self._update_snapshot(running=False)

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def get_snapshot(self) -> dict:
        with self._lock:
            return {
                **self._snapshot,
                "positions": dict(self._snapshot["positions"]),
                "signals": dict(self._snapshot["signals"]),
                "orders": list(self._snapshot["orders"]),
                "events": list(self._snapshot["events"]),
            }

    # -- internals --------------------------------------------------------

    def _run(self) -> None:
        try:
            self._broker = AlpacaBroker()
            equity, cash = self._broker.get_equity_and_cash()
            self._initial_equity = equity
            self._reset_risk_state(equity)
            self._update_snapshot(running=True, connected=True, equity=equity, cash=cash)
            self._log_event(f"Engine started. Universe: {', '.join(self._universe)}")
            self._log_event("Paper trading only — no real money is used.")
        except Exception as exc:
            self._log_event(f"Failed to connect: {exc}")
            self._update_snapshot(running=False, connected=False)
            return

        while not self._stop_event.is_set():
            try:
                self._run_cycle()
            except Exception as exc:
                self._log_event(f"Cycle error: {exc}")
                traceback.print_exc()
            self._stop_event.wait(CYCLE_SECONDS)

        self._log_event("Engine stopped.")
        self._update_snapshot(running=False)

    def _reset_risk_state(self, equity: float) -> None:
        positions = self._broker.get_positions() if self._broker else {}
        entry_prices = {
            symbol: p["avg_entry_price"] for symbol, p in positions.items()
        }
        self._risk_state = RiskState(day_start_equity=equity, entry_prices=entry_prices)
        self._risk_day = date.today()

    def _run_cycle(self) -> None:
        equity, cash = self._broker.get_equity_and_cash()
        if date.today() != self._risk_day:
            self._reset_risk_state(equity)
            self._log_event("New trading day: risk limits reset.")

        quotes = fetch_latest_quotes(self._universe)
        if quotes:
            log_quotes(quotes, LOGS_DIRECTORY)
        prices = {
            symbol: quote["last"] or quote["ask"] or quote["bid"]
            for symbol, quote in quotes.items()
        }

        bars = fetch_daily_bars_for_universe(self._universe, days=BAR_HISTORY_DAYS)
        signals = {
            symbol: latest_signal(bars[symbol]) if symbol in bars else 0
            for symbol in self._universe
        }

        halted = check_daily_loss(equity, self._risk_state)
        if halted:
            signals = {symbol: 0 for symbol in signals}
            self._log_event("Daily loss limit breached: liquidating and halting.")
        else:
            signals = apply_stop_losses(signals, prices, self._risk_state)

        positions = self._broker.get_positions()
        targets = size_positions(signals, equity)
        orders = self._rebalance(targets, positions, prices)

        cumulative_pnl = equity - self._initial_equity if self._initial_equity else None
        hit_rate = (
            sum(1 for pnl in self._closed_trades if pnl > 0) / len(self._closed_trades)
            if self._closed_trades
            else None
        )
        self._update_snapshot(
            running=True,
            connected=True,
            halted=halted,
            equity=equity,
            cash=cash,
            cumulative_pnl=cumulative_pnl,
            trade_count=self._trade_count,
            hit_rate=hit_rate,
            positions=positions,
            signals=signals,
            orders=orders,
        )

    def _rebalance(
        self,
        targets: dict[str, float],
        positions: dict[str, dict],
        prices: dict[str, float],
    ) -> list[dict]:
        """Submit market orders to move current holdings toward targets."""
        orders = []
        for symbol, target_notional in targets.items():
            price = prices.get(symbol)
            if price is None or price <= 0:
                continue
            held_qty = positions.get(symbol, {}).get("qty", 0.0)
            target_qty = int(target_notional // price)
            delta_qty = target_qty - int(held_qty)

            if delta_qty == 0:
                continue
            side = "buy" if delta_qty > 0 else "sell"
            try:
                order = self._broker.submit_market_order(symbol, abs(delta_qty), side)
            except Exception as exc:
                self._log_event(f"Order rejected for {symbol}: {exc}")
                continue

            orders.append(order)
            self._trade_count += 1
            self._log_event(
                f"PAPER {side.upper()} {abs(delta_qty)} {symbol} @ ~${price:.2f} "
                f"(status: {order['status']})"
            )

            if side == "buy":
                self._risk_state.entry_prices[symbol] = price
            else:
                entry_price = self._risk_state.entry_prices.pop(symbol, None)
                if entry_price and target_qty == 0:
                    self._closed_trades.append(price - entry_price)

        return orders

    def _log_event(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {message}"

        log_path = Path(LOGS_DIRECTORY) / "engine.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a") as log_file:
            log_file.write(line + "\n")
        print(line)

        with self._lock:
            events = self._snapshot["events"] + [line]
            self._snapshot["events"] = events[-MAX_EVENTS_KEPT:]

    def _update_snapshot(self, **kwargs) -> None:
        with self._lock:
            if "orders" in kwargs:
                kwargs["orders"] = (self._snapshot["orders"] + kwargs["orders"])[-50:]
            self._snapshot.update(kwargs)
