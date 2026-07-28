import pandas as pd


def rsi(df: pd.DataFrame, period: int = 14):
    """
    Adds an RSI column to the DataFrame.
    """

    df = df.copy()

    delta = df["close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss

    df[f"RSI_{period}"] = 100 - (100 / (1 + rs))

    return df