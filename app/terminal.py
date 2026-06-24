"""Simple Tkinter UI for live quotes and historical chart."""

import queue
import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from data_connector import QuoteStreamer, fetch_historical_bars


class MarketDataTerminal(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Market Data Terminal")
        self.geometry("900x600")

        self.symbol = tk.StringVar(value="AAPL")
        self.bid = tk.StringVar(value="—")
        self.ask = tk.StringVar(value="—")
        self.last = tk.StringVar(value="—")

        self._queue: queue.Queue = queue.Queue()
        self._status = tk.StringVar(value="Enter a ticker and click Subscribe")
        self._streamer = QuoteStreamer(
            on_quote=lambda q: self._queue.put(("quote", q)),
            on_trade=lambda t: self._queue.put(("trade", t)),
            on_error=lambda msg: self._queue.put(("error", msg)),
        )

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        live = ttk.Frame(notebook, padding=10)
        history = ttk.Frame(notebook, padding=10)
        notebook.add(live, text="Live Quotes")
        notebook.add(history, text="Historical Chart")

        self._build_live_tab(live)
        self._build_history_tab(history)
        self._poll()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_live_tab(self, parent: ttk.Frame) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X)
        ttk.Label(row, text="Ticker:").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.symbol, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(row, text="Subscribe", command=self._subscribe).pack(side=tk.LEFT)
        ttk.Label(parent, textvariable=self._status, foreground="gray").pack(
            anchor=tk.W, pady=(8, 0)
        )

        for label, var in [("Bid", self.bid), ("Ask", self.ask), ("Last", self.last)]:
            ttk.Label(parent, text=f"{label}:").pack(anchor=tk.W, pady=(10, 0))
            ttk.Label(parent, textvariable=var, font=("Helvetica", 18)).pack(anchor=tk.W)

    def _build_history_tab(self, parent: ttk.Frame) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X)
        ttk.Label(row, text="Ticker:").pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=self.symbol, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(row, text="Load Chart", command=self._load_chart).pack(side=tk.LEFT)
        self._chart_frame = ttk.Frame(parent)
        self._chart_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self._canvas = None

    def _subscribe(self) -> None:
        symbol = self.symbol.get().strip().upper()
        if not symbol:
            messagebox.showwarning("Error", "Enter a ticker.")
            return
        self.bid.set("—")
        self.ask.set("—")
        self.last.set("—")
        self._status.set(f"Subscribing to {symbol}…")
        try:
            self._streamer.subscribe(symbol)
            self._status.set(f"Streaming {symbol} (updates during market hours)")
        except Exception as exc:
            self._status.set("Subscribe failed")
            messagebox.showerror("Error", str(exc))

    def _load_chart(self) -> None:
        symbol = self.symbol.get().strip().upper()
        if not symbol:
            messagebox.showwarning("Error", "Enter a ticker.")
            return
        try:
            df = fetch_historical_bars(symbol)
            if df.empty:
                messagebox.showinfo("No Data", f"No data for {symbol}")
                return
            self._show_chart(symbol, df)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _show_chart(self, symbol: str, df) -> None:
        if self._canvas:
            self._canvas.get_tk_widget().destroy()

        fig, (ax_price, ax_vol) = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
        ax_price.plot(df.index, df["open"], label="Open", alpha=0.7)
        ax_price.plot(df.index, df["high"], label="High", alpha=0.7)
        ax_price.plot(df.index, df["low"], label="Low", alpha=0.7)
        ax_price.plot(df.index, df["close"], label="Close")
        ax_price.set_title(f"{symbol} — 30 days, 5-min OHLCV")
        ax_price.set_ylabel("Price")
        ax_price.legend(loc="upper left", fontsize=8)
        ax_vol.bar(df.index, df["volume"], width=0.003)
        ax_vol.set_ylabel("Volume")
        fig.tight_layout()

        self._canvas = FigureCanvasTkAgg(fig, master=self._chart_frame)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _poll(self) -> None:
        try:
            while True:
                kind, data = self._queue.get_nowait()
                if kind == "quote":
                    if data.bid_price is not None:
                        self.bid.set(f"${data.bid_price:.2f}")
                    if data.ask_price is not None:
                        self.ask.set(f"${data.ask_price:.2f}")
                elif kind == "trade" and data.price is not None:
                    self.last.set(f"${data.price:.2f}")
                elif kind == "error":
                    self._status.set(f"Stream error: {data}")
        except queue.Empty:
            pass
        self.after(100, self._poll)

    def _on_close(self) -> None:
        self._streamer.stop()
        plt.close("all")
        self.destroy()


def main() -> None:
    MarketDataTerminal().mainloop()
