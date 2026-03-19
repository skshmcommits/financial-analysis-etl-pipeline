from __future__ import annotations

from sqlalchemy import create_engine

from financial_research_pipeline.config.settings import DATABASE_URL


def get_engine(database_url: str | None = None):
    return create_engine(database_url or DATABASE_URL, future=True)
