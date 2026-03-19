# Financial Research Pipeline - Detailed Technical Documentation

## 1) Project Purpose and What It Delivers

This project is an end-to-end financial research system that automates the full workflow from market data collection to final analyst-ready reporting.

The implemented pipeline does all of the following:
1. Fetches historical market price data from Yahoo Finance.
2. Optionally fetches macroeconomic time series from FRED (if an API key is available).
3. Cleans and validates raw time-series data.
4. Engineers financial features used in quant analysis.
5. Loads processed data into a SQL database (SQLite via SQLAlchemy).
6. Computes return/risk/correlation analytics.
7. Generates chart artifacts and a PDF research report.
8. Exposes all steps through a CLI for modular execution or one-command automation.

This design mirrors the practical workflow used by research, strategy, and portfolio analytics teams.

---

## 2) Assets/Companies Being Tracked

Tracked symbols are configured in `config/settings.py` via:

- `AAPL` (Apple)
- `MSFT` (Microsoft)
- `GOOGL` (Alphabet)
- `AMZN` (Amazon)
- `SPY` (SPDR S&P 500 ETF, broad market proxy)

Start date is configured as `2015-01-01`.

Why this matters:
- The four mega-cap equities provide company-level behavior.
- `SPY` adds an index proxy for market regime/context comparison.
- This setup supports relative performance and diversification analysis.

---

## 3) System Architecture (Module by Module)

### A. Configuration Layer
File: `config/settings.py`

Defines:
- Output and base paths (`BASE_DIR`, `REPORT_OUTPUT_DIR`)
- Asset universe (`TICKERS`)
- Data horizon (`START_DATE`)
- Database connection (`DATABASE_URL`)
- Risk assumptions:
  - `RISK_FREE_RATE = 0.02`
  - `VAR_CONFIDENCE = 0.95`
- Macro series mapping (`MACRO_SERIES`)
- Report/chart output filenames

Operational value:
- Centralized controls make the pipeline reproducible and easy to tune.

---

### B. Data Ingestion Layer

#### 1. Market Data Ingestion
File: `data_ingestion/fetch_market_data.py`

Functions:

##### `_normalize_columns(dataframe)`
Purpose:
- Normalizes Yahoo output to consistent internal schema.

What it handles:
- MultiIndex columns from Yahoo responses (flattens to first level).
- Renames standard fields into canonical names.
- Removes duplicate columns.
- Backfills `adjusted_close` from `close` if not present.

##### `fetch_market_data(ticker, start_date)`
Purpose:
- Pulls one symbol’s historical OHLCV data.

Data source:
- `yfinance.download(...)`.

Data fetched:
- Date
- Open
- High
- Low
- Close
- Adjusted Close
- Volume

Transformations in this function:
1. Download raw data.
2. Catch network/provider exceptions and return empty standardized DataFrame.
3. Reset index to expose date as a column.
4. Normalize column names.
5. Append ticker identifier.
6. Return strict schema:
   - `date, ticker, open, high, low, close, adjusted_close, volume`

##### `fetch_market_data_bulk(tickers, start_date)`
Purpose:
- Fetches all configured tickers and concatenates non-empty outputs.

Behavior:
- Skips empty symbol responses.
- Returns empty schema DataFrame if all fetches fail.

Business value:
- Provides robust, partially fault-tolerant ingestion; one failed ticker does not kill the entire run.

#### 2. Macro Data Ingestion
File: `data_ingestion/fetch_macro_data.py`

Function:

##### `fetch_macro_series(series_id)`
Purpose:
- Pulls one macroeconomic time series from FRED.

Configured macro series:
- CPI (`CPIAUCSL`)
- GDP (`GDP`)
- Unemployment (`UNRATE`)
- Fed Funds Rate (`FEDFUNDS`)

Returned schema:
- `date, indicator, value`

Important runtime behavior:
- If `FRED_API_KEY` is not set, it logs a warning and returns empty output.

Business value:
- Enables macro-overlay extension for regime-aware research (inflation, growth, labor market, rates).

---

### C. Data Processing Layer

#### 1. Cleaning
File: `data_processing/clean_market_data.py`

Function:

##### `clean_market_data(dataframe)`
Purpose:
- Converts raw market data into analysis-ready time series.

Transformations:
1. Converts `date` to datetime (`errors='coerce'`).
2. Coerces numeric columns (`open, high, low, close, adjusted_close, volume`) to numeric.
3. Drops rows missing essential keys (`date`, `ticker`).
4. Sorts by `ticker, date`.
5. Removes duplicate ticker-date rows (keeps latest).
6. Fills missing numeric data per ticker with forward fill and backfill.
7. Drops rows where `close` remains missing.

Inference/impact:
- Ensures time-order correctness and stable feature generation.
- Reduces bad-data noise before analytics.

#### 2. Validation
File: `data_processing/validation.py`

Function:

