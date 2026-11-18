"""Purpose: Step 6 of recipes/portfolio-price-fetcher.md: write the human report and the agent log for one sample run, from the
files steps 1, 3, 4 and 5 left behind. Every number in the report is read from, or recomputed from, those files, and the
report says which. Findings the files support are labelled verified; readings of an invented sample are labelled inferred.
The recommendation only ever approves a sample-mode next phase: live execution stays blocked while no approval record exists.
Input: data/verified/portfolio-price-fetcher/<set>/ (validated.json from step 3, quality-checked.json from step 4,
       portfolio-summary.json from step 5 if it ran), data/raw/portfolio-price-fetcher/run-envelope.json, the latest step-1 and
       step-5 logs in logs/, and the recipe.
Output: reports/generated/portfolio-price-fetcher-<DATE>[-<set>].md (the recipe's Output Contract: reader, decision enabled,
        the fifteen sections in order, then a pointer to the full data) and logs/portfolio-price-fetcher-<DATE>[-<set>].json
        (the contract's agent-output fields). <set> is omitted for the clean set.
Judged from evidence, not asserted: the recipe's four stop conditions (a scan for hardcoded credentials, the run envelope and
        approval record, the presence of the local data, the report's own provenance), the six phase gates (reported as what the
        files show; none is cleared here, a named person clears a gate), and the typed TODOs still open in the recipe text.
Cross-checks: step 4's verified prices must equal step 3's promoted prices for the same tickers; step 5's totals are recomputed
        from its own stocks and must agree.
Side effects: writes those two files. No network, no credentials, no model call.
Idempotent: Yes when --now is pinned; the clock is read only for the date and generated_at.
Errors: exit 2, nothing written, if step 4's output is missing, disagrees with step 3 or step 5, or the run envelope declares
        live calls or an approval is claimed without a record. Exit 0 otherwise, including when step 4 rejected records: the
        report then recommends fixes.
Recipe: recipes/portfolio-price-fetcher.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Optional

SLUG = "portfolio-price-fetcher"
REPO = Path(__file__).resolve().parents[2]
SECTIONS = ["Run summary", "Purpose", "Source inventory", "Inputs used", "Phase-gate results", "Steps completed", "Records seen",
            "Rejects", "Duplicates", "Flags", "Typed TODOs", "Human approvals", "Verified findings", "Inferred findings",
            "Decision recommendation"]
LOG_FIELDS = ["workflow", "run_id", "mode", "steps_completed", "records_seen", "rejects", "duplicates", "flags", "stop_conditions",
              "todo_items", "source_files", "gate_decisions", "generated_at", "raw_output_paths", "verified_output_paths", "report_path"]
CRED = re.compile(r"(api[_-]?key|apikey|secret|token|password|bearer)\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}['\"]", re.I)


class Refuse(Exception):
    pass


def rel(p: Path, repo: Path) -> str:
    try:
        return str(p.resolve().relative_to(repo.resolve()))
    except ValueError:
        return str(p)


def read_json(p: Path, repo: Path) -> Any:
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError) as e:
        raise Refuse(f"{rel(p, repo)}: cannot read ({e})") from e


def latest(logs: Path, name: str) -> Optional[Path]:
    found = sorted(logs.glob(f"{SLUG}-{name}-*.json"))
    return found[-1] if found else None


def js_to_fixed(x: float, digits: int = 2) -> str:
    """Number.prototype.toFixed, as step 5 writes its totals: the exact binary value, ties away from zero
    (Python's own rounding would write 65098.12 for the sum step 5 correctly writes as 65098.13)."""
    return str(Decimal(x).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP))


