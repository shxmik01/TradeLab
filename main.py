from app.exchange.binance_service import get_klines
from app.strategy.sma_strategy import SMAStrategy
from fastapi import FastAPI, HTTPException

from app.database.database import Base, engine
from app.database import models

from app.exchange.binance_service import get_price
from app.portfolio.paper_wallet import PaperWallet

app = FastAPI(
    title="Crypto Paper Trading Bot",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

from app.core.state import wallet, strategy

@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Crypto Paper Trading Bot is online 🚀"
    }

@app.get("/klines/{symbol}")
def klines(symbol: str):

    df = get_klines(symbol.upper())

    return df.to_dict(orient="records")
@app.get("/price/{symbol}")
def price(symbol: str):
    return {
        "symbol": symbol.upper(),
        "price": get_price(symbol.upper())
    }
@app.post("/auto-trade/{symbol}")
def auto_trade(symbol: str):
    symbol = symbol.upper()

    signal = strategy.get_signal(symbol)
    price = get_price(symbol)

    positions = wallet.position_service.get_positions()

    if signal == "BUY" and symbol not in positions:
        result = wallet.buy(symbol, price)

    elif signal == "SELL" and symbol in positions:
        result = wallet.sell(symbol, price)

    else:
        result = {
            "success": True,
            "message": "No action taken"
        }

    return {
        "symbol": symbol,
        "price": price,
        "signal": signal,
        "result": result
    }
@app.get("/signal/{symbol}")
def signal(symbol: str):
    return {
        "symbol": symbol.upper(),
        "signal": strategy.get_signal(symbol.upper())
    }

@app.get("/wallet")
def wallet_info():
    return wallet.summary()


@app.get("/debug/db")
def debug_db():
    return {
        "cash": wallet.wallet_service.get_cash(),
        "positions": wallet.position_service.get_positions(),
        "trades": len(wallet.trade_service.get_all_trades())
    }


@app.post("/buy/{symbol}")
def buy(symbol: str):
    price = get_price(symbol.upper())

    result = wallet.buy(symbol.upper(), price)

    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )

    return wallet.summary()


@app.post("/sell/{symbol}")
def sell(symbol: str):
    price = get_price(symbol.upper())

    result = wallet.sell(symbol.upper(), price)

    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result["message"]
        )

    return {
        "profit": result["profit"],
        "wallet": wallet.summary()
    }
    