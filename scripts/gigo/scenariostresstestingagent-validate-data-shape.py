"""Purpose: Step 3 of recipes/scenariostresstestingagent.md: validate the shape of stress-test requests before any tool runs.
         The contract is the workflow's own "Validate Portfolio" node: holdings must exist, every holding needs a ticker,
         weights default to 0 and are rescaled to 1.0 when the total is more than 0.01 away from it. The rule code is the
         step-5 port's, imported, so the two cannot drift apart. ONE stated addition, written into every audit: the gate is
         stricter than the node about weights (finite, non-negative numbers with a positive total), about holdings (a
         non-empty array of objects) and about the scenario (a known template name, or a non-empty custom_scenario string).
Input: a folder of request files (default data/raw/scenariostresstestingagent/sample/clean/) and the sample manifest
       beside it (sample mode: this reads the fixture set directly; step 2, the ingest step, ingests the same fixtures).
Output: <out>/validated.json (record_count, required_fields_present, missing_fields, parse_errors, schema_version,
        plus accepted and rejected records) and <out>/validate-audit.md, a report for human judgment. Default <out>:
        data/verified/scenariostresstestingagent/<clean|defective>/ named after the input folder.
Side effects: writes those two files. No network, no credentials.
Idempotent: Yes; same inputs give the same bytes.
Errors: exit 1 if any request is rejected (the files are still written, so the reasons are kept). Exit 2, nothing
        written, if a fixture no longer matches the SHA-256 the manifest froze for it.
Recipe: recipes/scenariostresstestingagent.md
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

SLUG = "scenariostresstestingagent"
REPO = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "1"
TAG = "(gate addition)"
RULES = [
    "portfolio must have a holdings array (the node's message: Portfolio must have holdings array)",
    "every holding must have a ticker (the node's message: Each holding must have a ticker)",
    "weights default to 0 and are rescaled to 1.0 when the total is more than 0.01 from 1.0",
]
ADDITIONS = [
    "holdings must be a non-empty array of objects",
    "every weight must be present, a finite number, and not negative; the total must be positive",
    "scenario_type, if present, must be one of the five templates; with no custom_scenario and no scenario_type the workflow's default (tech_crash) applies",
    "custom_scenario, if present, must be a string; horizon_days, if present, must be a finite number",
]


def load_port():
    """The step-5 port, imported by path (its file name has hyphens). One source of truth for the node's rules."""
    p = REPO / "scripts" / "tools" / f"{SLUG}-run-approved-tools.py"
    spec = importlib.util.spec_from_file_location("stress_port", p)
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


def _is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def additions_for(item: dict, port) -> list[str]:
    reasons = []
    portfolio = item.get("portfolio")
    holdings = portfolio.get("holdings") if isinstance(portfolio, dict) else None
    if isinstance(holdings, list):
        if len(holdings) == 0:
            reasons.append(f"holdings is empty: nothing to stress-test {TAG}")
        total = 0.0
        usable = True
        for i, h in enumerate(holdings):
            if not isinstance(h, dict):
                reasons.append(f"holding {i} is not an object {TAG}")
                usable = False
                continue
            w = h.get("weight")
            if "weight" not in h or w is None:
                reasons.append(f"holding {i} ({h.get('ticker', 'no ticker')}) has no weight: the node counts it as 0 and the engine then fails on it {TAG}")
                usable = False
            elif not _is_number(w):
                reasons.append(f"holding {i} ({h.get('ticker', 'no ticker')}) has a weight that is not a number ({w!r}): JavaScript would join it as text {TAG}")
                usable = False
            elif not math.isfinite(w):
                reasons.append(f"holding {i} has a weight that is not finite {TAG}")
                usable = False
            elif w < 0:
                reasons.append(f"holding {i} ({h.get('ticker')}) has a negative weight ({w}): the engine would treat it as a short position without saying so {TAG}")
                usable = False
            else:
                total += w
        if usable and holdings and total <= 0:
            reasons.append(f"weights total {total}: rescaling by a zero total gives NaN weights {TAG}")
    elif holdings is not None and portfolio is not None:
        reasons.append(f"holdings is a {type(holdings).__name__}, not an array {TAG}")
    st, cs = item.get("scenario_type"), item.get("custom_scenario")
    if cs is not None and not isinstance(cs, str):
        reasons.append(f"custom_scenario is not a string {TAG}")
    if st is not None and (not isinstance(st, str) or st not in port.TEMPLATES) and not (isinstance(cs, str) and cs != "" and st is None):
        reasons.append(f"scenario_type {st!r} is not one of {sorted(port.TEMPLATES)}: the workflow would silently run {port.DEFAULT_TEMPLATE} {TAG}")
    hd = item.get("horizon_days")
    if hd is not None and (not _is_number(hd) or not math.isfinite(hd)):
        reasons.append(f"horizon_days is not a finite number {TAG}")
    return reasons


