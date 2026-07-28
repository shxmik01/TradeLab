"""Markets page: symbol search and a user-managed favorites list.

Frontend-only. Search reuses the existing generic `/price/{symbol}`
and `/klines/{symbol}` endpoints (they already accept any Binance
symbol, not just the 4 in WATCHLIST_SYMBOLS) — no backend changes.
"""

from __future__ import annotations

import streamlit as st

from app.components.common import (
    WATCHLIST_SYMBOLS,
    add_favorite,
    fetch_json,
    get_24h_change,
    get_favorites,
    remove_favorite,
)
from app.components.watchlist import render_watchlist
from app.dashboard.coming_soon import render_coming_soon

FOREX_FEATURES = [
    "Major currency pairs",
    "Pip calculator",
    "Currency strength meter",
    "Economic calendar",
    "Trading sessions",
]

FUTURES_FEATURES = [
    "Commodity futures",
    "Index futures",
    "Crypto futures",
]


def _init_favorites() -> None:
    """Load favorites from the backend if available, else fall back to a
    session-only list so the page still works before the /favorites
    route has been added to the backend."""
    if "favorite_symbols" in st.session_state:
        return

    persisted = get_favorites()
    st.session_state.favorites_persisted = persisted is not None
    st.session_state.favorite_symbols = persisted if persisted is not None else list(WATCHLIST_SYMBOLS)


def render_markets(prices: dict) -> None:
    """Render the Markets page: Crypto (live) plus Forex/Futures placeholders."""
    st.title("📊 Markets")

    crypto_tab, forex_tab, futures_tab = st.tabs(["🟢 Crypto", "🚧 Forex", "🚧 Futures"])

    with crypto_tab:
        _render_crypto_market(prices)
    with forex_tab:
        render_coming_soon("Forex", "🚧", FOREX_FEATURES)
    with futures_tab:
        render_coming_soon("Futures", "🚧", FUTURES_FEATURES)


def _render_crypto_market(prices: dict) -> None:
    """The existing Crypto search + favorites content."""
    _init_favorites()

    if not st.session_state.favorites_persisted:
        st.caption("⚠️ Favorites aren't saved to your account yet — add the `/favorites` route to persist them across sessions.")
    _render_search()
    st.divider()

    render_watchlist(
        prices,
        symbols=st.session_state.favorite_symbols,
        heading="⭐ Favorites",
    )

    if st.session_state.favorite_symbols:
        with st.expander("Manage favorites"):
            to_remove = st.selectbox("Remove a symbol", st.session_state.favorite_symbols, key="remove_favorite_select")
            if st.button("Remove", key="remove_favorite_button"):
                _remove_favorite(to_remove)
                st.rerun()


def _render_search() -> None:
    """Look up any symbol and show its live price with an add-to-favorites button."""
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input(
            "Search a symbol",
            placeholder="e.g. DOGEUSDT, BNBUSDT",
            label_visibility="collapsed",
        ).strip().upper()
    with col2:
        search_clicked = st.button("🔍 Search", use_container_width=True)

    if not (search_clicked and query):
        return

    payload = fetch_json(f"/price/{query}")
    if payload is None:
        st.warning(f"No price found for **{query}**. Check the symbol and try again.")
        return

    price = payload["price"]
    change = get_24h_change(query)
    change_str = f"{change:+.2f}%" if change is not None else "—"

    card_cols = st.columns([2, 2, 2, 2])
    with card_cols[0]:
        st.metric(query, f"${price:,.2f}")
    with card_cols[1]:
        st.metric("24h Change", change_str)
    with card_cols[2]:
        if st.button("Set as active chart", key=f"activate_{query}"):
            st.session_state.symbol = query
            st.rerun()
    with card_cols[3]:
        already_favorited = query in st.session_state.favorite_symbols
        if already_favorited:
            st.button("⭐ In favorites", key=f"fav_{query}", disabled=True)
        elif st.button("☆ Add to favorites", key=f"fav_{query}"):
            _add_favorite(query)
            st.rerun()


def _add_favorite(symbol: str) -> None:
    """Add a favorite, persisting to the backend when the route exists."""
    if st.session_state.favorites_persisted:
        updated = add_favorite(symbol)
        if updated is not None:
            st.session_state.favorite_symbols = updated
            return
    if symbol not in st.session_state.favorite_symbols:
        st.session_state.favorite_symbols.append(symbol)


def _remove_favorite(symbol: str) -> None:
    """Remove a favorite, persisting to the backend when the route exists."""
    if st.session_state.favorites_persisted:
        updated = remove_favorite(symbol)
        if updated is not None:
            st.session_state.favorite_symbols = updated
            return
    if symbol in st.session_state.favorite_symbols:
        st.session_state.favorite_symbols.remove(symbol)
