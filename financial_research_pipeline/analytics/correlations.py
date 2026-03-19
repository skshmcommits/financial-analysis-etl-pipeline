from __future__ import annotations

import pandas as pd


def compute_correlation_matrix(price_df: pd.DataFrame) -> pd.DataFrame:
    if price_df.empty:
        return pd.DataFrame()

    pivot_prices = price_df.pivot_table(index="date", columns="ticker", values="close")
    return pivot_prices.corr()
