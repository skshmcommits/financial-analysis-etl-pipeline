from __future__ import annotations

import numpy as np
import pandas as pd


def validate_market_data(dataframe: pd.DataFrame) -> dict:
    if dataframe.empty:
        return {
            "rows": 0,
            "missing_values": 0,
            "duplicates": 0,
            "negative_prices": 0,
            "extreme_outliers": 0,
        }

    working = dataframe.copy()
    missing_values = int(working.isna().sum().sum())
    duplicates = int(working.duplicated(subset=["ticker", "date"]).sum())

    price_cols = ["open", "high", "low", "close", "adjusted_close"]
    negative_prices = int((working[price_cols] < 0).sum().sum())

    working["daily_return"] = working.groupby("ticker")["close"].pct_change()
    std_dev = working["daily_return"].std(skipna=True)
    if std_dev and not np.isnan(std_dev) and std_dev > 0:
        z_scores = (working["daily_return"] - working["daily_return"].mean(skipna=True)) / std_dev
        extreme_outliers = int((z_scores.abs() > 5).sum())
    else:
        extreme_outliers = 0

    return {
        "rows": int(len(working)),
        "missing_values": missing_values,
        "duplicates": duplicates,
        "negative_prices": negative_prices,
        "extreme_outliers": extreme_outliers,
    }
