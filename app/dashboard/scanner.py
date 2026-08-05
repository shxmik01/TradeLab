"""Market Scanner page.

Screens the shared watchlist symbols using the existing strategy and
Binance service, then renders a color-coded results table. Selecting a
symbol updates the active dashboard symbol.
"""

from __future__ import annotations

import streamlit as st

from app.components.common import WATCHLIST_SYMBOLS
from app.components.scanner_table import render_scanner_table
from app.services.scanner_service import scan_symbols


def render_scanner() -> None:
    """Render the Market Scanner page."""
    st.title("🔍 Market Scanner")
    st.caption(
        "Screens the shared watchlist using the same strategy the trading bot runs — "
        "signals always match the bot."
    )

    results = scan_symbols(list(WATCHLIST_SYMBOLS))

    if not results:
        st.warning("No scanner results available. Check the Binance connection and try again.")
        return

    render_scanner_table(results)