##### `validate_market_data(dataframe)`
Purpose:
- Produces a structured data-quality report.

Checks performed:
- Total missing values.
- Duplicate ticker-date rows.
- Negative prices in OHLC/adjusted close.
- Extreme outliers in daily returns using z-score threshold `|z| > 5`.

Output fields:
- `rows`
- `missing_values`
- `duplicates`
- `negative_prices`
- `extreme_outliers`

Inference/impact:
- Provides quality gates and auditability before downstream analytics are trusted.

#### 3. Feature Engineering
File: `data_processing/feature_engineering.py`

Function:

##### `create_features(dataframe)`
Purpose:
- Derives standard quant features used for returns and risk analysis.

Features generated per ticker:
- `return`: simple daily return using `pct_change()`
- `log_return`: $\log\left(\frac{P_t}{P_{t-1}}\right)$
- `MA20`: 20-day moving average
- `MA50`: 50-day moving average
- `MA200`: 200-day moving average
- `volatility`: rolling 30-day std of returns (`min_periods=5`)

Inference/impact:
- Supports trend detection (MAs), short-term risk estimation (rolling volatility), and return modeling.

---

### D. Database Layer

#### 1. Engine Setup
File: `database/db_connection.py`

Function:

##### `get_engine(database_url=None)`
Purpose:
- Creates SQLAlchemy engine for SQLite (or alternate URL).

#### 2. Data Loading
File: `database/load_data.py`

Function:

##### `load_market_data(dataframe, table_name='market_prices')`
Purpose:
- Persists processed + feature-engineered data to SQL.

Behavior:
- Ensures expected schema columns exist.
- Reorders columns into canonical order.
- Writes using `to_sql(..., if_exists='replace')`.

Stored fields:
- `date, ticker, open, high, low, close, adjusted_close, volume`
- `return, log_return, MA20, MA50, MA200, volatility`

#### 3. Query Layer
File: `database/queries.py`

Functions:
- `get_prices(ticker)` -> full history for one ticker
- `get_returns(ticker)` -> return-focused subset
- `get_latest_data(limit=25)` -> newest records across symbols

Business value:
- SQL persistence enables reproducibility, downstream BI integration, and analyst querying.

---

### E. Analytics Layer

#### 1. Returns Analytics
File: `analytics/returns.py`

Function:

##### `compute_returns(dataframe)`
Computes per ticker:
- `cumulative_return`: $(1+r_1)(1+r_2)...(1+r_n)-1$
- `annual_return`: annualized from cumulative return over trading-day count
- `daily_return_std`: standard deviation of daily returns

Use case:
- Performance ranking and dispersion comparison across tracked assets.

#### 2. Risk Metrics
File: `analytics/risk_metrics.py`

Function:

##### `compute_risk_metrics(dataframe)`
Computes per ticker:
- `volatility` (annualized): $\sigma_{daily} \cdot \sqrt{252}$
- `sharpe_ratio`: $\frac{\mu_{annual}-r_f}{\sigma_{annual}}$ with `r_f = 0.02`
- `value_at_risk`: empirical quantile at 5% tail (`VAR_CONFIDENCE = 0.95`)

These are the key “ratios/metrics” currently used in the project.

Use case:
- Risk-adjusted return comparison.
- Tail-loss screening.
- Position sizing and watchlist prioritization.

#### 3. Correlation Analytics
File: `analytics/correlations.py`

Function:

##### `compute_correlation_matrix(price_df)`
Purpose:
- Builds close-price pivot table by date x ticker.
- Computes pairwise correlation matrix.

Use case:
- Diversification analysis and concentration risk identification.

---

### F. Reporting Layer

#### 1. Chart Generation
File: `reporting/charts.py`

Functions and outputs:
- `plot_price_series(...)` -> `price_chart.png`
- `plot_returns_distribution(...)` -> `returns_distribution.png`
- `plot_correlation_heatmap(...)` -> `correlation_heatmap.png`
- `plot_volatility_chart(...)` -> `volatility_chart.png`

How they help:
- Price chart: trend and regime visualization.
- Return histogram: distribution shape and tail intuition.
- Correlation heatmap: diversification map.
- Volatility bar chart: quick risk ranking across assets.

#### 2. PDF Research Report
File: `reporting/report_generator.py`

Primary function:

##### `generate_report(market_df, returns_df, risk_df, correlation_df, chart_files, output_file=None)`
What it includes:
1. Market overview (tickers analyzed, row count)
2. Price trends & return summary table text
3. Risk metrics table text
4. Correlation table text (if available)
5. Dedicated pages embedding generated charts

Output:
- `reports/research_report.pdf`

How this helps research workflows:
- Produces a portable, shareable briefing artifact for PMs, strategists, and interview/demo stakeholders.

---

### G. Orchestration Layer
File: `main.py`

Key functions:

#### `run_fetch()`
- Fetches market + macro data.
- Saves raw CSV artifacts:
  - `raw_market_data.csv`
  - `raw_macro_data.csv` (if macro data available)

