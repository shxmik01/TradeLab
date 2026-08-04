from app.bot import trader
from app.exchange import binance_service


class FakePositionService:
    def get_positions(self):
        return []


class FakeWallet:
    def __init__(self):
        self.position_service = FakePositionService()
        self.bought = []
        self.sold = []

    def buy(self, symbol, price):
        self.bought.append((symbol, price))

    def sell(self, symbol, price):
        self.sold.append((symbol, price))


def test_get_price_retries_and_returns_none(monkeypatch):
    attempts = {"count": 0}

    class FakeClient:
        def get_symbol_ticker(self, symbol):
            attempts["count"] += 1
            raise TimeoutError("ReadTimeout")

    monkeypatch.setattr(binance_service, "client", FakeClient())
    monkeypatch.setattr(binance_service.time, "sleep", lambda _: None)

    assert binance_service.get_price("BTCUSDT") is None
    assert attempts["count"] == 3


def test_run_bot_skips_failed_symbol_and_continues(monkeypatch):
    wallet = FakeWallet()

    class FakeStrategy:
        def get_signal(self, symbol):
            return "BUY"

    monkeypatch.setattr(trader, "strategy", FakeStrategy())
    monkeypatch.setattr(trader, "wallet", wallet)
    monkeypatch.setattr(trader, "WATCHLIST_SYMBOLS", ["BTCUSDT", "ETHUSDT"])

    def fake_get_price(symbol):
        return None if symbol == "BTCUSDT" else 100.0

    monkeypatch.setattr(trader, "get_price", fake_get_price)

    trader.run_bot()

    assert wallet.bought == [("ETHUSDT", 100.0)]
