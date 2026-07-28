import pandas as pd


def vwap(df: pd.DataFrame):
    """
    Adds a Volume Weighted Average Price (VWAP) column to the DataFrame.

    Computed as a cumulative VWAP over the fetched candle window (not
    reset at session/day boundaries), since the backend doesn't expose
    a separate "session start" marker to reset against.
    """

    df = df.copy()

    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    cumulative_pv = (typical_price * df["volume"]).cumsum()
    cumulative_volume = df["volume"].cumsum()

    df["VWAP"] = cumulative_pv / cumulative_volume

    return df
