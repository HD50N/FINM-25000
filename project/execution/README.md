# `execution/` — Order routing (Alpaca paper only)

The only module in the project that can place orders. Keeping every
`TradingClient` call behind one small class means "paper trading only" is
enforced in exactly one line of code.

## `AlpacaBroker`

- `__init__` — builds `TradingClient(api_key, secret_key, paper=True)`.
  `paper=True` is hard-coded, not configurable: there is deliberately no
  flag, env var, or code path that could reach a real-money account, per the
  assignment's hard requirement.
- `get_equity_and_cash()` — account snapshot for sizing and P&L.
- `get_positions()` — `dict[symbol, {qty, avg_entry_price, market_value,
  unrealized_pl}]`, the ground truth the engine rebalances against.
- `submit_market_order(symbol, qty, side)` — DAY market order; returns
  `{id, symbol, side, qty, status}` so callers can display and track state.
- `get_order_status(order_id)` — look up an order's current state
  (accepted / filled / partially_filled / canceled / rejected).

## Design notes and justification

**Why a thin wrapper instead of using `TradingClient` directly.** Three
reasons: (1) the paper-only guarantee lives in one place; (2) the rest of
the system deals in plain dicts and floats rather than Alpaca SDK objects,
so strategy/risk/engine stay SDK-agnostic and testable; (3) request
construction (`MarketOrderRequest`, `OrderSide`, `TimeInForce`) is written
once, following the exact pattern of `hw3/paper_trade.py`.

**Why market DAY orders.** The universe is mega-cap stocks and SPY; the
rebalance quantities are small relative to displayed liquidity, so market
orders fill immediately and completely in practice. That keeps order-state
handling simple — the status returned at submission plus
`get_order_status()` covers the assignment's submitted/filled/canceled
tracking without a pending-order reconciliation loop. Limit orders are the
first listed improvement in the project README.

**Error handling** is deliberately *not* swallowed here: `submit_order`
exceptions (rejected orders, invalid parameters, network errors) propagate
to the engine, which catches them per-order, logs the failure to the event
log, and continues the cycle — one bad symbol never kills the loop.

**Why integer share quantities.** Whole shares keep paper fills predictable
and mirror `hw3/paper_trade.py`. Fractional orders are an easy extension.
