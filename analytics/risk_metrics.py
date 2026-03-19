from __future__ import annotations

import numpy as np
import pandas as pd

from financial_research_pipeline.config.settings import RISK_FREE_RATE, VAR_CONFIDENCE


def _extract_macro_context(macro_df: pd.DataFrame | None) -> tuple[float, float]:
    risk_free_rate_used = RISK_FREE_RATE
    avg_inflation_yoy = np.nan

    if macro_df is None or macro_df.empty:
        return risk_free_rate_used, avg_inflation_yoy

    working = macro_df.copy()
    working["date"] = pd.to_datetime(working["date"], errors="coerce")
    working["value"] = pd.to_numeric(working["value"], errors="coerce")
    working = working.dropna(subset=["date", "value", "indicator"])

    fed_funds = working[working["indicator"] == "FEDFUNDS"].sort_values("date")
    if not fed_funds.empty:
        recent_fed_funds = fed_funds.tail(12)["value"].mean()
        if not np.isnan(recent_fed_funds):
            risk_free_rate_used = float(recent_fed_funds) / 100.0

    cpi = working[working["indicator"] == "CPIAUCSL"].sort_values("date")
    if not cpi.empty and len(cpi) > 12:
        cpi = cpi.copy()
        cpi["inflation_yoy"] = cpi["value"].pct_change(12)
        avg_recent_inflation = cpi["inflation_yoy"].tail(12).mean()
        if not np.isnan(avg_recent_inflation):
            avg_inflation_yoy = float(avg_recent_inflation)

    return risk_free_rate_used, avg_inflation_yoy


def compute_risk_metrics(dataframe: pd.DataFrame, macro_df: pd.DataFrame | None = None) -> pd.DataFrame:
    if dataframe.empty:
        return pd.DataFrame(
            columns=[
                "ticker",
                "volatility",
                "sharpe_ratio",
                "value_at_risk",
                "risk_free_rate_used",
                "avg_inflation_yoy",
                "real_annual_return_approx",
            ]
        )

    frame = dataframe.copy()
    if "return" not in frame.columns:
        frame["return"] = frame.groupby("ticker")["close"].pct_change()

    metrics = []
    alpha = 1 - VAR_CONFIDENCE
    risk_free_rate_used, avg_inflation_yoy = _extract_macro_context(macro_df)

    for ticker, ticker_df in frame.groupby("ticker"):
        returns = ticker_df["return"].dropna()
        if returns.empty:
            volatility = np.nan
            sharpe_ratio = np.nan
            value_at_risk = np.nan
            annual_return = np.nan
        else:
            volatility = returns.std() * np.sqrt(252)
            annual_return = returns.mean() * 252
            sharpe_ratio = (annual_return - risk_free_rate_used) / volatility if volatility and not np.isnan(volatility) else np.nan
            value_at_risk = returns.quantile(alpha)

        real_annual_return_approx = np.nan
        if not np.isnan(annual_return) and not np.isnan(avg_inflation_yoy):
            real_annual_return_approx = annual_return - avg_inflation_yoy

        metrics.append(
            {
                "ticker": ticker,
                "volatility": volatility,
                "sharpe_ratio": sharpe_ratio,
                "value_at_risk": value_at_risk,
                "risk_free_rate_used": risk_free_rate_used,
                "avg_inflation_yoy": avg_inflation_yoy,
                "real_annual_return_approx": real_annual_return_approx,
            }
        )

    return pd.DataFrame(metrics)
