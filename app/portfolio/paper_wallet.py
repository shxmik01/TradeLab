from app.core.config import get_float, get_int
from app.services.wallet_service import WalletService
from app.services.trade_service import TradeService
from app.services.position_service import PositionService
from app.database.database import SessionLocal


class PaperWallet:
    def __init__(self):
        self.db = SessionLocal()
        self.trade_service = TradeService()
        self.wallet_service = WalletService()
        self.position_service = PositionService()

        self.initial_balance = self.wallet_service.get_initial_balance()
        self.cash = self.wallet_service.get_cash()

        # Runtime values read from settings.json once at startup (singleton).
        # If a setting is missing or invalid, the previous hardcoded value
        # is used so behavior is always preserved.
        self.max_positions = get_int("max_open_positions", 4, min_value=1)
        self.position_size = get_float("order_size", 250.0, min_value=0.0, min_exclusive=True)

        self.positions = self.position_service.get_positions()
        self.trade_history = []

    def buy(self, symbol: str, price: float):
        if len(self.positions) >= self.max_positions:
            return {"success": False, "message": "Maximum positions reached"}

        if self.cash < self.position_size:
            return {"success": False, "message": "Insufficient cash"}

        if symbol in self.positions:
            return {"success": False, "message": "Position already exists"}

        quantity = self.position_size / price

        self.positions[symbol] = {
            "quantity": quantity,
            "entry_price": price
        }

        self.position_service.save_position(
            symbol=symbol,
            quantity=quantity,
            entry_price=price
        )

        self.trade_service.save_trade(
            trade_type="BUY",
            symbol=symbol,
            price=price,
            quantity=quantity,
            profit=0.0
        )

        self.cash -= self.position_size
        self.wallet_service.set_cash(self.cash)

        return {"success": True}

    def sell(self, symbol: str, price: float):
        if symbol not in self.positions:
            return {"success": False, "message": "Position not found"}

        position = self.positions[symbol]

        quantity = position["quantity"]
        proceeds = quantity * price
        cost = quantity * position["entry_price"]
        profit = proceeds - cost

        self.cash += proceeds
        self.wallet_service.set_cash(self.cash)

        self.trade_service.save_trade(
            trade_type="SELL",
            symbol=symbol,
            price=price,
            quantity=quantity,
            profit=profit
        )

        self.position_service.delete_position(symbol)
        del self.positions[symbol]

        return {
            "success": True,
            "profit": round(profit, 2)
        }

    def summary(self):
        cash = self.wallet_service.get_cash()
        positions = self.position_service.get_positions()
        trades = self.trade_service.get_all_trades()

        return {
            "initial_balance": self.wallet_service.get_initial_balance(),
            "cash": cash,
            "open_positions": len(positions),
            "positions": positions,
            "trades": len(trades),
            "trade_history": [
                {
                    "type": t.trade_type,
                    "symbol": t.symbol,
                    "price": t.price,
                    "quantity": t.quantity,
                    "profit": t.profit
                }
                for t in trades
            ]
        }