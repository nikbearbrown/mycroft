"""Purpose: Step 1 of recipes/what-if-simulation-agent.md: verify that the run rests on the declared source.
Input: the recipe (its node table and its "Original workflow JSON" input), that workflow JSON, the sample fixture
       manifest, and the approval record at logs/gate-decisions/what-if-simulation-agent-approval.json if one exists.
Output: logs/what-if-simulation-agent-provenance-<YYYY-MM-DD>.json with workflow, source_paths, exists, parsed_ok,
        approval_state, checked_at (the recipe's step-1 fields) plus node_table_match, chain_match, fixtures_ok and findings.
Side effects: writes that one JSON file. No network, no credentials.
Idempotent: Yes; same inputs give the same record except checked_at (pin it with --now).
Errors: exit 1 if the workflow is missing or unparseable, if its nodes differ from the recipe's node table, if its
        connections do not form the chain the port assumes (webhook, parse, three simulators, aggregate, prompt, Groq,
        parse, prepare, save, build response, respond), or if a fixture no longer matches the SHA-256 frozen in the
        manifest. The record is still written, so the reason is kept.
Recipe: recipes/what-if-simulation-agent.md
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

SLUG = "what-if-simulation-agent"
REPO = Path(__file__).resolve().parents[2]

# the node order the step-5 port relies on: each node's single downstream node (webhook to respond)
EXPECTED_CHAIN = [
    "🎯 Webhook — Receive Simulation Request", "🔍 Parse & Validate Input", "📈 Sim 1 — Growth vs Sentiment Tradeoff",
    "⚖️ Sim 2 — Risk Appetite Simulator", "🎯 Sim 3 — Threshold Break Simulator", "🧠 Aggregate & Score All Simulations",
    "📝 Build AI Prompt", "🤖 Groq — Generate Investment Insights", "🔄 Parse Groq Response", "🗄️ Prepare DB Record",
    "💾 Save to PostgreSQL", "📊 Build Final Response", "✅ Respond to Webhook",
]
PORTED = EXPECTED_CHAIN[1:7]          # the six nodes step 5 ports (parse .. build prompt)


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


def chain_from(workflow: dict) -> list[str]:
    """Follow single-output connections from the webhook; returns the node names in order."""
    conns = {k: [c["node"] for c in v.get("main", [[]])[0]] for k, v in workflow.get("connections", {}).items()}
    start = EXPECTED_CHAIN[0]
    order, seen, cur = [start], {start}, start
    # the workflow has two segments (the prompt feeds Groq; Groq feeds the rest): walk through them
    while conns.get(cur):
        nxt = conns[cur][0]
        if nxt in seen:
            break
        order.append(nxt)
        seen.add(nxt)
        cur = nxt
    return order


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


def verify(repo: Path, now: str | None = None) -> tuple[dict, bool]:
    recipe_path = repo / "recipes" / f"{SLUG}.md"
    findings: list[str] = []
    rec: dict[str, Any] = {"workflow": "What-If Simulation Agent", "source_paths": [], "exists": {}, "parsed_ok": {}}
    declared, table = recipe_sources(recipe_path.read_text())
    paths = [f"recipes/{SLUG}.md"] + ([declared] if declared else [])
    rec["source_paths"] = paths
    for p in paths:
        rec["exists"][p] = (repo / p).exists()
    wf_ok, workflow = False, {}
    if declared and (repo / declared).exists():
        try:
            workflow = json.loads((repo / declared).read_text())
            wf_ok = True
        except json.JSONDecodeError as e:
            findings.append(f"workflow does not parse: {e}")
    else:
        findings.append("declared workflow is missing")
    rec["parsed_ok"] = {f"recipes/{SLUG}.md": True, **({declared: wf_ok} if declared else {})}

    node_match = chain_match = None
    if wf_ok:
        wf_nodes = [(n["name"], n["type"]) for n in workflow["nodes"]]
        rec_nodes = [(n, t) for n, t in table]
        # the recipe writes types as `code`, the workflow as n8n-nodes-base.code: compare on the last segment
        norm = lambda lst: sorted((n, t.split(".")[-1]) for n, t in lst)
        node_match = norm(wf_nodes) == norm(rec_nodes)
        if not node_match:
            only_wf = sorted(set(norm(wf_nodes)) - set(norm(rec_nodes)))
            only_rec = sorted(set(norm(rec_nodes)) - set(norm(wf_nodes)))
            findings.append(f"node table differs from the workflow (workflow only: {only_wf}; recipe only: {only_rec})")
        walked = chain_from(workflow)
        # the prompt node feeds Groq, which feeds the rest: the walk covers the whole chain in order
        chain_match = walked == EXPECTED_CHAIN
        if not chain_match:
            findings.append(f"connections do not form the expected chain (walked {len(walked)} nodes; expected {len(EXPECTED_CHAIN)})")
        for n in PORTED:
            node = next((x for x in workflow["nodes"] if x["name"] == n), None)
            if not node or not node.get("parameters", {}).get("jsCode"):
                findings.append(f"ported node has no jsCode: {n}")
                chain_match = False
    rec["node_table_match"] = node_match
    rec["chain_match"] = chain_match
    fixtures_ok, fprob = check_fixtures(repo / "data" / "raw" / SLUG / "sample")
    rec["fixtures_ok"] = fixtures_ok
    findings += fprob
    approval = repo / "logs" / "gate-decisions" / f"{SLUG}-approval.json"
    rec["approval_state"] = "present" if approval.exists() else "none (sample mode; no live action requested)"
    rec["findings"] = findings
    rec["checked_at"] = now or datetime.now(timezone.utc).isoformat(timespec="seconds")
    ok = bool(wf_ok and node_match and chain_match and fixtures_ok is not False and not findings)
    return rec, ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--now", default=None, help="pin checked_at (ISO) and the file's date")
    args = ap.parse_args()
    repo = Path(args.repo)
    rec, ok = verify(repo, args.now)
    day = (args.now or datetime.now(timezone.utc).isoformat())[:10]
    out = repo / "logs" / f"{SLUG}-provenance-{day}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
    print(f"{'OK' if ok else 'PROBLEM'}: node table match {rec['node_table_match']}, chain match {rec['chain_match']}, "
          f"fixtures {rec['fixtures_ok']}; {len(rec['findings'])} finding(s) -> {out.relative_to(repo)}")
    for f in rec["findings"]:
        print(" -", f)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
