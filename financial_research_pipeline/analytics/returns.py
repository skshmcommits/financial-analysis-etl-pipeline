from __future__ import annotations

import numpy as np
import pandas as pd


def compute_returns(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return pd.DataFrame(columns=["ticker", "cumulative_return", "annual_return", "daily_return_std"])

    frame = dataframe.copy()
    if "return" not in frame.columns:
        frame["return"] = frame.groupby("ticker")["close"].pct_change()

    summaries = []
    for ticker, ticker_df in frame.groupby("ticker"):
        valid_returns = ticker_df["return"].dropna()
        if valid_returns.empty:
            cumulative_return = np.nan
            annual_return = np.nan
            daily_return_std = np.nan
        else:
            cumulative_return = (1 + valid_returns).prod() - 1
            annual_return = (1 + cumulative_return) ** (252 / max(len(valid_returns), 1)) - 1
            daily_return_std = valid_returns.std()

        summaries.append(
            {
                "ticker": ticker,
                "cumulative_return": cumulative_return,
                "annual_return": annual_return,
                "daily_return_std": daily_return_std,
            }
        )

    return pd.DataFrame(summaries)
