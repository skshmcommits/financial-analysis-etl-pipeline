from __future__ import annotations

import logging
from io import StringIO

import pandas as pd
import requests

from financial_research_pipeline.config.settings import FRED_API_KEY


LOGGER = logging.getLogger(__name__)


def _fetch_macro_series_public(series_id: str) -> pd.DataFrame:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    raw = pd.read_csv(StringIO(response.text))
    if raw.empty or raw.shape[1] < 2:
        return pd.DataFrame(columns=["date", "indicator", "value"])

    raw.columns = ["date", "value"]
    raw["date"] = pd.to_datetime(raw["date"], errors="coerce")
    raw["value"] = pd.to_numeric(raw["value"], errors="coerce")
    raw = raw.dropna(subset=["date", "value"]).copy()
    raw["indicator"] = series_id
    return raw[["date", "indicator", "value"]]


def fetch_macro_series(series_id: str) -> pd.DataFrame:
    try:
        from fredapi import Fred
    except ImportError as exc:
        LOGGER.warning("fredapi import failed (%s), using public FRED CSV fallback", exc)
        try:
            return _fetch_macro_series_public(series_id)
        except Exception as fallback_error:
            LOGGER.warning("Public FRED fallback failed for %s: %s", series_id, fallback_error)
            return pd.DataFrame(columns=["date", "indicator", "value"])

    if not FRED_API_KEY:
        LOGGER.warning("FRED_API_KEY not found; using public FRED CSV fallback for %s", series_id)
        try:
            return _fetch_macro_series_public(series_id)
        except Exception as fallback_error:
            LOGGER.warning("Public FRED fallback failed for %s: %s", series_id, fallback_error)
            return pd.DataFrame(columns=["date", "indicator", "value"])

    fred = Fred(api_key=FRED_API_KEY)
    series = fred.get_series(series_id)
    if series.empty:
        LOGGER.warning("No macro series returned for %s", series_id)
        return pd.DataFrame(columns=["date", "indicator", "value"])

    macro_df = series.reset_index()
    macro_df.columns = ["date", "value"]
    macro_df["date"] = pd.to_datetime(macro_df["date"], errors="coerce")
    macro_df["value"] = pd.to_numeric(macro_df["value"], errors="coerce")
    macro_df = macro_df.dropna(subset=["date", "value"]).copy()
    macro_df["indicator"] = series_id
    macro_df = macro_df[["date", "indicator", "value"]]
    return macro_df


def fetch_macro_data_bulk(series_ids: list[str]) -> pd.DataFrame:
    frames = [fetch_macro_series(series_id) for series_id in series_ids]
    non_empty = [frame for frame in frames if not frame.empty]
    if not non_empty:
        return pd.DataFrame(columns=["date", "indicator", "value"])
    return pd.concat(non_empty, ignore_index=True)
