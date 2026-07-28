import numpy as np
import pandas as pd

from app.indicators.atr import atr


def supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0):
    """
    Adds SuperTrend and SuperTrend_Direction columns to the DataFrame.
    Direction is 1 for an uptrend (line sits below price) and -1 for a
    downtrend (line sits above price).
    """

    df = atr(df, period=period)
    atr_col = f"ATR_{period}"

    hl2 = (df["high"] + df["low"]) / 2
    upper_band = hl2 + (multiplier * df[atr_col])
    lower_band = hl2 - (multiplier * df[atr_col])

    final_upper = upper_band.copy()
    final_lower = lower_band.copy()
    trend = np.ones(len(df))

    for i in range(1, len(df)):
        if df["close"].iloc[i - 1] > final_upper.iloc[i - 1]:
            trend[i] = 1
        elif df["close"].iloc[i - 1] < final_lower.iloc[i - 1]:
            trend[i] = -1
        else:
            trend[i] = trend[i - 1]

            if trend[i] == 1 and lower_band.iloc[i] < final_lower.iloc[i - 1]:
                final_lower.iloc[i] = final_lower.iloc[i - 1]
            if trend[i] == -1 and upper_band.iloc[i] > final_upper.iloc[i - 1]:
                final_upper.iloc[i] = final_upper.iloc[i - 1]

    df["SuperTrend"] = np.where(trend == 1, final_lower, final_upper)
    df["SuperTrend_Direction"] = trend

    return df
