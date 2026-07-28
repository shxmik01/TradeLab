from __future__ import annotations

import streamlit as st


def show() -> None:
    st.title("👤 About")

    st.markdown(
        """
        ## 🚀 Shxmik TradeLab

        *Professional Trading Platform*

        A modern cryptocurrency paper trading platform built with
        **Python**, **FastAPI**, **Streamlit**, **Plotly**, and the
        **Binance API**.

        Practice trading with real market data without risking real money.
        """
    )

    st.divider()

    st.subheader("✨ Features")

    st.markdown("""
- 📈 Live Market Data
- 📊 Interactive Charts
- 💰 Paper Trading
- 📁 Portfolio Tracking
- 📜 Trade History
- 📉 Technical Indicators
- 🤖 AI Features (Coming Soon)
""")

    st.divider()

    st.subheader("👨‍💻 Built By")

    st.success("""
**Shxmik Ahamed**

Python Developer

AI & Software Enthusiast
""")

    st.divider()

    st.subheader("📬 Contact")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Email")
        st.write("shxmik.01@gmail.com")

    with col2:
        st.markdown("### Website")
        st.write("https://yourwebsite.com")

    st.divider()

    st.subheader("🌐 Social Media")

    st.markdown("""
- 🐙 GitHub
- 💼 LinkedIn
- 🐦 X (Twitter)
- 📸 Instagram
- ▶️ YouTube
""")

    st.divider()

    st.caption("Shxmik TradeLab • Version 1.0.0")