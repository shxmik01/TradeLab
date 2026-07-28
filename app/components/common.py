from __future__ import annotations

import requests
import streamlit as st

API = "http://127.0.0.1:8000"

API_ERROR_MESSAGE = "Unable to connect to backend"

# Shared across common.py, metrics.py, watchlist.py, and app_refactored.py
# so the watchlist symbol list only has to be edited in one place.
WATCHLIST_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]


def initialize_session_state() -> None:
    """Initialize dashboard session defaults once per user session."""
    if "symbol" not in st.session_state:
        st.session_state.symbol = "BTCUSDT"

    if "interval" not in st.session_state:
        st.session_state.interval = "1h"


@st.cache_data(ttl=10)
def fetch_json(path: str, params: dict | None = None):
    """Fetch JSON from the FastAPI backend with a small timeout."""
    try:
        response = requests.get(f"{API}{path}", params=params, timeout=8)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


@st.cache_data(ttl=10)
def get_dashboard_payload() -> dict | None:
    """Load wallet summary and market prices for the dashboard."""
    wallet = fetch_json("/wallet")
    prices = {}

    for symbol in WATCHLIST_SYMBOLS:
        payload = fetch_json(f"/price/{symbol}")
        if payload:
            prices[symbol] = payload["price"]

    if wallet is None:
        return None

    return {"wallet": wallet, "prices": prices}


@st.cache_data(ttl=15)
def get_chart_data(symbol: str, interval: str):
    """Load candle data for a chosen symbol and timeframe."""
    return fetch_json(f"/klines/{symbol}", params={"interval": interval})


@st.cache_data(ttl=60)
def get_24h_change(symbol: str) -> float | None:
    """Compute a 24h percent change from existing daily kline data.

    There is no dedicated backend endpoint for this, so rather than
    displaying placeholder numbers, this reuses the existing
    `/klines/{symbol}?interval=1d` data (open vs. close of the most
    recent daily candle). Returns None if data isn't available, which
    callers should render as "—" rather than a fabricated value.
    """
    candles = fetch_json(f"/klines/{symbol}", params={"interval": "1d"})
    if not candles:
        return None

    latest = candles[-1]
    try:
        open_price = float(latest["open"])
        close_price = float(latest["close"])
    except (KeyError, TypeError, ValueError):
        return None

    if open_price == 0:
        return None

    return (close_price - open_price) / open_price * 100


@st.cache_data(ttl=10)
def get_favorites() -> list[str] | None:
    """Load the persisted favorites list, or None if the backend route isn't available yet."""
    return fetch_json("/favorites")


def add_favorite(symbol: str) -> list[str] | None:
    """Persist a new favorite symbol."""
    try:
        response = requests.post(f"{API}/favorites/{symbol}", timeout=8)
        response.raise_for_status()
        get_favorites.clear()
        return response.json()
    except requests.RequestException:
        return None


def remove_favorite(symbol: str) -> list[str] | None:
    """Remove a persisted favorite symbol."""
    try:
        response = requests.delete(f"{API}/favorites/{symbol}", timeout=8)
        response.raise_for_status()
        get_favorites.clear()
        return response.json()
    except requests.RequestException:
        return None


@st.cache_data(ttl=10)
def get_alerts() -> list[dict] | None:
    """Load persisted alerts, or None if the backend route isn't available yet."""
    return fetch_json("/alerts")


def add_alert(symbol: str, indicator: str, comparison: str, threshold: float = 0) -> list[dict] | None:
    """Persist a new alert rule."""
    try:
        response = requests.post(
            f"{API}/alerts",
            json={"symbol": symbol, "indicator": indicator, "comparison": comparison, "threshold": threshold},
            timeout=8,
        )
        response.raise_for_status()
        get_alerts.clear()
        return response.json()
    except requests.RequestException:
        return None


def remove_alert(alert_id: int) -> list[dict] | None:
    """Remove a persisted alert rule."""
    try:
        response = requests.delete(f"{API}/alerts/{alert_id}", timeout=8)
        response.raise_for_status()
        get_alerts.clear()
        return response.json()
    except requests.RequestException:
        return None
