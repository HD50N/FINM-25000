"""Submit paper trades on Alpaca based on the ML signal."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hw1.data_connector.config import get_alpaca_credentials
from hw3.backtest.runner import train_ml_pipeline_for_paper_trading
from hw3.config import DEFAULT_SYMBOL, LOGS_DIRECTORY, LONG_PROBABILITY_THRESHOLD


def get_open_share_count(trading_client: TradingClient, symbol: str) -> float:
    try:
        open_position = trading_client.get_open_position(symbol)
        return float(open_position.qty)
    except Exception:
        return 0.0


def write_log_line(log_path: Path, message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")
    print(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default=DEFAULT_SYMBOL, help="Ticker symbol")
    args = parser.parse_args()
    symbol = args.symbol.upper()

    api_key, secret_key = get_alpaca_credentials()
    trading_client = TradingClient(api_key, secret_key, paper=True)

    pipeline = train_ml_pipeline_for_paper_trading(symbol)
    latest_signal = pipeline["latest_signal"]
    latest_long_probability = pipeline["latest_long_probability"]
    latest_bar_date = pipeline["latest_bar_date"]

    log_path = Path(LOGS_DIRECTORY) / f"paper_trade_{symbol.lower()}.log"
    write_log_line(log_path, f"Symbol: {symbol}")
    write_log_line(log_path, f"Latest bar date: {latest_bar_date}")
    write_log_line(
        log_path,
        f"Long probability: {latest_long_probability:.4f} "
        f"(threshold: {LONG_PROBABILITY_THRESHOLD})",
    )
    write_log_line(
        log_path,
        f"Signal: {'Long' if latest_signal == 1 else 'Flat'}",
    )
    write_log_line(log_path, "Paper trading only — no real money is used.")

    open_share_count = get_open_share_count(trading_client, symbol)

    if latest_signal == 1 and open_share_count == 0:
        account = trading_client.get_account()
        cash = float(account.cash)
        latest_price = pipeline["latest_close_price"]
        share_quantity = int((cash * 0.95) // latest_price)
        if share_quantity <= 0:
            write_log_line(log_path, "No cash available for a buy order.")
            return

        buy_order = MarketOrderRequest(
            symbol=symbol,
            qty=share_quantity,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
        )
        order_response = trading_client.submit_order(buy_order)
        write_log_line(
            log_path,
            f"Submitted PAPER BUY order: {share_quantity} shares of {symbol} "
            f"(order id: {order_response.id})",
        )
    elif latest_signal == 0 and open_share_count > 0:
        sell_order = MarketOrderRequest(
            symbol=symbol,
            qty=int(open_share_count),
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY,
        )
        order_response = trading_client.submit_order(sell_order)
        write_log_line(
            log_path,
            f"Submitted PAPER SELL order: {int(open_share_count)} shares of {symbol} "
            f"(order id: {order_response.id})",
        )
    else:
        if latest_signal == 1:
            write_log_line(log_path, "Signal is Long and position already open. No order sent.")
        else:
            write_log_line(log_path, "Signal is Flat and no open position. No order sent.")

    write_log_line(log_path, f"Log saved to {log_path}")


if __name__ == "__main__":
    main()
