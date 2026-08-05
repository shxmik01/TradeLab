"""Analytics page: performance stats derived from trade history.

Everything here is computed frontend-side from `wallet["trade_history"]`
(the same field `components/trade_table.py` already renders on the
Trades page) — no new backend endpoints needed. Closed trades are
identified by `type == "SELL"`, matching `TradeService.get_closed_trades()`.

The `/wallet` payload does not serialize trade timestamps, so the
time-based sections (Equity Curve, Monthly Returns) enrich the frame
read-only from the existing `wallet.db` via `TradeService.get_all_trades()`
— the exact same query that builds the payload. If that enrichment is
unavailable or lengths differ, those sections degrade to trade-sequence
indices / an info note without failing the page.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.services.trade_service import TradeService


def _get(trade: dict, *keys, default=None):
    """Defensively read a field that may be named slightly differently
    depending on how the backend serializes the Trade model."""
    for key in keys:
        if key in trade and trade[key] is not None:
            return trade[key]
    return default


def _closed_trades_frame(trade_history: list[dict]) -> pd.DataFrame:
    """Build a DataFrame of closed (SELL) trades with normalized columns."""
    rows = []
    for trade in trade_history:
        trade_type = str(_get(trade, "trade_type", "type", default="")).upper()
        if trade_type != "SELL":
            continue

        rows.append(
            {
                "symbol": _get(trade, "symbol"),
                "profit": float(_get(trade, "profit", "pnl", default=0) or 0),
            }
        )

    return pd.DataFrame(rows)


def _enrich_timestamps(df: pd.DataFrame, trade_history: list[dict]) -> pd.DataFrame:
    """Best-effort attach of persisted trade timestamps (read-only).

    The `/wallet` payload omits `timestamp`, but the existing `Trade` rows
    store it. We reuse `TradeService.get_all_trades()` — the exact query that
    builds the payload — so row order and count match the serialized list.
    If the DB read fails or lengths disagree, the frame is returned without
    timestamps and time-based sections fall back gracefully.
    """
    if df.empty:
        return df

    service = None
    try:
        service = TradeService()
        orm_trades = service.get_all_trades()

        if len(orm_trades) != len(trade_history):
            return df

        timestamps = []
        for trade, orm in zip(trade_history, orm_trades):
            trade_type = str(_get(trade, "trade_type", "type", default="")).upper()
            if trade_type == "SELL":
                timestamps.append(getattr(orm, "timestamp", None))

        if len(timestamps) != len(df):
            return df

        df = df.copy()
        df["timestamp"] = pd.to_datetime(timestamps, errors="coerce")
        return df
    except Exception:
        return df
    finally:
        if service is not None:
            service.db.close()


def render_analytics(wallet: dict) -> None:
    """Render the Analytics page."""
    st.title("📈 Analytics")

    trade_history = wallet.get("trade_history", [])
    df = _closed_trades_frame(trade_history)

    if df.empty:
        st.info("No closed trades yet — analytics will populate once you close some positions.")
        return

    df = _enrich_timestamps(df, trade_history)
    has_time = "timestamp" in df.columns and bool(df["timestamp"].notna().any())
    if has_time:
        df = df.sort_values("timestamp", na_position="last").reset_index(drop=True)

    _render_summary_cards(wallet, df)
    st.divider()
    _render_equity_curve(wallet, df)
    st.divider()
    _render_monthly_returns(df, has_time)
    st.divider()
    _render_top_symbols(df)


def _render_summary_cards(wallet: dict, df: pd.DataFrame) -> None:
    """Render the headline performance metrics (streamlit native components)."""
    wins = df[df["profit"] > 0]
    losses = df[df["profit"] < 0]
    total_trades = len(df)

    total_return = df["profit"].sum()
    initial_balance = float(wallet.get("initial_balance", 0) or 0)
    total_return_pct = (total_return / initial_balance * 100) if initial_balance else 0.0

    win_rate = len(wins) / total_trades * 100 if total_trades else 0.0

    gross_profit = wins["profit"].sum()
    gross_loss = abs(losses["profit"].sum())
    if gross_loss > 0:
        profit_factor = gross_profit / gross_loss
    elif gross_profit > 0:
        profit_factor = float("inf")
    else:
        profit_factor = 0.0

    best_trade = df["profit"].max()
    worst_trade = df["profit"].min()

    avg_win = wins["profit"].mean() if not wins.empty else 0.0
    avg_loss = losses["profit"].mean() if not losses.empty else 0.0

    max_drawdown = _max_drawdown(df["profit"].cumsum())

    row1 = st.columns(5)
    row1[0].metric("Total Return", f"${total_return:+,.2f}", delta=f"{total_return_pct:+.1f}%")
    row1[1].metric("Win Rate", f"{win_rate:.1f}%")
    row1[2].metric("Profit Factor", "∞" if profit_factor == float("inf") else f"{profit_factor:.2f}")
    row1[3].metric("Best Trade", f"${best_trade:+,.2f}")
    row1[4].metric("Worst Trade", f"${worst_trade:+,.2f}")

    row2 = st.columns(5)
    row2[0].metric("Average Win", f"${avg_win:+,.2f}")
    row2[1].metric("Average Loss", f"${avg_loss:+,.2f}")
    row2[2].metric("Max Drawdown", f"${max_drawdown:,.2f}")
    row2[3].metric("Total Trades", f"{total_trades:,}")
    row2[4].metric("Top Symbol", _top_symbol(df))


def _top_symbol(df: pd.DataFrame) -> str:
    """Return the symbol with the highest net realized P/L."""
    grouped = df.assign(symbol=df["symbol"].fillna("UNKNOWN")).groupby("symbol")["profit"].sum()
    return grouped.idxmax() if not grouped.empty else "—"


def _max_drawdown(equity: pd.Series) -> float:
    """Largest peak-to-trough drop in cumulative P/L."""
    running_max = equity.cummax()
    drawdown = equity - running_max
    return abs(drawdown.min()) if not drawdown.empty else 0.0


def _render_equity_curve(wallet: dict, df: pd.DataFrame) -> None:
    """Equity curve: initial balance + cumulative realized P/L."""
    st.subheader("Equity Curve")

    initial_balance = float(wallet.get("initial_balance", 0) or 0)
    equity = initial_balance + df["profit"].cumsum()

    if "timestamp" in df.columns and df["timestamp"].notna().any():
        chart_df = pd.DataFrame({"timestamp": df["timestamp"], "Equity": equity})
        st.line_chart(chart_df, x="timestamp", y="Equity", height=380)
    else:
        st.line_chart(pd.DataFrame({"Equity": equity}), height=380)
        st.caption("Timestamps weren't available, so the X-axis uses trade sequence.")


def _render_monthly_returns(df: pd.DataFrame, has_time: bool) -> None:
    """Bar chart of net realized P/L per calendar month."""
    st.subheader("Monthly Returns")

    if not has_time:
        st.info("Monthly returns need trade timestamps, which aren't available in this data.")
        return

    monthly = (
        df.dropna(subset=["timestamp"])
        .set_index("timestamp")["profit"]
        .resample("ME")
        .sum()
    )

    if monthly.empty:
        st.info("No timestamped closed trades to group by month yet.")
        return

    monthly.index = monthly.index.strftime("%b %Y")
    st.bar_chart(pd.DataFrame({"Net P/L": monthly}), height=320)
    st.caption("Net realized P/L per calendar month (sum of closed-trade profits).")


def _render_top_symbols(df: pd.DataFrame) -> None:
    """Bar chart + table of per-symbol performance."""
    st.subheader("Top Performing Symbols")

    by_symbol = (
        df.assign(symbol=df["symbol"].fillna("UNKNOWN"))
        .groupby("symbol")
        .agg(
            net_pnl=("profit", "sum"),
            trades=("profit", "count"),
            avg_pnl=("profit", "mean"),
        )
        .sort_values("net_pnl", ascending=False)
        .reset_index()
    )

    st.bar_chart(by_symbol.set_index("symbol")["net_pnl"], height=320)

    st.dataframe(
        by_symbol.style.format(
            {"net_pnl": "${:+,.2f}", "avg_pnl": "${:+,.2f}"}
        ),
        hide_index=True,
        width="stretch",
    )