"""Trade history table renderer."""

import pandas as pd
import streamlit as st


def _pick_column(columns: list, *candidates: str) -> str | None:
    """Return the first candidate column name that exists in the DataFrame."""
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def _color_side(value) -> str:
    """Green for BUY, red for SELL."""
    if isinstance(value, str):
        upper = value.upper()
        if upper == "BUY":
            return "color: #00c853; font-weight: 600;"
        if upper == "SELL":
            return "color: #ff1744; font-weight: 600;"
    return ""


def _color_pnl(value) -> str:
    """Green for profit, red for loss."""
    try:
        num = float(value)
    except (TypeError, ValueError):
        return ""
    if num > 0:
        return "color: #00c853; font-weight: 600;"
    if num < 0:
        return "color: #ff1744; font-weight: 600;"
    return ""


def render_trade_history(wallet: dict) -> None:
    """Render trade history in a clean, formatted table view."""
    st.title("📜 Trade History")
    trades = wallet.get("trade_history", [])

    if not trades:
        st.info("No trades yet.")
        return

    df = pd.DataFrame(trades)

    # --- Summary strip (native metrics) ---
    total_trades = len(df)

    pnl_col = _pick_column(df.columns, "pnl", "profit", "p&l", "net_pnl", "realized_pnl")
    win_rate = None
    net_pnl = None

    if pnl_col is not None:
        pnl_series = pd.to_numeric(df[pnl_col], errors="coerce")
        if pnl_series.notna().any():
            wins = (pnl_series > 0).sum()
            win_rate = wins / pnl_series.notna().sum() if pnl_series.notna().sum() else 0.0
            net_pnl = pnl_series.sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Trades", f"{total_trades:,}")
    col2.metric("Win Rate", f"{win_rate * 100:.1f}%" if win_rate is not None else "—")
    col3.metric("Net P/L", f"{net_pnl:+,.2f}" if net_pnl is not None else "—")

    st.divider()

    # --- Identify relevant columns ---
    time_col = _pick_column(df.columns, "timestamp", "time", "date", "datetime", "created_at")
    side_col = _pick_column(df.columns, "side", "type", "action", "direction")
    price_col = _pick_column(df.columns, "price", "entry_price", "exit_price", "avg_price")
    qty_col = _pick_column(df.columns, "quantity", "qty", "amount", "size", "volume")

    # --- Build a pandas Styler for conditional coloring + formatting ---
    styler = df.style

    # Color BUY (green) / SELL (red)
    if side_col is not None:
        styler = styler.map(_color_side, subset=[side_col])

    # Color PnL: profit (green) / loss (red)
    if pnl_col is not None:
        styler = styler.map(_color_pnl, subset=[pnl_col])

    # Number / date formatting
    format_dict = {}
    if time_col is not None:
        format_dict[time_col] = lambda v: pd.Timestamp(v).strftime("%Y-%m-%d %H:%M:%S")
    if price_col is not None:
        format_dict[price_col] = "{:.6f}"
    if qty_col is not None:
        format_dict[qty_col] = "{:.6f}"
    if pnl_col is not None:
        format_dict[pnl_col] = "{:+.2f}"

    if format_dict:
        styler = styler.format(format_dict, na_rep="—")

    # --- Render table with fixed height + vertical scrolling ---
    st.dataframe(
        styler,
        hide_index=True,
        width="stretch",
        height=450,
    )