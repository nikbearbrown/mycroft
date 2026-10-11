"""Purpose: Step 1 of recipes/portfolio-dashboard.md: verify that the run rests on the declared source.
Input: the recipe (its node table and its "Original workflow JSON" input), that workflow JSON, the workflow
       of the recipe it calls (recipes/portfolio-price-fetcher.md's declared workflow), and the approval
       record at logs/gate-decisions/portfolio-dashboard-approval.json.
Output: logs/portfolio-dashboard-provenance-<YYYY-MM-DD>.json with workflow, source_paths, exists, parsed_ok,
        approval_state, checked_at (the recipe's step-1 fields) plus node_table_match, calls_price_fetcher
        and findings.
Side effects: writes that one JSON file. No network, no credentials.
Idempotent: Yes; same inputs give the same record except checked_at (pin it with --now).
Errors: exit 1 if the workflow is missing or unparseable, if its nodes differ from the recipe's node table,
        or if its "Call Portfolio Price Fetcher" node does not name the Portfolio Price Fetcher workflow.
        The record is still written, so the reason is kept.
Recipe: recipes/portfolio-dashboard.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SLUG = "portfolio-dashboard"
CALLED_SLUG = "portfolio-price-fetcher"
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


def load_workflow(rel: str | None) -> tuple[bool, bool, dict[str, Any], list[str]]:
    """(exists, parsed_ok, workflow, findings) for a repo-relative workflow path."""
    if not rel:
        return False, False, {}, ["no 'Original workflow JSON' input is declared"]
    p = REPO / rel if not Path(rel).is_absolute() else Path(rel)
    if not p.is_file():
        return False, False, {}, [f"declared workflow not found: {rel}"]
    try:
        wf = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        return True, False, {}, [f"workflow JSON does not parse ({rel}): {e}"]
    return True, isinstance(wf.get("nodes"), list), wf, []


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--recipe", default=str(REPO / "recipes" / f"{SLUG}.md"))
    ap.add_argument("--called-recipe", default=str(REPO / "recipes" / f"{CALLED_SLUG}.md"))
    ap.add_argument("--workflow", help="override the workflow path the recipe declares (tests only)")
    ap.add_argument("--out-dir", default=str(REPO / "logs"))
    ap.add_argument("--now", help="ISO-8601 timestamp for checked_at (reproducible runs)")
    a = ap.parse_args()

    now = a.now or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    declared, table = recipe_sources(Path(a.recipe).read_text())
    wf_rel = a.workflow or declared
    exists, parsed_ok, wf, findings = load_workflow(wf_rel)

    node_table_match, calls_price_fetcher = False, False
    if parsed_ok:
        actual = [(n.get("name", ""), n.get("type", "").split(".")[-1]) for n in wf["nodes"]]
        node_table_match = sorted(actual) == sorted(table)
        for name, typ in sorted(set(table) - set(actual)):
            findings.append(f"in the recipe's node table but not the workflow: {name} ({typ})")
        for name, typ in sorted(set(actual) - set(table)):
            findings.append(f"in the workflow but not the recipe's node table: {name} ({typ})")

        # the sub-workflow call: which workflow does it name, and does that match the called recipe's source?
        called_rel, _ = recipe_sources(Path(a.called_recipe).read_text())
        c_exists, c_parsed, called_wf, c_findings = load_workflow(called_rel)
        findings += c_findings
        calls = [n for n in wf["nodes"] if n.get("type", "").endswith("executeWorkflow")]
        if not calls:
            findings.append("no executeWorkflow node: the dashboard does not call another workflow")
        for n in calls:
            ref = (n.get("parameters") or {}).get("workflowId") or {}
            named = ref.get("cachedResultName") if isinstance(ref, dict) else None
            target = ref.get("value") if isinstance(ref, dict) else ref
            if c_parsed and named == called_wf.get("name"):
                calls_price_fetcher = True
            else:
                findings.append(f"'{n.get('name')}' names workflow {named!r}, not {called_wf.get('name')!r}")
            if isinstance(target, str) and target.startswith("YOUR_"):
                # recorded, not a stop: the link holds by name; the id must be set when the workflow is imported
                findings.append(f"note: '{n.get('name')}' carries a placeholder workflow id ({target}); "
                                "the link to the Price Fetcher holds by name only")

    approval_file = REPO / "logs" / "gate-decisions" / f"{SLUG}-approval.json"
    if approval_file.exists():
        rec = json.loads(approval_file.read_text())
        approval_state = f"{rec.get('decision', 'recorded')} ({approval_file.relative_to(REPO)})"
    else:
        approval_state = "no approval record: live mode (webhook, sub-workflow call) not approved"

    stops = [f for f in findings if not f.startswith("note:")]
    record: dict[str, Any] = {
        "workflow": wf.get("name") if parsed_ok else None,
        "source_paths": [p for p in [wf_rel, f"recipes/{SLUG}.md", f"recipes/{CALLED_SLUG}.md"] if p],
        "exists": exists,
        "parsed_ok": parsed_ok,
        "approval_state": approval_state,
        "checked_at": now,
        "node_table_match": node_table_match,
        "calls_price_fetcher": calls_price_fetcher,
        "findings": findings,
        "result": "pass" if (exists and parsed_ok and node_table_match and calls_price_fetcher and not stops) else "stop",
    }
    out = Path(a.out_dir) / f"{SLUG}-provenance-{now[:10]}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=1) + "\n")
    print(f"step 1 {record['result']}: {out}")
    for f in findings:
        print(f"  - {f}")
    return 0 if record["result"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