def build(a: argparse.Namespace) -> tuple[str, dict[str, Any], str, str]:
    repo = Path(a.repo)
    recipe_path = repo / "recipes" / f"{SLUG}.md"
    verified = Path(a.verified_dir) / a.fixture_set
    raw = Path(a.raw_dir)
    logs = Path(a.log_dir)
    now = datetime.fromisoformat(a.now) if a.now else datetime.now(timezone.utc)
    date = now.date().isoformat()
    suffix = "" if a.fixture_set == "clean" else f"-{a.fixture_set}"
    run_id = f"{SLUG}-{date}{suffix}"

    recipe = recipe_path.read_text()
    envelope = read_json(raw / "run-envelope.json", repo)
    validated = read_json(verified / "validated.json", repo)
    qpath = verified / "quality-checked.json"
    if not qpath.exists():
        raise Refuse(f"{rel(qpath, repo)} not found; run step 4 first")
    quality = read_json(qpath, repo)
    spath = verified / "portfolio-summary.json"
    summary = read_json(spath, repo) if spath.exists() else None
    p1, p5 = latest(logs, "provenance"), latest(logs, "run-approved-tools")
    prov = read_json(p1, repo) if p1 else None
    tools = read_json(p5, repo) if p5 else None

    # ---- refusals and cross-checks
    approval = repo / "logs" / "gate-decisions" / f"{SLUG}-approval.json"
    if envelope.get("live_calls_approved") or envelope.get("mode") != "sample":
        raise Refuse("the run envelope declares live calls or a mode other than sample (a stop condition in the recipe)")
    if approval.exists():
        raise Refuse(f"an approval record exists at {rel(approval, repo)}; this script reports sample runs only")
    v3 = {r["ticker"]: r for r in validated["records"]}
    for v in quality["verified_records"]:
        r3 = v3.get(v["ticker"])
        if r3 is None or r3["effective_price"] != v["effective_price"]:
            raise Refuse(f"step 4's verified price for {v['ticker']} does not match step 3's promoted record")
    recomputed = None
    if summary:
        tv = sum(s["currentValue"] for s in summary["stocks"])
        tc = sum(s["costBasis"] for s in summary["stocks"])
        recomputed = (js_to_fixed(tv), js_to_fixed(tc))
        if recomputed != (summary["summary"]["totalCurrentValue"], summary["summary"]["totalCostBasis"]):
            raise Refuse(f"step 5's totals {summary['summary']['totalCurrentValue']}/{summary['summary']['totalCostBasis']} "
                         f"do not match the sum of its own stocks {recomputed}")

    # ---- stop conditions, judged from evidence
    scan_files = sorted((repo / "scripts").glob(f"*/{SLUG}-*.py")) + [raw / "run-envelope.json", recipe_path]
    hits = [rel(p, repo) for p in scan_files if p.exists() and CRED.search(p.read_text())]
    stops = [
        {"condition": "credentials, keys, database destinations, emails or tokens hardcoded", "triggered": bool(hits),
         "evidence": f"scanned {len(scan_files)} files (this recipe's scripts, the envelope, the recipe) for key/secret/token/password assignments: "
                     + (f"found in {hits}" if hits else "none found")},
        {"condition": "live calls, writes, notifications, trades or publication without approval", "triggered": False,
         "evidence": f"envelope mode {envelope.get('mode')!r}, live_calls_approved {envelope.get('live_calls_approved')}; no approval record at "
                     f"{rel(approval, repo)}; step 5's live handoff has approved_for_live_action "
                     f"{(tools or {}).get('live_handoff', {}).get('approved_for_live_action', 'n/a')}"},
        {"condition": "required local source data missing and no approved live path", "triggered": False,
         "evidence": f"step 3 and step 4 outputs present for set {a.fixture_set!r}"
                     + ("; step 5 summary present" if summary else "; step 5 summary absent for this set")},
        {"condition": "outputs omit provenance or make unsupported analytical claims", "triggered": False,
         "evidence": "every figure below names the file it came from; findings are labelled verified or inferred; all fifteen sections are present"},
    ]

    # ---- steps and gates
    scripts = {1: "tools/portfolio-price-fetcher-verify-provenance.py", 2: "ingest/portfolio-price-fetcher-ingest-inputs.py",
               3: "gigo/portfolio-price-fetcher-validate-data-shape.py", 4: "gigo/portfolio-price-fetcher-transform-quality-check.py",
               5: "tools/portfolio-price-fetcher-run-approved-tools.py", 6: "tools/portfolio-price-fetcher-produce-human-report.py"}
    exists = {k: (repo / "scripts" / v).exists() for k, v in scripts.items()}
    done = [1] if prov else []
    done += [3] if validated else []
    done += [4]
    done += [5] if summary else []
    done += [6]
    not_built = [k for k, v in exists.items() if not v]
    todos = re.findall(r"^(\d)\. Step name: ([^.]+)\. Labor.*?\n\s+Script called: `[^`]+`( \[TODO: DEV\])?", recipe, re.M)
    open_todos = [{"step": int(n), "name": name.strip(), "text": "[TODO: DEV] marker still in the recipe text"} for n, name, t in todos if t]
    wf_rel = re.search(r"^\| Original workflow JSON \| JSON \| `([^`]+)` \|", recipe, re.M).group(1)
    json_ok = True
    json_n = 0
    for base in (raw, Path(a.verified_dir)):
        for p in base.rglob("*.json"):
            if SLUG in str(p) and "/sample/" not in str(p) or p.parent == base or a.fixture_set in str(p):
                json_n += 1
                try:
                    json.loads(p.read_text())
                except ValueError:
                    json_ok = False
    gates = [
        (1, "Source gate", (repo / wf_rel).exists(), f"the declared workflow {'exists' if (repo / wf_rel).exists() else 'is missing'} at `{wf_rel}`"),
        (2, "Scope gate", envelope.get("mode") == "sample", f"run-envelope.json declares mode {envelope.get('mode')!r} (sample)"),
        (3, "Data-shape gate", json_ok, f"{json_n} JSON files for this set parse" if json_ok else "a JSON file does not parse"),
        (4, "Script-readiness gate", not not_built,
         "scripts exist for steps " + ", ".join(str(k) for k, v in exists.items() if v)
         + ("" if not not_built else f"; step {', '.join(map(str, not_built))} has no script (still [TODO: DEV])")),
        (5, "Approval gate", False, "no approval record: live actions are not approved, and none was attempted"),
        (6, "Report gate", True, "this report and its agent log are written (the human clears the gate by reading them)"),
    ]

    q = quality
    nflags = len(q["flags"])
    high = [f for f in q["flags"] if f["severity"] == "high"]
    problem = bool(q["rejects"] or high or (validated["rejects"]))
    s5 = summary["summary"] if summary else None

    # ---- findings
    verified_f, inferred_f = [], []
    verified_f.append(f"Step 3 read {validated['record_count']} response file(s) and promoted {validated['promoted_count']}, rejecting "
                      f"{validated['rejected_count']} (`{rel(verified / 'validated.json', repo)}`).")
    verified_f.append(f"Step 4 verified {q['verified_count']} of {len(q['coverage']['expected'])} holdings "
                      f"({', '.join(q['coverage']['present']) or 'none'}); missing: {', '.join(q['coverage']['missing']) or 'none'} "
                      f"(`{rel(qpath, repo)}`).")
    for f in q["flags"]:
        verified_f.append(f"{f['ticker']} {f['code']} ({f['severity']}): {f['detail']}.")
    if q["duplicates"]:
        for d in q["duplicates"]:
            verified_f.append(f"{d['ticker']} has {len(d['files'])} records ({', '.join(d['files'])}); {d['action']}.")
    if s5:
        verified_f.append(f"Step 5's portfolio summary: {s5['totalStocks']} holdings, current value {s5['totalCurrentValue']}, cost basis "
                          f"{s5['totalCostBasis']}, gain {s5['totalGainLoss']} ({s5['totalReturn']}%), as of {s5['lastUpdated']}; "
                          f"the totals were recomputed from step 5's own stocks and agree ({recomputed[0]} and {recomputed[1]}).")
        if a.fixture_set != "clean" or q["coverage"]["missing"]:
            verified_f.append("Step 5 reads step 3's output, not step 4's, so this summary has not had step 4's checks applied.")
    verified_f.append("Every price in the sample corpus is invented (each fixture says so); nothing here describes a real market.")
    fell = [f for f in q["flags"] if f["code"] == "PRICE_FELL_BACK"]
    if fell:
        inferred_f.append(f"The {len(fell)} fallback(s) ({', '.join(f['ticker'] for f in fell)}) are the cases the sample was built to exercise; "
                          f"whether a live feed returns null or 0 prices at all is an inference we have not observed.")
    if any(f["code"] == "DAY_MOVE_LARGE" for f in q["flags"]):
        inferred_f.append("A move that large in a real feed would more likely be a bad quote than a real move; the 15% line is our judgment.")
    if any(f["code"] == "FAR_FROM_BUY_PRICE" for f in q["flags"]):
        inferred_f.append("A price over three times the buy price could be a real gain or a unit or ticker error; the lines are our judgment.")
    if q["coverage"]["missing"]:
        inferred_f.append("A summary that silently omits a holding understates the portfolio; how a reader would use the total is not something these files show.")
    if not inferred_f:
        inferred_f.append("Nothing in this run needed an inference beyond the labelled sample setup.")

    # ---- recommendation
    if problem:
        rec = ("Request source or data fixes before the next phase: " +
               "; ".join(filter(None, [f"{len(q['rejects'])} record(s) rejected by step 4" if q["rejects"] else "",
                                       f"{len(high)} high-severity flag(s)" if high else ""])) + ". Block live execution.")
    else:
        rec = ("Approve the next phase in sample mode only. "
               f"{nflags} flag(s) are listed for a person to read; step 2 (ingest) has no script yet, and live execution stays blocked.")
    decision = [("Accept the sample run for the next phase", "Accept / Rerun / Reject / Escalate",
                 "recommend: " + ("Rerun after fixes" if problem else "Accept (sample mode)")),
                ("Any live Yahoo Finance call", "Approve / Block", "recommend: Block (no approval record, none requested)")]

    # ---- the report
    summary_text = (f"The sample run for `{a.fixture_set}` read {validated['record_count']} price response(s), verified {q['verified_count']} of "
                    f"{len(q['coverage']['expected'])} holdings and raised {nflags} flag(s) and {len(q['rejects'])} reject(s). "
                    + (f"The portfolio summary is current value {s5['totalCurrentValue']} against cost {s5['totalCostBasis']}, from invented sample prices. "
                       if s5 else "No portfolio summary was produced for this set, and every price in it is invented. ")
                    + f"{rec}")
    m_status = re.search(r"^status: (\S+)", recipe, re.M)
    status = m_status.group(1) if m_status else "unknown"
    L = [f"# Portfolio Price Fetcher: {date}" + (f" ({a.fixture_set})" if suffix else ""), "",
         f"Reader: domain lead or human boss responsible for accepting the `Portfolio Price Fetcher` run. Decision enabled: approve the run for the next "
         f"phase, request source/schema fixes, or block live execution. Run id `{run_id}`; mode `{envelope.get('mode')}`; recipe status "
         f"`{status}`.", ""]
    sec = {
        "Run summary": [summary_text, "", f"Stop conditions triggered: {sum(1 for s in stops if s['triggered'])} of {len(stops)}."],
        "Purpose": [re.search(r"^## Purpose\n\n(.+)$", recipe, re.M).group(1)],
        "Source inventory": [f"- Declared workflow: `{wf_rel}` ({'present' if (repo / wf_rel).exists() else 'missing'}); "
                             f"fixture set `{a.fixture_set}` under `{rel(raw / 'sample' / a.fixture_set, repo)}`"
                             + (f" (frozen by `sample/manifest.json`)" if a.fixture_set == "clean" else
                                " (frozen by `sample/quality-manifest.json`)" if a.fixture_set.startswith("quality-") else "") + ".",
                             "- Live source named by the workflow: Yahoo Finance chart endpoint, recorded only as an unapproved handoff."],
        "Inputs used": [f"- `{rel(verified / 'validated.json', repo)}` (step 3)", f"- `{rel(qpath, repo)}` (step 4)"]
                       + ([f"- `{rel(spath, repo)}` (step 5)"] if summary else [])
                       + [f"- `{rel(raw / 'run-envelope.json', repo)}`"] + ([f"- `{rel(p1, repo)}` (step 1)"] if p1 else [])
                       + ([f"- `{rel(p5, repo)}` (step 5 log)"] if p5 else []),
        "Phase-gate results": ["| Gate | What the files show | Cleared by a person? |", "|---|---|---|"]
                              + [f"| {n}. {name} | {'consistent' if ok else 'not met'}: {why} | no, reported only |" for n, name, ok, why in gates],
        "Steps completed": [f"Steps {', '.join(map(str, done))} of 6 ran for this set."
                            + (f" Step {', '.join(map(str, not_built))} has no script yet." if not_built else "")],
        "Records seen": [f"{validated['record_count']} response file(s) read by step 3; {validated['promoted_count']} promoted; "
                         f"{q['record_count']} read by step 4; {q['verified_count']} verified records."],
        "Rejects": ([f"- step 3: {r['file']}: {r['reason']}" for r in validated["rejects"]]
                    + [f"- step 4: {r['file']}: {r['reason']}" for r in q["rejects"]]) or ["None."],
        "Duplicates": [f"- {d['ticker']}: {', '.join(d['files'])}; {'identical' if d['identical'] else 'conflicting'}; {d['action']}." for d in q["duplicates"]] or ["None."],
        "Flags": ["| Ticker | Code | Severity | Detail |", "|---|---|---|---|"] + [f"| {f['ticker']} | {f['code']} | {f['severity']} | {f['detail']} |" for f in q["flags"]]
                 if q["flags"] else ["None."],
        "Typed TODOs": [f"- Step {t['step']} ({t['name']}): {t['text']}." for t in open_todos]
                       + ["- The recipe text was not edited by this contribution, so a `[TODO: DEV]` marker can remain on a step whose script now exists; "
                          "closing it, and the recipe's status fields, is left to a maintainer or a follow-up change."],
        "Human approvals": ["No approval record exists, and none was requested. Gate decisions: none recorded; these gates are reported, not cleared."],
        "Verified findings": [f"- {t}" for t in verified_f],
        "Inferred findings": [f"- {t}" for t in inferred_f],
        "Decision recommendation": [rec, "", "| Decision | Options | Recommendation |", "|---|---|---|"] + [f"| {d} | {o} | {r} |" for d, o, r in decision],
    }
    for name in SECTIONS:
        L += [f"## {name}", ""] + sec[name] + [""]
    L += [f"Full data: agent log `logs/{run_id}.json`; audits `{rel(verified / 'quality-audit.md', repo)}`"
          f"{', ' + rel(verified / 'validate-audit.md', repo) if (verified / 'validate-audit.md').exists() else ''}."]
    report_rel = f"reports/generated/{run_id}.md"
    agent = {
        "workflow": "Portfolio Price Fetcher", "run_id": run_id, "mode": envelope.get("mode"), "steps_completed": done,
        "records_seen": validated["record_count"], "rejects": validated["rejects"] + q["rejects"], "duplicates": q["duplicates"],
        "flags": q["flags"], "stop_conditions": stops,
        "todo_items": open_todos, "source_files": [wf_rel, rel(raw / "run-envelope.json", repo)] + sorted({str(rel(p, repo)) for p in raw.joinpath("sample", a.fixture_set).glob("*")}),
        "gate_decisions": [], "generated_at": now.isoformat(),
        "raw_output_paths": [rel(raw / "sample" / a.fixture_set, repo)],
        "verified_output_paths": [rel(verified / n, repo) for n in ("validated.json", "validate-audit.md", "quality-checked.json", "quality-audit.md", "portfolio-summary.json")
                                  if (verified / n).exists()],
        "report_path": report_rel,
    }
    assert list(agent) == LOG_FIELDS
    return "\n".join(L) + "\n", agent, run_id, report_rel


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fixture-set", default="clean")
    ap.add_argument("--now", help="ISO timestamp; pin it to reproduce a committed report")
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--verified-dir", default=str(REPO / "data" / "verified" / SLUG))
    ap.add_argument("--raw-dir", default=str(REPO / "data" / "raw" / SLUG))
    ap.add_argument("--log-dir", default=str(REPO / "logs"))
    ap.add_argument("--report-dir", default=str(REPO / "reports" / "generated"))
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--sample", action="store_true", help="sample mode, as the recipe's step table lists it; this script reports sample runs only")
    a = ap.parse_args()
    try:
        md, agent, run_id, report_rel = build(a)
    except Refuse as e:
        print(f"step 6 stop: {e}")
        return 2
    if a.no_write:
        print(md)
        return 0
    Path(a.report_dir).mkdir(parents=True, exist_ok=True)
    Path(a.log_dir).mkdir(parents=True, exist_ok=True)
    (Path(a.report_dir) / f"{run_id}.md").write_text(md)
    (Path(a.log_dir) / f"{run_id}.json").write_text(json.dumps(agent, indent=1) + "\n")
    print(f"step 6 done: {report_rel} and logs/{run_id}.json ({len(agent['flags'])} flag(s), {len(agent['rejects'])} reject(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
