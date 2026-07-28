import pandas as pd


def atr(df: pd.DataFrame, period: int = 14):
    """
    Adds an Average True Range (ATR) column to the DataFrame.
    """

    df = df.copy()

    prev_close = df["close"].shift(1)
    high_low = df["high"] - df["low"]
    high_prev_close = (df["high"] - prev_close).abs()
    low_prev_close = (df["low"] - prev_close).abs()

    true_range = pd.concat([high_low, high_prev_close, low_prev_close], axis=1).max(axis=1)

    df[f"ATR_{period}"] = true_range.ewm(alpha=1 / period, adjust=False).mean()

    return df
