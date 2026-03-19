from __future__ import annotations

import json
import logging

import pandas as pd

from financial_research_pipeline.analytics.correlations import compute_correlation_matrix
from financial_research_pipeline.analytics.risk_metrics import compute_risk_metrics
from financial_research_pipeline.analytics.returns import compute_returns
from financial_research_pipeline.config import settings
from financial_research_pipeline.data_ingestion.fetch_macro_data import fetch_macro_data_bulk
from financial_research_pipeline.data_ingestion.fetch_market_data import fetch_market_data_bulk
from financial_research_pipeline.data_processing.clean_market_data import clean_market_data
from financial_research_pipeline.data_processing.feature_engineering import create_features
from financial_research_pipeline.data_processing.validation import validate_market_data
from financial_research_pipeline.database.load_data import load_market_data
from financial_research_pipeline.reporting.charts import (
    plot_correlation_heatmap,
    plot_price_series,
    plot_returns_distribution,
    plot_volatility_chart,
)
from financial_research_pipeline.reporting.report_generator import generate_report


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
LOGGER = logging.getLogger(__name__)


def run_fetch() -> dict:
    LOGGER.info("Fetching market data")
    market_df = fetch_market_data_bulk(settings.TICKERS, settings.START_DATE)
    if market_df.empty:
        raise RuntimeError("No market data fetched; check tickers and network access")

    macro_df = fetch_macro_data_bulk(list(settings.MACRO_SERIES.values()))

    raw_market_csv = settings.REPORT_OUTPUT_DIR / "raw_market_data.csv"
    raw_macro_csv = settings.REPORT_OUTPUT_DIR / "raw_macro_data.csv"
    market_df.to_csv(raw_market_csv, index=False)
    macro_df.to_csv(raw_macro_csv, index=False)

    return {
        "rows_market": len(market_df),
        "rows_macro": len(macro_df),
        "raw_market_file": raw_market_csv,
        "raw_macro_file": raw_macro_csv if not macro_df.empty else "not_generated",
    }


def _prepare_features() -> tuple[pd.DataFrame, dict]:
    market_df = fetch_market_data_bulk(settings.TICKERS, settings.START_DATE)
    cleaned_df = clean_market_data(market_df)
    validation_report = validate_market_data(cleaned_df)
    featured_df = create_features(cleaned_df)
    return featured_df, validation_report


def run_process() -> dict:
    LOGGER.info("Processing market data")
    featured_df, validation_report = _prepare_features()

    processed_file = settings.REPORT_OUTPUT_DIR / "processed_market_data.csv"
    validation_file = settings.REPORT_OUTPUT_DIR / "validation_report.json"
    featured_df.to_csv(processed_file, index=False)
    validation_file.write_text(json.dumps(validation_report, indent=2), encoding="utf-8")

    return {
        "rows_processed": len(featured_df),
        "processed_file": processed_file,
        "validation_file": validation_file,
    }


def run_load() -> dict:
    LOGGER.info("Loading market data into database")
    featured_df, validation_report = _prepare_features()
    load_market_data(featured_df)

    validation_file = settings.REPORT_OUTPUT_DIR / "validation_report.json"
    validation_file.write_text(json.dumps(validation_report, indent=2), encoding="utf-8")

    return {
        "rows_loaded": len(featured_df),
        "database_url": settings.DATABASE_URL,
        "validation_file": validation_file,
    }


def run_analyze() -> dict:
    LOGGER.info("Running analytics")
    featured_df, _ = _prepare_features()
    macro_df = fetch_macro_data_bulk(list(settings.MACRO_SERIES.values()))

    returns_df = compute_returns(featured_df)
    risk_df = compute_risk_metrics(featured_df, macro_df=macro_df)
    correlation_df = compute_correlation_matrix(featured_df)

    analytics_summary_file = settings.REPORT_OUTPUT_DIR / "analytics_summary.json"
    summary_payload = {
        "returns": returns_df.to_dict(orient="records"),
        "risk_metrics": risk_df.to_dict(orient="records"),
        "macro_rows": int(len(macro_df)),
        "correlations": correlation_df.round(4).to_dict() if not correlation_df.empty else {},
    }
    analytics_summary_file.write_text(json.dumps(summary_payload, indent=2, default=str), encoding="utf-8")

    return {
        "returns_rows": len(returns_df),
        "risk_rows": len(risk_df),
        "macro_rows": len(macro_df),
        "correlation_shape": list(correlation_df.shape),
        "analytics_file": analytics_summary_file,
    }


def run_report() -> dict:
    LOGGER.info("Generating charts and report")
    featured_df, _ = _prepare_features()
    macro_df = fetch_macro_data_bulk(list(settings.MACRO_SERIES.values()))
    returns_df = compute_returns(featured_df)
    risk_df = compute_risk_metrics(featured_df, macro_df=macro_df)
    correlation_df = compute_correlation_matrix(featured_df)

    chart_files = [
        plot_price_series(featured_df, settings.CHART_PRICE_FILE),
        plot_returns_distribution(featured_df, settings.CHART_RETURNS_FILE),
        plot_volatility_chart(risk_df, settings.CHART_VOLATILITY_FILE),
    ]
    if not correlation_df.empty:
        chart_files.append(plot_correlation_heatmap(correlation_df, settings.CHART_CORRELATION_FILE))

    report_file = generate_report(
        market_df=featured_df,
        returns_df=returns_df,
        risk_df=risk_df,
        correlation_df=correlation_df,
        chart_files=chart_files,
        output_file=settings.REPORT_PDF_FILE,
    )

    return {
        "report_file": report_file,
        "charts": [str(path) for path in chart_files],
    }


def run_full_pipeline() -> dict:
    LOGGER.info("Running full pipeline")
    fetch_output = run_fetch()
    process_output = run_process()
    load_output = run_load()
    analyze_output = run_analyze()
    report_output = run_report()

    return {
        "fetch": fetch_output,
        "process": process_output,
        "load": load_output,
        "analyze": analyze_output,
        "report": report_output,
    }


if __name__ == "__main__":
    result = run_full_pipeline()
    print(json.dumps(result, indent=2, default=str))
