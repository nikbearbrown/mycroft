#!/usr/bin/env python3
"""Purpose: Step 6 of recipes/scenariostresstestingagent.md: write the human report and the agent log for one sample run, from the verified
         files steps 3, 4 and 5 left behind. Nothing here is computed from outside the repo; every number in the report is read from, or
         recomputed from, those files and the report says which. Findings the data supports are labelled verified; readings of an invented
         sample are labelled inferred. The recommendation only ever approves a sample-mode next phase: live execution stays blocked
         while no approval record exists. The recipe's four stop conditions are judged from evidence (a scan for hardcoded credentials, the run envelope and approval
         record, the sample folder and its manifest, the report's provenance sections), recorded in the agent log, and counted in the report's run summary.
Input: data/verified/scenariostresstestingagent/<clean|defective>/ (validated.json from step 3, stress-results.json from step 5 if any
       request ran, quality-check.json from step 4), data/raw/scenariostresstestingagent/run-envelope.json, the latest step-1 and step-5
       logs in logs/, and the recipe.
Output: reports/generated/scenariostresstestingagent-<DATE>[-defective].md (the recipe's Output Contract: reader, decision enabled, fifteen
        sections in order) and logs/scenariostresstestingagent-<DATE>[-defective].json (the contract's agent-output fields).
Side effects: writes those two files. No network, no credentials, no model call.
Idempotent: Yes when --now is pinned; the clock is read only for the date and generated_at.
Errors: exit 2, nothing written, if step 4's output is missing, does not match step 3 and 5's files, or the run envelope declares live
        calls, network or database writes (a stop condition in the recipe). Exit 0 otherwise, including for the defective set, whose
        report records that nothing ran.
Recipe: recipes/scenariostresstestingagent.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SLUG = "scenariostresstestingagent"
REPO = Path(__file__).resolve().parents[2]
RECIPE = REPO / "recipes" / f"{SLUG}.md"
RAW = REPO / "data" / "raw" / SLUG
VERIFIED = REPO / "data" / "verified" / SLUG
LOGS = REPO / "logs"
SECTIONS = ["Run summary", "Purpose", "Source inventory", "Inputs used", "Phase-gate results", "Steps completed", "Records seen", "Rejects",
            "Duplicates", "Flags", "Typed TODOs", "Human approvals", "Verified findings", "Inferred findings", "Decision recommendation"]
BOUNDS = (10, 20, 30)           # the engine's risk lines (RISK_LEVELS in the step-5 port); used only to describe nearness


class Refuse(Exception):
    pass


def rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(REPO))
    except ValueError:
        return str(p)


def read_json(p: Path):
    try:
        return json.loads(p.read_text())
    except (OSError, ValueError) as e:
        raise Refuse(f"{rel(p)}: cannot read ({e})") from e


def latest(prefix: str) -> Path | None:
    found = sorted(LOGS.glob(f"{SLUG}-{prefix}-*.json"))
    return found[-1] if found else None


# ------------------------------------------------------------------------------------------------ the recipe
def parse_recipe() -> dict:
    text = RECIPE.read_text()
    front = dict(re.findall(r"^(status|todos_open|recipe_version|last_gate):\s*([^\n#]*)", text, flags=re.M))
    purpose = re.search(r"## Purpose\s+(.+?)\n\n", text, flags=re.S)
    steps = []
    steps_text = (re.search(r"^## Steps\s*\n(.*?)(?=^## )", text, flags=re.M | re.S) or [None, ""])[1]    # the recipe's own Steps section only, not the preserved notes
    for m in re.finditer(r"^(\d+)\. Step name: (.+?)\. Labor:.*?\n(.*?)(?=^\d+\. Step name:|\Z)", steps_text, flags=re.M | re.S):
        script = re.search(r"Script called: (.+)", m.group(3))
        line = script.group(1) if script else ""
        steps.append({"n": int(m.group(1)), "name": m.group(2), "script": (re.search(r"`([^`]+\.py)`", line) or [None, None])[1],
                      "open": "[TODO: DEV]" in line, "closed_note": "Closed " in m.group(3)})
    mappings = re.findall(r"Script called: `\[TODO: DEV\] Create or map script path: ([^`]+)`", text)
    stops = re.search(r"## Stop Conditions\s+(.+?)\n\n", text, flags=re.S)
    return {"text": text, "front": {k: v.strip() for k, v in front.items()}, "purpose": (purpose.group(1).strip() if purpose else ""), "steps": steps,
            "mapping_todos": mappings, "stop_conditions": [s[2:].strip() for s in (stops.group(1).splitlines() if stops else []) if s.startswith("- ")]}


# ------------------------------------------------------------------------------------------------ gates, from evidence
def evaluate_gates(recipe: dict, envelope: dict, folder: str) -> list[dict]:
    parse_fail = []
    n_json = 0
    for base in (RAW, VERIFIED):
        for p in sorted(base.rglob("*.json")):
            n_json += 1
            try:
                json.loads(p.read_text())
            except ValueError:
                parse_fail.append(rel(p))
    steps = recipe["steps"]
    missing = [s for s in steps if s["script"] and not (REPO / s["script"]).exists() and not s["open"]]
    open_steps = [s for s in steps if s["open"]]
    approval = LOGS / "gate-decisions" / f"{SLUG}-approval.json"
    return [
        {"gate": "1 Source gate", "result": "PASS" if RECIPE.exists() and (RAW / "sample" / folder).exists() else "FAIL",
         "evidence": f"the recipe and the sample folder `data/raw/{SLUG}/sample/{folder}/` exist; the sources are the invented sample corpus"},
        {"gate": "2 Scope gate", "result": "PASS" if envelope.get("mode") == "sample" else "FAIL",
         "evidence": f"`run-envelope.json` parses and declares mode `{envelope.get('mode')}`, live_calls {envelope.get('live_calls')}, network {envelope.get('network')}, database_writes {envelope.get('database_writes')}"},
        {"gate": "3 Data-shape gate", "result": "PASS" if not parse_fail else "FAIL",
         "evidence": f"{n_json} JSON file(s) under the raw and verified folders parse" + (f"; failed: {parse_fail}" if parse_fail else "")},
        {"gate": "4 Script-readiness gate", "result": "PASS" if not missing else "FAIL",
         "evidence": f"{len(steps) - len(open_steps)} of {len(steps)} step scripts exist; step(s) {', '.join(str(s['n']) for s in open_steps) or 'none'} still carry a typed `[TODO: DEV]`"},
        {"gate": "5 Approval gate", "result": "NOT NEEDED (sample mode)",
         "evidence": f"no live call, external write or credential was requested; the approval record `logs/gate-decisions/{SLUG}-approval.json` "
                     + ("exists" if approval.exists() else "does not exist, so live execution stays blocked")},
        {"gate": "6 Report gate", "result": "PENDING", "evidence": "evaluated after the report and agent log are written"},
    ]


# ------------------------------------------------------------------------------------------------ stop conditions, from evidence
# A quoted literal of 8 or more characters assigned to a credential-like name, an `sk-` key, or a Bearer token. The patterns are assignments and
# literals, so the words in this file's own regexes do not match them (a scan of this recipe's files, this one included, finds none).
CREDENTIAL_PATTERNS = (
    re.compile(r"""(?i)\b(api[_-]?key|secret|token|passwd|password|authorization)\b["']?\s*[:=]\s*["'][^"'\s]{8,}["']"""),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{20,}"),
)


