# `backtest/` — Historical simulation

Backtest mode required by the assignment: the same strategy and the same
position-sizing code as live trading, run over five years of daily Alpaca
bars for the whole universe, compared against an equal-weight buy-and-hold
benchmark.

## Files

- `engine.py` — `run_portfolio_backtest(bars, initial_capital)`: builds the
  0/1 signal matrix with `strategies.generate_signals`, converts each day's
  signals into portfolio weights via `risk.limits.size_positions`
  (called with `equity=1.0` so notionals *are* fractions), and compounds
  the weighted daily returns into an equity curve. Also extracts the trade
  list (every signal flip per symbol, with date/side/price).
- `metrics.py` — `compute_metrics`: total return, CAGR, annualized
  volatility, Sharpe, max drawdown, trade count, and win rate (matched
  buy→sell round trips per symbol). `make_metrics_table` formats the
  comparison table shown in the UI and CLI.
- `runner.py` — fetches the data, runs strategy and benchmark, and packages
  results/metrics/table for the UI tab and `run_backtest.py`.

## Design notes and justification

**The backtest reuses the live risk code.** Weights come from the very same
`size_positions` function the live engine calls. If a sizing rule changes in
`risk/limits.py`, the backtest changes with it automatically — the backtest
stays evidence about the system that actually trades, which is the point of
having a backtest mode at all.

**No look-ahead.** Signals are already shifted one bar inside
`generate_signals`; day *t*'s weights are therefore based on information
through day *t−1*'s close and are applied to day *t*'s return.

**Why an equal-weight buy-and-hold benchmark.** The natural null hypothesis
for a long-only strategy on this universe: "just hold everything." The
comparison isolates what the trend filter adds (drawdown control) and what
it costs (upside in unbroken bull markets).

**Simplifying assumptions, stated.** Fills at the daily close, no slippage,
no commissions (Alpaca is commission-free; the others are idealizations),
dates intersected across symbols (`dropna`) so the weight matrix is always
complete. Stop-losses and the daily halt are *not* simulated — they depend
on intraday prices the daily backtest doesn't see — so backtest results are,
if anything, conservative about what the risk layer adds.

**Style lineage.** The engine/metrics/runner split, the metric set, and the
formatted `metrics_table` mirror `hw2/backtest/` and `hw3/backtest/`, so
anyone who read those assignments can read this immediately.

## Example output (July 2026, default config)

```
                  Return    CAGR Volatility Sharpe Max Drawdown Trades Win Rate
Trend Following   51.53%   8.68%     15.44%   0.62      -25.76%    275   42.65%
Equal Weight B&H  78.13%  12.26%     21.92%   0.64      -43.02%      0    0.00%
```

Typical trend-following shape: fewer points of return in a bull market,
similar Sharpe, roughly half the volatility-of-pain (max drawdown −26% vs
−43%), and a sub-50% win rate — trend systems win by letting the few big
winners run, not by being right often.
