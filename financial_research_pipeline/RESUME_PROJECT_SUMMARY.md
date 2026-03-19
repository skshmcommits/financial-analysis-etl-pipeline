# Resume Project Summary

Built an end-to-end **Automated Financial Research Data Pipeline** in Python to ingest, process, analyze, and report on equity market data.

- Designed a modular pipeline architecture (ingestion, processing, database, analytics, reporting, CLI) for reproducible financial research workflows.
- Integrated market data ingestion via `yfinance` and optional macroeconomic ingestion via FRED APIs.
- Implemented data quality controls: schema normalization, type coercion, deduplication, missing value handling, and validation reporting.
- Engineered financial features including daily/log returns, MA20/MA50/MA200, and rolling volatility.
- Developed risk and performance analytics (cumulative return, annualized return, volatility, Sharpe ratio, VaR, correlation matrix).
- Persisted processed datasets into SQLite using SQLAlchemy and exposed query-ready outputs.
- Automated deliverables with a CLI (`run-all`) that generates CSV/JSON artifacts, visualization charts, and a PDF research report.
- Added test coverage with `pytest` for core cleaning, feature engineering, and analytics logic.

**Tech stack:** Python, pandas, numpy, yfinance, fredapi, SQLAlchemy, SQLite, matplotlib, reportlab, pytest.
