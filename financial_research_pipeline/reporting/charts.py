from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_price_series(dataframe: pd.DataFrame, output_file: Path) -> Path:
    plt.figure(figsize=(12, 6))
    for ticker, ticker_df in dataframe.groupby("ticker"):
        plt.plot(pd.to_datetime(ticker_df["date"]), ticker_df["close"], label=ticker)
    plt.title("Price Time Series")
    plt.xlabel("Date")
    plt.ylabel("Close Price")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    return output_file


def plot_returns_distribution(dataframe: pd.DataFrame, output_file: Path) -> Path:
    plt.figure(figsize=(10, 6))
    valid_returns = dataframe["return"].dropna()
    plt.hist(valid_returns, bins=50)
    plt.title("Return Distribution")
    plt.xlabel("Daily Return")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    return output_file


def plot_correlation_heatmap(corr_df: pd.DataFrame, output_file: Path) -> Path:
    plt.figure(figsize=(8, 6))
    image = plt.imshow(corr_df, interpolation="nearest", aspect="auto")
    plt.colorbar(image)
    plt.xticks(range(len(corr_df.columns)), corr_df.columns.tolist(), rotation=45, ha="right")
    plt.yticks(range(len(corr_df.index)), corr_df.index.tolist())
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    return output_file


def plot_volatility_chart(risk_df: pd.DataFrame, output_file: Path) -> Path:
    plt.figure(figsize=(10, 6))
    plt.bar(risk_df["ticker"], risk_df["volatility"])
    plt.title("Annualized Volatility by Ticker")
    plt.xlabel("Ticker")
    plt.ylabel("Volatility")
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()
    return output_file
