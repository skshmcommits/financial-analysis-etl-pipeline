from __future__ import annotations

from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from financial_research_pipeline.config import settings


def _draw_table_like_text(pdf_canvas: canvas.Canvas, start_y: int, title: str, dataframe: pd.DataFrame) -> int:
    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(50, start_y, title)
    y = start_y - 18

    pdf_canvas.setFont("Helvetica", 9)
    text = dataframe.round(4).to_string(index=False)
    for line in text.splitlines()[:20]:
        pdf_canvas.drawString(50, y, line[:110])
        y -= 11
        if y < 80:
            pdf_canvas.showPage()
            y = 740
            pdf_canvas.setFont("Helvetica", 9)
    return y - 10


def generate_report(
    market_df: pd.DataFrame,
    returns_df: pd.DataFrame,
    risk_df: pd.DataFrame,
    correlation_df: pd.DataFrame,
    chart_files: list[Path],
    output_file: Path | None = None,
) -> Path:
    report_file = output_file or settings.REPORT_PDF_FILE
    report_file.parent.mkdir(parents=True, exist_ok=True)

    pdf = canvas.Canvas(str(report_file), pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, height - 50, "Automated Financial Research Report")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, height - 80, "1. Market Overview")
    pdf.drawString(70, height - 100, f"Tickers analyzed: {', '.join(sorted(market_df['ticker'].unique()))}")
    pdf.drawString(70, height - 118, f"Rows analyzed: {len(market_df):,}")

    y = height - 150
    y = _draw_table_like_text(pdf, int(y), "2. Price Trends & Returns", returns_df)
    y = _draw_table_like_text(pdf, int(y), "3. Risk Metrics", risk_df)

    if not correlation_df.empty:
        y = _draw_table_like_text(pdf, int(y), "4. Correlation Analysis", correlation_df.reset_index())

    for chart_file in chart_files:
        if not chart_file.exists():
            continue
        pdf.showPage()
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, height - 40, f"Chart: {chart_file.name}")
        img = ImageReader(str(chart_file))
        pdf.drawImage(img, 40, 140, width=530, height=560, preserveAspectRatio=True, mask="auto")

    pdf.save()
    return report_file
