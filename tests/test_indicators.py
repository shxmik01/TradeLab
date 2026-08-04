from app.exchange.binance_service import get_klines
from app.bot.indicators import add_indicators

df = get_klines("BTCUSDT")
df = add_indicators(df)

print(df[["close", "EMA50", "EMA200", "RSI"]].tail())