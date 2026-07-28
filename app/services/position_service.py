from app.database.database import SessionLocal
from app.database.models import Position


class PositionService:
    def __init__(self):
        self.db = SessionLocal()

    def save_position(self, symbol, quantity, entry_price):
        position = Position(
            symbol=symbol,
            quantity=quantity,
            entry_price=entry_price
        )

        self.db.add(position)
        self.db.commit()
        self.db.refresh(position)

        return position

    def get_positions(self):
        positions = self.db.query(Position).all()

        return {
            p.symbol: {
                "quantity": p.quantity,
                "entry_price": p.entry_price
            }
            for p in positions
        }

    def delete_position(self, symbol):
        position = (
            self.db.query(Position)
            .filter(Position.symbol == symbol)
            .first()
        )

        if position:
            self.db.delete(position)
            self.db.commit()

    def clear_positions(self):
        self.db.query(Position).delete()
        self.db.commit()