"""Timeframe selector used above the chart."""

import streamlit as st


def render_timeframe_selector() -> None:
    """Render horizontal timeframe buttons above the chart.

    The active interval is rendered with Streamlit's "primary" button
    style (styled via the `[kind="primary"]` rule in dashboard.css) so
    the current selection is visible, matching a real trading terminal.
    """
    intervals = ["1m", "5m", "15m", "1h", "4h", "1d"]
    cols = st.columns(len(intervals))
    active_interval = st.session_state.get("interval")

    for col, interval in zip(cols, intervals):
        with col:
            is_active = interval == active_interval
            clicked = st.button(
                interval,
                key=f"timeframe_{interval}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            )
            if clicked:
                st.session_state.interval = interval