def judge(path: Path, port) -> dict:
    """One request file -> {'id', 'source', 'accepted': bool, 'reasons': [...], 'request'}."""
    rec = {"id": path.stem, "source": str(path.relative_to(REPO)) if path.is_relative_to(REPO) else str(path)}
    try:
        req = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return {**rec, "accepted": False, "reasons": [f"does not parse as JSON ({e.__class__.__name__}: {str(e)[:60]})"]}
    if not isinstance(req, dict):
        return {**rec, "accepted": False, "reasons": ["a request must be a JSON object"]}
    if not isinstance(req.get("body"), dict):
        return {**rec, "accepted": False, "reasons": ["the request has no body object (the Edit Fields node reads $json.body.*)"]}
    item = port.edit_fields(req)
    reasons = []
    try:
        port.validate_portfolio(json.loads(json.dumps(item)))      # the node's own rules; it mutates, so use a copy
    except (port.ValidationFailed, port.JSTypeError) as e:
        reasons.append(str(e) + " (the node's own rule)")
    except port.NotModelled:
        pass                                                         # the additions below name the problem
    reasons += additions_for(item, port)
    return {**rec, "accepted": not reasons, "reasons": reasons, "request": req}


def audit_md(name: str, results: list[dict], sample_dir: Path) -> str:
    acc = [r for r in results if r["accepted"]]
    rej = [r for r in results if not r["accepted"]]
    lines = [f"# Validate data shape: {SLUG}, `{name}`", "",
             "Written by `scripts/gigo/scenariostresstestingagent-validate-data-shape.py`. This audit says what was found; it does not say pass.", "",
             f"- Folder read: `{sample_dir.relative_to(REPO) if sample_dir.is_relative_to(REPO) else sample_dir}` (sample mode, invented requests)",
             f"- Requests in: {len(results)}; accepted: {len(acc)}; rejected: {len(rej)}",
             "- Contract: the workflow's `Validate Portfolio` node, with its own two messages.",
             "- **One stated addition**, marked in every reason that comes from it: " + "; ".join(ADDITIONS) + ".",
             "- Open question for the maintainers, not a finding: several requests this gate rejects are ones the workflow itself would run "
             "(a negative weight, an unknown scenario_type, an empty holdings array); the reasons say what the workflow would do.", ""]
    if acc:
        lines += ["## Accepted", "", "| Request | Scenario route |", "|---|---|"]
        for r in acc:
            body = r["request"]["body"]
            cs = body.get("custom_scenario")
            route = "custom scenario: needs the Groq call, recorded as a handoff" if isinstance(cs, str) and cs != "" else f"template `{body.get('scenario_type', 'tech_crash (default)')}`"
            lines.append(f"| `{r['id']}` | {route} |")
        lines.append("")
    if rej:
        lines += ["## Rejected", "", "| Request | Reason |", "|---|---|"]
        for r in rej:
            reason = " ; ".join(r["reasons"]).replace("|", "\\|")   # a pipe would split the table cell
            lines.append(f"| `{r['id']}` | {reason} |")
        lines.append("")
    lines += ["## What this audit did not look at", "",
              "- Whether any portfolio describes a real holding: every one is invented.",
              "- Anything past the input rules (the stress test runs in step 5).",
              "- The five template scenarios' numbers: they are the workflow's own, copied, not judged.", ""]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sample-dir", default=str(REPO / f"data/raw/{SLUG}/sample/clean"))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    sample_dir = Path(args.sample_dir).resolve()
    files = sorted(p for p in sample_dir.iterdir() if p.is_file() and p.suffix == ".json")
    problems = check_manifest(sample_dir, files)
    if problems:
        print("STOP: " + "; ".join(problems), file=sys.stderr)
        return 2
    port = load_port()
    results = [judge(p, port) for p in files]
    out = Path(args.out) if args.out else REPO / f"data/verified/{SLUG}" / sample_dir.name
    out.mkdir(parents=True, exist_ok=True)
    accepted = [{"id": r["id"], "source": r["source"], "request": r["request"]} for r in results if r["accepted"]]
    rejected = [{"id": r["id"], "source": r["source"], "reasons": r["reasons"]} for r in results if not r["accepted"]]
    doc = {"step": "validate-data-shape", "mode": "sample", "schema_version": SCHEMA_VERSION, "record_count": len(results),
           "required_fields_present": all("portfolio" in r["request"]["body"] for r in results if r["accepted"]),
           "missing_fields": sorted({k for r in results if r["accepted"] for k in ("scenario_type", "custom_scenario", "horizon_days") if k not in r["request"]["body"]}),
           "parse_errors": sum(1 for r in results if r["reasons"] and r["reasons"][0].startswith("does not parse")),
           "contract": {"source": "the workflow's Validate Portfolio node", "required_fields": ["portfolio.holdings", "holding.ticker"],
                        "defaults": "weight defaults to 0; weights are rescaled to 1.0 when the total is more than 0.01 from 1.0", "rules": RULES,
                        "addition": ADDITIONS},
           "accepted": accepted, "rejected": rejected}
    (out / "validated.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    (out / "validate-audit.md").write_text(audit_md(sample_dir.name, results, sample_dir))
    print(f"{sample_dir.name}: {len(results)} in, {len(accepted)} accepted, {len(rejected)} rejected -> {out}")
    return 1 if rejected else 0


if __name__ == "__main__":
    sys.exit(main())
