from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String

from app.database.database import Base


class Wallet(Base):
    __tablename__ = "wallet"

    id = Column(Integer, primary_key=True)
    cash = Column(Float)
    initial_balance = Column(Float)


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)

    symbol = Column(String, unique=True)
    quantity = Column(Float)
    entry_price = Column(Float)


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)

    trade_type = Column(String)
    symbol = Column(String)

    price = Column(Float)
    quantity = Column(Float)

    profit = Column(Float, default=0)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)

    symbol = Column(String)
    indicator = Column(String)   # "price" | "rsi" | "macd_cross" | "ema_cross"
    comparison = Column(String)  # "above" | "below" for price/rsi, "bullish" | "bearish" for crosses
    threshold = Column(Float, default=0)
    active = Column(Integer, default=1)  # SQLite has no native bool; 1/0