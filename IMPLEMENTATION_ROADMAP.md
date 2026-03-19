# Financial Research Pipeline - Implementation Roadmap

## Scope and Principles
- Build an end-to-end Python pipeline exactly as specified: ingestion -> cleaning/validation -> features -> DB -> analytics -> charts -> PDF report -> CLI orchestration.
- Start with SQLite and local execution.
- Keep modules small, testable, and independently runnable.
- Prefer deterministic outputs (repeatable runs, stable filenames, explicit date ranges).

## Target Architecture
```text
financial_research_pipeline/
  config/
    settings.py
  data_ingestion/
    fetch_market_data.py
    fetch_macro_data.py
  data_processing/
    clean_market_data.py
    validation.py
    feature_engineering.py
  database/
    db_connection.py
    load_data.py
    queries.py
  analytics/
    returns.py
    risk_metrics.py
    correlations.py
  reporting/
    charts.py
    report_generator.py
  cli/
    pipeline_cli.py
  tests/
  main.py
  requirements.txt
  README.md
```

## Delivery Phases (Implementable Sequence)

### Phase 0 - Project Skeleton and Tooling
Deliverables:
- Folder structure and Python package init files.
- `requirements.txt` with core dependencies.
- Base logging setup and `README.md` starter.

Acceptance criteria:
- `python main.py` runs without import errors.
- `python -m pytest` discovers test folder.

---

### Phase 1 - Configuration and Ingestion
Deliverables:
- `config/settings.py` with tickers, dates, DB URL, report paths, macro series list.
- `data_ingestion/fetch_market_data.py` using `yfinance`.
- `data_ingestion/fetch_macro_data.py` using `fredapi` (with graceful fallback if API key missing).

Acceptance criteria:
- Fetching one ticker returns standardized columns:
  `date, ticker, open, high, low, close, adjusted_close, volume`.
- Macro fetch returns:
  `date, indicator, value`.

---

### Phase 2 - Data Processing
Deliverables:
- `clean_market_data.py`: datetime conversion, sort, de-duplication, numeric coercion, missing value handling.
- `validation.py`: missing values, negatives, outlier flags, duplicates report.
- `feature_engineering.py`: return, log return, MA20/MA50/MA200, rolling 30-day volatility.

Acceptance criteria:
- Cleaned dataset has expected types and ordering.
- Validation returns dictionary report with counts.
- Feature columns are present and numerically valid.

---

### Phase 3 - Database Layer
Deliverables:
- `db_connection.py` with SQLAlchemy engine factory.
- `load_data.py` writing `market_prices` table via `to_sql`.
- `queries.py` with `get_prices`, `get_returns`, `get_latest_data`.

Acceptance criteria:
- Data can be loaded and retrieved for a ticker.
- Table schema includes engineered features.

---

### Phase 4 - Analytics Layer
Deliverables:
- `returns.py`: cumulative and annualized returns, distribution summary.
- `risk_metrics.py`: annualized volatility, Sharpe ratio, VaR percentile.
- `correlations.py`: correlation matrix across assets.

Acceptance criteria:
- Analytics functions work directly from DataFrames loaded from DB queries.
- Metrics are returned in structured dict/DataFrame outputs for reporting.

---

### Phase 5 - Reporting and Visualization
Deliverables:
- `charts.py` for price series, returns histogram, heatmap, volatility chart.
- `report_generator.py` to assemble sections and emit `reports/research_report.pdf`.

Acceptance criteria:
- Chart image files are produced in `reports/`.
- PDF report is generated with all required sections.

---

### Phase 6 - CLI and Pipeline Orchestration
Deliverables:
- `cli/pipeline_cli.py` commands:
  `fetch`, `process`, `load`, `analyze`, `report`, `run-all`.
- `main.py` orchestration function matching specified flow.

Acceptance criteria:
- `python cli/pipeline_cli.py run-all` executes full pipeline end-to-end.

---

### Phase 7 - Tests and Hardening
Deliverables:
- Unit tests for cleaning, feature engineering, and analytics math.
- Logging across modules and error handling for API/database/report generation failures.

Acceptance criteria:
- Core tests pass.
- Failures produce actionable logs.

## Implementation Contract (What I can build next)
I can implement this in the following immediate order:
1. Create full project skeleton + dependencies + config.
2. Implement market ingestion and cleaning/feature modules.
3. Implement DB load/query and verify persisted outputs.
4. Implement analytics and chart generation.
5. Implement report PDF generation.
6. Implement CLI commands and full `run-all` workflow.
7. Add tests for critical transformations and metrics.

## MVP Milestone (First usable version)
An MVP can be considered complete when:
- One command (`run-all`) fetches market data for configured tickers.
- Engineered features are stored in SQLite.
- At least 3 charts + one PDF report are produced.
- Basic risk metrics and correlations are included in report output.

## Risks and Mitigations
- External API instability -> retries + clear logging + partial success handling.
- Missing FRED API key -> skip macro ingestion with warning.
- PDF engine incompatibility (`pdfkit`) -> fallback option (`reportlab`) if needed.
- Data quality issues (NaNs/outliers) -> validation report stored and logged.

## Definition of Done
- Full pipeline command runs successfully on a clean environment.
- Output artifacts generated in DB + `reports/`.
- Tests pass for processing and analytics modules.
- README documents setup, commands, and expected outputs.