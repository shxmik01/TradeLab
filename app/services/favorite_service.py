from app.database.database import SessionLocal
from app.database.models import Favorite

_DEFAULT_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]


class FavoriteService:
    def __init__(self):
        self.db = SessionLocal()

    def get_all(self):
        favorites = self.db.query(Favorite).all()

        if not favorites:
            # Seed with the default watchlist so a fresh install isn't empty.
            for symbol in _DEFAULT_SYMBOLS:
                self.db.add(Favorite(symbol=symbol))
            self.db.commit()
            favorites = self.db.query(Favorite).all()

        return [f.symbol for f in favorites]

    def add(self, symbol):
        symbol = symbol.upper()
        exists = self.db.query(Favorite).filter(Favorite.symbol == symbol).first()

        if not exists:
            self.db.add(Favorite(symbol=symbol))
            self.db.commit()

        return self.get_all()

    def remove(self, symbol):
        symbol = symbol.upper()
        self.db.query(Favorite).filter(Favorite.symbol == symbol).delete()
        self.db.commit()

        return self.get_all()
