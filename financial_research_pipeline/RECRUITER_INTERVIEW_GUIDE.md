# Recruiter Interview Guide - Financial Research Pipeline

## How to Use This Guide

This document is designed for interview prep. It focuses on:
- what recruiters typically ask,
- what they are really evaluating,
- concise, high-quality answers you can give.

All answers are aligned with the current implementation in this repository.

---

## 1) 30-Second Project Pitch (Use This First)

"I built an end-to-end Python financial research pipeline that automatically fetches market and macro data, cleans and validates it, engineers quant features, stores the results in SQL, computes risk/return analytics, and generates charts plus a PDF research report through a CLI. It mirrors the workflow used by data strat and quant research teams, and can run stage-by-stage or fully automated with a single command." 

---

## 2) What Recruiters Usually Care About Most

### Core points of interest
1. **End-to-end ownership** - Did you build just analysis code, or a full pipeline?
2. **Data engineering discipline** - How did you handle quality, schema, and reliability?
3. **Financial understanding** - Which metrics are used and why?
4. **Production mindset** - Logging, tests, CLI orchestration, fault handling.
5. **Communication quality** - Can you explain complex systems clearly?

### How this project scores well
- Full lifecycle from ingestion to reporting is implemented.
- Data quality checks and validation report are included.
- Common buy-side/sell-side metrics are implemented (volatility, Sharpe, VaR, correlations).
- Reproducible outputs are generated (CSV/JSON/DB/charts/PDF).

---

## 3) Likely Recruiter Questions + Strong Answers

## Q1) "What problem does your project solve?"
**Answer:**
It automates a manual research workflow. Instead of separately downloading prices, cleaning in notebooks, calculating metrics ad hoc, and manually creating slides, this pipeline standardizes the process into a repeatable system: fetch -> process -> validate -> analyze -> report.

---

## Q2) "What makes this project technically strong?"
**Answer:**
It is modular and production-style. I separated responsibilities into ingestion, processing, database, analytics, and reporting modules, and exposed each stage through a CLI command. That makes it testable, easier to debug, and close to how real data platforms are organized.

---

## Q3) "Which companies/assets are tracked, and why these?"
**Answer:**
I track `AAPL`, `MSFT`, `GOOGL`, `AMZN`, and `SPY`. The four equities provide single-name behavior from mega-cap tech, while `SPY` acts as a broad market benchmark. This combination is useful for relative performance and diversification analysis.

---

## Q4) "What data do you fetch exactly?"
**Answer:**
From Yahoo Finance, for each ticker and date: `open`, `high`, `low`, `close`, `adjusted_close`, and `volume`, plus normalized `date` and `ticker`. Optionally, from FRED I fetch macro indicators like CPI, GDP, unemployment, and Fed Funds when `FRED_API_KEY` is set.

---

## Q5) "How do you ensure data quality?"
**Answer:**
I implemented a cleaning and validation pipeline:
- convert dates and numeric columns safely,
- sort by ticker/date,
- deduplicate ticker-date rows,
- fill missing numeric values by ticker,
- report missing values, duplicates, negative prices, and outliers.
The validation output is saved as a JSON artifact so quality is auditable.

---

## Q6) "What transformations/features did you engineer?"
**Answer:**
For each ticker, I compute:
- daily return,
- log return,
- MA20/MA50/MA200 moving averages,
- rolling 30-day volatility.
These features support trend, momentum, and risk analysis.

---

## Q7) "Which financial ratios or metrics are used?"
**Answer:**
Main metrics:
- **Cumulative Return** for total performance,
- **Annualized Return** for normalized comparison,
- **Annualized Volatility** as risk proxy,
- **Sharpe Ratio** for risk-adjusted return,
- **Value at Risk (VaR, 95%)** for tail risk,
- **Correlation Matrix** for diversification insight.

---

