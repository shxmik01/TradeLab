from app.exchange.binance_service import get_klines
from app.bot.indicators import add_indicators


BUY = "BUY"
SELL = "SELL"
HOLD = "HOLD"


def analyze(symbol: str):

    df = get_klines(symbol)

    df = add_indicators(df)

    latest = df.iloc[-1]

    price = latest["close"]
    ema50 = latest["EMA50"]
    ema200 = latest["EMA200"]
    rsi = latest["RSI"]

    print(
        f"{symbol} | Price={price:.2f} "
        f"EMA50={ema50:.2f} "
        f"EMA200={ema200:.2f} "
        f"RSI={rsi:.2f}"
    )

    # Buy Signal
    if rsi < 30 and ema50 > ema200:
        return BUY

    # Sell Signal
    if rsi > 70:
        return SELL

    return HOLD