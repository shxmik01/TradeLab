"""Overview metric cards for the trading dashboard."""

import streamlit as st

from app.components.common import WATCHLIST_SYMBOLS


def render_metrics(wallet: dict, prices: dict) -> None:
    """Render the main hero metrics for the dashboard."""
    st.subheader("📊 Portfolio Overview")

    pnl = wallet.get("cash", 0) - wallet.get("initial_balance", 0)
    cols = st.columns(4)

    with cols[0]:
        st.metric("💰 Cash", f"${wallet.get('cash', 0):,.2f}")

    with cols[1]:
        st.metric("📦 Positions", wallet.get("open_positions", 0))

    with cols[2]:
        st.metric("📜 Trades", wallet.get("trades", 0))

    with cols[3]:
        st.metric("💹 Total P/L", f"${pnl:,.2f}")


def render_live_prices(prices: dict) -> None:
    """Render compact live price cards for top market symbols."""
    st.subheader("📈 Live Market")

    cols = st.columns(len(WATCHLIST_SYMBOLS))

    for col, symbol in zip(cols, WATCHLIST_SYMBOLS):
        with col:
            label = symbol.removesuffix("USDT")
            st.metric(label, f"${prices.get(symbol, 0):,.2f}")
