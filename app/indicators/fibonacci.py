import pandas as pd

_LEVELS = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]


def fibonacci_levels(df: pd.DataFrame) -> dict:
    """
    Returns Fibonacci retracement price levels for the swing high/low of
    the given DataFrame's window. Unlike the other indicators, this
    isn't a rolling per-row column — it's a fixed set of price levels
    to draw as horizontal lines over the visible chart range.
    """

    swing_high = df["high"].max()
    swing_low = df["low"].min()
    price_range = swing_high - swing_low

    return {f"{int(level * 100)}%": swing_high - (price_range * level) for level in _LEVELS}
