"""Purpose: Step 2 of recipes/portfolio-price-fetcher.md: ingest the declared inputs, and account for every source the
workflow names, without a live call (the conductor's "Source and Credential Check").
Input: the run envelope (data/raw/portfolio-price-fetcher/run-envelope.json), the workflow JSON the recipe declares (its
       Define Portfolio holdings and its Fetch Stock Prices request), the sample fixtures under
       data/raw/portfolio-price-fetcher/sample/ with the SHA-256 frozen in manifest.json (sets clean and defective) and
       quality-manifest.json (the four quality-* sets), step 1's provenance record if one exists, and the approval
       record at logs/gate-decisions/portfolio-price-fetcher-approval.json if one exists.
Output: under data/raw/portfolio-price-fetcher/ingest/:
        <set>/ingested.json     the recipe's step-2 fields (records, source_name, source_type, fetched_at, sample_mode,
                                rejects) plus record_count, a naming ledger and the step-1 record it follows;
        <set>/ingest-audit.md   the same, for a person to read;
        source-check.json       every node the workflow names that carries a source, each available, skipped with a
                                reason, or approval-required, with the prior step's result beside it.
Side effects: writes those files unless --no-write. No network, no model call, no credential read: the environment is
              never asked for a value.
Idempotent: Yes; byte-identical files for the same inputs (fetched_at is the envelope's as_of unless --now pins another).
Errors: exit 1 (stop before transformation) if the run envelope is missing, is not sample mode or approves live calls;
        if the workflow is missing, unparseable, or lacks the Define Portfolio or Fetch Stock Prices node; if a
        manifest is missing; or if any fixture is missing, is not listed in a manifest, differs from the SHA-256 frozen
        there, or is not valid JSON. The files are still written, so the reason is kept. Exit 2 is argparse, or a set
        folder that does not exist.
What this step does not do: it does not judge a response. A response with no price, an unknown ticker or an empty result
        is valid JSON and is ingested like any other; two responses for one ticker are both ingested; judging shape
        is step 3's work and judging the set is step 4's. The naming ledger lists file names against declared
        holdings and says nothing about what is inside a file.
DELIBERATELY ABSENT: the live Yahoo Finance request (Fetch Stock Prices). This step names it as an approval-required
        handoff and never makes it.
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
SOURCE_NAME = "Yahoo Finance chart API (stood in for by invented sample fixtures)"
SOURCE_TYPE = "sample fixtures (invented Yahoo Finance chart responses)"
MANIFESTS = ("manifest.json", "quality-manifest.json")
NO_CRED = "none known (the public chart endpoint takes no key)"
MANUAL, CODE, HTTP = "n8n-nodes-base.manualTrigger", "n8n-nodes-base.code", "n8n-nodes-base.httpRequest"


def rel(repo: Path, p: Path) -> str:
    try:
        return str(p.relative_to(repo))
    except ValueError:
        return str(p)


def recipe_workflow_path(repo: Path) -> str | None:
    text = (repo / "recipes" / f"{SLUG}.md").read_text(encoding="utf-8")
    m = re.search(r"^\| Original workflow JSON \| JSON \| `([^`]+)` \|", text, re.M)
    return m.group(1) if m else None


def read_envelope(path: Path, repo: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not path.exists():
        return None, [f"the run envelope is missing ({rel(repo, path)}); no scope was declared"]
    try:
        env = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, [f"the run envelope is not readable JSON ({e})"]
    problems = []
    if env.get("mode") != "sample":
        problems.append(f"the run envelope declares mode {env.get('mode')!r}; this step implements sample mode only")
    if env.get("live_calls_approved") is not False:
        problems.append(f"the run envelope declares live_calls_approved: {env.get('live_calls_approved')!r}; sample mode needs false")
    return env, problems


def read_workflow(path: Path | None, repo: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if path is None or not path.exists():
        return None, [f"the workflow the recipe declares is missing ({rel(repo, path) if path else 'recipe names none'})"]
    try:
        wf = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, [f"the workflow is not readable JSON ({e})"]
    names = {n.get("name") for n in wf.get("nodes", [])}
    return wf, [f"the workflow has no {n!r} node" for n in ("Define Portfolio", "Fetch Stock Prices") if n not in names]


def declared_portfolio(wf: dict[str, Any]) -> dict[str, dict[str, float]]:
    """The holdings exactly as the Define Portfolio node declares them (the workflow is the source of truth)."""
    code = next((n["parameters"].get("jsCode", "") for n in wf.get("nodes", []) if n.get("name") == "Define Portfolio"), "")
    rows = re.findall(r"ticker:\s*'([^']+)',\s*shares:\s*([\d.]+),\s*buyPrice:\s*([\d.]+)", code)
    return {t: {"shares": float(s), "buyPrice": float(b)} for t, s, b in rows}


def host_of(url: str) -> str:
    m = re.match(r"^\s*=?\s*https?://([^/:?#{]+)", url or "")
    return m.group(1).lower() if m else ""


def read_manifests(sample_dir: Path, repo: Path) -> tuple[dict[str, dict[str, Any]], dict[str, str], list[str]]:
    """Every fixture the frozen manifests list, and which manifest holds it."""
    entries: dict[str, dict[str, Any]] = {}
    where: dict[str, str] = {}
    problems: list[str] = []
    for name in MANIFESTS:
        p = sample_dir / name
        if not p.exists():
            problems.append(f"the manifest {rel(repo, p)} is missing")
            continue
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            problems.append(f"the manifest {rel(repo, p)} is not readable JSON ({e})")
            continue
        for k, v in doc.get("files", {}).items():
            entries[k] = v
            where[k] = name
    return entries, where, problems


def latest_step1(logs_dir: Path, repo: Path) -> dict[str, Any]:
    cands = sorted(logs_dir.glob(f"{SLUG}-provenance-*.json"))
    if not cands:
        return {"found": False, "note": "no step-1 provenance record under logs/; step 1 is a separate gate and this step does not run it"}
    p = cands[-1]
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"found": True, "file": rel(repo, p), "readable": False}
    return {"found": True, "file": rel(repo, p), "readable": True, "result": doc.get("result"), "checked_at": doc.get("checked_at"),
            "approval_state": doc.get("approval_state")}


def classify_sources(wf: dict[str, Any], portfolio: dict[str, dict[str, float]], total_fixtures: int, approval_present: bool) -> list[dict[str, Any]]:
    """One row per source-bearing node: its role, and its sample-mode status (available, skipped or approval-required)."""
    rows: list[dict[str, Any]] = []
    for node in wf.get("nodes", []):
        ntype, name = node.get("type", ""), node.get("name", "")
        params = node.get("parameters", {}) or {}
        row: dict[str, Any] | None = None
        if ntype == MANUAL:
            row = {"role": "trigger: manual start", "status": "available",
                   "reason": "sample mode: the run envelope stands in for the manual start"}
        elif ntype == CODE and name == "Define Portfolio":
            row = {"role": "declared input: the holdings", "status": "available",
                   "reason": f"read from the workflow itself: {len(portfolio)} holdings ({', '.join(sorted(portfolio))})", "records": len(portfolio)}
        elif ntype == HTTP:
            host = host_of(str(params.get("url", ""))) or "an unnamed host"
            row = {"role": f"live HTTP request to {host}", "status": "approval-required",
                   "reason": (f"a live network call, one per holding; sample mode never makes it (the {total_fixtures} invented fixtures stand in), "
                              "and a live run needs an approval record")}
        elif node.get("credentials"):
            row = {"role": f"credentialed node of type {ntype}", "status": "approval-required",
                   "reason": "an unrecognised node type that carries credentials; held back until a person has read what it does"}
        if row is None:
            continue
        needs = row["status"] == "approval-required"
        row.update({"node": name, "node_type": ntype, "credential_env": NO_CRED if needs else "none known",
                    "approval_record_present": approval_present if needs else None,
                    "approved_for_live_action": False, "live_call_performed": False})
        rows.append(row)
    return rows


def stem_ticker(filename: str) -> str:
    """The ticker a file name claims: the part of the stem before the first hyphen (NVDA-restated.json claims NVDA)."""
    return Path(filename).stem.split("-", 1)[0]


def ingest_set(sample_dir: Path, set_name: str, entries: dict[str, dict[str, Any]], where: dict[str, str], portfolio: dict[str, Any],
               step1: dict[str, Any], now: str, repo: Path) -> dict[str, Any]:
    """Read every file of one set, trust it only if it matches the frozen manifest, keep its body unchanged."""
    folder = sample_dir / set_name
    listed = {k: v for k, v in entries.items() if k.split("/", 1)[0] == set_name}
    records: list[dict[str, Any]] = []
    rejects: list[dict[str, str]] = []
    for p in sorted(x for x in folder.iterdir() if x.is_file()):
        key = f"{set_name}/{p.name}"
        data = p.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if key not in listed:
            rejects.append({"file": key, "reason": "not listed in a frozen manifest, so its origin is not vouched for"})
        elif digest != listed[key].get("sha256"):
            rejects.append({"file": key, "reason": f"differs from the SHA-256 frozen in {where[key]} (frozen {str(listed[key].get('sha256'))[:12]}, found {digest[:12]})"})
        else:
            try:
                body = json.loads(data.decode("utf-8"))
            except (UnicodeDecodeError, ValueError) as e:
                rejects.append({"file": key, "reason": f"not valid JSON ({getattr(e, 'msg', e)})"})
            else:
                records.append({"file": key, "sha256": digest, "manifest": where[key], "exercises": listed[key].get("exercises", ""), "body": body})
    for key in sorted(listed):
        if not (sample_dir / key).exists():
            rejects.append({"file": key, "reason": f"listed in {where[key]} but missing"})
    rejects.sort(key=lambda r: r["file"])
    names = [Path(r["file"]).name for r in records]
    by_ticker = {t: [n for n in names if stem_ticker(n) == t] for t in sorted(portfolio)}
    return {
        "recipe": SLUG, "set": set_name, "source_name": SOURCE_NAME, "source_type": SOURCE_TYPE, "fetched_at": now, "sample_mode": True,
        "record_count": len(records), "records": records, "rejects": rejects,
        "naming_ledger": {
            "note": "File names against declared holdings only. What a file contains is judged by step 3 and the set by step 4; this ledger never looks inside.",
            "holdings_declared": sorted(portfolio),
            "files_by_holding": by_ticker,
            "holdings_with_no_named_file": [t for t, f in by_ticker.items() if not f],
            "files_named_for_no_holding": sorted(n for n in names if stem_ticker(n) not in portfolio),
        },
        "follows_step_1": step1,
    }


def audit_md(doc: dict[str, Any]) -> str:
    L = [f"# Step 2 ingest audit: {SLUG}, set `{doc['set']}`", "",
         f"Source: {doc['source_name']}. Type: {doc['source_type']}. Fetched at {doc['fetched_at']} (sample mode: {str(doc['sample_mode']).lower()}).",
         f"Records ingested: {doc['record_count']}. Rejects: {len(doc['rejects'])}.", "",
         "| File | Manifest | SHA-256 (first 12) | What it exercises |", "|---|---|---|---|"]
    L += [f"| {r['file']} | {r['manifest']} | {r['sha256'][:12]} | {r['exercises'] or '-'} |" for r in doc["records"]]
    L += ["", "## Rejects", ""]
    L += [f"- `{r['file']}`: {r['reason']}" for r in doc["rejects"]] or ["None."]
    nl = doc["naming_ledger"]
    L += ["", "## Naming ledger (file names only)", "",
          f"- Holdings declared by the workflow: {', '.join(nl['holdings_declared'])}.",
          f"- Holdings with no file named for them: {', '.join(nl['holdings_with_no_named_file']) or 'none'}.",
          f"- Files named for no holding: {', '.join(nl['files_named_for_no_holding']) or 'none'}.",
          "- Files named for one holding: " + ("; ".join(f"{t}: {', '.join(f)}" for t, f in nl['files_by_holding'].items() if len(f) > 1) or "none"), "",
          "This step ingests; it does not judge. A response with no price, an unknown ticker, an empty result, or a second response for a ticker is ingested like any other. Step 3 judges each response and step 4 judges the set.", "",
          f"Follows step 1: {json.dumps(doc['follows_step_1'], sort_keys=True)}", ""]
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--set", dest="sets", default=None, help="a set name, or 'all' (default: the run envelope's fixture_set)")
    ap.add_argument("--raw-dir", default=None, help="the data/raw/<slug> directory (default: the repository's)")
    ap.add_argument("--out-dir", default=None, help="where ingest/ is written (default: <raw-dir>/ingest)")
    ap.add_argument("--now", default=None, help="pin fetched_at (default: the envelope's as_of, so reruns are byte-identical)")
    ap.add_argument("--sample", action="store_true", help="sample mode, the only mode this step implements (accepted so the recipe's command line works; the run envelope must still say sample)")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--repo", default=str(REPO), help="the repository root (the self-test points this at a scratch copy)")
    args = ap.parse_args()
    repo = Path(args.repo).resolve()
    raw = Path(args.raw_dir).resolve() if args.raw_dir else repo / "data" / "raw" / SLUG
    out = Path(args.out_dir).resolve() if args.out_dir else raw / "ingest"
    sample_dir = raw / "sample"
    stops: list[str] = []

    env, p1 = read_envelope(raw / "run-envelope.json", repo)
    stops += p1
    wf_rel = recipe_workflow_path(repo) if (repo / "recipes" / f"{SLUG}.md").exists() else None
    wf, p2 = read_workflow(repo / wf_rel if wf_rel else None, repo)
    stops += p2
    entries, where, p3 = read_manifests(sample_dir, repo)
    stops += p3
    portfolio = declared_portfolio(wf) if wf else {}
    now = args.now or (env or {}).get("as_of") or datetime.now(timezone.utc).isoformat(timespec="seconds")

    all_sets = sorted(d.name for d in sample_dir.iterdir() if d.is_dir()) if sample_dir.exists() else []
    wanted = all_sets if args.sets == "all" else [args.sets or (env or {}).get("fixture_set") or "clean"]
    for s in wanted:
        if s not in all_sets:
            print(f"set {s!r} has no folder under {rel(repo, sample_dir)}", file=sys.stderr)
            return 2

    step1 = latest_step1(repo / "logs", repo)
    approval_present = (repo / "logs" / "gate-decisions" / f"{SLUG}-approval.json").exists()
    docs = [ingest_set(sample_dir, s, entries, where, portfolio, step1, now, repo) for s in wanted] if not p3 else []
    sources = classify_sources(wf, portfolio, len(entries), approval_present) if wf else []
    source_doc = {"recipe": SLUG, "checked_at": now, "mode": (env or {}).get("mode"), "live_calls_approved": (env or {}).get("live_calls_approved"),
                  "sources": sources, "prior_step_outputs": {"step_1_provenance": step1},
                  "stops": stops}

    rejects = sum(len(d["rejects"]) for d in docs)
    if not args.no_write and (docs or stops):
        out.mkdir(parents=True, exist_ok=True)
        (out / "source-check.json").write_text(json.dumps(source_doc, indent=1) + "\n", encoding="utf-8")
        for d in docs:
            (out / d["set"]).mkdir(parents=True, exist_ok=True)
            (out / d["set"] / "ingested.json").write_text(json.dumps(d, indent=1) + "\n", encoding="utf-8")
            (out / d["set"] / "ingest-audit.md").write_text(audit_md(d), encoding="utf-8")
    for d in docs:
        print(f"set {d['set']}: {d['record_count']} ingested, {len(d['rejects'])} rejected")
    for s_ in stops:
        print(f"STOP: {s_}")
    for r in sources:
        print(f"source {r['node']}: {r['status']}")
    return 1 if (stops or rejects) else 0


if __name__ == "__main__":
    sys.exit(main())