## Q8) "How are those metrics actually calculated?"
**Answer:**
- Volatility is daily return std scaled by $\sqrt{252}$.
- Sharpe is $(\mu_{annual} - r_f)/\sigma_{annual}$ with risk-free rate set to 2%.
- VaR uses the empirical 5th percentile of returns (95% confidence).
- Correlations are pairwise correlations of pivoted close-price series.

---

## Q9) "What outputs does the pipeline produce?"
**Answer:**
It produces machine-friendly and human-friendly outputs:
- raw/processed CSVs,
- validation and analytics JSON summaries,
- SQLite database table,
- charts (price trend, return distribution, volatility, correlation heatmap),
- final PDF research report.

---

## Q10) "How does the CLI help?"
**Answer:**
The CLI allows both partial and full execution:
- `fetch`, `process`, `load`, `analyze`, `report`, and `run-all`.
This is useful for debugging individual stages and for automated daily runs in one command.

---

## Q11) "How did you handle failure scenarios?"
**Answer:**
I added defensive behavior for external dependency issues:
- if a ticker fetch fails, that symbol is skipped rather than crashing the entire run,
- if FRED API key is missing, macro ingestion is skipped with warnings,
- structured logging is enabled across modules for diagnosability.

---

## Q12) "How did you test correctness?"
**Answer:**
I added `pytest` tests for key logic:
- cleaning behavior,
- feature generation,
- analytics output structure.
I also validated end-to-end execution through the `run-all` CLI command.

---

## Q13) "What trade-offs did you make?"
**Answer:**
I prioritized reliability and modularity over micro-optimization in this version.
- SQLite is used first for simplicity.
- Pipeline stages currently re-fetch data in some steps for isolation and consistency of stage behavior.
The next optimization is shared in-memory/serialized handoff between stages to reduce duplicate API calls.

---

## Q14) "How is this relevant to data strat / quant / research roles?"
**Answer:**
It demonstrates three capabilities recruiters look for:
1. **Data engineering**: ingestion, schema normalization, SQL persistence, validation.
2. **Financial analytics**: returns/risk/correlation and risk-adjusted interpretation.
3. **Automation & communication**: CLI pipeline and report generation for stakeholders.

---

## Q15) "If we hired you, what would you improve first?"
**Answer:**
Immediate high-impact upgrades:
1. add caching and single-fetch pipeline execution,
2. integrate macro factors directly into analytics,
3. add incremental DB loading (`append` with upsert logic),
4. add scheduling/monitoring (Airflow or cron + alerts),
5. package for deployment with environment-specific configs.

---

## 4) Recruiter-Friendly "Impact" Talking Points

Use these in resume screens or behavioral rounds:
- "Reduced a multi-step manual research flow to a one-command automated pipeline."
- "Implemented data-quality checks and persisted analytics artifacts for reproducibility."
- "Combined engineering and finance concepts in one deliverable: SQL + risk metrics + reporting."
- "Built interview-ready evidence of ownership from raw data to stakeholder-facing outputs."

---

## 5) Fast Answers for Common Follow-ups

### "Is this only for equities?"
Current implementation targets equities/ETF symbols from Yahoo; architecture can be extended to other asset classes by replacing ingestion adapters and schema mapping.

### "Why include SPY?"
It provides market context and helps interpret whether single-name movement is idiosyncratic or market-driven.

### "How do you justify Sharpe usage?"
It’s a standard first-pass risk-adjusted metric; in production I would add constraints around non-normal distributions and complementary metrics like Sortino.

### "How do you know data is trustworthy?"
I quantify quality through a saved validation report and enforce deterministic cleaning steps before any metric computation.

---

## 6) Suggested Closing Statement for Interviews

"This project demonstrates that I can own the complete research data lifecycle: acquiring noisy market data, transforming it into analysis-grade datasets, calculating financial risk/return metrics, and delivering both machine- and human-consumable outputs. The system is modular, testable, and designed to scale into a production research stack." 
