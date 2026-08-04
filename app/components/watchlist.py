"""Watchlist component for symbol selection.

Renders into whatever Streamlit container it's given (defaults to the
main panel) so it can be reused on the Dashboard, the Markets page, or
(if ever needed again) the sidebar — instead of being hard-wired to
`st.sidebar` as before.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from app.components.common import WATCHLIST_SYMBOLS, get_24h_change

_LOGO_FILES = {
    "BTCUSDT": "btc.png",
    "ETHUSDT": "eth.png",
    "SOLUSDT": "sol.png",
    "XRPUSDT": "xrp.png",
}


def render_watchlist(prices: dict, container=st, symbols: list[str] | None = None, heading: str = "⭐ Watchlist") -> None:
    """Display a compact watchlist with logo, symbol, price, and 24h change.

    `container` defaults to the main panel (`st`); pass `st.sidebar` to
    render there instead. `symbols` defaults to the shared
    `WATCHLIST_SYMBOLS` list but can be any symbol list (e.g. a user's
    favorites on the Markets page).
    """
    assets_dir = Path(__file__).resolve().parents[1] / "dashboard" / "assets"
    active_symbol = st.session_state.get("symbol")
    symbols = symbols if symbols is not None else WATCHLIST_SYMBOLS

    if heading:
        container.markdown(f"##### {heading}")

    for symbol in symbols:
        _render_watchlist_row(symbol, assets_dir, prices, active_symbol, container)


def _render_watchlist_row(symbol: str, assets_dir: Path, prices: dict, active_symbol: str | None, container) -> None:
    """Render a single watchlist row (logo, price, 24h change, select button)."""
    logo = assets_dir / _LOGO_FILES.get(symbol, "")
    change = get_24h_change(symbol)
    is_active = symbol == active_symbol

    row_class = "watchlist-row watchlist-row-active" if is_active else "watchlist-row"
    container.markdown(f"<div class='{row_class}'>", unsafe_allow_html=True)

    cols = container.columns([1, 3, 2, 2, 1])

    with cols[0]:
        if logo.exists():
            st.image(str(logo), width=24)
        else:
            st.write("🪙")

    with cols[1]:
        label = f"**{symbol}**" + (" 🔵" if is_active else "")
        st.write(label)

    with cols[2]:
        st.write(f"${prices.get(symbol, 0):,.2f}")

    with cols[3]:
        st.markdown(_format_change(change), unsafe_allow_html=True)

    with cols[4]:
        if st.button("▶", key=f"watch_{symbol}", width="content"):
            st.session_state.symbol = symbol

    container.markdown("</div>", unsafe_allow_html=True)
    container.markdown("---")


def _format_change(change: float | None) -> str:
    """Format a 24h change value as colored HTML, or a dash if unavailable."""
    if change is None:
        return "<span style='color:#8b93a7;'>—</span>"

    css_class = "price-up" if change >= 0 else "price-down"
    return f"<span class='{css_class}'>{change:+.2f}%</span>"
