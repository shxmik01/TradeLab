from __future__ import annotations

import streamlit as st

from app.components.bot_panel import render_bot_panel
from app.components.order_panel import render_order_panel
from app.components.chart import render_chart
from app.components.alerts import render_alert_banner
from app.components.common import (
    API_ERROR_MESSAGE,
    get_dashboard_payload,
    initialize_session_state,
)
from app.components.metrics import render_live_prices, render_metrics
from app.components.portfolio_table import (
    render_open_positions,
    render_portfolio,
)
from app.components.settings import render_settings
from app.components.sidebar import load_sidebar
from app.components.timeframe import render_timeframe_selector
from app.components.trade_table import render_trade_history
from app.components.watchlist import render_watchlist

from app.dashboard.styles import load_css
from app.dashboard.about import show as render_about
from app.dashboard.analytics import render_analytics
from app.dashboard.coming_soon import render_coming_soon
from app.dashboard.hero import render_hero
from app.dashboard.market import render_markets
from app.dashboard.topbar import render_topbar


def configure_page() -> None:
    st.set_page_config(
        page_title="Crypto Bot",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_css()


def render_dashboard(payload: dict) -> None:
    wallet = payload["wallet"]
    prices = payload["prices"]

    # Hero
    render_hero()

    # Top bar
    render_topbar(prices)

    # Alerts
    render_alert_banner()

    # Metrics
    render_metrics(wallet, prices)

    # Live Prices
    render_live_prices(prices)

    # Watchlist
    render_watchlist(prices)

    st.divider()

    # Trading View
    st.subheader("📈 Trading View")

    render_timeframe_selector()

    symbol = st.session_state.symbol
    interval = st.session_state.interval

    render_chart(symbol, interval)

    price = prices.get(symbol, 0)
render_order_panel(symbol, price)

st.error("AFTER ORDER PANEL")

render_bot_panel()

st.error("AFTER BOT PANEL")

render_open_positions(wallet, prices)
    # AI Section
    st.divider()

    with st.expander("🤖 AI Insights"):
        render_coming_soon(
            "AI Insights",
            "🤖",
            [
                "Market summary",
                "Risk analysis",
                "Strategy suggestions",
                "Portfolio analysis",
            ],
        )


def main() -> None:
    configure_page()
    initialize_session_state()

    payload = get_dashboard_payload()

    if payload is None:
        st.error(API_ERROR_MESSAGE)
        st.stop()

    prices = payload["prices"]

    page = load_sidebar(prices)

    if page == "Dashboard":
        render_dashboard(payload)

    elif page == "Markets":
        render_markets(prices)

    elif page == "Portfolio":
        render_portfolio(payload["wallet"], prices)

    elif page == "Trades":
        render_trade_history(payload["wallet"])

    elif page == "Analytics":
        render_analytics(payload["wallet"])

    elif page == "Settings":
        render_settings()

    elif page == "About":
        render_about()


if __name__ == "__main__":
    main()