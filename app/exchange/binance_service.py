import os
import time
from datetime import datetime

import pandas as pd
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()

client = Client(
    os.getenv("BINANCE_API_KEY"),
    os.getenv("BINANCE_SECRET_KEY")
)


def _timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def _request_with_retry(action, *args, **kwargs):
    """Execute a Binance request with capped retries and exponential backoff."""
    last_error = None
    for attempt in range(1, 4):
        try:
            return action(*args, **kwargs)
        except Exception as exc:
            last_error = exc
            if attempt == 3:
                break
            wait_seconds = 2 ** (attempt - 1)
            print(f"[{_timestamp()}] ERROR Retry {attempt}/3 for Binance request in {wait_seconds}s: {exc}")
            time.sleep(wait_seconds)

    print(f"[{_timestamp()}] ERROR Binance request failed after 3 attempts: {last_error}")
    return None


def get_price(symbol: str):
    """Fetch the latest price for a symbol with retry/backoff protection."""
    result = _request_with_retry(lambda: client.get_symbol_ticker(symbol=symbol))
    if result is None:
        return None

    try:
        return float(result["price"])
    except (KeyError, TypeError, ValueError) as exc:
        print(f"[{_timestamp()}] ERROR Invalid price payload for {symbol}: {exc}")
        return None


def get_klines(symbol: str, interval="1h", limit=200):
    """Fetch klines for a symbol with retry/backoff protection."""
    result = _request_with_retry(
        lambda: client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
        )
    )
    if result is None:
        return None

    df = pd.DataFrame(
        result,
        columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ]
    )

    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float) 
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
    df["volume"] = df["volume"].astype(float)
    
    return df