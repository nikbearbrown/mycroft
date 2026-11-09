"""Purpose: Step 3 of recipes/what-if-simulation-agent.md: validate the shape of simulation requests before any tool runs.
         The contract is the workflow's own "Parse & Validate Input" node: its defaults and its five rules, with its
         own messages (it shares the rule code with the step-5 port, so the two cannot drift apart). Where this gate
         is stricter, it says so in the audit: numeric fields must be finite.
Input: a folder of request files (default data/raw/what-if-simulation-agent/sample/clean/) and the sample manifest
       beside it (sample mode: step 2, the ingest step, is still open, so this reads the fixture set directly).
Output: <out>/validated.json (record_count, required_fields_present, missing_fields, parse_errors, schema_version,
        plus accepted and rejected records) and <out>/validate-audit.md, a report for human judgment. Default <out>:
        data/verified/what-if-simulation-agent/<clean|defective>/ named after the input folder.
Side effects: writes those two files. No network, no credentials.
Idempotent: Yes; same inputs give the same bytes.
Errors: exit 1 if any request is rejected (the files are still written, so the reasons are kept). Exit 2, nothing
        written, if a fixture no longer matches the SHA-256 the manifest froze for it.
Recipe: recipes/what-if-simulation-agent.md
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

SLUG = "what-if-simulation-agent"
REPO = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "1"
NUMERIC = ("revenue_growth", "sentiment_score", "current_price", "pe_ratio", "debt_equity", "market_cap_billions")
CONTRACT_FIELDS = ("company", "ticker", "revenue_growth", "sentiment_score", "risk_appetite", "time_horizon",
                   "current_price", "pe_ratio", "debt_equity", "market_cap_billions")
RULES = [
    "revenue_growth must be between -1.0 and 20.0",
    "sentiment_score must be 0–1",
    "risk_appetite must be low | medium | high",
    "pe_ratio must be positive",
    "debt_equity must be positive",
]


def load_port():
    """The step-5 port, imported by path (its file name has hyphens). One source of truth for the rules."""
    p = REPO / "scripts" / "tools" / f"{SLUG}-run-approved-tools.py"
    spec = importlib.util.spec_from_file_location("whatif_port", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_manifest(sample_dir: Path, files: list[Path]) -> list[str]:
    manifest = sample_dir.parent / "manifest.json"
    if not manifest.exists():
        return []
    frozen = json.loads(manifest.read_text())["files"]
    problems = []
    for f in files:
        rel = f"{sample_dir.name}/{f.name}"
        if rel in frozen and hashlib.sha256(f.read_bytes()).hexdigest() != frozen[rel]["sha256"]:
            problems.append(f"{rel} changed since the manifest froze it")
    return problems


def judge(path: Path, port) -> dict:
    """One request file -> {'id', 'source', 'accepted': bool, 'reasons': [...], 'request', 'defaulted'}."""
    rec = {"id": path.stem, "source": str(path.relative_to(REPO)) if path.is_relative_to(REPO) else str(path)}
    try:
        req = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return {**rec, "accepted": False, "reasons": [f"does not parse as JSON ({e.__class__.__name__}: {str(e)[:60]})"]}
    if not isinstance(req, dict):
        return {**rec, "accepted": False, "reasons": ["a request must be a JSON object"]}
    parsed, errors = port.parse_input_collect(req)       # the workflow's own defaults and rules
    reasons = list(errors)
    for k in NUMERIC:
        if isinstance(parsed[k], float) and not math.isfinite(parsed[k]):
            reasons.append(f"{k} is not a finite number (the workflow's range checks let it through; this gate does not)")
    body = req.get("body") if port.js_truthy(req.get("body")) else req
    defaulted = [k for k in CONTRACT_FIELDS if body.get(k) is None]
    return {**rec, "accepted": not reasons, "reasons": reasons, "request": req, "defaulted_fields": defaulted}


def audit_md(name: str, results: list[dict], sample_dir: Path) -> str:
    acc = [r for r in results if r["accepted"]]
    rej = [r for r in results if not r["accepted"]]
    lines = [f"# Validate data shape: {SLUG}, `{name}`", "",
             "Written by `scripts/gigo/what-if-simulation-agent-validate-data-shape.py`. This audit says what was found; it does not say pass.", "",
             f"- Folder read: `{sample_dir.relative_to(REPO) if sample_dir.is_relative_to(REPO) else sample_dir}` (sample mode, invented requests)",
             f"- Requests in: {len(results)}; accepted: {len(acc)}; rejected: {len(rej)}",
             "- Contract: the workflow's `Parse & Validate Input` node (defaults, then five rules, same messages). One stated addition: "
             "numeric fields must be finite.",
             "- Open question for the maintainers, not a finding: in JavaScript a value that parses to NaN passes every comparison, so "
             "the node's own rules accept it; this gate rejects it so that no simulation runs on a non-number.", ""]
    if acc:
        lines += ["## Accepted", "", "| Request | Fields filled by the workflow's defaults |", "|---|---|"]
        for r in acc:
            lines.append(f"| `{r['id']}` | {', '.join(r['defaulted_fields']) or 'none'} |")
        lines.append("")
    if rej:
        lines += ["## Rejected", "", "| Request | Reason |", "|---|---|"]
        for r in rej:
            reason = " ; ".join(r["reasons"]).replace("|", "\\|")   # a pipe would split the table cell
            lines.append(f"| `{r['id']}` | {reason} |")
        lines.append("")
    lines += ["## What this audit did not look at", "",
              "- Whether any request describes a real company: every one is invented.",
              "- Anything past the input rules (the simulators run in step 5).", ""]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sample-dir", default=str(REPO / f"data/raw/{SLUG}/sample/clean"))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    sample_dir = Path(args.sample_dir).resolve()
    files = sorted(p for p in sample_dir.iterdir() if p.is_file())
    problems = check_manifest(sample_dir, files)
    if problems:
        print("STOP: " + "; ".join(problems), file=sys.stderr)
        return 2
    port = load_port()
    results = [judge(p, port) for p in files]
    out = Path(args.out) if args.out else REPO / f"data/verified/{SLUG}" / sample_dir.name
    out.mkdir(parents=True, exist_ok=True)
    accepted = [{"id": r["id"], "source": r["source"], "request": r["request"], "defaulted_fields": r["defaulted_fields"]} for r in results if r["accepted"]]
    rejected = [{"id": r["id"], "source": r["source"], "reasons": r["reasons"]} for r in results if not r["accepted"]]
    doc = {"step": "validate-data-shape", "mode": "sample", "schema_version": SCHEMA_VERSION, "record_count": len(results),
           "required_fields_present": True,   # the workflow requires none: every field has a default; missing_fields lists the ones it filled
           "missing_fields": sorted({k for r in results if r["accepted"] for k in r["defaulted_fields"]}),
           "parse_errors": sum(1 for r in results if r["reasons"] and r["reasons"][0].startswith("does not parse")),
           "contract": {"source": "the workflow's Parse & Validate Input node", "required_fields": [], "defaults": "every field has one", "rules": RULES,
                        "addition": "numeric fields must be finite"},
           "accepted": accepted, "rejected": rejected}
    (out / "validated.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    (out / "validate-audit.md").write_text(audit_md(sample_dir.name, results, sample_dir))
    print(f"{sample_dir.name}: {len(results)} in, {len(accepted)} accepted, {len(rejected)} rejected -> {out}")
    return 1 if rejected else 0


if __name__ == "__main__":
    sys.exit(main())
