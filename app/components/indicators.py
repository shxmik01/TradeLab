"""Indicator selector UI + trace builders for the trading chart.

Calculation logic lives in app/indicators/*; this module is only
responsible for (1) letting the user pick which indicators to show,
and (2) turning the resulting DataFrame columns into Plotly traces.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.indicators.adx import adx
from app.indicators.bollinger import bollinger_bands
from app.indicators.fibonacci import fibonacci_levels
from app.indicators.ichimoku import ichimoku
from app.indicators.macd import macd
from app.indicators.rsi import rsi
from app.indicators.stochastic_rsi import stochastic_rsi
from app.indicators.supertrend import supertrend
from app.indicators.vwap import vwap

OVERLAY_OPTIONS = ["Bollinger Bands", "VWAP", "SuperTrend", "Ichimoku Cloud", "Fibonacci"]
OSCILLATOR_OPTIONS = ["RSI", "MACD", "ADX", "Stochastic RSI"]


def render_indicator_selector() -> tuple[list[str], list[str]]:
    """Render the multiselect controls and return (overlays, oscillators)."""
    cols = st.columns(2)
    with cols[0]:
        overlays = st.multiselect("Overlays", OVERLAY_OPTIONS, key="chart_overlays")
    with cols[1]:
        oscillators = st.multiselect("Oscillators", OSCILLATOR_OPTIONS, key="chart_oscillators")
    return overlays, oscillators


def apply_overlays(df: pd.DataFrame, overlays: list[str]) -> pd.DataFrame:
    """Compute the selected overlay indicators, adding columns to df."""
    if "Bollinger Bands" in overlays:
        df = bollinger_bands(df)
    if "VWAP" in overlays:
        df = vwap(df)
    if "SuperTrend" in overlays:
        df = supertrend(df)
    if "Ichimoku Cloud" in overlays:
        df = ichimoku(df)
    return df


def apply_oscillators(df: pd.DataFrame, oscillators: list[str]) -> pd.DataFrame:
    """Compute the selected oscillator indicators, adding columns to df."""
    if "RSI" in oscillators:
        df = rsi(df)
    if "MACD" in oscillators:
        df = macd(df)
    if "ADX" in oscillators:
        df = adx(df)
    if "Stochastic RSI" in oscillators:
        df = stochastic_rsi(df)
    return df


def add_overlay_traces(fig: go.Figure, df: pd.DataFrame, overlays: list[str], row: int) -> None:
    """Add overlay traces (price-row lines + Fibonacci's horizontal levels)."""
    x = df["open_time"]

    if "Bollinger Bands" in overlays:
        fig.add_trace(go.Scatter(x=x, y=df["BB_Upper_20"], name="BB Upper", line=dict(color="rgba(0,200,255,0.5)", width=1)), row=row, col=1)
        fig.add_trace(
            go.Scatter(
                x=x, y=df["BB_Lower_20"], name="BB Lower",
                line=dict(color="rgba(0,200,255,0.5)", width=1),
                fill="tonexty", fillcolor="rgba(0,200,255,0.06)",
            ),
            row=row, col=1,
        )
        fig.add_trace(go.Scatter(x=x, y=df["BB_Middle_20"], name="BB Middle", line=dict(color="rgba(0,200,255,0.8)", width=1, dash="dot")), row=row, col=1)

    if "VWAP" in overlays:
        fig.add_trace(go.Scatter(x=x, y=df["VWAP"], name="VWAP", line=dict(color="#ffb020", width=2)), row=row, col=1)

    if "SuperTrend" in overlays:
        up = df["SuperTrend"].where(df["SuperTrend_Direction"] == 1)
        down = df["SuperTrend"].where(df["SuperTrend_Direction"] == -1)
        fig.add_trace(go.Scatter(x=x, y=up, name="SuperTrend (Up)", line=dict(color="#00ff88", width=2)), row=row, col=1)
        fig.add_trace(go.Scatter(x=x, y=down, name="SuperTrend (Down)", line=dict(color="#ff4b4b", width=2)), row=row, col=1)

    if "Ichimoku Cloud" in overlays:
        fig.add_trace(go.Scatter(x=x, y=df["Ichimoku_SenkouA"], name="Senkou A", line=dict(color="rgba(0,255,136,0.4)", width=1)), row=row, col=1)
        fig.add_trace(
            go.Scatter(
                x=x, y=df["Ichimoku_SenkouB"], name="Senkou B",
                line=dict(color="rgba(255,75,75,0.4)", width=1),
                fill="tonexty", fillcolor="rgba(0,200,255,0.05)",
            ),
            row=row, col=1,
        )
        fig.add_trace(go.Scatter(x=x, y=df["Ichimoku_Tenkan"], name="Tenkan-sen", line=dict(color="#00c8ff", width=1)), row=row, col=1)
        fig.add_trace(go.Scatter(x=x, y=df["Ichimoku_Kijun"], name="Kijun-sen", line=dict(color="#ffb020", width=1)), row=row, col=1)

    if "Fibonacci" in overlays:
        for label, price in fibonacci_levels(df).items():
            fig.add_hline(
                y=price, line_dash="dot", line_color="rgba(255,255,255,0.25)",
                annotation_text=label, annotation_position="left", row=row, col=1,
            )


def add_oscillator_traces(fig: go.Figure, df: pd.DataFrame, name: str, row: int) -> None:
    """Add one oscillator's traces to its own subplot row."""
    x = df["open_time"]

    if name == "RSI":
        fig.add_trace(go.Scatter(x=x, y=df["RSI_14"], name="RSI 14", line=dict(color="#00c8ff", width=1.5)), row=row, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="rgba(255,75,75,0.4)", row=row, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="rgba(0,255,136,0.4)", row=row, col=1)

    elif name == "MACD":
        fig.add_trace(go.Bar(x=x, y=df["MACD_Histogram"], name="MACD Histogram", marker_color="rgba(0,200,255,0.4)"), row=row, col=1)
        fig.add_trace(go.Scatter(x=x, y=df["MACD"], name="MACD", line=dict(color="#00c8ff", width=1.5)), row=row, col=1)
        fig.add_trace(go.Scatter(x=x, y=df["MACD_Signal"], name="Signal", line=dict(color="#ffb020", width=1.5)), row=row, col=1)

    elif name == "ADX":
        fig.add_trace(go.Scatter(x=x, y=df["ADX_14"], name="ADX", line=dict(color="#f2f6ff", width=1.5)), row=row, col=1)
        fig.add_trace(go.Scatter(x=x, y=df["Plus_DI"], name="+DI", line=dict(color="#00ff88", width=1)), row=row, col=1)
        fig.add_trace(go.Scatter(x=x, y=df["Minus_DI"], name="-DI", line=dict(color="#ff4b4b", width=1)), row=row, col=1)

    elif name == "Stochastic RSI":
        fig.add_trace(go.Scatter(x=x, y=df["StochRSI_K"], name="StochRSI %K", line=dict(color="#00c8ff", width=1.5)), row=row, col=1)
        fig.add_trace(go.Scatter(x=x, y=df["StochRSI_D"], name="StochRSI %D", line=dict(color="#ffb020", width=1.5)), row=row, col=1)
        fig.add_hline(y=80, line_dash="dot", line_color="rgba(255,75,75,0.4)", row=row, col=1)
        fig.add_hline(y=20, line_dash="dot", line_color="rgba(0,255,136,0.4)", row=row, col=1)
