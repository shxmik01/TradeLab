import pandas as pd


def macd(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
):
    """
    Adds MACD, Signal Line, and Histogram columns to the DataFrame.
    """

    df = df.copy()

    ema_fast = df["close"].ewm(span=fast_period, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow_period, adjust=False).mean()

    df["MACD"] = ema_fast - ema_slow
    df["MACD_Signal"] = (
        df["MACD"]
        .ewm(span=signal_period, adjust=False)
        .mean()
    )

    df["MACD_Histogram"] = (
        df["MACD"] - df["MACD_Signal"]
    )

    return df
