import pandas as pd

from financial_research_pipeline.data_processing.clean_market_data import clean_market_data


def test_clean_market_data_removes_duplicates_and_sorts():
    df = pd.DataFrame(
        {
            "date": ["2024-01-02", "2024-01-01", "2024-01-02"],
            "ticker": ["AAPL", "AAPL", "AAPL"],
            "open": [10, 9, 10],
            "high": [11, 10, 11],
            "low": [9, 8, 9],
            "close": [10.5, 9.5, 10.5],
            "adjusted_close": [10.5, 9.5, 10.5],
            "volume": [100, 90, 100],
        }
    )

    cleaned = clean_market_data(df)
    assert len(cleaned) == 2
    assert cleaned.iloc[0]["date"] < cleaned.iloc[1]["date"]
