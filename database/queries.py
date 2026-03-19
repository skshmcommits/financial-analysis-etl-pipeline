from __future__ import annotations

import pandas as pd
from sqlalchemy import text

from financial_research_pipeline.database.db_connection import get_engine


def get_prices(ticker: str) -> pd.DataFrame:
    engine = get_engine()
    query = text("SELECT * FROM market_prices WHERE ticker = :ticker ORDER BY date")
    return pd.read_sql(query, con=engine, params={"ticker": ticker})


def get_returns(ticker: str) -> pd.DataFrame:
    engine = get_engine()
    query = text(
        "SELECT date, ticker, return, log_return FROM market_prices "
        "WHERE ticker = :ticker ORDER BY date"
    )
    return pd.read_sql(query, con=engine, params={"ticker": ticker})


def get_latest_data(limit: int = 25) -> pd.DataFrame:
    engine = get_engine()
    query = text("SELECT * FROM market_prices ORDER BY date DESC LIMIT :limit")
    return pd.read_sql(query, con=engine, params={"limit": limit})
