import pandas as pd

from app.indicators.rsi import rsi


def stochastic_rsi(df: pd.DataFrame, period: int = 14, smooth_k: int = 3, smooth_d: int = 3):
    """
    Adds StochRSI_K and StochRSI_D columns to the DataFrame, built on
    top of the existing rsi() indicator rather than recomputing RSI.
    """

    df = rsi(df, period=period)
    rsi_col = f"RSI_{period}"

    rsi_min = df[rsi_col].rolling(period).min()
    rsi_max = df[rsi_col].rolling(period).max()

    stoch_rsi = (df[rsi_col] - rsi_min) / (rsi_max - rsi_min)

    df["StochRSI_K"] = (stoch_rsi * 100).rolling(smooth_k).mean()
    df["StochRSI_D"] = df["StochRSI_K"].rolling(smooth_d).mean()

    return df
