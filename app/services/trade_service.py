from app.database.database import SessionLocal
from app.database.models import Trade


class TradeService:
    def __init__(self):
        self.db = SessionLocal()

    def save_trade(
        self,
        trade_type,
        symbol,
        price,
        quantity,
        profit=0.0
    ):
        trade = Trade(
            trade_type=trade_type,
            symbol=symbol,
            price=price,
            quantity=quantity,
            profit=profit
        )

        self.db.add(trade)
        self.db.commit()
        self.db.refresh(trade)

        return trade

    def get_all_trades(self):
        return self.db.query(Trade).all()

    def get_closed_trades(self):
        return (
            self.db.query(Trade)
            .filter(Trade.trade_type == "SELL")
            .all()
        )

    def clear_trades(self):
        self.db.query(Trade).delete()
        self.db.commit()