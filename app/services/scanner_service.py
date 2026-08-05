"""Market scanner service.

Screens a list of symbols using the exact same strategy instance the
trading bot uses (`app.core.state.strategy`), so the scanner and the
bot always produce identical BUY / HOLD / SELL signals.

Indicator calculations (RSI, EMA) are reused from the existing
`app.indicators` modules — nothing is duplicated here. The symbol list
is reused from the existing `WATCHLIST_SYMBOLS` constant so it only has
to be maintained in one place.
"""

from __future__ import annotations

import pandas as pd

from app.components.common import WATCHLIST_SYMBOLS
from app.core.state import strategy
from app.exchange.binance_service import get_klines, get_price
from app.indicators.moving_average import ema
from app.indicators.rsi import rsi

# EMA periods used to derive the trend direction.
EMA_FAST = 20
EMA_SLOW = 50

# Score weights — signal carries the most weight to stay aligned with
# the trading bot, then RSI and EMA trend contribute momentum/trend.
SIGNAL_WEIGHT = 0.4
RSI_WEIGHT = 0.3
EMA_WEIGHT = 0.3


def _signal_score(signal: str) -> float:
    """Map the strategy signal to a 0–100 sub-score."""
    return {"BUY": 100.0, "HOLD": 50.0, "SELL": 0.0}.get(signal, 50.0)


def _rsi_score(rsi_value: float | None) -> float:
    """Map RSI to a 0–100 sub-score.

    Lower RSI (oversold) scores higher as a buying opportunity; higher
    RSI (overbought) scores lower.
    """
    if rsi_value is None or pd.isna(rsi_value):
        return 50.0
    if rsi_value <= 30:
        return 100.0
    if rsi_value >= 70:
        return 0.0
    return (70.0 - rsi_value) / 40.0 * 100.0


def _ema_trend(df: pd.DataFrame) -> tuple[str | None, float | None]:
    """Return (trend_label, ema_score) from a fast/slow EMA comparison."""
    try:
        trend_df = ema(df, EMA_FAST)
        trend_df = ema(trend_df, EMA_SLOW)

        fast = trend_df[f"EMA_{EMA_FAST}"].iloc[-1]
        slow = trend_df[f"EMA_{EMA_SLOW}"].iloc[-1]

        if pd.isna(fast) or pd.isna(slow):
            return None, 50.0
        if fast > slow:
            return "Bullish", 100.0
        if fast < slow:
            return "Bearish", 0.0
        return "Flat", 50.0
    except (KeyError, IndexError, TypeError):
        return None, 50.0


def _recommendation(score: float) -> str:
    """Map a composite score (0–100) to a human-readable recommendation."""
    if score >= 75:
        return "Strong Buy"
    if score >= 60:
        return "Buy"
    if score >= 40:
        return "Hold"
    if score >= 25:
        return "Sell"
    return "Strong Sell"


def _analyze_symbol(symbol: str) -> dict | None:
    """Analyze a single symbol and return a scanner result row."""
    try:
        df = get_klines(symbol, interval="1h", limit=100)
        if df is None or df.empty:
            return None

        # --- Reused indicator calculations (no duplication) ---
        rsi_df = rsi(df, 14)
        last_rsi = rsi_df["RSI_14"].iloc[-1]
        last_rsi = None if pd.isna(last_rsi) else round(float(last_rsi), 2)

        trend_label, ema_score = _ema_trend(df)

        # --- Reuse the trading bot's exact signal ---
        signal = strategy.get_signal(symbol)

        price = get_price(symbol)
        if price is None:
            price = float(df["close"].iloc[-1])

        score = round(
            SIGNAL_WEIGHT * _signal_score(signal)
            + RSI_WEIGHT * _rsi_score(last_rsi)
            + EMA_WEIGHT * ema_score,
            1,
        )

        return {
            "symbol": symbol,
            "price": price,
            "signal": signal,
            "rsi": last_rsi,
            "ema_trend": trend_label or "—",
            "score": score,
            "recommendation": _recommendation(score),
        }

    except Exception:
        # A single symbol failure must not break the whole scan.
        return None


def scan_symbols(symbols: list[str] | None = None) -> list[dict]:
    """Scan a list of symbols and return results sorted by score (highest first).

    `symbols` defaults to the shared `WATCHLIST_SYMBOLS` constant.
    Passing a custom list (e.g. a user watchlist) is supported without
    changing the scan logic — ready for future expansion to 20+ coins.
    """
    scan_list = symbols if symbols is not None else list(WATCHLIST_SYMBOLS)
    results = [_analyze_symbol(symbol) for symbol in scan_list]
    results = [row for row in results if row is not None]
    results.sort(key=lambda row: row["score"], reverse=True)
    return results