"""Trading bot worker.

`run_bot()` performs one auto-trading pass over the watchlist symbols,
reusing the existing SMAStrategy + PaperWallet (the same components the
FastAPI `/auto-trade` endpoint uses). It is called by the scheduler
thread every INTERVAL seconds.
"""

from datetime import datetime

from app.components.common import WATCHLIST_SYMBOLS
from app.core.state import strategy, wallet
from app.exchange.binance_service import get_price


def _timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


def run_bot() -> None:
    """Run one auto-trading pass over the watchlist symbols."""
    for symbol in WATCHLIST_SYMBOLS:
        try:
            signal = strategy.get_signal(symbol)
            price = get_price(symbol)
            if price is None:
                print(f"[{_timestamp()}] ERROR {symbol} Price unavailable")
                continue

            positions = wallet.position_service.get_positions()

            if signal == "BUY" and symbol not in positions:
                wallet.buy(symbol, price)
                print(f"[{_timestamp()}] {symbol} BUY @ {price:.2f}")

            elif signal == "SELL" and symbol in positions:
                wallet.sell(symbol, price)
                print(f"[{_timestamp()}] {symbol} SELL @ {price:.2f}")

        except Exception as exc:
            print(f"[{_timestamp()}] ERROR {symbol} {exc}")