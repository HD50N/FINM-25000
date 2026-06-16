"""Load Alpaca API credentials and paper-trading endpoint configuration."""

import os

from dotenv import load_dotenv

load_dotenv()

# Paper trading REST API (orders, account, etc.)
DEFAULT_PAPER_API_URL = "https://paper-api.alpaca.markets/v2"

# Market data uses a separate host; paper keys work with this endpoint.
DEFAULT_MARKET_DATA_URL = "https://data.alpaca.markets"


def get_alpaca_credentials() -> tuple[str, str]:
    """Return (api_key, secret_key) from environment variables."""
    api_key = os.getenv("ALPACA_API_KEY") or os.getenv("APCA_API_KEY_ID")
    secret_key = os.getenv("ALPACA_SECRET_KEY") or os.getenv("APCA_API_SECRET_KEY")

    if not api_key or not secret_key:
        raise ValueError(
            "Missing Alpaca API credentials. Set ALPACA_API_KEY and ALPACA_SECRET_KEY "
            "(or APCA_API_KEY_ID and APCA_API_SECRET_KEY) in your environment or .env file."
        )

    return api_key, secret_key


def get_paper_api_url() -> str:
    """Return the configured paper trading API URL (includes /v2)."""
    return os.getenv("ALPACA_API_BASE_URL", DEFAULT_PAPER_API_URL).rstrip("/")


def get_paper_api_base_url() -> str:
    """Return paper API host for TradingClient (without /v2 suffix)."""
    url = get_paper_api_url()
    if url.endswith("/v2"):
        return url[:-3]
    return url


def get_market_data_url() -> str:
    """Return the market data REST API base URL."""
    return os.getenv("ALPACA_DATA_API_URL", DEFAULT_MARKET_DATA_URL).rstrip("/")


def get_trading_client():
    """Create an authenticated Alpaca paper TradingClient."""
    from alpaca.trading.client import TradingClient

    api_key, secret_key = get_alpaca_credentials()
    return TradingClient(
        api_key=api_key,
        secret_key=secret_key,
        paper=True,
        url_override=get_paper_api_base_url(),
    )


def verify_paper_auth() -> str:
    """Verify API keys against the paper trading endpoint."""
    account = get_trading_client().get_account()
    return f"Connected to paper API — account {account.account_number} ({account.status})"
