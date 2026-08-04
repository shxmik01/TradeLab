import streamlit as st
from app.bot.scheduler import start_bot, stop_bot, is_running


def render_bot_panel():
    st.subheader("🤖 Trading Bot")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶ Start Bot", width="stretch"):
            start_bot()

    with col2:
        if st.button("⏹ Stop Bot", width="stretch"):
            stop_bot()

    status = "🟢 Running" if is_running() else "🔴 Stopped"
    st.info(f"Status: {status}")