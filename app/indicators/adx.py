import pandas as pd

from app.indicators.atr import atr


def adx(df: pd.DataFrame, period: int = 14):
    """
    Adds ADX, +DI, and -DI columns to the DataFrame.
    """

    df = atr(df, period=period)

    up_move = df["high"].diff()
    down_move = -df["low"].diff()

    plus_dm = ((up_move > down_move) & (up_move > 0)) * up_move
    minus_dm = ((down_move > up_move) & (down_move > 0)) * down_move

    atr_col = f"ATR_{period}"
    smoothed_atr = df[atr_col].replace(0, pd.NA)

    plus_di = 100 * (plus_dm.ewm(alpha=1 / period, adjust=False).mean() / smoothed_atr)
    minus_di = 100 * (minus_dm.ewm(alpha=1 / period, adjust=False).mean() / smoothed_atr)

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)

    df["Plus_DI"] = plus_di
    df["Minus_DI"] = minus_di
    df[f"ADX_{period}"] = dx.ewm(alpha=1 / period, adjust=False).mean()

    return df
