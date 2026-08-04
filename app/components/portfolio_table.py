"""Portfolio table renderer, shared by the Portfolio page and the
compact "Open Positions" section on the Dashboard page.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st


def build_positions_dataframe(wallet: dict, prices: dict) -> pd.DataFrame | None:
    """Build a positions DataFrame with live P/L, or None if there are none."""
    positions = wallet.get("positions")
    if not positions:
        return None

    rows = []
    for symbol, pos in positions.items():
        current = prices.get(symbol, pos["entry_price"])
        value = current * pos["quantity"]
        cost = pos["quantity"] * pos["entry_price"]
        pnl = value - cost

        rows.append(
            {
                "Symbol": symbol,
                "Quantity": round(pos["quantity"], 6),
                "Entry": round(pos["entry_price"], 2),
                "Current": round(current, 2),
                "Value": round(value, 2),
                "P/L": round(pnl, 2),
            }
        )

    return pd.DataFrame(rows)


def render_portfolio(wallet: dict, prices: dict) -> None:
    """Render the full portfolio table on the dedicated Portfolio page."""
    st.title("💼 Portfolio")
    render_positions_table(wallet, prices)


def render_open_positions(wallet: dict, prices: dict) -> None:
    """Render a compact open-positions table for the bottom of the Dashboard."""
    st.subheader("📂 Open Positions")
    render_positions_table(wallet, prices)


def render_positions_table(wallet: dict, prices: dict) -> None:
    """Render the shared positions table, or an empty-state message."""
    df = build_positions_dataframe(wallet, prices)
    if df is not None:
        st.dataframe(df, width="stretch", hide_index=True)
    else:
        st.info("No open positions.")
