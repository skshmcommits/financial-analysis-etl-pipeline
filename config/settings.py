from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_OUTPUT_DIR = BASE_DIR / "reports"
REPORT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "SPY"]
START_DATE = "2015-01-01"

DATABASE_URL = f"sqlite:///{(BASE_DIR / 'financial_data.db').as_posix()}"

RISK_FREE_RATE = 0.02
VAR_CONFIDENCE = 0.95

MACRO_SERIES = {
    "CPI": "CPIAUCSL",
    "GDP": "GDP",
    "UNEMPLOYMENT": "UNRATE",
    "FED_FUNDS": "FEDFUNDS",
}
FRED_API_KEY = os.getenv("FRED_API_KEY", "")

CHART_PRICE_FILE = REPORT_OUTPUT_DIR / "price_chart.png"
CHART_RETURNS_FILE = REPORT_OUTPUT_DIR / "returns_distribution.png"
CHART_CORRELATION_FILE = REPORT_OUTPUT_DIR / "correlation_heatmap.png"
CHART_VOLATILITY_FILE = REPORT_OUTPUT_DIR / "volatility_chart.png"
REPORT_PDF_FILE = REPORT_OUTPUT_DIR / "research_report.pdf"
