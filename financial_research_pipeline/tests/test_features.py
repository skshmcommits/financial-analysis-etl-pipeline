import pandas as pd

from financial_research_pipeline.data_processing.feature_engineering import create_features


def test_create_features_adds_expected_columns():
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=30),
            "ticker": ["AAPL"] * 30,
            "open": range(30),
            "high": range(1, 31),
            "low": range(30),
            "close": range(1, 31),
            "adjusted_close": range(1, 31),
            "volume": [100] * 30,
        }
    )
    output = create_features(df)

    for column in ["return", "log_return", "MA20", "MA50", "MA200", "volatility"]:
        assert column in output.columns
