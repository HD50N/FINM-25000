# `execution/` — Order routing (Alpaca paper only)

The only module in the project that can place orders. Keeping every
`TradingClient` call behind one small class means "paper trading only" is
enforced in exactly one line of code.

## `AlpacaBroker`

- `__init__` — builds `TradingClient(api_key, secret_key, paper=True)`.
  `paper=True` is hard-coded, not configurable: there is deliberately no
  flag, env var, or code path that could reach a real-money account.
- `get_equity_and_cash()` — account snapshot for sizing and P&L.
- `get_positions()` — `dict[symbol, {qty, avg_entry_price, market_value,
  unrealized_pl}]`, the ground truth the engine rebalances against.
- `submit_market_order(symbol, qty, side)` — DAY market order; validates
  qty/side, then returns `{id, symbol, side, qty, filled_qty, status}`.
- `get_open_orders()` — currently open orders (accepted / pending / …),
  used so the engine does not re-submit while a prior order is still live.
- `get_order(order_id)` / `get_order_status(order_id)` — look up current
  state (submitted / pending_new / filled / partially_filled / canceled /
  rejected).
- `wait_for_order_update(order_id)` — polls until a terminal status
  (filled, partially_filled, canceled, rejected, …) or timeout, so the UI
  does not get stuck showing only `pending_new`.

## Design notes and justification

**Why a thin wrapper instead of using `TradingClient` directly.** Three
reasons: (1) the paper-only guarantee lives in one place; (2) the rest of
the system deals in plain dicts and floats rather than Alpaca SDK objects,
so strategy/risk/engine stay SDK-agnostic and testable; (3) request
construction (`MarketOrderRequest`, `OrderSide`, `TimeInForce`) is written
once, following the exact pattern of `hw3/paper_trade.py`.

**Why market DAY orders + status polling.** The universe is mega-cap stocks
and SPY, so market orders usually fill quickly. Alpaca often returns
`pending_new` at submit time; the engine therefore polls via
`wait_for_order_update` and logs the assignment's required states
(submitted → filled / partially_filled / canceled). Limit orders remain a
listed improvement in the project README.

**Error handling** is deliberately *not* swallowed here: `submit_order`
exceptions (rejected orders, invalid parameters, network errors) propagate
to the engine, which catches them per-order, logs the failure to the event
log, and continues the cycle — one bad symbol never kills the loop.
Invalid qty/side are rejected locally before hitting the API.

**Why integer share quantities.** Whole shares keep paper fills predictable
and mirror `hw3/paper_trade.py`. Fractional orders are an easy extension.
