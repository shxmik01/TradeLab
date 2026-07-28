import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"


def render_order_panel(symbol: str, price: float):
    st.subheader("🛒 Paper Trading")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🟢 BUY", use_container_width=True):
            r = requests.post(f"{API_URL}/buy/{symbol}")
            if r.ok:
                st.success(f"Bought {symbol}")
                st.rerun()
            else:
                st.error(r.json().get("detail", "Buy failed"))

    with col2:
        if st.button("🔴 SELL", use_container_width=True):
            r = requests.post(f"{API_URL}/sell/{symbol}")
            if r.ok:
                st.success(f"Sold {symbol}")
                st.rerun()
            else:
                st.error(r.json().get("detail", "Sell failed"))

    st.caption(f"Current Price: ${price:,.2f}")