# Automated Financial Research Data Pipeline

Python pipeline for ingesting market/macro data, processing and validating it, storing it in SQL, computing analytics, and generating automated research reports.

## Architecture
- `config/`: centralized settings and paths
- `data_ingestion/`: market and macro data fetchers
- `data_processing/`: cleaning, validation, and feature engineering
- `database/`: SQLAlchemy engine, loaders, and query helpers
- `analytics/`: returns, risk metrics, and correlation analysis
- `reporting/`: chart generation and PDF report generation
- `cli/`: command-line interface for partial or full pipeline runs

## Setup
1. Create and activate a Python 3.11+ environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

Optional macro data support:
- Set `FRED_API_KEY` in your environment.

## CLI Commands
Run from the parent directory of the package:

```bash
python -m financial_research_pipeline.cli.pipeline_cli fetch
python -m financial_research_pipeline.cli.pipeline_cli process
python -m financial_research_pipeline.cli.pipeline_cli load
python -m financial_research_pipeline.cli.pipeline_cli analyze
python -m financial_research_pipeline.cli.pipeline_cli report
python -m financial_research_pipeline.cli.pipeline_cli run-all
```

## Expected Outputs
- SQLite database: `financial_data.db`
- Reports directory artifacts:
  - `reports/research_report.pdf`
  - `reports/price_chart.png`
  - `reports/correlation_heatmap.png`
  - `reports/volatility_chart.png`
  - `reports/returns_distribution.png`

## Tests
```bash
pytest financial_research_pipeline/tests
```