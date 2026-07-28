from app.database.database import SessionLocal
from app.database.models import Wallet


class WalletService:
    def __init__(self):
        self.db = SessionLocal()

    def get_wallet(self):
        wallet = self.db.query(Wallet).first()

        if wallet is None:
            wallet = Wallet(
                initial_balance=2000.0,
                cash=2000.0
            )
            self.db.add(wallet)
            self.db.commit()
            self.db.refresh(wallet)

        return wallet

    def get_cash(self):
        return self.get_wallet().cash

    def set_cash(self, cash):
        wallet = self.get_wallet()
        wallet.cash = cash
        self.db.commit()

    def get_initial_balance(self):
        return self.get_wallet().initial_balance

    def reset_wallet(self):
        wallet = self.get_wallet()
        wallet.initial_balance = 2000.0
        wallet.cash = 2000.0
        self.db.commit()