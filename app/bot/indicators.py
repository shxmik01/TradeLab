import pandas as pd


def calculate_ema(df: pd.DataFrame, period: int):
    """
    Calculate Exponential Moving Average (EMA).
    """
    return df["close"].ewm(span=period, adjust=False).mean()


def calculate_rsi(df: pd.DataFrame, period: int = 14):
    """
    Calculate Relative Strength Index (RSI).
    """

    delta = df["close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def add_indicators(df: pd.DataFrame):
    """
    Add all indicators required by the strategy.
    """

    df = df.copy()

    df["EMA50"] = calculate_ema(df, 50)
    df["EMA200"] = calculate_ema(df, 200)
    df["RSI"] = calculate_rsi(df)

    return df