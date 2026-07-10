"""Tkinter tabs for the final project: paper trading dashboard and backtest."""

import threading
import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from project.config import CYCLE_SECONDS, UNIVERSE
from project.engine.live_engine import LiveTradingEngine
from project.viz.charts import (
    make_drawdown_chart,
    make_equity_curve_chart,
    make_exposure_chart,
)

REFRESH_MILLISECONDS = 1000


class PaperTradingFrame(ttk.Frame):
    """Monitor and control the live paper trading engine."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, padding=10)
        self._engine = LiveTradingEngine()
        self._refresh_after_id: str | None = None

        controls = ttk.Frame(self)
        controls.pack(fill=tk.X)
        self._start_button = ttk.Button(controls, text="Start", command=self._start)
        self._start_button.pack(side=tk.LEFT)
        self._stop_button = ttk.Button(
            controls, text="Stop", command=self._stop, state=tk.DISABLED
        )
        self._stop_button.pack(side=tk.LEFT, padx=5)

        self._status = tk.StringVar(
            value=f"Stopped | mode: paper | universe: {', '.join(UNIVERSE)} "
            f"| cycle: {CYCLE_SECONDS}s"
        )
        ttk.Label(self, textvariable=self._status, foreground="gray").pack(
            anchor=tk.W, pady=(8, 0)
        )

        self._account = tk.StringVar(
            value="Equity: — | Cash: — | P&L: — | Drawdown: — | Trades: —"
        )
        ttk.Label(self, textvariable=self._account, font=("Helvetica", 14)).pack(
            anchor=tk.W, pady=(4, 8)
        )

        columns = ("symbol", "signal", "qty", "entry", "value", "pnl")
        self._positions_tree = ttk.Treeview(
            self, columns=columns, show="headings", height=len(UNIVERSE)
        )
        headings = {
            "symbol": "Symbol",
            "signal": "Signal",
            "qty": "Qty",
            "entry": "Avg Entry",
            "value": "Market Value",
            "pnl": "Unrealized P&L",
        }
        for column, heading in headings.items():
            self._positions_tree.heading(column, text=heading)
            self._positions_tree.column(column, width=100, anchor=tk.E)
        self._positions_tree.column("symbol", anchor=tk.W)
        self._positions_tree.pack(fill=tk.X)

        ttk.Label(self, text="Recent orders (submitted → filled / partial / canceled):").pack(
            anchor=tk.W, pady=(8, 0)
        )
        order_columns = ("id", "side", "qty", "symbol", "filled", "status")
        self._orders_tree = ttk.Treeview(
            self, columns=order_columns, show="headings", height=5
        )
        order_headings = {
            "id": "Order ID",
            "side": "Side",
            "qty": "Qty",
            "symbol": "Symbol",
            "filled": "Filled",
            "status": "Status",
        }
        for column, heading in order_headings.items():
            self._orders_tree.heading(column, text=heading)
            self._orders_tree.column(column, width=90, anchor=tk.E)
        self._orders_tree.column("id", width=120, anchor=tk.W)
        self._orders_tree.column("symbol", anchor=tk.W)
        self._orders_tree.column("status", width=120, anchor=tk.W)
        self._orders_tree.pack(fill=tk.X)

        ttk.Label(self, text="Events (signals, orders, fills, errors):").pack(
            anchor=tk.W, pady=(8, 0)
        )
        self._events_text = tk.Text(self, height=10, wrap=tk.NONE)
        self._events_text.pack(fill=tk.BOTH, expand=True)
        self._events_text.configure(state=tk.DISABLED)

        self._refresh()

    def _start(self) -> None:
        self._engine.start()
        self._start_button.configure(state=tk.DISABLED)
        self._stop_button.configure(state=tk.NORMAL)

    def _stop(self) -> None:
        self._stop_button.configure(state=tk.DISABLED)
        threading.Thread(target=self._engine.stop, daemon=True).start()
        self._start_button.configure(state=tk.NORMAL)

    def _refresh(self) -> None:
        snapshot = self._engine.get_snapshot()

        state = "Halted (daily loss limit)" if snapshot["halted"] else (
            "Running" if snapshot["running"] else "Stopped"
        )
        connection = "connected" if snapshot["connected"] else "disconnected"
        self._status.set(
            f"{state} | {connection} | mode: {snapshot['mode']} "
            f"| universe: {', '.join(UNIVERSE)} | cycle: {CYCLE_SECONDS}s"
        )

        equity = snapshot["equity"]
        cash = snapshot["cash"]
        pnl = snapshot["cumulative_pnl"]
        drawdown = snapshot.get("drawdown")
        hit_rate = snapshot["hit_rate"]
        self._account.set(
            f"Equity: {f'${equity:,.2f}' if equity is not None else '—'} | "
            f"Cash: {f'${cash:,.2f}' if cash is not None else '—'} | "
            f"P&L: {f'${pnl:,.2f}' if pnl is not None else '—'} | "
            f"Drawdown: {f'{drawdown * 100:.2f}%' if drawdown is not None else '—'} | "
            f"Trades: {snapshot['trade_count']} | "
            f"Hit rate: {f'{hit_rate * 100:.0f}%' if hit_rate is not None else '—'}"
        )

        self._positions_tree.delete(*self._positions_tree.get_children())
        for symbol in UNIVERSE:
            position = snapshot["positions"].get(symbol, {})
            signal = snapshot["signals"].get(symbol)
            self._positions_tree.insert(
                "",
                tk.END,
                values=(
                    symbol,
                    {1: "Long", 0: "Flat"}.get(signal, "—"),
                    f"{position['qty']:.0f}" if position else "0",
                    f"${position['avg_entry_price']:.2f}" if position else "—",
                    f"${position['market_value']:,.2f}" if position else "—",
                    f"${position['unrealized_pl']:,.2f}" if position else "—",
                ),
            )

        self._orders_tree.delete(*self._orders_tree.get_children())
        for order in reversed(snapshot.get("orders", [])[-20:]):
            self._orders_tree.insert(
                "",
                tk.END,
                values=(
                    order.get("id", "")[:8],
                    str(order.get("side", "")).upper(),
                    order.get("qty", "—"),
                    order.get("symbol", "—"),
                    f"{order.get('filled_qty', 0):g}",
                    order.get("status", "—"),
                ),
            )

        self._events_text.configure(state=tk.NORMAL)
        self._events_text.delete("1.0", tk.END)
        self._events_text.insert(tk.END, "\n".join(snapshot["events"][-100:]))
        self._events_text.see(tk.END)
        self._events_text.configure(state=tk.DISABLED)

        self._refresh_after_id = self.after(REFRESH_MILLISECONDS, self._refresh)

    def shutdown(self) -> None:
        if self._refresh_after_id is not None:
            try:
                self.after_cancel(self._refresh_after_id)
            except tk.TclError:
                pass
            self._refresh_after_id = None
        self._engine.stop()


class ProjectBacktestFrame(ttk.Frame):
    """Run the portfolio backtest over the configured universe."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, padding=10)

        row = ttk.Frame(self)
        row.pack(fill=tk.X)
        ttk.Label(row, text=f"Universe: {', '.join(UNIVERSE)}").pack(side=tk.LEFT)
        ttk.Button(row, text="Run Backtest", command=self._run_backtest).pack(
            side=tk.LEFT, padx=10
        )

        self._metrics_text = tk.Text(self, height=5, wrap=tk.NONE)
        self._metrics_text.pack(fill=tk.X, pady=(10, 0))
        self._metrics_text.configure(state=tk.DISABLED)

        self._charts = ttk.Notebook(self)
        self._charts.pack(fill=tk.BOTH, expand=True, pady=10)
        self._chart_frames = {
            "Equity Curve": ttk.Frame(self._charts),
            "Drawdown": ttk.Frame(self._charts),
            "Exposure": ttk.Frame(self._charts),
        }
        for title, frame in self._chart_frames.items():
            self._charts.add(frame, text=title)
        self._canvases: dict[str, FigureCanvasTkAgg] = {}

    def _run_backtest(self) -> None:
        from project.backtest.runner import run_backtest

        try:
            results = run_backtest()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        self._metrics_text.configure(state=tk.NORMAL)
        self._metrics_text.delete("1.0", tk.END)
        self._metrics_text.insert(tk.END, results["metrics_table"].to_string())
        self._metrics_text.configure(state=tk.DISABLED)

        figures = {
            "Equity Curve": make_equity_curve_chart(
                {
                    "Trend Following": results["strategy_result"]["equity_curve"],
                    "Equal Weight B&H": results["benchmark_result"]["equity_curve"],
                }
            ),
            "Drawdown": make_drawdown_chart(
                {
                    "Trend Following": results["metrics"]["Trend Following"]["drawdown"],
                    "Equal Weight B&H": results["metrics"]["Equal Weight B&H"]["drawdown"],
                }
            ),
            "Exposure": make_exposure_chart(results["strategy_result"]["signals"]),
        }

        for title, figure in figures.items():
            if title in self._canvases:
                self._canvases[title].get_tk_widget().destroy()
            canvas = FigureCanvasTkAgg(figure, master=self._chart_frames[title])
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self._canvases[title] = canvas
