"""Fetch and log the latest quotes for the universe."""

import csv
from datetime import datetime
from pathlib import Path

from alpaca.data.enums import DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, StockLatestTradeRequest

from hw1.data_connector.config import get_alpaca_credentials

QUOTE_LOG_COLUMNS = ["timestamp", "symbol", "bid", "ask", "last", "volume"]


def fetch_latest_quotes(symbols: list[str]) -> dict[str, dict]:
    """Return a dict of symbol -> {bid, ask, last} from the latest quote and trade."""
    api_key, secret_key = get_alpaca_credentials()
    client = StockHistoricalDataClient(api_key, secret_key)

    upper_symbols = [s.upper() for s in symbols]
    quote_request = StockLatestQuoteRequest(symbol_or_symbols=upper_symbols, feed=DataFeed.IEX)
    trade_request = StockLatestTradeRequest(symbol_or_symbols=upper_symbols, feed=DataFeed.IEX)
    quotes = client.get_stock_latest_quote(quote_request)
    trades = client.get_stock_latest_trade(trade_request)

    snapshot = {}
    for symbol in upper_symbols:
        quote = quotes.get(symbol)
        trade = trades.get(symbol)
        if quote is None and trade is None:
            continue
        snapshot[symbol] = {
            "bid": float(quote.bid_price) if quote else None,
            "ask": float(quote.ask_price) if quote else None,
            "last": float(trade.price) if trade else None,
            "volume": float(trade.size) if trade else None,
        }

    return snapshot


def log_quotes(snapshot: dict[str, dict], logs_directory: str) -> Path:
    """Append the quote snapshot to a daily CSV file and return its path."""
    now = datetime.now()
    log_path = Path(logs_directory) / f"quotes_{now:%Y%m%d}.csv"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    is_new_file = not log_path.exists()
    with log_path.open("a", newline="") as log_file:
        writer = csv.writer(log_file)
        if is_new_file:
            writer.writerow(QUOTE_LOG_COLUMNS)
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        for symbol, quote in snapshot.items():
            writer.writerow(
                [timestamp, symbol, quote["bid"], quote["ask"], quote["last"], quote["volume"]]
            )

    return log_path
