# `ui/` — Monitoring and control

Two Tkinter frames that `app/terminal.py` mounts as tabs, covering the
project's UI requirements: show positions and P&L, recent signals and
orders, and system status; provide start/stop control and a backtest mode.

## `PaperTradingFrame` (tab: "Paper Trading")

- **Controls** — Start / Stop buttons for the live engine.
- **Status line** — Running / Stopped / Halted, connected / disconnected,
  mode (`paper`), the configured universe, and the cycle interval.
- **Account line** — equity, cash, cumulative P&L since engine start,
  current drawdown from peak equity, trade count, hit rate.
- **Positions table** — one row per universe symbol: current signal
  (Long/Flat), quantity, average entry, market value, unrealized P&L.
- **Recent orders table** — order id, side, qty, filled qty, and status
  (`filled` / `partially_filled` / `canceled` / …).
- **Event feed** — the engine's timestamped log: submitted → filled /
  canceled transitions, position qty fill confirmations, risk halts,
  errors.

The frame polls `engine.get_snapshot()` once per second with Tk's `after()`.
The engine never touches widgets — all UI mutation happens on the Tk main
thread, which Tkinter requires. This is the same poll-don't-push pattern the
terminal already uses for HW1's quote stream. `shutdown()` cancels the timer
and stops the engine; the terminal calls it from its window-close handler so
closing the app never leaves a trading thread running.

Stop is dispatched on a helper thread because `engine.stop()` joins the
engine thread (up to its cycle wait) and must not freeze the UI.

## `ProjectBacktestFrame` (tab: "Project Backtest")

Runs `backtest.runner.run_backtest()` over the configured universe and
shows the strategy-vs-benchmark metrics table plus three charts (equity
curve, drawdown, long-position exposure) in an embedded notebook — the same
`Text` + `FigureCanvasTkAgg` presentation as the HW2/HW3 tabs.

The runner import happens inside the button handler so merely opening the
app never triggers a data download.

## Why Tkinter, and why this file layout

The project permits any lightweight GUI toolkit. This repo already has a
shared Tkinter terminal with one tab per assignment; adding tabs keeps a
single, consistent operator surface instead of a second web stack running in
parallel. The frames live here (not in `app/terminal.py`) so the UI is a
separate module as the assignment's structure requires — `app/terminal.py`
only instantiates them and forwards its close event, keeping the shared
terminal small.

Parameters (universe, risk limits, cycle time) are adjusted via
`project/config.py` rather than in-UI editing, which the project
explicitly allows ("adjust key parameters (e.g., risk limits) via config").
