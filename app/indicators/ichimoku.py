import pandas as pd


def ichimoku(
    df: pd.DataFrame,
    conversion_period: int = 9,
    base_period: int = 26,
    leading_span_b_period: int = 52,
    displacement: int = 26,
):
    """
    Adds Ichimoku Cloud columns to the DataFrame: Tenkan-sen (conversion),
    Kijun-sen (base), Senkou Span A/B (leading cloud edges, shifted
    forward by `displacement`), and Chikou Span (lagging, shifted back).
    """

    df = df.copy()

    def _midpoint(period: int) -> pd.Series:
        return (df["high"].rolling(period).max() + df["low"].rolling(period).min()) / 2

    df["Ichimoku_Tenkan"] = _midpoint(conversion_period)
    df["Ichimoku_Kijun"] = _midpoint(base_period)

    df["Ichimoku_SenkouA"] = ((df["Ichimoku_Tenkan"] + df["Ichimoku_Kijun"]) / 2).shift(displacement)
    df["Ichimoku_SenkouB"] = _midpoint(leading_span_b_period).shift(displacement)

    df["Ichimoku_Chikou"] = df["close"].shift(-displacement)

    return df
