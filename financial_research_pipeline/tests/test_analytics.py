import pandas as pd

from financial_research_pipeline.analytics.risk_metrics import compute_risk_metrics
from financial_research_pipeline.analytics.returns import compute_returns


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=6),
            "ticker": ["AAPL"] * 6,
            "close": [100, 102, 101, 103, 104, 105],
        }
    )


def test_compute_returns_has_one_row_per_ticker():
    result = compute_returns(_sample_df())
    assert list(result["ticker"]) == ["AAPL"]


def test_compute_risk_metrics_has_expected_columns():
    result = compute_risk_metrics(_sample_df())
    for column in ["ticker", "volatility", "sharpe_ratio", "value_at_risk"]:
        assert column in result.columns
