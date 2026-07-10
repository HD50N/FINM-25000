# `tests/` — Unit tests

Offline unit tests for the two modules where a silent mistake costs money:
signal generation and risk limits. No network, no API keys, no Alpaca —
they run anywhere in well under a second:

```bash
python -m pytest project/tests
```

## What is covered, and why these tests

`test_strategy.py` (synthetic price series):

- A clean uptrend produces a long signal; a clean downtrend produces flat —
  the strategy's basic contract.
- **`test_signals_are_shifted_no_lookahead`** — pins the one-bar signal
  shift. Look-ahead is the classic silent backtest bug: everything runs,
  metrics look great, and the results are meaningless. This test makes that
  regression impossible to miss.
- Insufficient history (< slow window) yields flat — the conservative
  default the live engine relies on at startup.

`test_risk.py`:

- A single long position is capped at `MAX_POSITION_FRACTION`.
- Ten longs stay within `MAX_GROSS_EXPOSURE` in total and the per-asset cap
  individually — i.e., no leverage can arise from sizing.
- No longs ⇒ all cash (zero targets).
- The stop-loss fires exactly at the configured threshold and does not fire
  just above it.
- The daily loss halt latches at the configured breach and does not trigger
  on smaller losses.

Tests assert against the constants in `project/config.py` rather than
hard-coded numbers, so retuning limits doesn't break the suite — the tests
verify the *mechanism*, not a particular parameter choice.

## What is deliberately not unit-tested

`data_connector`, `execution`, and `engine` are thin orchestration around
the Alpaca SDK; meaningful tests would be mocks asserting that mocks were
called. They are exercised end-to-end instead: `run_backtest.py` validates
the full data → signals → sizing → metrics path against the real data API,
and the paper account validates order routing. The pure logic those modules
depend on (strategy, risk) is exactly what the unit suite covers.

Each test file inserts the repo root into `sys.path`, the same pattern as
`main.py` and the other runnable scripts in this repo, so `pytest` works
from the repo root with no packaging or conftest machinery.
