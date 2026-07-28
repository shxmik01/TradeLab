"""Professional settings panel placeholder module."""

import streamlit as st

from app.components.alerts import render_alert_manager


def render_settings() -> None:
    """Render a polished settings page with placeholders for future enhancements."""
    st.title("⚙ Settings")

    st.markdown("### Configuration")
    st.info("These controls are placeholders and can be wired to persistent settings later.")

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Theme", ["Dark", "Light", "System"], key="theme_setting")
            st.selectbox("Default Symbol", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"], key="default_symbol")
        with col2:
            st.selectbox("Default Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"], key="default_timeframe")
            st.checkbox("Notifications", value=True, key="notifications")

    st.divider()
    st.markdown("### Risk Management")
    st.checkbox("Auto-stop loss", key="risk_stop")
    st.checkbox("Auto-take profit", key="risk_take_profit")
    st.slider("Max risk per trade (%)", 0, 10, 2, key="risk_percent")

    st.divider()
    render_alert_manager()
