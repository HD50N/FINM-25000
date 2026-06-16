"""Alpaca market data connector for historical bars and live quotes."""

from .config import get_alpaca_credentials, get_paper_api_url, verify_paper_auth
from .historical import fetch_historical_bars, get_historical_client
from .streaming import QuoteStreamer

__all__ = [
    "get_alpaca_credentials",
    "get_paper_api_url",
    "verify_paper_auth",
    "fetch_historical_bars",
    "get_historical_client",
    "QuoteStreamer",
]
