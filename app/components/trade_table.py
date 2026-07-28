"""Trade history table renderer."""

import pandas as pd
import streamlit as st


def render_trade_history(wallet: dict) -> None:
    """Render trade history in a clean table view."""
    st.title("📜 Trade History")
    trades = wallet.get("trade_history", [])

    if trades:
        df = pd.DataFrame(trades)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No trades yet.")
