from __future__ import annotations

import numpy as np
import pandas as pd


def create_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe.copy()

    features = dataframe.copy().sort_values(["ticker", "date"]).reset_index(drop=True)

    grouped_close = features.groupby("ticker")["close"]
    features["return"] = grouped_close.pct_change()
    features["log_return"] = np.log(features["close"] / grouped_close.shift(1))
    features["MA20"] = grouped_close.transform(lambda series: series.rolling(window=20, min_periods=1).mean())
    features["MA50"] = grouped_close.transform(lambda series: series.rolling(window=50, min_periods=1).mean())
    features["MA200"] = grouped_close.transform(lambda series: series.rolling(window=200, min_periods=1).mean())
    features["volatility"] = features.groupby("ticker")["return"].transform(
        lambda series: series.rolling(window=30, min_periods=5).std()
    )

    return features
