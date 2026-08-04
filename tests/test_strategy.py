from app.bot.strategy import analyze

coins = [
    "BTCUSDT",
    "ETHUSDT",
    "XRPUSDT"
]

for coin in coins:
    signal = analyze(coin)
    print(f"{coin}: {signal}")