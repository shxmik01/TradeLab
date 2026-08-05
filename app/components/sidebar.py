"""Sidebar composition — navigation only (no watchlist, per spec)."""

import streamlit as st


def load_sidebar(prices: dict):
    """Render the main sidebar and return the selected page."""
    st.sidebar.title("🚀 TEST SIDEBAR")
    st.sidebar.caption("Professional Trading Platform")
    page = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Markets",
            "Scanner",
            "Portfolio",
            "Trades",
            "Analytics",
            "Settings",
            "About",
        ],
        format_func=_nav_label,
        key="sidebar_navigation",
    )
    st.sidebar.divider()
    st.sidebar.success("Paper Trading")
    return page


_NAV_ICONS = {
    "Dashboard": "🏠 Dashboard",
    "Markets": "📊 Markets",
    "Scanner": "🔍 Scanner",
    "Portfolio": "💼 Portfolio",
    "Trades": "📜 Trades",
    "Analytics": "📈 Analytics",
    "Settings": "⚙️ Settings",
    "About": "👤 About",
}
def _nav_label(page: str) -> str:
    return _NAV_ICONS.get(page, page)
