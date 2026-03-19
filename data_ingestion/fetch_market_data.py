from __future__ import annotations

import logging

import pandas as pd
import yfinance as yf


LOGGER = logging.getLogger(__name__)


STANDARD_COLUMNS = [
    "date",
    "ticker",
    "open",
    "high",
    "low",
    "close",
    "adjusted_close",
    "volume",
]


def _normalize_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    if isinstance(dataframe.columns, pd.MultiIndex):
        dataframe.columns = dataframe.columns.get_level_values(0)

    dataframe = dataframe.rename(
        columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adjusted_close",
            "Volume": "volume",
        }
    )
    dataframe = dataframe.loc[:, ~dataframe.columns.duplicated()]

    if "adjusted_close" not in dataframe.columns and "close" in dataframe.columns:
        dataframe["adjusted_close"] = dataframe["close"]

    return dataframe


def fetch_market_data(ticker: str, start_date: str) -> pd.DataFrame:
    LOGGER.info("Fetching market data for %s", ticker)
    try:
        market_df = yf.download(
            ticker,
            start=start_date,
            progress=False,
            auto_adjust=False,
        )
    except Exception as error:
        LOGGER.warning("Market data fetch failed for %s: %s", ticker, error)
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    if market_df.empty:
        LOGGER.warning("No market data returned for %s", ticker)
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    market_df = market_df.reset_index()
    market_df = _normalize_columns(market_df)
    market_df["ticker"] = ticker

    normalized = pd.DataFrame(
        {
            "date": market_df["date"],
            "ticker": market_df["ticker"],
            "open": market_df["open"],
            "high": market_df["high"],
            "low": market_df["low"],
            "close": market_df["close"],
            "adjusted_close": market_df["adjusted_close"],
            "volume": market_df["volume"],
        }
    )
    return normalized


def fetch_market_data_bulk(tickers: list[str], start_date: str) -> pd.DataFrame:
    frames = [fetch_market_data(ticker, start_date) for ticker in tickers]
    frames = [frame for frame in frames if not frame.empty]
    if not frames:
        return pd.DataFrame(columns=STANDARD_COLUMNS)
    combined = pd.concat(frames, ignore_index=True)
    return combined
