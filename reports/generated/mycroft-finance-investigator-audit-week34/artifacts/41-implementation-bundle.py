"""Build and verify an immutable Finance Investigator audit bundle.

The bundle packages the machine and human views already produced by the
workflow. SHA-256 checks establish file integrity; they are checksums, not a
human signature, attestation, or release decision.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class BundleError(RuntimeError):
    """Raised when bundle inputs or packaged artifacts violate the contract."""


REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class SourceArtifact:
    role: str
    path: Path
    bundled_name: str


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _portable_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _load_json(path: Path, role: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BundleError(f"{role} is not readable JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise BundleError(f"{role} must contain one JSON object")
    return payload


def default_bundle_sources(repo_root: Path = REPO_ROOT) -> list[SourceArtifact]:
    """Return the canonical Week 34 handoff inventory in stable order."""

    project = repo_root / "projects/Mycroft-Finance-Investigator"
    raw = repo_root / "data/raw/mycroft-finance-investigator"
    verified = repo_root / "data/verified/mycroft-finance-investigator"
    package = project / "mycroft_finance_investigator"
    specs: list[tuple[str, Path, str]] = [
        ("raw_readme", raw / "README.md", "raw-readme.md"),
        ("raw_provenance", raw / "provenance.json", "raw-provenance.json"),
    ]
    for file_name in (
        "account_mapping.csv",
        "budget.csv",
        "actuals.csv",
        "ledger.csv",
        "customers.csv",
        "headcount.csv",
    ):
        label = file_name.removesuffix(".csv").replace("_", "-")
        specs.append((f"raw_{label}", raw / file_name, f"raw-{label}.csv"))
    for file_name in (
        "account_mapping.csv",
        "budget.csv",
        "actuals.csv",
        "ledger.csv",
        "customers.csv",
        "headcount.csv",
    ):
        label = file_name.removesuffix(".csv").replace("_", "-")
        specs.append(
            (f"verified_{label}", verified / file_name, f"verified-{label}.csv")
        )
    specs.extend(
        [
            (
                "verified_provenance",
                verified / "provenance.json",
                "verified-provenance.json",
            ),
            (
                "validation_result",
                verified / "validation-result.json",
                "validation-result.json",
            ),
            (
                "validation_audit",
                verified / "validation-audit.md",
                "validation-audit.md",
            ),
            (
                "investigation_config",
                project / "config/sample-investigation.json",
                "investigation-config.json",
            ),
            (
                "investigation_log",
                repo_root / "logs/mycroft-finance-investigator-sample-2026-02.json",
                "investigation-log.json",
            ),
            (
                "investigation_report",
                repo_root
                / "reports/generated/mycroft-finance-investigator-sample-2026-02.md",
                "investigation-report.md",
            ),
            (
                "review_request",
                repo_root
                / "logs/gate-decisions"
                / "mycroft-finance-investigator-sample-2026-02-review-request.json",
                "open-review-request.json",
            ),
            (
                "evaluation_cases",
                project / "evaluations/cases.json",
                "evaluation-cases.json",
            ),
            (
                "evaluation_log",
                repo_root / "logs/mycroft-finance-investigator-evaluation-week32.json",
                "evaluation-log.json",
            ),
            (
                "evaluation_report",
                repo_root
                / "reports/generated/mycroft-finance-investigator-evaluation-week32.md",
                "evaluation-report.md",
            ),
            (
                "scenario_plan",
                project / "config/sample-scenarios.json",
                "scenario-plan.json",
            ),
            (
                "scenario_log",
                repo_root / "logs/mycroft-finance-investigator-scenarios-week33.json",
                "scenario-log.json",
            ),
            (
                "scenario_report",
                repo_root
                / "reports/generated/mycroft-finance-investigator-scenarios-week33.md",
                "scenario-report.md",
            ),
            (
                "recipe",
                repo_root / "recipes/mycroft-finance-investigator.md",
                "recipe.md",
            ),
            (
                "conductor",
                repo_root / "conductor/mycroft-finance-investigator.md",
                "conductor.md",
            ),
            ("project_readme", project / "README.md", "project-readme.md"),
            ("project_contract", project / "MYCROFT.md", "project-contract.md"),
            ("package_metadata", project / "pyproject.toml", "pyproject.toml"),
        ]
    )
    for module_name in (
        "__init__.py",
        "validation.py",
        "finance.py",
        "agent.py",
        "reporting.py",
        "review.py",
        "evaluation.py",
        "scenario.py",
        "bundle.py",
        "cli.py",
    ):
        role = f"implementation_{module_name.removesuffix('.py').strip('_')}"
        specs.append((role, package / module_name, f"implementation-{module_name}"))
    for schema_name in (
        "finance-pack.schema.json",
        "review-decision.schema.json",
        "evaluation-cases.schema.json",
        "scenario-plan.schema.json",
        "audit-bundle.schema.json",
    ):
        role = f"schema_{schema_name.removesuffix('.schema.json')}"
        specs.append((role, project / "schemas" / schema_name, schema_name))
    for test_name in (
        "test_validation.py",
        "test_finance.py",
        "test_agent.py",
        "test_review.py",
        "test_evaluation.py",
        "test_scenario.py",
        "test_bundle.py",
    ):
        role = f"test_{test_name.removeprefix('test_').removesuffix('.py')}"
        specs.append((role, project / "tests" / test_name, test_name))
    return [
        SourceArtifact(role, path, f"{index:02d}-{name}")
        for index, (role, path, name) in enumerate(specs, start=1)
    ]


def _source_map(sources: list[SourceArtifact]) -> dict[str, SourceArtifact]:
    by_role: dict[str, SourceArtifact] = {}
    names: set[str] = set()
    for source in sources:
        if source.role in by_role:
            raise BundleError(f"duplicate bundle role: {source.role}")
        if source.bundled_name in names:
            raise BundleError(f"duplicate bundled filename: {source.bundled_name}")
        if not source.path.is_file():
            raise BundleError(f"required bundle source is missing: {source.path}")
        by_role[source.role] = source
        names.add(source.bundled_name)
    required = {
        "raw_provenance",
        "validation_result",
        "validation_audit",
        "investigation_config",
        "investigation_log",
        "investigation_report",
        "review_request",
        "evaluation_cases",
        "evaluation_log",
        "evaluation_report",
        "scenario_plan",
        "scenario_log",
        "scenario_report",
        "recipe",
        "conductor",
    }
    missing = sorted(required - set(by_role))
    if missing:
        raise BundleError(f"bundle inventory is missing roles: {missing}")
    return by_role


def _validate_cross_artifact_contract(
    by_role: dict[str, SourceArtifact],
) -> tuple[str, list[dict[str, str]], list[str]]:
    run_path = by_role["investigation_log"].path
    run_log = _load_json(run_path, "investigation_log")
    if run_log.get("workflow") != "mycroft-finance-investigator":
        raise BundleError("investigation log belongs to a different workflow")
    run_id = run_log.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise BundleError("investigation log is missing run_id")
    investigation = run_log.get("investigation")
    if not isinstance(investigation, dict):
        raise BundleError("investigation log is missing investigation")
    if investigation.get("status") != "COMPLETED_PENDING_HUMAN_REVIEW":
        raise BundleError("investigation is not complete and pending human review")
    human_gate = investigation.get("human_gate")
    if not isinstance(human_gate, dict) or human_gate.get("status") != "OPEN":
        raise BundleError("investigation must retain an open human gate")

    validation = _load_json(by_role["validation_result"].path, "validation_result")
    if validation.get("status") != "CONFORMANT_SAMPLE":
        raise BundleError("validation result is not a conformant sample")
    if run_log.get("validation") != validation:
        raise BundleError("standalone validation result differs from investigation log")

    review = _load_json(by_role["review_request"].path, "review_request")
    if review.get("run_id") != run_id:
        raise BundleError("review request does not match the investigation run_id")
    if review.get("source_run_sha256") != _sha256(run_path):
        raise BundleError("review request hash does not match the investigation log")
    if review.get("gate_status") != "OPEN" or review.get("decision") != "":
        raise BundleError("sample review request must remain open and undecided")

    evaluation = _load_json(by_role["evaluation_log"].path, "evaluation_log")
    if evaluation.get("workflow") != "mycroft-finance-investigator-evaluation":
        raise BundleError("evaluation log belongs to a different workflow")
    summary = evaluation.get("summary")
    if not isinstance(summary, dict) or summary.get("status") != "PASS":
        raise BundleError("evaluation contains unexpected results")
    if summary.get("matched_count") != summary.get("case_count"):
        raise BundleError("evaluation did not match every named expectation")
    cases_path = by_role["evaluation_cases"].path
    if evaluation.get("source_cases_sha256") != _sha256(cases_path):
        raise BundleError("evaluation case hash does not match its specification")
    if evaluation.get("adequacy") != "PENDING_HUMAN_REVIEW":
        raise BundleError("evaluation adequacy boundary is missing")

    raw_dir = by_role["raw_provenance"].path.parent
    expected_raw_hashes = evaluation.get("source_data_sha256")
    if not isinstance(expected_raw_hashes, dict):
        raise BundleError("evaluation log is missing raw source hashes")
    for file_name, expected_hash in expected_raw_hashes.items():
        source_path = raw_dir / file_name
        if not source_path.is_file() or _sha256(source_path) != expected_hash:
            raise BundleError(f"raw source hash mismatch: {file_name}")

    scenario = _load_json(by_role["scenario_log"].path, "scenario_log")
    if scenario.get("workflow") != "mycroft-finance-investigator-scenarios":
        raise BundleError("scenario log belongs to a different workflow")
    if scenario.get("baseline_run_id") != run_id:
        raise BundleError("scenario log does not match the investigation run_id")
    if scenario.get("baseline_run_sha256") != _sha256(run_path):
        raise BundleError("scenario baseline hash does not match the investigation log")
    scenario_plan_path = by_role["scenario_plan"].path
    if scenario.get("source_plan_sha256") != _sha256(scenario_plan_path):
        raise BundleError("scenario plan hash does not match its specification")
    if scenario.get("classification") != "SIMULATION_NOT_FORECAST":
        raise BundleError("scenario classification boundary is missing")
    if scenario.get("recommendation") is not None:
        raise BundleError("scenario output must not contain a recommendation")
    if scenario.get("decision") != "HUMAN_REQUIRED":
        raise BundleError("scenario output must retain a human decision")

    verified_dir = by_role["validation_result"].path.parent
    verified_hashes = scenario.get("verified_data_sha256")
    if not isinstance(verified_hashes, dict):
        raise BundleError("scenario log is missing verified source hashes")
    for file_name, expected_hash in verified_hashes.items():
        source_path = verified_dir / file_name
        if not source_path.is_file() or _sha256(source_path) != expected_hash:
            raise BundleError(f"verified source hash mismatch: {file_name}")

    recipe_text = by_role["recipe"].path.read_text(encoding="utf-8")
    if "status: DRAFT" not in recipe_text.split("---", 2)[1]:
        raise BundleError("recipe must remain DRAFT while human gates are open")

    checks = [
        {
            "name": "baseline-run",
            "status": "MATCHED",
            "observed": f"{run_id} is complete with human gate OPEN",
        },
        {
            "name": "validation-lineage",
            "status": "MATCHED",
            "observed": "standalone validation equals the run-log validation",
        },
        {
            "name": "review-binding",
            "status": "MATCHED",
            "observed": "review request run ID and SHA-256 match the baseline",
        },
        {
            "name": "evaluation-observations",
            "status": "MATCHED",
            "observed": (
                f"{summary['matched_count']} of {summary['case_count']} named "
                "expectations matched"
            ),
        },
        {
            "name": "scenario-binding",
            "status": "MATCHED",
            "observed": "scenario plan, baseline run, and verified data hashes match",
        },
        {
            "name": "judgment-boundary",
            "status": "PRESERVED",
            "observed": "recipe DRAFT; no recommendation; human gate OPEN",
        },
    ]
    open_gates = [
        "Named finance owner has not approved or replaced demo materiality.",
        "Named finance reviewer has not supplied an evidence-backed causal explanation.",
        "A human has not judged the seven-case evaluation set adequate for production use.",
        "Scenario assumptions are synthetic exercises, not approved forecasts or plans.",
        "Distribution has not been authorized by a named human.",
    ]
    return run_id, checks, open_gates


def _write_review(
    path: Path, manifest: dict[str, Any], manifest_digest: str
) -> None:
    summary = manifest["summary"]
    lines = [
        "# Finance Investigator Audit Bundle",
        "",
        f"- Bundle: `{manifest['bundle_id']}`",
        f"- Baseline run: `{manifest['baseline_run_id']}`",
        f"- Packaged artifacts: {summary['artifact_count']}",
        f"- Integrity manifest SHA-256: `{manifest_digest}`",
        "- Machine integrity: `MATCHED`",
        "- Recipe status: `DRAFT`",
        "- Release status: `BLOCKED_PENDING_HUMAN_REVIEW`",
        "",
        (
            "The SHA-256 file is an integrity checksum, not a digital signature, "
            "human attestation, or release approval."
        ),
        "",
        "## Machine Observations",
        "",
        "| Check | Status | Observed |",
        "|---|---|---|",
    ]
    for check in manifest["checks"]:
        lines.append(
            f"| {check['name']} | `{check['status']}` | {check['observed']} |"
        )
    lines.extend(["", "## Packaged Artifact Inventory", ""])
    lines.extend(
        [
            "| Role | Bundled path | Bytes | SHA-256 |",
            "|---|---|---:|---|",
        ]
    )
    for artifact in manifest["artifacts"]:
        lines.append(
            f"| {artifact['role']} | `{artifact['bundled_path']}` | "
            f"{artifact['bytes']} | `{artifact['sha256']}` |"
        )
    lines.extend(["", "## Open Human Gates", ""])
    lines.extend(f"- {item}" for item in manifest["open_human_gates"])
    lines.extend(
        [
            "",
            "## Reviewer Handoff",
            "",
            "- [ ] Confirm the manifest checksum from a trusted location.",
            "- [ ] Read the validation and evaluation audits; judge test adequacy.",
            "- [ ] Approve or replace the demo materiality policy with reasoning.",
            "- [ ] Supply causal explanations supported by evidence from the exact run.",
            "- [ ] Approve, request changes, or block the scenario assumptions.",
            "- [ ] Record the named human distribution decision separately.",
            "",
            "## Did Not Establish",
            "",
            (
                "This bundle does not establish production fitness, business "
                "causation, forecast likelihood, scenario preference, or "
                "permission to distribute."
            ),
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def build_audit_bundle(
    bundle_id: str,
    output_dir: Path,
    sources: list[SourceArtifact] | None = None,
) -> dict[str, Any]:
    """Validate, package, and checksum a new immutable audit bundle."""

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", bundle_id):
        raise BundleError(
            "bundle_id must start with an alphanumeric character and contain "
            "only letters, numbers, periods, underscores, or hyphens"
        )
    if output_dir.exists():
        raise BundleError(f"audit bundle already exists: {output_dir}")
    selected = sources or default_bundle_sources()
    by_role = _source_map(selected)
    baseline_run_id, checks, open_gates = _validate_cross_artifact_contract(by_role)

    artifacts = []
    for source in selected:
        artifacts.append(
            {
                "role": source.role,
                "source_path": _portable_path(source.path),
                "bundled_path": f"artifacts/{source.bundled_name}",
                "bytes": source.path.stat().st_size,
                "sha256": _sha256(source.path),
            }
        )
    manifest = {
        "schema_version": "0.1.0",
        "workflow": "mycroft-finance-investigator-audit-bundle",
        "bundle_id": bundle_id,
        "baseline_run_id": baseline_run_id,
        "release_status": "BLOCKED_PENDING_HUMAN_REVIEW",
        "integrity_algorithm": "SHA-256",
        "summary": {
            "artifact_count": len(artifacts),
            "machine_check_count": len(checks),
            "open_human_gate_count": len(open_gates),
        },
        "checks": checks,
        "open_human_gates": open_gates,
        "artifacts": artifacts,
        "human_attestation": None,
    }

    artifact_dir = output_dir / "artifacts"
    artifact_dir.mkdir(parents=True)
    for source in selected:
        shutil.copyfile(source.path, artifact_dir / source.bundled_name)
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    manifest_digest = _sha256(manifest_path)
    review_path = output_dir / "REVIEW.md"
    _write_review(review_path, manifest, manifest_digest)
    review_digest = _sha256(review_path)
    (output_dir / "manifest.sha256").write_text(
        (
            f"{manifest_digest}  manifest.json\n"
            f"{review_digest}  REVIEW.md\n"
        ),
        encoding="utf-8",
    )
    return manifest


def verify_audit_bundle(bundle_dir: Path) -> dict[str, Any]:
    """Recompute all packaged hashes and reject any changed artifact."""

    manifest_path = bundle_dir / "manifest.json"
    checksum_path = bundle_dir / "manifest.sha256"
    manifest = _load_json(manifest_path, "bundle manifest")
    try:
        checksum_lines = checksum_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise BundleError(f"bundle checksum is missing: {checksum_path}") from exc
    checksums: dict[str, str] = {}
    for line in checksum_lines:
        parts = line.split()
        if len(parts) != 2:
            raise BundleError("manifest.sha256 has an invalid format")
        checksums[parts[1]] = parts[0]
    if set(checksums) != {"manifest.json", "REVIEW.md"}:
        raise BundleError("manifest.sha256 has an invalid format")
    observed_manifest_hash = _sha256(manifest_path)
    if checksums["manifest.json"] != observed_manifest_hash:
        raise BundleError("manifest checksum does not match manifest.json")
    review_path = bundle_dir / "REVIEW.md"
    if not review_path.is_file() or checksums["REVIEW.md"] != _sha256(review_path):
        raise BundleError("review checksum does not match REVIEW.md")

    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise BundleError("bundle manifest has no artifact inventory")
    roles: set[str] = set()
    paths: set[str] = set()
    bundle_root = bundle_dir.resolve()
    artifact_root = (bundle_root / "artifacts").resolve()
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            raise BundleError(f"artifacts[{index}] must be an object")
        bundled_path = artifact.get("bundled_path")
        if not isinstance(bundled_path, str) or not bundled_path.startswith("artifacts/"):
            raise BundleError(f"artifacts[{index}] has an invalid bundled path")
        role = artifact.get("role")
        if not isinstance(role, str) or not role or role in roles:
            raise BundleError(f"artifacts[{index}] has an invalid or duplicate role")
        if bundled_path in paths:
            raise BundleError(f"artifacts[{index}] has a duplicate bundled path")
        roles.add(role)
        paths.add(bundled_path)
        path = (bundle_dir / bundled_path).resolve()
        try:
            path.relative_to(artifact_root)
        except ValueError as exc:
            raise BundleError(
                f"bundled artifact escapes the artifact directory: {bundled_path}"
            ) from exc
        if not path.is_file():
            raise BundleError(f"bundled artifact is missing: {bundled_path}")
        if path.stat().st_size != artifact.get("bytes"):
            raise BundleError(f"bundled artifact size mismatch: {bundled_path}")
        if _sha256(path) != artifact.get("sha256"):
            raise BundleError(f"bundled artifact hash mismatch: {bundled_path}")
    observed_paths = {
        str(path.relative_to(bundle_root))
        for path in artifact_root.rglob("*")
        if path.is_file()
    }
    if observed_paths != paths:
        unexpected = sorted(observed_paths - paths)
        missing = sorted(paths - observed_paths)
        raise BundleError(
            f"bundle inventory mismatch; unexpected={unexpected}, missing={missing}"
        )
    return {
        "bundle_id": manifest.get("bundle_id"),
        "status": "INTEGRITY_MATCHED_HUMAN_REVIEW_OPEN",
        "manifest_sha256": observed_manifest_hash,
        "artifact_count": len(artifacts),
        "release_status": manifest.get("release_status"),
    }
