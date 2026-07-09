# `engine/` — Live trading engine

`LiveTradingEngine` is the orchestrator: a background thread that runs the
data → signals → risk → orders cycle every `CYCLE_SECONDS` and publishes a
thread-safe snapshot for the UI. It owns no trading logic of its own — it
sequences the other modules.

## Lifecycle

- `start()` — spawns a daemon thread; connects to Alpaca, records starting
  equity (the baseline for cumulative P&L), initializes `RiskState` from
  existing positions, then loops.
- `stop()` — sets a `threading.Event`; the loop exits at the next check
  (the event doubles as the sleep timer, so stopping is immediate, not
  delayed by up to a full cycle).
- `get_snapshot()` — returns a copy of the current state: running /
  connected / halted flags, mode ("paper"), equity, cash, cumulative P&L,
  trade count, hit rate, positions, signals, recent orders, recent events.

## One cycle, in order

1. Refresh equity/cash; if the calendar day changed, reset `RiskState`
   (new day-start equity, entry prices re-seeded from actual positions).
2. Fetch latest quotes for the universe and append them to
   `logs/quotes_YYYYMMDD.csv` — the assignment's live data pipeline with
   logging of timestamps, prices, and volumes.
3. Fetch daily bars and compute `latest_signal` per symbol.
4. Risk: `check_daily_loss` (halt ⇒ all signals to 0 ⇒ full liquidation),
   otherwise `apply_stop_losses`.
5. `size_positions` into dollar targets; diff target share counts against
   actual Alpaca positions; submit market orders only for the differences.
6. Update trade statistics (count, closed-trade hit rate) and the snapshot.

## Design notes and justification

**Why rebalance-to-target instead of event-driven buys/sells.** Each cycle
re-derives the desired portfolio from scratch and compares it to *broker
truth* (`get_positions()`), not to local bookkeeping. Cycles are therefore
idempotent — a no-change cycle sends zero orders — and self-healing: after
a rejected order, a crash, or a restart, the next cycle simply converges to
target again. This is the simplest architecture that is robust to the error
cases the assignment asks about.

**Why a thread + snapshot instead of callbacks into the UI.** Tkinter
widgets may only be touched from the Tk main thread. The engine therefore
never calls the UI; it updates a dict under a lock, and the UI polls it on
an `after()` timer — the same one-directional pattern as HW1's
`QuoteStreamer` + queue + `_poll()` in `app/terminal.py`.

**Why errors don't stop the loop.** Each cycle body is wrapped in
try/except: a network blip or a rejected order is logged to the event feed
and `logs/engine.log`, and the engine tries again next cycle. Only a failure
to connect at startup aborts, since nothing can work without credentials.

**Why per-order try/except in `_rebalance`.** One symbol's rejected order
(e.g., a halted stock) must not prevent the remaining orders from going out.

**Logging.** Every event is timestamped `[YYYY-MM-DD HH:MM:SS] message`,
appended to `project/logs/engine.log`, echoed to stdout, and kept (last 200)
in the snapshot for the UI — the same `write_log_line` format as
`hw3/paper_trade.py`.

**Known limitation.** Trade count and hit rate live in memory and reset on
restart; positions and P&L do not (they come from the broker). A persistent
trade journal is listed as an improvement in the project README.
