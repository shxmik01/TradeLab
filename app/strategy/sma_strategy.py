from app.exchange.binance_service import get_klines
from app.indicators.moving_average import sma


class SMAStrategy:

    def __init__(self, period=20):
        self.period = period

    def get_signal(self, symbol: str):

        df = get_klines(symbol, interval="1h", limit=100)

        df = sma(df, self.period)

        last_close = df["close"].iloc[-1]
        last_sma = df[f"SMA_{self.period}"].iloc[-1]

        if last_close > last_sma:
            return "BUY"

        elif last_close < last_sma:
            return "SELL"

        return "HOLD"