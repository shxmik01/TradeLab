"""Analytics page: performance stats derived from trade history.

Everything here is computed frontend-side from `wallet["trade_history"]`
(the same field `components/trade_table.py` already renders on the
Trades page) — no new backend endpoints needed. Closed trades are
identified by `trade_type == "SELL"`, matching `TradeService.get_closed_trades()`.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


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
                "timestamp": _get(trade, "timestamp", "time", "date"),
            }
        )

    df = pd.DataFrame(rows)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.sort_values("timestamp", na_position="last").reset_index(drop=True)

    return df


def render_analytics(wallet: dict) -> None:
    """Render the Analytics page."""
    st.title("📈 Analytics")

    trade_history = wallet.get("trade_history", [])
    df = _closed_trades_frame(trade_history)

    if df.empty:
        st.info("No closed trades yet — analytics will populate once you close some positions.")
        return

    _render_summary_cards(df)
    st.divider()
    _render_equity_curve(wallet, df)
    st.divider()
    _render_trade_distribution(df)


def _render_summary_cards(df: pd.DataFrame) -> None:
    wins = df[df["profit"] > 0]
    losses = df[df["profit"] < 0]

    win_rate = len(wins) / len(df) * 100 if len(df) else 0.0

    gross_profit = wins["profit"].sum()
    gross_loss = abs(losses["profit"].sum())
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float("inf")

    # Sharpe ratio proxy: per-trade profit as the "return" series (not
    # annualized — the trade data has no notion of holding period /
    # position size normalization to compute a textbook return %).
    returns = df["profit"]
    sharpe = (returns.mean() / returns.std()) if returns.std() not in (0, None) else 0.0

    max_drawdown = _max_drawdown(df["profit"].cumsum())

    cols = st.columns(5)
    with cols[0]:
        st.metric("Win Rate", f"{win_rate:.1f}%")
    with cols[1]:
        st.metric("Profit Factor", "∞" if profit_factor == float("inf") else f"{profit_factor:.2f}")
    with cols[2]:
        st.metric("Sharpe (per-trade)", f"{sharpe:.2f}")
    with cols[3]:
        st.metric("Max Drawdown", f"${max_drawdown:,.2f}")
    with cols[4]:
        st.metric("Closed Trades", len(df))

    st.caption(
        "Sharpe ratio here is a simplified per-trade proxy (mean profit / std of profit), "
        "not an annualized return-based Sharpe ratio — the backend doesn't currently expose "
        "position size or holding period needed for that calculation."
    )


def _max_drawdown(equity: pd.Series) -> float:
    """Largest peak-to-trough drop in cumulative P/L."""
    running_max = equity.cummax()
    drawdown = equity - running_max
    return abs(drawdown.min()) if not drawdown.empty else 0.0


def _render_equity_curve(wallet: dict, df: pd.DataFrame) -> None:
    st.subheader("Equity Curve")

    starting_balance = wallet.get("initial_balance", 0)
    equity = starting_balance + df["profit"].cumsum()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"] if df["timestamp"].notna().any() else list(range(len(df))),
            y=equity,
            mode="lines",
            line=dict(color="#00c8ff", width=2),
            fill="tozeroy",
            fillcolor="rgba(0, 200, 255, 0.08)",
            name="Equity",
        )
    )
    fig.update_layout(
        template="plotly_dark",
        height=380,
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="white", size=13),
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis=dict(side="right", showgrid=True, gridcolor="#20242D", tickprefix="$"),
        xaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig, width="stretch")


def _render_trade_distribution(df: pd.DataFrame) -> None:
    st.subheader("Trade P/L Distribution")

    colors = ["#00ff88" if p >= 0 else "#ff4b4b" for p in df["profit"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(range(1, len(df) + 1)), y=df["profit"], marker_color=colors, name="P/L per trade"))
    fig.update_layout(
        template="plotly_dark",
        height=320,
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="white", size=13),
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis=dict(side="right", showgrid=True, gridcolor="#20242D", tickprefix="$"),
        xaxis=dict(title="Trade #", showgrid=False),
    )
    st.plotly_chart(fig, width="stretch")