def scan_for_credentials() -> tuple[int, list[str]]:
    files = sorted((REPO / "scripts").glob(f"*/{SLUG}-*.py")) + sorted(RAW.rglob("*.json")) + [RECIPE]
    hits = []
    for p in files:
        text = p.read_text(errors="ignore")
        if any(rx.search(text) for rx in CREDENTIAL_PATTERNS):
            hits.append(rel(p))
    return len(files), hits


def evaluate_stop_conditions(recipe: dict, envelope: dict, folder: str, run: dict, source_files: list[str], validated: dict) -> list[dict]:
    """The recipe's Stop Conditions, each judged from evidence. Returns one {condition, triggered, evidence} per condition, in the recipe's order."""
    out = []
    conds = recipe["stop_conditions"]
    n_scanned, hits = scan_for_credentials()
    live = [k for k in ("live_calls", "network", "database_writes") if envelope.get(k)]
    approval = LOGS / "gate-decisions" / f"{SLUG}-approval.json"
    sample = RAW / "sample" / folder
    manifest = RAW / "sample" / "manifest.json"
    n_req = len([p for p in sample.glob("*.json")]) if sample.exists() else 0
    missing = (not sample.exists()) or (not manifest.exists()) or n_req == 0
    omits = (not source_files) or ("Source inventory" not in SECTIONS) or ("Inputs used" not in SECTIONS)
    handoffs = run.get("handoffs_not_made") or []
    evidence = [
        (bool(hits), f"scanned {n_scanned} file(s) (this recipe's scripts, its raw data and the recipe) for a quoted literal assigned to an api key, secret, token, password or authorization, an `sk-` key or a Bearer token: " + (f"found in {', '.join(hits)}" if hits else "none found")),
        (bool(live) and not approval.exists(), f"run envelope: live_calls {envelope.get('live_calls')}, network {envelope.get('network')}, database_writes {envelope.get('database_writes')}; "
            + (f"{', '.join(live)} requested and no approval record exists" if (live and not approval.exists()) else f"nothing live requested, so no approval is needed; {len(handoffs)} hand-off(s) recorded in the step-5 log, none made")),
        (missing, f"the `{folder}` sample folder {'exists' if sample.exists() else 'is missing'} with {n_req} request file(s) and the manifest {'exists' if manifest.exists() else 'is missing'}; step 3 read {len(validated['accepted']) + len(validated['rejected'])}"),
        (omits, f"the log lists {len(source_files)} source file(s); the report carries Source inventory and Inputs used, and keeps readings of the sample under Inferred findings, labelled"),
    ]
    for i, c in enumerate(conds):
        trig, ev = evidence[i] if i < len(evidence) else (False, "no check is defined for this condition")
        out.append({"condition": c, "triggered": bool(trig), "evidence": ev})
    return out


