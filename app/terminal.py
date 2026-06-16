"""Tkinter market data terminal — historical chart and live quotes."""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from data_connector import QuoteStreamer, fetch_historical_bars, get_paper_api_url, verify_paper_auth

DEFAULT_SYMBOL = "AAPL"
HISTORY_DAYS = 30
BAR_MINUTES = 5


class MarketDataTerminal(tk.Tk):
  def __init__(self) -> None:
    super().__init__()
    self.title("Mini Market Data Terminal — Alpaca")
    self.geometry("1100x720")
    self.minsize(900, 600)

    self._event_queue: queue.Queue = queue.Queue()
    self._streamer = QuoteStreamer(
      on_quote=self._enqueue_quote,
      on_trade=self._enqueue_trade,
    )
    self._live_symbol = tk.StringVar(value=DEFAULT_SYMBOL)
    self._history_symbol = tk.StringVar(value=DEFAULT_SYMBOL)
    self._status = tk.StringVar(
      value=f"Connecting to {get_paper_api_url()}…"
    )

    self._bid = tk.StringVar(value="—")
    self._ask = tk.StringVar(value="—")
    self._last = tk.StringVar(value="—")
    self._quote_time = tk.StringVar(value="—")

    self._build_ui()
    self._poll_events()
    self._verify_auth_async()
    self.protocol("WM_DELETE_WINDOW", self._on_close)

  def _verify_auth_async(self) -> None:
    def _check() -> None:
      try:
        message = verify_paper_auth()
      except ValueError as exc:
        message = str(exc)
      except Exception as exc:
        message = f"Paper API auth failed: {exc}"
      self.after(0, lambda: self._set_status(message))

    threading.Thread(target=_check, daemon=True).start()

  def _build_ui(self) -> None:
    header = ttk.Frame(self, padding=10)
    header.pack(fill=tk.X)
    ttk.Label(
      header,
      text="Mini Market Data Terminal",
      font=("Helvetica", 16, "bold"),
    ).pack(side=tk.LEFT)
    ttk.Label(header, textvariable=self._status, foreground="#555").pack(
      side=tk.RIGHT
    )

    notebook = ttk.Notebook(self)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    self._live_tab = ttk.Frame(notebook, padding=10)
    self._history_tab = ttk.Frame(notebook, padding=10)
    notebook.add(self._live_tab, text="Live Quotes")
    notebook.add(self._history_tab, text="Historical Chart")

    self._build_live_tab()
    self._build_history_tab()

  def _build_live_tab(self) -> None:
    controls = ttk.Frame(self._live_tab)
    controls.pack(fill=tk.X, pady=(0, 16))

    ttk.Label(controls, text="Ticker:").pack(side=tk.LEFT)
    entry = ttk.Entry(controls, textvariable=self._live_symbol, width=12)
    entry.pack(side=tk.LEFT, padx=(6, 10))
    entry.bind("<Return>", lambda _e: self._start_stream())

    ttk.Button(controls, text="Subscribe", command=self._start_stream).pack(
      side=tk.LEFT, padx=(0, 6)
    )
    ttk.Button(controls, text="Stop", command=self._stop_stream).pack(side=tk.LEFT)

    quote_frame = ttk.LabelFrame(self._live_tab, text="Live Market Data", padding=20)
    quote_frame.pack(fill=tk.BOTH, expand=True)

    rows = [
      ("Bid", self._bid, "#1a7f37"),
      ("Ask", self._ask, "#b42318"),
      ("Last Trade", self._last, "#175cd3"),
      ("Quote Time", self._quote_time, "#344054"),
    ]
    for idx, (label, var, color) in enumerate(rows):
      ttk.Label(quote_frame, text=f"{label}:", font=("Helvetica", 12)).grid(
        row=idx, column=0, sticky=tk.W, pady=10, padx=(0, 20)
      )
      ttk.Label(
        quote_frame,
        textvariable=var,
        font=("Helvetica", 20, "bold"),
        foreground=color,
      ).grid(row=idx, column=1, sticky=tk.W, pady=10)

    ttk.Label(
      self._live_tab,
      text="Quotes update automatically while subscribed (market hours).",
      foreground="#667085",
    ).pack(anchor=tk.W, pady=(12, 0))

  def _build_history_tab(self) -> None:
    controls = ttk.Frame(self._history_tab)
    controls.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(controls, text="Ticker:").pack(side=tk.LEFT)
    ttk.Entry(controls, textvariable=self._history_symbol, width=12).pack(
      side=tk.LEFT, padx=(6, 10)
    )
    ttk.Button(controls, text="Load Chart", command=self._load_history).pack(
      side=tk.LEFT
    )
    ttk.Label(
      controls,
      text=f"  ({HISTORY_DAYS} days, {BAR_MINUTES}-minute bars)",
      foreground="#667085",
    ).pack(side=tk.LEFT)

    self._chart_container = ttk.Frame(self._history_tab)
    self._chart_container.pack(fill=tk.BOTH, expand=True)

    self._history_canvas: FigureCanvasTkAgg | None = None
    self._history_toolbar: NavigationToolbar2Tk | None = None

  def _set_status(self, message: str) -> None:
    self._status.set(message)

  def _enqueue_quote(self, data) -> None:
    self._event_queue.put(("quote", data))

  def _enqueue_trade(self, data) -> None:
    self._event_queue.put(("trade", data))

  def _poll_events(self) -> None:
    try:
      while True:
        event_type, data = self._event_queue.get_nowait()
        if event_type == "quote":
          self._update_quote_display(data)
        elif event_type == "trade":
          self._update_trade_display(data)
    except queue.Empty:
      pass
    self.after(100, self._poll_events)

  def _update_quote_display(self, quote) -> None:
    self._bid.set(f"${quote.bid_price:,.2f}" if quote.bid_price else "—")
    self._ask.set(f"${quote.ask_price:,.2f}" if quote.ask_price else "—")
    if quote.timestamp:
      ts = quote.timestamp
      if hasattr(ts, "strftime"):
        self._quote_time.set(ts.strftime("%Y-%m-%d %H:%M:%S %Z"))
      else:
        self._quote_time.set(str(ts))

  def _update_trade_display(self, trade) -> None:
    if trade.price:
      self._last.set(f"${trade.price:,.2f}")

  def _start_stream(self) -> None:
    symbol = self._live_symbol.get().strip().upper()
    if not symbol:
      messagebox.showwarning("Invalid Symbol", "Please enter a ticker symbol.")
      return

    self._bid.set("—")
    self._ask.set("—")
    self._last.set("—")
    self._quote_time.set("—")

    try:
      self._streamer.subscribe(symbol)
      self._set_status(f"Streaming live quotes for {symbol}…")
    except ValueError as exc:
      messagebox.showerror("Configuration Error", str(exc))
    except Exception as exc:
      messagebox.showerror("Stream Error", str(exc))

  def _stop_stream(self) -> None:
    self._streamer.stop()
    self._set_status("Stream stopped.")

  def _load_history(self) -> None:
    symbol = self._history_symbol.get().strip().upper()
    if not symbol:
      messagebox.showwarning("Invalid Symbol", "Please enter a ticker symbol.")
      return

    self._set_status(f"Loading {HISTORY_DAYS} days of {BAR_MINUTES}m bars for {symbol}…")
    self.update_idletasks()

    try:
      df = fetch_historical_bars(symbol, days=HISTORY_DAYS, timeframe_minutes=BAR_MINUTES)
      if df.empty:
        messagebox.showinfo("No Data", f"No historical bars returned for {symbol}.")
        self._set_status("No historical data found.")
        return
      self._render_history_chart(symbol, df)
      self._set_status(
        f"Loaded {len(df):,} bars for {symbol} ({df.index.min():%Y-%m-%d} → {df.index.max():%Y-%m-%d})"
      )
    except ValueError as exc:
      messagebox.showerror("Configuration Error", str(exc))
      self._set_status("Failed to load history.")
    except Exception as exc:
      messagebox.showerror("Data Error", str(exc))
      self._set_status("Failed to load history.")

  def _render_history_chart(self, symbol: str, df: pd.DataFrame) -> None:
    if self._history_canvas is not None:
      self._history_canvas.get_tk_widget().destroy()
      self._history_canvas = None
    if self._history_toolbar is not None:
      self._history_toolbar.destroy()
      self._history_toolbar = None

    plot_df = df[["open", "high", "low", "close", "volume"]].copy()
    plot_df.columns = ["Open", "High", "Low", "Close", "Volume"]
    plot_df.index.name = "Date"

    fig = mpf.figure(style="yahoo", figsize=(10, 6))
    ax_ohlc = fig.add_subplot(2, 1, 1)
    ax_vol = fig.add_subplot(2, 1, 2, sharex=ax_ohlc)

    mpf.plot(
      plot_df,
      type="candle",
      ax=ax_ohlc,
      volume=ax_vol,
      style="yahoo",
      warn_too_much_data=len(plot_df) + 1,
    )
    ax_ohlc.set_title(f"{symbol} — {BAR_MINUTES}-Minute OHLCV ({HISTORY_DAYS} Days)")
    ax_ohlc.set_ylabel("Price ($)")
    ax_vol.set_ylabel("Volume")
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
    fig.tight_layout()

    self._history_canvas = FigureCanvasTkAgg(fig, master=self._chart_container)
    self._history_canvas.draw()
    self._history_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    self._history_toolbar = NavigationToolbar2Tk(self._history_canvas, self._chart_container)
    self._history_toolbar.update()
    self._history_toolbar.pack(fill=tk.X)

  def _on_close(self) -> None:
    self._streamer.stop()
    plt.close("all")
    self.destroy()


def main() -> None:
  app = MarketDataTerminal()
  app.mainloop()


if __name__ == "__main__":
  main()
