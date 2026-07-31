"""Command-line entry point for the Mycroft Finance Investigator."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from .agent import InvestigationAgent
from .finance import FinanceData, FinanceEngine
from .reporting import write_human_report, write_machine_log
from .review import record_review_decision, write_review_request
from .validation import validate_finance_pack


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RAW = REPO_ROOT / "data/raw/mycroft-finance-investigator"
DEFAULT_VERIFIED = REPO_ROOT / "data/verified/mycroft-finance-investigator"
DEFAULT_SCHEMA = PROJECT_ROOT / "schemas/finance-pack.schema.json"
DEFAULT_CONFIG = PROJECT_ROOT / "config/sample-investigation.json"
DEFAULT_RUN_LOG = REPO_ROOT / "logs/mycroft-finance-investigator-sample-2026-02.json"


def _run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_config(path: Path) -> dict[str, str | int]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validation_payload(verified_dir: Path) -> dict[str, object]:
    return json.loads(
        (verified_dir / "validation-result.json").read_text(encoding="utf-8")
    )


def run_validation(raw_dir: Path, verified_dir: Path, schema: Path) -> dict[str, object]:
    result = validate_finance_pack(raw_dir, verified_dir, schema)
    print(f"validated {sum(result.row_counts.values())} rows across {len(result.row_counts)} datasets")
    print(f"verified sample: {verified_dir}")
    return result.to_dict()


def run_investigation(
    verified_dir: Path,
    config_path: Path,
    run_id: str,
    log_path: Path | None = None,
    report_path: Path | None = None,
) -> dict[str, object]:
    config = _load_config(config_path)
    data = FinanceData(verified_dir)
    engine = FinanceEngine(data)
    agent = InvestigationAgent(engine, max_steps=int(config["max_agent_steps"]))
    investigation = agent.run(
        question=str(config["question"]),
        threshold=Decimal(str(config["materiality_amount"])),
    )
    target_log = log_path or REPO_ROOT / "logs" / f"mycroft-finance-investigator-{run_id}.json"
    target_report = report_path or REPO_ROOT / "reports/generated" / f"mycroft-finance-investigator-{run_id}.md"
    write_machine_log(
        target_log,
        run_id,
        "0.1.0",
        config,
        _validation_payload(verified_dir),
        investigation,
    )
    write_human_report(target_report, run_id, config, investigation)
    print(f"investigation status: {investigation['status']}")
    print(f"machine log: {target_log}")
    print(f"human report: {target_report}")
    return investigation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "investigate", "all"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW)
        sub.add_argument("--verified-dir", type=Path, default=DEFAULT_VERIFIED)
        sub.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
        sub.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
        sub.add_argument("--run-id", default=None)
        sub.add_argument("--log-path", type=Path, default=None)
        sub.add_argument("--report-path", type=Path, default=None)
    review_request = subparsers.add_parser(
        "review-request", help="create an open human-review request"
    )
    review_request.add_argument("--run-log", type=Path, default=DEFAULT_RUN_LOG)
    review_request.add_argument("--output", type=Path, required=True)
    record_review = subparsers.add_parser(
        "record-review", help="validate and immutably record a human decision"
    )
    record_review.add_argument("--run-log", type=Path, default=DEFAULT_RUN_LOG)
    record_review.add_argument("--decision", type=Path, required=True)
    record_review.add_argument("--output", type=Path, required=True)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command in {"validate", "all"}:
        run_validation(args.raw_dir, args.verified_dir, args.schema)
    if args.command in {"investigate", "all"}:
        run_investigation(
            args.verified_dir,
            args.config,
            args.run_id or _run_id(),
            args.log_path,
            args.report_path,
        )
    if args.command == "review-request":
        request = write_review_request(args.run_log, args.output)
        print(f"review gate: {request['gate_status']}")
        print(f"review request: {args.output}")
    if args.command == "record-review":
        artifact = record_review_decision(args.run_log, args.decision, args.output)
        print(f"review gate: {artifact['gate_status']}")
        print(f"review decision: {args.output}")


if __name__ == "__main__":
    main()
