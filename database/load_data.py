from __future__ import annotations

import pandas as pd

from financial_research_pipeline.database.db_connection import get_engine


MARKET_COLUMNS = [
    "date",
    "ticker",
    "open",
    "high",
    "low",
    "close",
    "adjusted_close",
    "volume",
    "return",
    "log_return",
    "MA20",
    "MA50",
    "MA200",
    "volatility",
]


def load_market_data(dataframe: pd.DataFrame, table_name: str = "market_prices") -> None:
    if dataframe.empty:
        return

    to_store = dataframe.copy()
    for column in MARKET_COLUMNS:
        if column not in to_store.columns:
            to_store[column] = None

    to_store = to_store[MARKET_COLUMNS]
    engine = get_engine()
    to_store.to_sql(table_name, con=engine, if_exists="replace", index=False)
