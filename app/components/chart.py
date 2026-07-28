"""Plotly chart renderer for the main trading chart."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from app.components.common import API_ERROR_MESSAGE, get_chart_data
from app.components.indicators import (
    add_oscillator_traces,
    add_overlay_traces,
    apply_oscillators,
    apply_overlays,
    render_indicator_selector,
)


def render_chart(symbol: str, interval: str) -> None:
    """Render the main candlestick chart with moving averages and volume."""
    data = get_chart_data(symbol, interval)
    if not data:
        st.warning(API_ERROR_MESSAGE)
        return

    df = pd.DataFrame(data)
    df["open"] = pd.to_numeric(df["open"], errors="coerce")
    df["high"] = pd.to_numeric(df["high"], errors="coerce")
    df["low"] = pd.to_numeric(df["low"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

    df["SMA20"] = df["close"].rolling(20).mean()
    df["EMA50"] = df["close"].ewm(span=50).mean()

    overlays, oscillators = render_indicator_selector()
    df = apply_overlays(df, overlays)
    df = apply_oscillators(df, oscillators)

    oscillator_rows = len(oscillators)
    total_rows = 2 + oscillator_rows
    price_height = 0.55 if oscillator_rows else 0.75
    volume_height = 0.15 if oscillator_rows else 0.25
    oscillator_height = (1.0 - price_height - volume_height) / oscillator_rows if oscillator_rows else 0
    row_heights = [price_height, volume_height] + [oscillator_height] * oscillator_rows

    fig = make_subplots(rows=total_rows, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=row_heights)

    fig.add_trace(
        go.Candlestick(
            x=df["open_time"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Price",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(go.Scatter(x=df["open_time"], y=df["SMA20"], name="SMA 20", line=dict(color="gold", width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["open_time"], y=df["EMA50"], name="EMA 50", line=dict(color="deepskyblue", width=2)), row=1, col=1)
    add_overlay_traces(fig, df, overlays, row=1)
    fig.add_trace(go.Bar(x=df["open_time"], y=df["volume"], name="Volume"), row=2, col=1)

    for i, name in enumerate(oscillators):
        add_oscillator_traces(fig, df, name, row=3 + i)

    last_price = df["close"].iloc[-1]
    fig.add_hline(y=last_price, line_dash="dot", line_color="red", annotation_text=f"${last_price:.2f}", annotation_position="right", row=1, col=1)

    fig.update_layout(
        template="plotly_dark",
        height=650 + (120 * oscillator_rows),
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="white", size=13),
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis_rangeslider_visible=False,
        yaxis=dict(side="right", showgrid=True, gridcolor="#20242D"),
        legend=dict(orientation="h", y=1.02, x=0),
    )
    for r in range(1, total_rows + 1):
        fig.update_xaxes(showgrid=True, gridcolor="#20242D", row=r, col=1)
        fig.update_yaxes(side="right", showgrid=True, gridcolor="#20242D", row=r, col=1)

    st.plotly_chart(fig, use_container_width=True)
