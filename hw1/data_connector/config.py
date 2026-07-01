"""Load Alpaca API keys from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()


def get_alpaca_credentials() -> tuple[str, str]:
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")

    if not api_key or not secret_key:
        raise ValueError("Set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env")

    return api_key, secret_key
