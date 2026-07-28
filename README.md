# 📈 TradeLab

TradeLab is an AI-assisted cryptocurrency paper trading platform built with Python. It allows users to simulate cryptocurrency trading using live market prices without risking real money.

The project is designed as a foundation for a complete algorithmic trading platform, beginning with paper trading and expanding toward automated strategies, backtesting, and advanced portfolio analytics.

---

## Features

- 📊 Live cryptocurrency market prices
- 💼 Paper trading (Buy & Sell)
- 💰 Virtual wallet management
- 📈 Portfolio tracking
- 🔄 Real-time dashboard
- ⚡ FastAPI backend
- 🎨 Streamlit frontend
- 🗄️ SQLite database

---

## Supported Assets

- Bitcoin (BTC)
- Ethereum (ETH)
- XRP

---

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Core application |
| FastAPI | Backend API |
| Streamlit | Web dashboard |
| SQLite | Local database |
| Binance API | Live cryptocurrency prices |

---

## Project Structure

```
crypto-paper-bot/
│
├── app/
│   ├── api/
│   ├── components/
│   ├── database/
│   ├── services/
│   └── utils/
│
├── wallet.db
├── main.py
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/shxmik01/TradeLab.git
```

Move into the project directory:

```bash
cd TradeLab
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI backend.

Start the Streamlit frontend.

Open the application in your browser.

---

## Current Status

✅ Live market data

✅ Paper trading

✅ Portfolio management

✅ Wallet system

🚧 Strategy automation (in progress)

🚧 Performance analytics (planned)

🚧 Backtesting (planned)

---

## Roadmap

### Version 1.0

- Live market prices
- Paper trading
- Portfolio dashboard
- Wallet management

### Version 1.1

- Automated trading strategies
- Trade history
- Stop-loss / Take-profit
- Performance statistics

### Version 2.0

- Strategy backtesting
- Portfolio analytics
- Multi-strategy support
- Risk management

---

## License

This project is released under the MIT License.

---

## Author

Developed by **Shxmik**.