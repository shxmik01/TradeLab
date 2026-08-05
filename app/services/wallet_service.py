from app.core.config import get_float
from app.database.database import SessionLocal
from app.database.models import Wallet


class WalletService:
    def __init__(self):
        self.db = SessionLocal()

    def _starting_balance(self) -> float:
        """Read the configured starting balance (fallback: previous default)."""
        return get_float("starting_balance", 2000.0, min_value=0.0, min_exclusive=True)

    def get_wallet(self):
        wallet = self.db.query(Wallet).first()

        if wallet is None:
            # Config-backed value is used ONLY when the wallet row is first
            # created — an existing wallet's balance is never overwritten.
            starting = self._starting_balance()
            wallet = Wallet(
                initial_balance=starting,
                cash=starting
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
        # Explicit reset — re-seeded from the configured starting balance.
        starting = self._starting_balance()
        wallet.initial_balance = starting
        wallet.cash = starting
        self.db.commit()
