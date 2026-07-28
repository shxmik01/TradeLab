import pandas as pd


def sma(df: pd.DataFrame, period: int = 20):
    """
    Adds a Simple Moving Average (SMA) column to the DataFrame.
    """

    df = df.copy()
    df[f"SMA_{period}"] = df["close"].rolling(window=period).mean()

    return df


def ema(df: pd.DataFrame, period: int = 20):
    """
    Adds an Exponential Moving Average (EMA) column to the DataFrame.
    """

    df = df.copy()
    df[f"EMA_{period}"] = df["close"].ewm(span=period, adjust=False).mean()

    return df