"""Purpose: Step 1 of recipes/scenariostresstestingagent.md: verify that the run rests on the declared source.
Input: the recipe (its node table and its "Original workflow JSON" input), that workflow JSON, the sample fixture
       manifest, and the approval record at logs/gate-decisions/scenariostresstestingagent-approval.json if one exists.
Output: logs/scenariostresstestingagent-provenance-<YYYY-MM-DD>.json with workflow, source_paths, exists, parsed_ok,
        approval_state, checked_at (the recipe's step-1 fields) plus node_table_match, chain_match, ported_nodes_ok,
        fixtures_ok and findings.
Side effects: writes that one JSON file. No network, no credentials.
Idempotent: Yes; same inputs give the same record except checked_at (pin it with --now).
Errors: exit 1 if the workflow is missing or unparseable, if its nodes differ from the recipe's node table, if its
        connections differ from the wiring the port assumes (webhook, parse, edit, validate, merge, custom-scenario
        branch, template or LLM route, merge, engine, respond), if a ported node's language is not the one the port
        copies, or if a fixture no longer matches the SHA-256 frozen in the manifest. The record is still written, so
        the reason is kept.
Recipe: recipes/scenariostresstestingagent.md
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

SLUG = "scenariostresstestingagent"
REPO = Path(__file__).resolve().parents[2]

# every connection the step-5 port relies on: (from, output, to, input index). 18 edges.
EXPECTED_EDGES = {
    ("Webhook Trigger", "main", "Parse Input", 0),
    ("Parse Input", "main", "Edit Fields", 0),
    ("Edit Fields", "main", "Validate Portfolio", 0),
    ("Edit Fields", "main", "Fetch_Data", 0),
    ("Validate Portfolio", "main", "Merge", 1),
    ("Fetch_Data", "main", "Merge", 0),
    ("Merge", "main", "Custom Scenario?", 0),
    ("Custom Scenario?", "main", "Save_Portfolio_Before_LLM", 0),     # true branch: a custom scenario
    ("Custom Scenario?", "main", "Load_Template_Scenario", 0),        # false branch: a template
    ("Save_Portfolio_Before_LLM", "main", "Basic LLM Chain", 0),
    ("Save_Portfolio_Before_LLM", "main", "Parse_LLM_Response", 0),
    ("Basic LLM Chain", "main", "Parse_LLM_Response", 0),
    ("Groq Chat Model", "ai_languageModel", "Basic LLM Chain", 0),
    ("When chat message received", "main", "Basic LLM Chain", 0),
    ("Parse_LLM_Response", "main", "Merge1", 0),
    ("Load_Template_Scenario", "main", "Merge1", 1),
    ("Merge1", "main", "Stress_Test_Engine", 0),
    ("Stress_Test_Engine", "main", "Respond to Webhook", 0),
}
# the code nodes the port copies, with the language the port assumes for each
PORTED = {"Validate Portfolio": "javascript", "Load_Template_Scenario": "python",
          "Save_Portfolio_Before_LLM": "python", "Stress_Test_Engine": "python"}


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


def edges_of(workflow: dict) -> set[tuple[str, str, str, int]]:
    out = set()
    for src, kinds in workflow.get("connections", {}).items():
        for kind, outputs in kinds.items():
            for branch in outputs:
                for c in branch:
                    out.add((src, kind, c["node"], c.get("index", 0)))
    return out


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
    return (not problems), problems


def verify(repo: Path, now: str | None = None, workflow_override: Path | None = None,
           sample_override: Path | None = None) -> tuple[dict, bool]:
    recipe_path = repo / "recipes" / f"{SLUG}.md"
    findings: list[str] = []
    rec: dict[str, Any] = {"workflow": "ScenarioStressTestingAgent", "source_paths": [], "exists": {}, "parsed_ok": {}}
    declared, table = recipe_sources(recipe_path.read_text())
    paths = [f"recipes/{SLUG}.md"] + ([declared] if declared else [])
    rec["source_paths"] = paths
    wf_file = workflow_override or (repo / declared if declared else None)
    for p in paths:
        rec["exists"][p] = (repo / p).exists()
    wf_ok, workflow = False, {}
    if wf_file is not None and wf_file.exists():
        try:
            workflow = json.loads(wf_file.read_text())
            wf_ok = True
        except json.JSONDecodeError as e:
            findings.append(f"workflow does not parse: {e}")
    else:
        findings.append("declared workflow is missing")
    rec["parsed_ok"] = {f"recipes/{SLUG}.md": True, **({declared: wf_ok} if declared else {})}

    node_match = chain_match = ported_ok = None
    if wf_ok:
        wf_nodes = [(n["name"], n["type"]) for n in workflow["nodes"]]
        # the recipe writes types as `code`, the workflow as n8n-nodes-base.code: compare on the last segment
        norm = lambda lst: sorted((n, t.split(".")[-1]) for n, t in lst)
        node_match = norm(wf_nodes) == norm(table)
        if not node_match:
            only_wf = sorted(set(norm(wf_nodes)) - set(norm(table)))
            only_rec = sorted(set(norm(table)) - set(norm(wf_nodes)))
            findings.append(f"node table differs from the workflow (workflow only: {only_wf}; recipe only: {only_rec})")
        got = edges_of(workflow)
        chain_match = got == EXPECTED_EDGES
        if not chain_match:
            findings.append(f"connections differ from the wiring the port assumes (missing: {sorted(EXPECTED_EDGES - got)}; extra: {sorted(got - EXPECTED_EDGES)})")
        ported_ok = True
        by_name = {n["name"]: n for n in workflow["nodes"]}
        for name, lang in PORTED.items():
            node = by_name.get(name)
            if not node or node["type"].split(".")[-1] != "code":
                findings.append(f"ported node is not a code node: {name}")
                ported_ok = False
                continue
            params = node.get("parameters", {})
            has_js, has_py = bool(params.get("jsCode")), bool(params.get("pythonCode"))
            got_lang = "python" if params.get("language") == "python" or (has_py and not has_js) else "javascript"
            if got_lang != lang or not (has_js or has_py):
                findings.append(f"ported node {name} is {got_lang}, the port copies {lang}")
                ported_ok = False
    rec["node_table_match"] = node_match
    rec["chain_match"] = chain_match
    rec["ported_nodes_ok"] = ported_ok
    fixtures_ok, fprob = check_fixtures(sample_override or (repo / "data" / "raw" / SLUG / "sample"))
    rec["fixtures_ok"] = fixtures_ok
    findings += fprob
    approval = repo / "logs" / "gate-decisions" / f"{SLUG}-approval.json"
    rec["approval_state"] = "present" if approval.exists() else "none (sample mode; no live action requested)"
    rec["findings"] = findings
    rec["checked_at"] = now or datetime.now(timezone.utc).isoformat(timespec="seconds")
    ok = bool(wf_ok and node_match and chain_match and ported_ok and fixtures_ok is not False and not findings)
    return rec, ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--now", default=None, help="pin checked_at (ISO) and the file's date")
    ap.add_argument("--workflow", default=None, help="check this workflow file instead of the declared one (self-test)")
    ap.add_argument("--sample-dir", default=None, help="check this sample folder instead of the repo's (self-test)")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo)
    rec, ok = verify(repo, args.now, Path(args.workflow) if args.workflow else None, Path(args.sample_dir) if args.sample_dir else None)
    day = (args.now or datetime.now(timezone.utc).isoformat())[:10]
    out = repo / "logs" / f"{SLUG}-provenance-{day}.json"
    if not args.no_write:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
    print(f"{'OK' if ok else 'PROBLEM'}: node table match {rec['node_table_match']}, chain match {rec['chain_match']}, "
          f"ported nodes {rec['ported_nodes_ok']}, fixtures {rec['fixtures_ok']}; {len(rec['findings'])} finding(s)"
          + ("" if args.no_write else f" -> {out.relative_to(repo)}"))
    for f in rec["findings"]:
        print(" -", f)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
