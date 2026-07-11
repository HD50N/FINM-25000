# `risk/` — Position sizing and risk limits

Everything that stands between a raw signal and an order. The live engine
and the backtest both call this module, so simulated and real behavior
cannot drift apart.

## Files

`limits.py` exposes three pure functions and one small state object:

- `size_positions(signals, equity)` — converts 0/1 signals into target
  dollar notionals. Long symbols split equity equally, subject to both caps
  (see below). Flat symbols get 0.
- `apply_stop_losses(signals, prices, risk_state)` — forces a signal to 0
  when the live price has fallen `STOP_LOSS_FRACTION` below the recorded
  entry price.
- `check_daily_loss(equity, risk_state)` — returns True (and latches
  `halted`) once equity has dropped `MAX_DAILY_LOSS_FRACTION` below the
  day's starting equity.
- `RiskState` — a dataclass carrying the cross-cycle bookkeeping the pure
  functions need: day-start equity, per-symbol entry prices, halted flag.
  The engine resets it at the start of each trading day.

## The limits, and why these ones

| Limit | Value | Rationale |
|---|---|---|
| Per-asset cap | 15% of equity | Caps single-name blowup risk; with 10 names, equal weight is ~9.5%, so the cap binds only when few names are long |
| Gross exposure cap | 95% of equity | No leverage — consistent with this repo's deliberate switch from buying power to cash (commit `7689df1`) — with a 5% cash buffer so market orders don't bounce on insufficient funds |
| Stop-loss | 5% from entry | A trend that instantly loses 5% was a false breakout; exit rather than wait for the slow crossover to confirm |
| Daily loss halt | 3% of day-start equity | Circuit breaker against fast market breaks and, importantly, against *system bugs* — a runaway engine can lose at most ~3% a day |

All four are constants in `project/config.py`.

## Design notes and justification

**Why pure functions + a state dataclass.** The checks themselves are
side-effect-free (easy to unit test — see `tests/test_risk.py`), and all
mutable bookkeeping is confined to one visible `RiskState` object owned by
the engine. This mirrors the codebase's functions-first style.

**Why the halt liquidates.** Once the daily loss limit is hit, the engine
zeroes all signals, which the rebalancer turns into closing orders. Holding
positions while "halted" would keep risk on while removing the ability to
manage it.

**Why stop-losses act on signals rather than sending orders directly.** A
stop just overrides the signal to 0; the normal rebalancing path then closes
the position. One order path means one place where orders happen — simpler
to audit and impossible for stop and rebalance logic to fight each other.
