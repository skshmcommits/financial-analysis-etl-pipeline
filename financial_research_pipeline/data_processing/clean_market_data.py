from __future__ import annotations

import pandas as pd


NUMERIC_COLUMNS = ["open", "high", "low", "close", "adjusted_close", "volume"]


def clean_market_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe.copy()

    cleaned = dataframe.copy()
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")

    for column in NUMERIC_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    cleaned = cleaned.dropna(subset=["date", "ticker"]).sort_values(["ticker", "date"])
    cleaned = cleaned.drop_duplicates(subset=["ticker", "date"], keep="last")

    cleaned[NUMERIC_COLUMNS] = cleaned.groupby("ticker")[NUMERIC_COLUMNS].transform(
        lambda series: series.ffill().bfill()
    )

    cleaned = cleaned.dropna(subset=["close"]).reset_index(drop=True)
    return cleaned
