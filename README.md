# 📈 TradeLab

<div align="center">

# AI-Assisted Cryptocurrency Paper Trading Platform

A modern cryptocurrency paper trading platform built with **Python**, **FastAPI**, and **Streamlit**.

Simulate crypto trading with live market data, track your portfolio, and test trading strategies without risking real money.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red?logo=streamlit)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?logo=sqlite)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-yellow)

</div>

---

# 🚀 Overview

TradeLab is a cryptocurrency paper trading platform that allows users to practice trading using live market prices without risking real funds.

The project is designed to provide a realistic trading experience while serving as the foundation for future algorithmic trading features including automated strategies, portfolio analytics, and backtesting.

---

# ✨ Features

- 📈 Live cryptocurrency prices
- 💰 Virtual wallet management
- 💼 Portfolio tracking
- 🛒 Buy & Sell orders
- 📊 Real-time dashboard
- ⚡ FastAPI REST API
- 🎨 Streamlit web interface
- 💾 SQLite database
- 🔄 Paper trading environment
- 📉 Profit & Loss tracking

---

# 🪙 Supported Cryptocurrencies

- Bitcoin (BTC)
- Ethereum (ETH)
- XRP

More cryptocurrencies will be added in future releases.

---

# 🛠 Technology Stack

| Layer | Technology |
|--------|------------|
| Language | Python |
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | SQLite |
| Market Data | Binance API |
| Version Control | Git & GitHub |

---

# 🏗 Architecture

```
                    Binance API
                         │
                         ▼
                 Market Data Service
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
   FastAPI Backend                  SQLite Database
        │
        ▼
 Streamlit Dashboard
        │
        ▼
     User Interface
```

---

# 📂 Project Structure

```
TradeLab
│
├── app
│   ├── api
│   ├── components
│   ├── database
│   ├── services
│   ├── utils
│   └── static
│
├── wallet.db
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 📷 Screenshots

### Dashboard

> *(Add screenshot here later)*

```
images/dashboard.png
```

---

### Portfolio

> *(Add screenshot here later)*

```
images/portfolio.png
```

---

### Wallet

> *(Add screenshot here later)*

```
images/wallet.png
```

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/shxmik01/TradeLab.git
```

Move into the project directory

```bash
cd TradeLab
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the FastAPI backend

```bash
python main.py
```

Run the Streamlit frontend

```bash
streamlit run app.py
```

Open your browser and start paper trading.

---

# 🎯 Current Features

✅ Live cryptocurrency prices

✅ Paper trading

✅ Portfolio dashboard

✅ Wallet management

✅ Buy & Sell orders

✅ SQLite database

---

# 🚀 Roadmap

## Version 1.0

- [x] Live cryptocurrency prices
- [x] Paper trading
- [x] Portfolio dashboard
- [x] Wallet management
- [x] Buy & Sell functionality

---

## Version 1.1

- [ ] Trading history
- [ ] Stop Loss
- [ ] Take Profit
- [ ] Portfolio analytics
- [ ] Performance statistics

---

## Version 2.0

- [ ] Automated trading strategies
- [ ] Strategy Builder
- [ ] Backtesting engine
- [ ] Multi-strategy support
- [ ] Risk management

---

## Future Vision

- AI-assisted trading insights
- MT5 integration
- Multi-exchange support
- Cloud deployment
- Mobile dashboard
- Advanced portfolio optimization

---

# 🤝 Contributing

Contributions are welcome.

If you would like to improve TradeLab:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push your branch
5. Open a Pull Request

---

# 📜 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Shxmik**

GitHub:
https://github.com/shxmik01

---

<div align="center">

### ⭐ If you like this project, consider giving it a star!

TradeLab is under active development.

More exciting features are coming soon 🚀

</div>