# ------------------------------------------------------------------------------------------------ numbers, recomputed from the files
def describe(results: list[dict]) -> dict:
    ran = [r for r in results if r.get("result")]
    levels = {k: sum(1 for r in ran if r["result"]["risk_level"] == k) for k in ("CRITICAL", "HIGH", "MODERATE", "LOW")}
    by_scn: dict[str, list[float]] = {}
    for r in ran:
        by_scn.setdefault(r["result"]["scenario_name"], []).append(r["result"]["drawdown_pct"])
    worst = min(ran, key=lambda r: r["result"]["drawdown_pct"], default=None)
    mildest = max(ran, key=lambda r: r["result"]["drawdown_pct"], default=None)
    near = [r["id"] for r in ran if any(abs(abs(r["result"]["drawdown_pct"]) - b) <= 5 for b in BOUNDS)]
    return {"ran": ran, "levels": levels, "by_scenario": {k: (round(sum(v) / len(v), 2), len(v)) for k, v in sorted(by_scn.items())}, "worst": worst,
            "mildest": mildest, "near_boundary": near}


def build(folder: str, now: datetime) -> tuple[str, dict, Path, Path]:
    vdir = VERIFIED / folder
    recipe = parse_recipe()
    envelope = read_json(RAW / "run-envelope.json")
    if envelope.get("live_calls") or envelope.get("network") or envelope.get("database_writes"):
        raise Refuse("the run envelope declares live calls, network or database writes: the recipe's stop condition; no approval record exists")
    validated = read_json(vdir / "validated.json")
    quality = read_json(vdir / "quality-check.json")
    spath = vdir / "stress-results.json"
    results = read_json(spath)["results"] if spath.exists() else []
    acc_ids = sorted(a["id"] for a in validated["accepted"])
    failed_ids = sorted({f["id"] for f in quality.get("failures", [])})
    if sorted(quality["verified_records"] + quality.get("handed_off", []) + failed_ids) != acc_ids:
        raise Refuse("quality-check.json does not account for exactly the requests step 3 accepted (re-run step 4)")
    if quality["record_count"] != len(acc_ids) or sorted(r["id"] for r in results) != acc_ids:
        raise Refuse("quality-check.json, validated.json and stress-results.json disagree about which requests there are (re-run steps 3 to 5)")
    prov_p, run_p = latest("provenance"), latest("run-approved-tools")
    prov = read_json(prov_p) if prov_p else {}
    run = read_json(run_p) if run_p else {}
    d = describe(results)
    day = now.date().isoformat()
    tag = "" if folder == "clean" else f"-{folder}"
    report_path = REPO / "reports" / "generated" / f"{SLUG}-{day}{tag}.md"
    log_path = LOGS / f"{SLUG}-{day}{tag}.json"
    gates = evaluate_gates(recipe, envelope, folder)
    steps = recipe["steps"]
    open_steps = [s for s in steps if s["open"]]
    closed_steps = [s["n"] for s in steps if not s["open"]]
    todos = [f"Step {s['n']} ({s['name']}): `[TODO: DEV]` {s['script']}" for s in open_steps] + [f"Script mapping: `{m}`" for m in recipe["mapping_todos"]]
    rejected = validated["rejected"]
    n_in = len(acc_ids) + len(rejected)
    reasons_of = lambda r: r.get("reasons") or r.get("reason") or []
    source_files = [rel(RECIPE), rel(RAW / "run-envelope.json")] + sorted(rel(p) for p in (RAW / "sample" / folder).glob("*.json"))
    stops = evaluate_stop_conditions(recipe, envelope, folder, run, source_files, validated)
    n_trig = sum(1 for x in stops if x["triggered"])
    if folder == "clean":
        approve = bool(not failed_ids and not quality["duplicates"] and not rejected and not n_trig)
    else:
        approve = False
    fix = bool(rejected or failed_ids or quality["duplicates"])
    levels = d["levels"]

    # ---------------------------------------------------------------- the report
    R = [f"# Scenario Stress Testing Agent: sample run `{folder}`, {day}", "",
         "**Reader:** the domain lead or human boss responsible for accepting the `ScenarioStressTestingAgent` run.  ",
         "**Decision enabled:** approve the run for the next phase, request source or schema fixes, or block live execution.", ""]
    sec = {}
    sec["Run summary"] = [f"- {n_in} request(s) read from the `{folder}` sample folder; {len(acc_ids)} accepted at step 3, {len(rejected)} rejected there.",
                          f"- {len(d['ran'])} stress-tested at step 5, {len(results) - len(d['ran'])} stopped at the Groq handoff; {len(quality['verified_records'])} reconciled on every step-4 check, "
                          f"{len(failed_ids)} failed one, {len(quality['duplicates'])} duplicate group(s), {len(quality['flags'])} advisory flag(s).",
                          f"- Stop conditions: {n_trig} of {len(stops)} triggered" + (" (" + "; ".join(x["condition"].split(":")[0][:60] for x in stops if x["triggered"]) + ")." if n_trig else "; each is judged from evidence in the agent log."),
                          "- Mode **sample**: every request is invented; no Groq call, Alpha Vantage request, webhook reply, database write or credential was used."]
    sec["Purpose"] = [recipe["purpose"] or "(the recipe's Purpose section was not found)"]
    sec["Source inventory"] = ["| Source | What it is | Where |", "|---|---|---|",
                               f"| the recipe | intent, steps, contracts (status `{recipe['front'].get('status')}`, version {recipe['front'].get('recipe_version')}) | `recipes/{SLUG}.md` |",
                               f"| sample corpus | {n_in} invented requests in `{folder}/` with a SHA-256 manifest | `data/raw/{SLUG}/sample/{folder}/` |",
                               f"| run envelope | declares sample mode and that nothing live runs | `data/raw/{SLUG}/run-envelope.json` |",
                               "| the original workflow | the n8n workflow the recipe was converted from (read by step 1 only) | named in the recipe's Inputs and Provenance |"]
    sec["Inputs used"] = [f"- Step 3: `{rel(vdir / 'validated.json')}`", f"- Step 5: `{rel(spath)}`" if spath.exists() else "- Step 5: no stress results for this folder (nothing was accepted)",
                          f"- Step 4: `{rel(vdir / 'quality-check.json')}`", f"- Step 1 log: `{rel(prov_p)}`" if prov_p else "- Step 1 log: none found",
                          f"- Step 5 log: `{rel(run_p)}`" if run_p else "- Step 5 log: none found"]
    sec["Phase-gate results"] = ["| Gate | Result | Evidence |", "|---|---|---|"] + [f"| {g['gate']} | {g['result']} | {g['evidence']} |" for g in gates]
    sec["Steps completed"] = [f"| {s['n']} | {s['name']} | {'closed' if not s['open'] else 'OPEN (`[TODO: DEV]`)'} | `{s['script']}` |" for s in steps]
    sec["Steps completed"] = ["| Step | Name | Status | Script |", "|---|---|---|---|"] + sec["Steps completed"]
    sec["Records seen"] = [f"- Requests in: {n_in}. Accepted: {len(acc_ids)}. Stress-tested: {len(d['ran'])}. Handed off, not run: {len(quality.get('handed_off', []))}.",
                           f"- Risk levels over the {len(d['ran'])} stress-tested requests: CRITICAL {levels['CRITICAL']}, HIGH {levels['HIGH']}, MODERATE {levels['MODERATE']}, LOW {levels['LOW']}."]
    sec["Rejects"] = ([f"- `{r['id']}` at step 3: " + "; ".join(str(x) for x in reasons_of(r)) for r in rejected] +
                      [f"- `{f['id']}` at step 4 ({f['check']}): {f['detail']}" for f in quality.get("failures", [])]) or ["- none"]
    sec["Duplicates"] = [f"- {x['kind']}: {', '.join('`' + i + '`' for i in x['ids'])}: {x['detail']}" for x in quality["duplicates"]] or ["- none found, by id or by content"]
    sec["Flags"] = [f"- `{f['id']}` **{f['flag']}**: {f['detail']}" for f in quality["flags"]] or ["- none"]
    sec["Typed TODOs"] = [f"- {t}" for t in todos] or ["- none open"]
    appr = sorted((LOGS / "gate-decisions").glob(f"{SLUG}-*.json")) if (LOGS / "gate-decisions").exists() else []
    sec["Human approvals"] = ([f"- `{rel(p)}`" for p in appr] or [f"- None recorded. No approval record exists at `logs/gate-decisions/{SLUG}-approval.json`, so nothing live is approved, and a named human has not yet cleared the sample run for the next phase."])
    vf = [f"- {len(quality['verified_records'])} of {len(d['ran'])} stress results reconcile on all {len(quality['checks_run'])} step-4 checks: each position's shock re-derived from the workflow's own template shocks, losses and totals added up, drawdown and risk level re-derived, ordering and weights checked (`{rel(vdir / 'quality-check.json')}`)."] if d["ran"] else \
         ["- No request was accepted, so no stress result exists to verify."]
    if d["worst"]:
        w, m = d["worst"], d["mildest"]
        vf += [f"- Largest drawdown: `{w['id']}`, {w['result']['drawdown_pct']}% under {w['result']['scenario_name']} ({w['result']['risk_level']}). Smallest: `{m['id']}`, {m['result']['drawdown_pct']}% ({m['result']['risk_level']}).",
               f"- The step-5 log's risk-level counts {run.get('risk_levels')} " + ("match" if run.get("risk_levels") == levels else "DIFFER from") + " the counts recomputed here from the results."]
    if prov:
        vf.append(f"- Step 1's log: node table match {prov.get('node_table_match')}, workflow wiring match {prov.get('chain_match')}, ported nodes ok {prov.get('ported_nodes_ok')}, fixtures ok {prov.get('fixtures_ok')}.")
    if rejected:
        vf.append(f"- {len(rejected)} of {n_in} requests were rejected at step 3 with a reason each; none reached the stress-test chain.")
    sec["Verified findings"] = vf
    inf = ["- These are readings of an invented sample, not claims about real portfolios and not a judgment of the template shocks or risk lines."]
    if d["by_scenario"]:
        inf.append("- Average drawdown by scenario in this sample (n in brackets): " + "; ".join(f"{k} {v[0]}% ({v[1]})" for k, v in d["by_scenario"].items()) + ".")
        inf.append(f"- {len(d['near_boundary'])} of {len(d['ran'])} results sit within 5 points of a risk line ({', '.join('`' + i + '`' for i in d['near_boundary']) or 'none'}); a small change in the shocks would move their level, so those levels should be read as soft.")
    else:
        inf.append("- Nothing ran, so there is nothing to read.")
    sec["Inferred findings"] = inf
    dec = [f"- **Approve for the next phase (sample mode only): {'YES' if approve else 'NO'}.** " +
           ("Every accepted request reconciled, no duplicates, nothing rejected; the next phase is still a sample run, and a named human has to clear it." if approve
            else "This folder holds requests the gate rejects on purpose; nothing ran, so there is nothing to approve." if folder != "clean"
            else f"{n_trig} stop condition(s) triggered; see the agent log's stop_conditions for the evidence." if n_trig else "A request was rejected, failed a check or duplicated another; see the sections above."),
           f"- **Request source or schema fixes: {'YES' if fix else 'NO'}.** " + (f"{len(rejected)} reject(s), {len(failed_ids)} failed check(s), {len(quality['duplicates'])} duplicate group(s) are listed above." if fix else "None needed for the sample corpus."),
           f"- **Block live execution: YES.** No approval record exists; step 2 (ingest) is still open, the Alpha Vantage request, the Groq call and the webhook reply are only recorded handoffs, and the custom-scenario route stops at the handoff."]
    sec["Decision recommendation"] = dec
    for name in SECTIONS:
        R += [f"## {name}", ""] + sec[name] + [""]
    report = "\n".join(R)

    # ---------------------------------------------------------------- the agent log, with the contract's fields
    log = {"workflow": "ScenarioStressTestingAgent", "run_id": f"sample-{day}-{folder}", "mode": "sample", "steps_completed": closed_steps,
           "records_seen": n_in, "rejects": [{"id": r["id"], "stage": "step 3", "reasons": reasons_of(r)} for r in rejected] + [{"id": f["id"], "stage": f"step 4 ({f['check']})", "reasons": [f["detail"]]} for f in quality.get("failures", [])],
           "duplicates": quality["duplicates"], "flags": quality["flags"], "stop_conditions": stops, "todo_items": todos,
           "source_files": source_files,
           "gate_decisions": [{"gate": g["gate"], "result": g["result"]} for g in gates] + [{"gate": "human clearance", "result": "none recorded"}],
           "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "raw_output_paths": [rel(RAW / "run-envelope.json")],
           "verified_output_paths": [rel(p) for p in (vdir / "validated.json", spath, vdir / "quality-check.json", vdir / "quality-notes.md") if p.exists()],
           "report_path": rel(report_path)}
    return report, log, report_path, log_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--folder", default="clean", choices=("clean", "defective"))
    ap.add_argument("--now", default=None, help="pin the clock (ISO, e.g. 2026-11-01T09:00:00Z)")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    now = datetime.fromisoformat(args.now.replace("Z", "+00:00")) if args.now else datetime.now(timezone.utc)
    try:
        report, log, rpath, lpath = build(args.folder, now)
    except Refuse as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
    # the report gate (gate 6) is judged on the files as written
    problems = [s for s in SECTIONS if f"## {s}" not in report] + [k for k in ("workflow", "run_id", "mode", "steps_completed", "records_seen", "rejects", "duplicates", "flags",
                "stop_conditions", "todo_items", "source_files", "gate_decisions", "generated_at", "raw_output_paths", "verified_output_paths", "report_path") if k not in log]
    gate6 = "PASS" if not problems else f"FAIL ({problems})"
    report = report.replace("| 6 Report gate | PENDING | evaluated after the report and agent log are written |",
                            f"| 6 Report gate | {gate6} | the agent log has its {len(log)} required fields and the report its {len(SECTIONS)} sections |")
    log["gate_decisions"] = [dict(g, result=gate6) if g["gate"] == "6 Report gate" else g for g in log["gate_decisions"]]
    if not args.no_write:
        rpath.parent.mkdir(parents=True, exist_ok=True)
        rpath.write_text(report if report.endswith("\n") else report + "\n")
        lpath.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n")
    print(f"report {args.folder}: {log['records_seen']} request(s), gate 6 {gate6}" + ("" if args.no_write else f" -> {rel(rpath)} and {rel(lpath)}"))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
