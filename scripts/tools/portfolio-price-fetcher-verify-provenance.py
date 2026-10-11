"""Purpose: Step 1 of recipes/portfolio-price-fetcher.md: verify that the run rests on the declared source.
Input: the recipe (its node table and its "Original workflow JSON" input), that workflow JSON, the sample
       fixture manifest, and the approval record at logs/gate-decisions/portfolio-price-fetcher-approval.json.
Output: logs/portfolio-price-fetcher-provenance-<YYYY-MM-DD>.json with workflow, source_paths, exists,
        parsed_ok, approval_state, checked_at (the recipe's step-1 fields) plus node_table_match,
        portfolio_consistent, fixtures_ok and findings.
Side effects: writes that one JSON file. No network, no credentials.
Idempotent: Yes; same inputs give the same record except checked_at (pin it with --now).
Errors: exit 1 if the workflow is missing or unparseable, if its nodes differ from the recipe's node table,
        if the portfolio is defined differently in the two nodes that each define it, or if a fixture no
        longer matches the SHA-256 frozen in the manifest. The record is still written, so the reason is kept.
Recipe: recipes/portfolio-price-fetcher.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SLUG = "portfolio-price-fetcher"
REPO = Path(__file__).resolve().parents[2]


def recipe_sources(recipe_text: str) -> tuple[str | None, list[tuple[str, str]]]:
    """(declared workflow path, [(node name, node type)]) read from the recipe's own tables."""
    m = re.search(r"^\| Original workflow JSON \| JSON \| `([^`]+)` \|", recipe_text, re.M)
    nodes, in_table = [], False
    for line in recipe_text.splitlines():
        if line.startswith("| Node Name | Node Type | Classification |"):
            in_table = True
            continue
        if in_table:
            if line.startswith("|---"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not line.startswith("|") or len(cells) < 2:
                break
            nodes.append((cells[0], cells[1].strip("`")))
    return (m.group(1) if m else None), nodes


def portfolio_from_define_node(code: str) -> dict[str, tuple[float, float]]:
    """{ticker: (shares, buyPrice)} from the Define Portfolio node's array literal."""
    rows = re.findall(r"ticker:\s*'([^']+)',\s*shares:\s*([\d.]+),\s*buyPrice:\s*([\d.]+)", code)
    return {t: (float(s), float(b)) for t, s, b in rows}


def portfolio_from_metrics_node(code: str) -> dict[str, tuple[float, float]]:
    """{ticker: (shares, buyPrice)} from the Calculate Metrics node's object literal."""
    rows = re.findall(r"'([^']+)':\s*\{\s*shares:\s*([\d.]+),\s*buyPrice:\s*([\d.]+)\s*\}", code)
    return {t: (float(s), float(b)) for t, s, b in rows}


def check_fixtures(sample_dir: Path) -> tuple[bool | None, list[str]]:
    manifest = sample_dir / "manifest.json"
    if not manifest.exists():
        return None, ["no fixture manifest (sample corpus not present)"]
    problems = []
    for rel, meta in json.loads(manifest.read_text())["files"].items():
        p = sample_dir / rel
        if not p.exists():
            problems.append(f"fixture missing: {rel}")
        elif hashlib.sha256(p.read_bytes()).hexdigest() != meta["sha256"]:
            problems.append(f"fixture changed since the manifest froze it: {rel}")
    return not problems, problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--recipe", default=str(REPO / "recipes" / f"{SLUG}.md"))
    ap.add_argument("--workflow", help="override the workflow path the recipe declares (tests only)")
    ap.add_argument("--sample-dir", default=str(REPO / "data" / "raw" / SLUG / "sample"))
    ap.add_argument("--out-dir", default=str(REPO / "logs"))
    ap.add_argument("--now", help="ISO-8601 timestamp for checked_at (reproducible runs)")
    a = ap.parse_args()

    now = a.now or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    findings: list[str] = []
    declared, table = recipe_sources(Path(a.recipe).read_text())
    wf_rel = a.workflow or declared
    if not wf_rel:
        findings.append("the recipe declares no 'Original workflow JSON' input")
    wf_path = (REPO / wf_rel) if wf_rel and not Path(wf_rel).is_absolute() else Path(wf_rel or "")
    exists = bool(wf_rel) and wf_path.is_file()
    parsed_ok, wf = False, {}
    if exists:
        try:
            wf = json.loads(wf_path.read_text())
            parsed_ok = isinstance(wf.get("nodes"), list)
        except json.JSONDecodeError as e:
            findings.append(f"workflow JSON does not parse: {e}")
    elif wf_rel:
        findings.append(f"declared workflow not found: {wf_rel}")

    node_table_match, portfolio_consistent = False, False
    if parsed_ok:
        actual = [(n.get("name", ""), n.get("type", "").split(".")[-1]) for n in wf["nodes"]]
        node_table_match = sorted(actual) == sorted(table)
        for name, typ in sorted(set(table) - set(actual)):
            findings.append(f"in the recipe's node table but not the workflow: {name} ({typ})")
        for name, typ in sorted(set(actual) - set(table)):
            findings.append(f"in the workflow but not the recipe's node table: {name} ({typ})")
        code = {n.get("name"): (n.get("parameters") or {}).get("jsCode", "") for n in wf["nodes"]}
        defined = portfolio_from_define_node(code.get("Define Portfolio", ""))
        looked_up = portfolio_from_metrics_node(code.get("Calculate Metrics", ""))
        portfolio_consistent = bool(defined) and defined == looked_up
        if not portfolio_consistent:
            findings.append(f"the portfolio differs between Define Portfolio {defined} and Calculate Metrics {looked_up}")

    fixtures_ok, fixture_problems = check_fixtures(Path(a.sample_dir))
    findings += fixture_problems if fixtures_ok is False else []

    approval_file = REPO / "logs" / "gate-decisions" / f"{SLUG}-approval.json"
    if approval_file.exists():
        rec = json.loads(approval_file.read_text())
        approval_state = f"{rec.get('decision', 'recorded')} ({approval_file.relative_to(REPO)})"
    else:
        approval_state = "no approval record: live mode not approved; sample mode only"

    record: dict[str, Any] = {
        "workflow": wf.get("name") if parsed_ok else None,
        "source_paths": [p for p in [wf_rel, str(Path(a.recipe).relative_to(REPO)) if Path(a.recipe).is_relative_to(REPO) else a.recipe] if p],
        "exists": exists,
        "parsed_ok": parsed_ok,
        "approval_state": approval_state,
        "checked_at": now,
        "node_table_match": node_table_match,
        "portfolio_consistent": portfolio_consistent,
        "fixtures_ok": fixtures_ok,
        "findings": findings,
        "result": "pass" if (exists and parsed_ok and node_table_match and portfolio_consistent
                             and fixtures_ok is not False) else "stop",
    }
    out = Path(a.out_dir) / f"{SLUG}-provenance-{now[:10]}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=1) + "\n")
    print(f"step 1 {record['result']}: {out.relative_to(REPO) if out.is_relative_to(REPO) else out}")
    for f in findings:
        print(f"  - {f}")
    return 0 if record["result"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
