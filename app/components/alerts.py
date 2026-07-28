"""Price / RSI / MACD / EMA-crossover alerts.

Streamlit has no background scheduler, so alerts aren't "pushed" —
they're evaluated live every time the Dashboard page loads/reruns,
and any that are currently true render as a banner. Rules themselves
persist via the backend (with the same session-only fallback pattern
used for favorites) so they survive a page refresh.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.components.common import (
    add_alert,
    fetch_json,
    get_alerts,
    get_chart_data,
    remove_alert,
)
from app.indicators.moving_average import ema
from app.indicators.macd import macd
from app.indicators.rsi import rsi

INDICATOR_LABELS = {
    "price": "Price",
    "rsi": "RSI (14)",
    "macd_cross": "MACD Crossover",
    "ema_cross": "EMA Crossover (20/50)",
}
THRESHOLD_COMPARISONS = ["above", "below"]
CROSS_COMPARISONS = ["bullish", "bearish"]


def _init_alerts() -> None:
    if "alert_rules" in st.session_state:
        return

    persisted = get_alerts()
    st.session_state.alerts_persisted = persisted is not None
    st.session_state.alert_rules = persisted if persisted is not None else []


def render_alert_manager() -> None:
    """Render the alert creation form + existing-alerts list (used on Settings)."""
    _init_alerts()

    st.markdown("### 🔔 Alerts")
    if not st.session_state.alerts_persisted:
        st.caption("⚠️ Alerts aren't saved to your account yet — add the `/alerts` routes to persist them across sessions.")

    with st.form("new_alert_form", clear_on_submit=True):
        cols = st.columns(4)
        with cols[0]:
            symbol = st.text_input("Symbol", value="BTCUSDT").strip().upper()
        with cols[1]:
            indicator = st.selectbox("Type", list(INDICATOR_LABELS), format_func=lambda k: INDICATOR_LABELS[k])
        with cols[2]:
            is_cross = indicator in ("macd_cross", "ema_cross")
            comparison = st.selectbox("Condition", CROSS_COMPARISONS if is_cross else THRESHOLD_COMPARISONS)
        with cols[3]:
            threshold = st.number_input("Threshold", value=0.0, disabled=is_cross, help="Ignored for crossover alerts")

        if st.form_submit_button("➕ Add Alert") and symbol:
            _add_alert(symbol, indicator, comparison, threshold)
            st.rerun()

    if not st.session_state.alert_rules:
        st.info("No alerts set up yet.")
        return

    for idx, alert in enumerate(st.session_state.alert_rules):
        row = st.columns([2, 2, 2, 2, 1])
        row[0].write(f"**{alert['symbol']}**")
        row[1].write(INDICATOR_LABELS.get(alert["indicator"], alert["indicator"]))
        row[2].write(alert["comparison"])
        row[3].write("—" if alert["indicator"] in ("macd_cross", "ema_cross") else alert["threshold"])
        if row[4].button("🗑️", key=f"del_alert_{idx}_{alert.get('id')}"):
            _remove_alert(alert)
            st.rerun()


def _add_alert(symbol: str, indicator: str, comparison: str, threshold: float) -> None:
    if st.session_state.alerts_persisted:
        updated = add_alert(symbol, indicator, comparison, threshold)
        if updated is not None:
            st.session_state.alert_rules = updated
            return
    st.session_state.alert_rules.append(
        {"id": None, "symbol": symbol, "indicator": indicator, "comparison": comparison, "threshold": threshold}
    )


def _remove_alert(alert: dict) -> None:
    if st.session_state.alerts_persisted and alert.get("id") is not None:
        updated = remove_alert(alert["id"])
        if updated is not None:
            st.session_state.alert_rules = updated
            return
    st.session_state.alert_rules = [a for a in st.session_state.alert_rules if a is not alert]


def _load_kline_df(symbol: str, interval: str = "1h") -> pd.DataFrame | None:
    """Fetch + numeric-cast kline data for indicator alerts. None on failure."""
    data = get_chart_data(symbol, interval)
    if not data:
        return None

    df = pd.DataFrame(data)
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _check_alert(alert: dict) -> str | None:
    """Return a triggered message if the alert's condition currently holds, else None."""
    symbol = alert["symbol"]
    indicator = alert["indicator"]
    comparison = alert["comparison"]
    threshold = alert.get("threshold", 0)

    if indicator == "price":
        payload = fetch_json(f"/price/{symbol}")
        if not payload:
            return None
        price = payload["price"]
        if (comparison == "above" and price > threshold) or (comparison == "below" and price < threshold):
            return f"🔔 **{symbol}** price is {comparison} ${threshold:,.2f} (now ${price:,.2f})"
        return None

    df = _load_kline_df(symbol)
    if df is None or len(df) < 2:
        return None

    if indicator == "rsi":
        df = rsi(df)
        latest = df["RSI_14"].iloc[-1]
        if pd.isna(latest):
            return None
        if (comparison == "above" and latest > threshold) or (comparison == "below" and latest < threshold):
            return f"🔔 **{symbol}** RSI is {comparison} {threshold:.0f} (now {latest:.1f})"
        return None

    if indicator == "macd_cross":
        df = macd(df)
        prev_diff = df["MACD"].iloc[-2] - df["MACD_Signal"].iloc[-2]
        curr_diff = df["MACD"].iloc[-1] - df["MACD_Signal"].iloc[-1]
        if pd.isna(prev_diff) or pd.isna(curr_diff):
            return None
        crossed_bullish = prev_diff <= 0 and curr_diff > 0
        crossed_bearish = prev_diff >= 0 and curr_diff < 0
        if (comparison == "bullish" and crossed_bullish) or (comparison == "bearish" and crossed_bearish):
            return f"🔔 **{symbol}** MACD {comparison} crossover just happened"
        return None

    if indicator == "ema_cross":
        df = ema(df, period=20)
        df = ema(df, period=50)
        prev_diff = df["EMA_20"].iloc[-2] - df["EMA_50"].iloc[-2]
        curr_diff = df["EMA_20"].iloc[-1] - df["EMA_50"].iloc[-1]
        if pd.isna(prev_diff) or pd.isna(curr_diff):
            return None
        crossed_bullish = prev_diff <= 0 and curr_diff > 0
        crossed_bearish = prev_diff >= 0 and curr_diff < 0
        if (comparison == "bullish" and crossed_bullish) or (comparison == "bearish" and crossed_bearish):
            return f"🔔 **{symbol}** EMA 20/50 {comparison} crossover just happened"
        return None

    return None


def render_alert_banner() -> None:
    """Evaluate all active alerts and show a banner for any that currently hold.

    Called on the Dashboard so alerts are checked once per page load —
    there's no background process checking them continuously.
    """
    _init_alerts()
    if not st.session_state.alert_rules:
        return

    triggered = [msg for alert in st.session_state.alert_rules if (msg := _check_alert(alert))]
    if not triggered:
        return

    for message in triggered:
        st.warning(message)
