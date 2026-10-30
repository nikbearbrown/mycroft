"""Command-line entry point for the Mycroft Finance Investigator."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

from .agent import InvestigationAgent
from .bundle import build_audit_bundle, verify_audit_bundle
from .evaluation import run_evaluation, write_evaluation_artifacts
from .finance import FinanceData, FinanceEngine
from .orchestration import run_orchestration, write_orchestration_artifacts
from .reporting import write_human_report, write_machine_log
from .reinvestigation import run_reinvestigation, write_reinvestigation_artifacts
from .distribution import write_evaluation as write_distribution
from .coverage import write_check as write_coverage
from .disagreement import append_disagreement
from .freshness import write_assessment as write_freshness
from .materiality import (
    record_approval,
    write_approval_request as write_materiality_request,
)
from .review import record_review_decision, write_review_request
from .scenario import run_scenarios, write_scenario_artifacts
from .trend import run_trend, write_trend_artifacts
from .validation import validate_finance_pack


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RAW = REPO_ROOT / "data/raw/mycroft-finance-investigator"
DEFAULT_VERIFIED = REPO_ROOT / "data/verified/mycroft-finance-investigator"
DEFAULT_SCHEMA = PROJECT_ROOT / "schemas/finance-pack.schema.json"
DEFAULT_CONFIG = PROJECT_ROOT / "config/sample-investigation.json"
DEFAULT_RUN_LOG = REPO_ROOT / "logs/mycroft-finance-investigator-sample-2026-02.json"
DEFAULT_EVALUATION_CASES = PROJECT_ROOT / "evaluations/cases.json"
DEFAULT_SCENARIO_PLAN = PROJECT_ROOT / "config/sample-scenarios.json"
DEFAULT_TREND_PLAN = PROJECT_ROOT / "config/sample-trend.json"
DEFAULT_ROUTING_PLAN = PROJECT_ROOT / "config/sample-routing.json"
DEFAULT_TREND_LOG = REPO_ROOT / "logs/mycroft-finance-investigator-trend-week35.json"
DEFAULT_ROUTING_LOG = REPO_ROOT / "logs/mycroft-finance-investigator-routing-week36.json"
DEFAULT_FOLLOW_UP_REQUEST = PROJECT_ROOT / "config/sample-follow-up-request.json"


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
    print(
        f"validated {sum(result.row_counts.values())} rows across "
        f"{len(result.row_counts)} datasets"
    )
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
    target_log = (
        log_path
        or REPO_ROOT / "logs" / f"mycroft-finance-investigator-{run_id}.json"
    )
    target_report = (
        report_path
        or REPO_ROOT
        / "reports/generated"
        / f"mycroft-finance-investigator-{run_id}.md"
    )
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
    distribution = subparsers.add_parser(
        "distribution-gate",
        help="decide whether a report may leave the system (blocked by default)",
    )
    for flag in ("materiality", "freshness", "coverage-report", "review",
                 "disagreements"):
        distribution.add_argument(f"--{flag}", type=Path, default=None)
    distribution.add_argument("--output", type=Path, required=True)
    coverage = subparsers.add_parser(
        "coverage", help="resolve every evidence reference against the pack"
    )
    coverage.add_argument("--run-log", type=Path, default=DEFAULT_RUN_LOG)
    coverage.add_argument("--verified-dir", type=Path, required=True)
    coverage.add_argument("--output", type=Path, required=True)
    disagree = subparsers.add_parser(
        "record-disagreement",
        help="append a named reviewer's position against an engine finding",
    )
    disagree.add_argument("--run-log", type=Path, default=DEFAULT_RUN_LOG)
    disagree.add_argument("--record", type=Path, required=True)
    disagree.add_argument("--log", type=Path, required=True)
    freshness = subparsers.add_parser(
        "freshness", help="measure arrival lag and shelf age of a verified pack"
    )
    freshness.add_argument("--verified-dir", type=Path, required=True)
    freshness.add_argument("--as-of", required=True, help="YYYY-MM-DD")
    freshness.add_argument("--max-lag-days", type=int, required=True)
    freshness.add_argument("--max-age-days", type=int, required=True)
    freshness.add_argument("--output", type=Path, required=True)
    materiality_request = subparsers.add_parser(
        "materiality-request",
        help="prepare the materiality approval a named human must sign",
    )
    materiality_request.add_argument("--verified-dir", type=Path, required=True)
    materiality_request.add_argument("--entity", required=True)
    materiality_request.add_argument("--period", required=True)
    materiality_request.add_argument("--demo-amount", required=True)
    materiality_request.add_argument("--output", type=Path, required=True)
    record_materiality = subparsers.add_parser(
        "record-materiality",
        help="validate and immutably record a materiality approval",
    )
    record_materiality.add_argument("--request", type=Path, required=True)
    record_materiality.add_argument("--decision", type=Path, required=True)
    record_materiality.add_argument("--output", type=Path, required=True)
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
    evaluate = subparsers.add_parser(
        "evaluate", help="run deterministic planted-discrepancy cases"
    )
    evaluate.add_argument("--cases", type=Path, default=DEFAULT_EVALUATION_CASES)
    evaluate.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW)
    evaluate.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    evaluate.add_argument("--run-log", type=Path, default=DEFAULT_RUN_LOG)
    evaluate.add_argument("--run-id", default="week32-evaluation")
    evaluate.add_argument("--output-log", type=Path, required=True)
    evaluate.add_argument("--output-report", type=Path, required=True)
    scenario = subparsers.add_parser(
        "scenario", help="run deterministic what-if sensitivities"
    )
    scenario.add_argument("--plan", type=Path, default=DEFAULT_SCENARIO_PLAN)
    scenario.add_argument("--verified-dir", type=Path, default=DEFAULT_VERIFIED)
    scenario.add_argument("--run-log", type=Path, default=DEFAULT_RUN_LOG)
    scenario.add_argument("--run-id", default="week33-scenarios")
    scenario.add_argument("--output-log", type=Path, required=True)
    scenario.add_argument("--output-report", type=Path, required=True)
    trend = subparsers.add_parser(
        "trend", help="compare verified monthly investigations"
    )
    trend.add_argument("--plan", type=Path, default=DEFAULT_TREND_PLAN)
    trend.add_argument("--run-id", default="week35-trend")
    trend.add_argument("--output-log", type=Path, required=True)
    trend.add_argument("--output-report", type=Path, required=True)
    orchestrate = subparsers.add_parser(
        "orchestrate", help="route recurring evidence gaps to specialists"
    )
    orchestrate.add_argument("--plan", type=Path, default=DEFAULT_ROUTING_PLAN)
    orchestrate.add_argument("--trend-log", type=Path, default=DEFAULT_TREND_LOG)
    orchestrate.add_argument("--run-id", default="week36-routing")
    orchestrate.add_argument("--output-log", type=Path, required=True)
    orchestrate.add_argument("--output-report", type=Path, required=True)
    follow_up = subparsers.add_parser(
        "follow-up", help="replay and classify requested specialist follow-ups"
    )
    follow_up.add_argument("--request", type=Path, default=DEFAULT_FOLLOW_UP_REQUEST)
    follow_up.add_argument("--source-log", type=Path, default=DEFAULT_ROUTING_LOG)
    follow_up.add_argument("--run-id", default="week37-follow-up")
    follow_up.add_argument("--output-log", type=Path, required=True)
    follow_up.add_argument("--output-report", type=Path, required=True)
    bundle = subparsers.add_parser(
        "bundle", help="package an immutable reviewer handoff"
    )
    bundle.add_argument("--bundle-id", required=True)
    bundle.add_argument("--output-dir", type=Path, required=True)
    verify_bundle = subparsers.add_parser(
        "verify-bundle", help="recompute a packaged audit bundle's hashes"
    )
    verify_bundle.add_argument("--bundle-dir", type=Path, required=True)
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
    if args.command == "distribution-gate":
        result = write_distribution(
            args.output,
            materiality=args.materiality,
            freshness=args.freshness,
            coverage=args.coverage_report,
            review=args.review,
            disagreements=args.disagreements,
        )
        print(f"distribution: {result['status']}")
        for condition in result["conditions"]:
            print(f"  {condition['status']:8} {condition['condition']}: "
                  f"{condition['reason']}")
        print(f"distribution gate: {args.output}")
    if args.command == "coverage":
        report = write_coverage(args.run_log, args.verified_dir, args.output)
        print(f"coverage: {report['references_resolved']}/"
              f"{report['references_checked']} references resolved across "
              f"{report['claims_checked']} claims")
        for problem in report["problems"]:
            print(f"  - {problem['failure']}: {problem['claim']} "
                  f"{problem['reference'] or '(no evidence)'}")
        print(f"coverage report: {args.output}")
    if args.command == "record-disagreement":
        log = append_disagreement(args.record, args.run_log, args.log)
        latest = log["entries"][-1]
        print(f"disagreement: {latest['reviewer']} -> {latest['position']} "
              f"on {latest['claim']}")
        print(f"engine finding unchanged: variance "
              f"{latest['engine_finding'].get('variance')}")
        print(f"disagreement log: {args.log} ({len(log['entries'])} entries)")
    if args.command == "freshness":
        assessment = write_freshness(
            args.verified_dir,
            date.fromisoformat(args.as_of),
            args.max_lag_days,
            args.max_age_days,
            args.output,
        )
        print(f"freshness: {assessment['verdict']} "
              f"(lag {assessment['lag_days']}d, age {assessment['age_days']}d)")
        for reason in assessment["reasons"]:
            print(f"  - {reason}")
        print(f"freshness assessment: {args.output}")
    if args.command == "materiality-request":
        request = write_materiality_request(
            args.verified_dir,
            args.entity,
            args.period,
            Decimal(str(args.demo_amount)),
            args.output,
        )
        print(f"materiality: {request['demo_status']} pending named approval")
        print(f"materiality request: {args.output}")
    if args.command == "record-materiality":
        with args.request.open(encoding="utf-8") as handle:
            request = json.load(handle)
        record = record_approval(args.decision, request, args.output)
        print(f"materiality: {record['materiality_status']} "
              f"at {record['approved_amount']} by {record['approved_by']}")
        print(f"materiality approval: {args.output}")
    if args.command == "review-request":
        request = write_review_request(args.run_log, args.output)
        print(f"review gate: {request['gate_status']}")
        print(f"review request: {args.output}")
    if args.command == "record-review":
        artifact = record_review_decision(args.run_log, args.decision, args.output)
        print(f"review gate: {artifact['gate_status']}")
        print(f"review decision: {args.output}")
    if args.command == "evaluate":
        payload = run_evaluation(
            args.cases,
            args.raw_dir,
            args.schema,
            args.run_log,
            args.run_id,
        )
        write_evaluation_artifacts(payload, args.output_log, args.output_report)
        print(
            f"evaluation: {payload['summary']['matched_count']} / "
            f"{payload['summary']['case_count']} expectations matched"
        )
        print(f"machine scorecard: {args.output_log}")
        print(f"human scorecard: {args.output_report}")
        if payload["summary"]["status"] != "PASS":
            raise SystemExit(1)
    if args.command == "scenario":
        payload = run_scenarios(
            args.plan,
            args.verified_dir,
            args.run_log,
            args.run_id,
        )
        write_scenario_artifacts(payload, args.output_log, args.output_report)
        print(f"scenario baseline EBITDA: {payload['baseline_ebitda']}")
        print(f"scenarios rendered: {payload['scenario_count']}")
        print(f"machine decision pack: {args.output_log}")
        print(f"human decision pack: {args.output_report}")
    if args.command == "trend":
        payload = run_trend(args.plan, args.run_id)
        write_trend_artifacts(payload, args.output_log, args.output_report)
        print(f"historical periods compared: {payload['period_count']}")
        print(
            "recurring material adverse categories: "
            + ", ".join(
                payload["verified_findings"][
                    "recurring_material_adverse_categories"
                ]
            )
        )
        print(f"machine comparison: {args.output_log}")
        print(f"human comparison: {args.output_report}")
    if args.command == "orchestrate":
        payload = run_orchestration(args.plan, args.trend_log, args.run_id)
        write_orchestration_artifacts(payload, args.output_log, args.output_report)
        print(f"specialist tasks: {len(payload['tasks'])}")
        print(
            f"delegations: {payload['supervisor']['delegations_used']} / "
            f"{payload['supervisor']['max_delegations']}"
        )
        print(f"machine routing trace: {args.output_log}")
        print(f"human evidence queue: {args.output_report}")
    if args.command == "follow-up":
        payload = run_reinvestigation(args.request, args.source_log, args.run_id)
        write_reinvestigation_artifacts(
            payload, args.output_log, args.output_report
        )
        print(f"replay status: {payload['replay']['status']}")
        print(
            "follow-up outcomes: "
            f"{payload['summary']['verified_count']} verified, "
            f"{payload['summary']['unsupported_count']} unsupported, "
            f"{payload['summary']['open_count']} open"
        )
        print(f"machine closure log: {args.output_log}")
        print(f"human closure report: {args.output_report}")
    if args.command == "bundle":
        payload = build_audit_bundle(args.bundle_id, args.output_dir)
        print(f"audit bundle: {args.output_dir}")
        print(f"artifacts packaged: {payload['summary']['artifact_count']}")
        print(f"release status: {payload['release_status']}")
    if args.command == "verify-bundle":
        result = verify_audit_bundle(args.bundle_dir)
        print(f"bundle integrity: {result['status']}")
        print(f"manifest SHA-256: {result['manifest_sha256']}")
        print(f"release status: {result['release_status']}")


if __name__ == "__main__":
    main()
