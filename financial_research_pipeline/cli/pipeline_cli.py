from __future__ import annotations

import argparse
import json
from pathlib import Path

from financial_research_pipeline.main import (
    run_analyze,
    run_fetch,
    run_full_pipeline,
    run_load,
    run_process,
    run_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Financial research pipeline CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("fetch", help="Fetch market and macro data")
    subparsers.add_parser("process", help="Fetch and process market data")
    subparsers.add_parser("load", help="Fetch/process and load data to database")
    subparsers.add_parser("analyze", help="Run analytics and output summary")
    subparsers.add_parser("report", help="Generate charts and PDF report")
    subparsers.add_parser("run-all", help="Run complete end-to-end pipeline")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "fetch":
        outputs = run_fetch()
    elif args.command == "process":
        outputs = run_process()
    elif args.command == "load":
        outputs = run_load()
    elif args.command == "analyze":
        outputs = run_analyze()
    elif args.command == "report":
        outputs = run_report()
    elif args.command == "run-all":
        outputs = run_full_pipeline()
    else:
        parser.error("Unknown command")
        return

    serializable = {key: str(value) if isinstance(value, Path) else value for key, value in outputs.items()}
    print(json.dumps(serializable, indent=2, default=str))


if __name__ == "__main__":
    main()