#### `_prepare_features()`
- Internal helper for repeated steps:
  1. Fetch market data
  2. Clean data
  3. Validate data
  4. Engineer features

#### `run_process()`
- Saves processed dataset and validation report:
  - `processed_market_data.csv`
  - `validation_report.json`

#### `run_load()`
- Loads processed data into SQLite.
- Writes validation report.

#### `run_analyze()`
- Produces analytics outputs and stores JSON summary:
  - `analytics_summary.json`

#### `run_report()`
- Produces charts and final PDF report.

#### `run_full_pipeline()`
- Executes full lifecycle:
  - fetch -> process -> load -> analyze -> report

---

### H. CLI Layer
File: `cli/pipeline_cli.py`

Commands:
- `fetch`
- `process`
- `load`
- `analyze`
- `report`
- `run-all`

This CLI allows both:
- Stepwise debugging (run one stage)
- One-shot production-style execution (`run-all`)

---

## 4) Exactly What Data Is Being Fetched

### Market Data (Yahoo Finance)
For each ticker and each date since start date:
- `open`
- `high`
- `low`
- `close`
- `adjusted_close`
- `volume`

Plus metadata added in pipeline:
- `ticker`
- normalized `date`

### Macro Data (FRED, optional)
For each configured macro indicator:
- `date`
- `indicator` (series id)
- `value`

Note:
- Macro series are fetched but currently not joined into the final analytics calculations in this version.

---

## 5) Data Transformations and Inferences

### Transformations
1. Structural normalization:
   - Standardized schema and data types.
2. Temporal ordering:
   - Sorted by ticker/date to preserve causal sequence.
3. Missing-value strategy:
   - Forward/back fill within ticker for numeric continuity.
4. De-duplication:
   - One row per ticker-date retained.
5. Feature expansion:
   - Returns, log returns, moving averages, rolling volatility.

### Inferences Produced by Analytics
- Performance inference:
  - Cumulative and annualized return identify absolute winners/laggards.
- Stability/risk inference:
  - Volatility and daily return dispersion identify riskier symbols.
- Risk-adjusted efficiency inference:
  - Sharpe ratio compares return per unit of risk.
- Tail-risk inference:
  - VaR estimates downside threshold under historical distribution.
- Portfolio construction inference:
  - Correlation matrix highlights diversification opportunities and co-movement clusters.

---

## 6) Reports Generated and How They Help

### File Artifacts
Generated in `reports/`:
- `raw_market_data.csv`
- `raw_macro_data.csv` (when available)
- `processed_market_data.csv`
- `validation_report.json`
- `analytics_summary.json`
- `price_chart.png`
- `returns_distribution.png`
- `correlation_heatmap.png`
- `volatility_chart.png`
- `research_report.pdf`

### Decision Support Value
- Data quality report (`validation_report.json`):
  - Confidence checkpoint before decisions.
- Analytics summary (`analytics_summary.json`):
  - Structured machine-readable KPI payload for dashboards/APIs.
- Charts:
  - Fast visual interpretation for meetings and daily monitoring.
- PDF report:
  - Human-readable narrative pack for stakeholders and archives.

---

## 7) Methods, Assumptions, and Current Constraints

### Assumptions
- 252 trading days per year for annualization.
- Constant risk-free rate of 2%.
- Historical quantile method for VaR (non-parametric).

### Current Constraints
- Macro data fetch requires `FRED_API_KEY`; otherwise macro path is skipped.
- `run-all` currently re-fetches data at multiple stages (functionally correct, less efficient).
- Data source reliability depends on external API/network behavior.

---

## 8) Why This Is Useful for Real Financial Research Work

The system provides a repeatable research process with explicit quality controls and traceable outputs. In practical terms, it enables teams to:

- Keep an up-to-date market dataset with minimal manual effort.
- Monitor core risk-return signals consistently.
- Compare single-name behavior to market proxy behavior.
- Export both machine-readable and executive-readable outputs.
- Build an extensible base for deeper quant modeling.

---

## 9) Quick Function Index

### Ingestion
- `fetch_market_data`
- `fetch_market_data_bulk`
- `fetch_macro_series`

### Processing
- `clean_market_data`
- `validate_market_data`
- `create_features`

### Database
- `get_engine`
- `load_market_data`
- `get_prices`
- `get_returns`
- `get_latest_data`

### Analytics
- `compute_returns`
- `compute_risk_metrics`
- `compute_correlation_matrix`

### Reporting
- `plot_price_series`
- `plot_returns_distribution`
- `plot_correlation_heatmap`
- `plot_volatility_chart`
- `generate_report`

### Orchestration & CLI
- `run_fetch`, `run_process`, `run_load`, `run_analyze`, `run_report`, `run_full_pipeline`
- CLI commands: `fetch`, `process`, `load`, `analyze`, `report`, `run-all`
