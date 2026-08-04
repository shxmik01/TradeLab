import streamlit as st

def render_bot_control():
    st.subheader("🤖 Trading Bot")

    if "bot_running" not in st.session_state:
        st.session_state.bot_running = False

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶ Start Bot"):
            st.session_state.bot_running = True

    with col2:
        if st.button("⏹ Stop Bot"):
            st.session_state.bot_running = False

    if st.session_state.bot_running:
        st.success("🟢 Bot is Running")
    else:
        st.warning("🔴 Bot is Stopped")