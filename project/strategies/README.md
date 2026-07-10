# `strategies/` — Signal generation

The systematic trading rules. Pure functions from price data to 0/1 signals —
no state, no I/O, no broker knowledge — which is what makes them trivially
backtestable and unit-testable offline.

## Strategy: trend-following SMA crossover

`momentum.py` holds a stock while its 20-day simple moving average is above
its 50-day SMA, and stays in cash otherwise. Long-only.

- `generate_signals(df)` — full 0/1 series over a bar history (used by the
  backtest).
- `latest_signal(df)` — the current 0/1 signal from the most recent closed
  bars (used by the live engine each cycle). Returns 0 (flat) when there is
  not enough history for the slow window — the conservative default.

## What behavior it exploits, and why it should work

Prices trend more than a random walk would suggest: information diffuses
gradually (investors underreact to news), and flows herd (momentum begets
momentum). A slow/fast moving-average crossover is the simplest robust
detector of such trends — it holds through noise while a trend is intact and
steps aside when it breaks. The expected payoff profile is not higher raw
return than buy-and-hold, but *better risk-adjusted* return: trend filters
historically cut drawdowns sharply (our 5-year backtest: −26% max drawdown
vs −43% for buy-and-hold at a comparable Sharpe) because they move to cash
in sustained declines.

## Design notes and justification

**No look-ahead.** Signals are shifted one bar: a crossover observed at the
close of day *t* is only tradable on day *t+1*. This is the same convention
as `hw2/strategies/trend_following.py` (`.shift(1).fillna(0).astype(int)`),
and one of the tests (`test_signals_are_shifted_no_lookahead`) locks it in.

**Why 20/50 days.** Standard short/intermediate trend windows; 20 matches
the rolling windows used across HW2/HW3. Both are single constants in
`project/config.py`, so tuning them requires no code change — a requirement
of the assignment (strategy parameters in config).

**Why the signal is binary rather than weighted.** Position *sizing* is the
risk module's job (`risk/limits.py`). Keeping the strategy's output to
{0, 1} keeps the separation of concerns the assignment asks for: strategy
says *what* to hold, risk says *how much*.

**Why one strategy.** Depth over breadth: the engineering around the signal
(pipeline, risk, execution, UI) is the substance of the project. The package
layout supports adding more strategy modules alongside `momentum.py`.
