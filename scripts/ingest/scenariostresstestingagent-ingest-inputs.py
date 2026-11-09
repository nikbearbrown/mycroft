"""Purpose: Step 2 of recipes/scenariostresstestingagent.md: ingest the declared inputs, and check every source and
credential the workflow names, without a live call (the conductor's "Source and Credential Check").
Input: the run envelope (data/raw/scenariostresstestingagent/run-envelope.json), the workflow JSON the recipe declares,
       the sample fixture folder with its frozen manifest, the environment (only to see whether a credential NAME is
       set), and the approval record at logs/gate-decisions/scenariostresstestingagent-approval.json if one exists.
Output: under data/raw/scenariostresstestingagent/ingest/:
        clean/ingested.json and defective/ingested.json  the recipe's step-2 fields (records, source_name, source_type,
                                                          fetched_at, sample_mode, rejects) plus record_count;
        source-check.json                                 every source and credential the workflow names, each
                                                          available, skipped with a reason, or approval-required;
        ingest-audit.md                                   the same, for a person.
Side effects: writes those four files unless --no-write. No network, no model call, no credential value is read or
              kept: the environment is asked only whether a name is set.
Idempotent: Yes; same inputs give the same files except fetched_at and checked_at (pin them with --now).
Errors: exit 1 (stop before transformation) if the run envelope is missing, is not sample mode, or declares live calls,
        network or database writes; if the workflow is missing, unparseable or declares no webhook for the fixtures to
        stand in for; if the manifest is missing; or if any fixture is missing, is not in the manifest, differs from the
        SHA-256 frozen in it, or is not valid JSON. The files are still written, so the reason is kept. Exit 2 is argparse.
What this step does not do: it does not judge a request's shape. A defective request ingests like any other (it is
        valid JSON); judging shape is step 3's work.
DELIBERATELY ABSENT: the live Alpha Vantage fetch (Fetch_Data) and the Groq call (Groq Chat Model). This step names them
        as approval-required handoffs and never makes them.
Recipe: recipes/scenariostresstestingagent.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SLUG = "scenariostresstestingagent"
REPO = Path(__file__).resolve().parents[2]
SAMPLE_TYPE = "sample fixture (invented webhook request body)"
FOLDER_TYPE = "sample fixtures (invented webhook request bodies)"
NO_CRED = "none known"

# What each kind of source-bearing node is, and what sample mode does about it. A node that carries credentials but is
# not listed here is still reported, as approval-required, so nothing credentialed can pass unnoticed.
WEBHOOK = "n8n-nodes-base.webhook"
CHAT = "@n8n/n8n-nodes-langchain.chatTrigger"
HTTP = "n8n-nodes-base.httpRequest"
GROQ = "@n8n/n8n-nodes-langchain.lmChatGroq"
CREDENTIAL_ENV = {GROQ: "GROQ_API_KEY"}                 # the HTTP node's name depends on its host, see below
HOST_ENV = {"alphavantage.co": "ALPHA_VANTAGE_API_KEY"}  # host fragment -> environment variable name


def rel(repo: Path, p: Path) -> str:
    try:
        return str(p.relative_to(repo))
    except ValueError:
        return str(p)


def recipe_workflow_path(repo: Path) -> str | None:
    text = (repo / "recipes" / f"{SLUG}.md").read_text(encoding="utf-8")
    m = re.search(r"^\| Original workflow JSON \| JSON \| `([^`]+)` \|", text, re.M)
    return m.group(1) if m else None


def read_envelope(repo: Path) -> tuple[dict[str, Any] | None, list[str]]:
    p = repo / "data" / "raw" / SLUG / "run-envelope.json"
    if not p.exists():
        return None, [f"the run envelope is missing ({rel(repo, p)}); no scope was declared"]
    try:
        env = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, [f"the run envelope is not readable JSON ({e})"]
    problems = []
    if env.get("mode") != "sample":
        problems.append(f"the run envelope declares mode {env.get('mode')!r}; this step implements sample mode only")
    for key in ("live_calls", "network", "database_writes"):
        if env.get(key) is not False:
            problems.append(f"the run envelope declares {key}: {env.get(key)!r}; sample mode needs false")
    return env, problems


def host_of(url: str) -> str:
    m = re.match(r"^\s*=?\s*https?://([^/:?#]+)", url or "")
    return m.group(1).lower() if m else ""


def credential_env_for(node: dict[str, Any]) -> str:
    ntype = node.get("type", "")
    if ntype in CREDENTIAL_ENV:
        return CREDENTIAL_ENV[ntype]
    if ntype == HTTP:
        host = host_of(str(node.get("parameters", {}).get("url", "")))
        for frag, name in HOST_ENV.items():
            if frag in host:
                return name
    return NO_CRED


def classify_sources(workflow: dict[str, Any], sample_counts: dict[str, int], approval_present: bool) -> list[dict[str, Any]]:
    """One row per source-bearing node: its role, and its sample-mode status (available, skipped or approval-required)."""
    rows: list[dict[str, Any]] = []
    for node in workflow.get("nodes", []):
        ntype, name = node.get("type", ""), node.get("name", "")
        params = node.get("parameters", {}) or {}
        row: dict[str, Any] | None = None
        if ntype == WEBHOOK:
            total = sum(sample_counts.values())
            row = {"role": f"trigger: {params.get('httpMethod', 'POST')} /{params.get('path', '')} request body", "status": "available",
                   "reason": f"sample mode: the {total} invented requests under data/raw/{SLUG}/sample/ stand in for webhook bodies", "records": total}
        elif ntype == CHAT:
            row = {"role": "trigger: chat message", "status": "skipped",
                   "reason": "the invented corpus has no chat-message fixture, so the chat entry point is not exercised in sample mode"}
        elif ntype == HTTP:
            host = host_of(str(params.get("url", ""))) or "an unnamed host"
            row = {"role": f"live HTTP request to {host}", "status": "approval-required",
                   "reason": "a live network call; sample mode never makes it, and a live run needs an approval record and a credential from the environment"}
        elif ntype == GROQ:
            row = {"role": f"live model call ({params.get('model', 'model not named')})", "status": "approval-required",
                   "reason": "a live model call; sample mode never makes it, and a live run needs an approval record and a credential from the environment"}
        elif node.get("credentials"):
            row = {"role": f"credentialed node of type {ntype}", "status": "approval-required",
                   "reason": "an unrecognised node type that carries credentials; held back until a person has read what it does"}
        if row is None:
            continue
        env_name = credential_env_for(node) if row["status"] == "approval-required" else NO_CRED
        row.update({"node": name, "node_type": ntype, "credential_env": env_name,
                    "credential_present": (bool(os.environ.get(env_name)) if env_name != NO_CRED else None),
                    "approval_record_present": approval_present if row["status"] == "approval-required" else None,
                    "approved_for_live_action": False, "live_call_performed": False})
        rows.append(row)
    return rows


def ingest_folder(sample_dir: Path, manifest: dict[str, Any], folder: str, now: str) -> tuple[dict[str, Any], list[str]]:
    """Read every fixture of one folder, trust it only if it matches the frozen manifest, keep its body unchanged."""
    entries = {k: v for k, v in manifest.get("files", {}).items() if k.split("/", 1)[0] == folder}
    records, rejects = [], []
    for key in sorted(entries):
        name = key.split("/", 1)[1]
        path = sample_dir / key
        if not path.exists():
            rejects.append({"source_name": name, "reason": "listed in the frozen manifest but not on disk"})
            continue
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != entries[key].get("sha256"):
            rejects.append({"source_name": name, "reason": "differs from the SHA-256 frozen in the manifest (the file changed since it was frozen)"})
            continue
        try:
            body = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as e:
            rejects.append({"source_name": name, "reason": f"not valid JSON ({str(e)[:80]})"})
            continue
        records.append({"record_id": key, "source_name": name, "source_type": SAMPLE_TYPE, "sha256": digest, "body": body})
    folder_path = sample_dir / folder
    if folder_path.is_dir():
        for p in sorted(folder_path.glob("*.json")):
            if f"{folder}/{p.name}" not in entries:
                rejects.append({"source_name": p.name, "reason": "on disk but not in the frozen manifest, so its origin is unknown"})
    out = {"workflow": "ScenarioStressTestingAgent", "step": "ingest-inputs", "folder": folder,
           "source_name": f"data/raw/{SLUG}/sample/{folder}", "source_type": FOLDER_TYPE, "fetched_at": now, "sample_mode": True,
           "record_count": len(records), "records": records, "rejects": rejects}
    return out, [f"{folder}/{r['source_name']}: {r['reason']}" for r in rejects]


def audit_markdown(sources: list[dict[str, Any]], folders: dict[str, dict[str, Any]], problems: list[str], now: str, approval_present: bool) -> str:
    L = [f"# Step 2 audit: ingest declared inputs ({SLUG})", "",
         f"Checked {now}. Mode: sample (no live call, no network, no database write). Approval record present: {'yes' if approval_present else 'no'}.", "",
         "## Requests ingested", "", "| Folder | Read | Rejected |", "|---|---|---|"]
    L += [f"| {f} | {d['record_count']} | {len(d['rejects'])} |" for f, d in folders.items()]
    L += ["", "Ingest keeps each request body exactly as it was frozen. It rejects only what it cannot read or cannot trust (missing, changed, unlisted or not JSON); whether a request has the right shape is step 3's work, so the defective folder ingests too.", "",
          "## Sources and credentials the workflow names", "", "| Node | Role | Status | Credential name | Set in the environment | Why |", "|---|---|---|---|---|---|"]
    for s in sources:
        cp = "n/a" if s["credential_present"] is None else ("yes" if s["credential_present"] else "no")
        L.append(f"| {s['node']} | {s['role']} | {s['status']} | {s['credential_env']} | {cp} | {s['reason']} |")
    L += ["", "No source marked approval-required was contacted. A credential is reported only as set or not set; its value is never read into a variable or a file.", "",
          "## Handoff condition (conductor step 2)", "", "Every source is available, skipped with a reason, or approval-required: " + ("**met**." if not problems else "**not met**.")]
    if problems:
        L += ["", "Stopped before transformation:"] + [f"- {p}" for p in problems]
    return "\n".join(L) + "\n"


def run(repo: Path, now: str, write: bool, workflow_override: str | None, sample_dir_override: str | None) -> tuple[int, dict[str, Any]]:
    problems: list[str] = []
    env, env_problems = read_envelope(repo)
    problems += env_problems
    if env is None or env_problems:
        return 1, {"problems": problems, "wrote": False}          # no scope, no ingest: nothing is written
    wf_rel = workflow_override or recipe_workflow_path(repo)
    workflow: dict[str, Any] = {}
    if not wf_rel or not (repo / wf_rel).exists():
        problems.append(f"the declared workflow JSON is missing ({wf_rel}); the sources cannot be declared")
    else:
        try:
            workflow = json.loads((repo / wf_rel).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            problems.append(f"the declared workflow JSON is not readable ({e})")
    sample_dir = Path(sample_dir_override) if sample_dir_override else repo / "data" / "raw" / SLUG / "sample"
    manifest_path = sample_dir / "manifest.json"
    if not manifest_path.exists():
        problems.append(f"the frozen manifest is missing ({rel(repo, manifest_path)}); no fixture can be trusted")
        manifest: dict[str, Any] = {}
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            problems.append(f"the frozen manifest is not readable JSON ({e})")
            manifest = {}
    folders: dict[str, dict[str, Any]] = {}
    for folder in ("clean", "defective"):
        data, rejected = ingest_folder(sample_dir, manifest, folder, now)
        folders[folder] = data
        problems += rejected
    approval_present = (repo / "logs" / "gate-decisions" / f"{SLUG}-approval.json").exists()
    sources = classify_sources(workflow, {f: d["record_count"] for f, d in folders.items()}, approval_present) if workflow else []
    if workflow and not any(s["node_type"] == WEBHOOK for s in sources):
        problems.append("the workflow declares no webhook trigger, so the sample fixtures stand in for no declared source")
    bad = [s for s in sources if s["status"] not in ("available", "skipped", "approval-required") or not s.get("reason")]
    problems += [f"source {s['node']} has no usable status or reason" for s in bad]
    check = {"workflow": "ScenarioStressTestingAgent", "step": "ingest-inputs", "checked_at": now, "mode": env.get("mode"),
             "run_envelope": f"data/raw/{SLUG}/run-envelope.json", "live_calls": env.get("live_calls"), "network": env.get("network"),
             "database_writes": env.get("database_writes"), "approval_record_present": approval_present, "sources": sources,
             "handoff_condition": "every source is available, skipped with a reason, or approval-required",
             "handoff_condition_met": not problems, "problems": problems}
    wrote = False
    if write:
        out = repo / "data" / "raw" / SLUG / "ingest"
        for folder, data in folders.items():
            (out / folder).mkdir(parents=True, exist_ok=True)
            (out / folder / "ingested.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (out / "source-check.json").write_text(json.dumps(check, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (out / "ingest-audit.md").write_text(audit_markdown(sources, folders, problems, now, approval_present), encoding="utf-8")
        wrote = True
    return (0 if not problems else 1), {"problems": problems, "wrote": wrote, "folders": {f: (d["record_count"], len(d["rejects"])) for f, d in folders.items()}, "sources": sources}


def main() -> int:
    ap = argparse.ArgumentParser(description="Step 2: ingest the declared inputs and check every source and credential, in sample mode.")
    ap.add_argument("--sample", action="store_true", help="sample mode (the only mode this step implements)")
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--now", default=None, help="pin fetched_at and checked_at (ISO)")
    ap.add_argument("--workflow", default=None, help="read the sources from this workflow file instead of the declared one (self-test)")
    ap.add_argument("--sample-dir", default=None, help="ingest this sample folder instead of the repo's (self-test)")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    now = args.now or datetime.now(timezone.utc).isoformat(timespec="seconds")
    code, info = run(Path(args.repo), now, not args.no_write, args.workflow, args.sample_dir)
    if "folders" in info:
        print("ingested: " + "; ".join(f"{f} {n} read, {r} rejected" for f, (n, r) in info["folders"].items()))
        print("sources: " + "; ".join(f"{s['node']} {s['status']}" for s in info["sources"]))
    if info["problems"]:
        print(f"STOP before transformation ({len(info['problems'])} problem(s)):")
        for p in info["problems"]:
            print(f"  - {p}")
    else:
        print("handoff condition met: every source is available, skipped with a reason, or approval-required"
              + ("" if info["wrote"] else " (--no-write: nothing written)"))
    return code


if __name__ == "__main__":
    sys.exit(main())
