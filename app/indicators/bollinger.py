import pandas as pd


def bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0):
    """
    Adds Bollinger Band columns (middle/upper/lower) to the DataFrame.
    """

    df = df.copy()

    middle = df["close"].rolling(window=period).mean()
    std = df["close"].rolling(window=period).std()

    df[f"BB_Middle_{period}"] = middle
    df[f"BB_Upper_{period}"] = middle + (std * std_dev)
    df[f"BB_Lower_{period}"] = middle - (std * std_dev)

    return df
