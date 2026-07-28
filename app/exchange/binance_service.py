from binance.client import Client
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

client = Client(
    os.getenv("BINANCE_API_KEY"),
    os.getenv("BINANCE_SECRET_KEY")
)


def get_price(symbol: str):
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker["price"])


def get_klines(symbol: str, interval="1h", limit=200):
    klines = client.get_klines(
        symbol=symbol,
        interval=interval,
        limit=limit
    )

    df = pd.DataFrame(
        klines,
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