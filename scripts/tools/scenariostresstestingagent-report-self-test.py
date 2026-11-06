#!/usr/bin/env python3
"""Purpose: Evidence for steps 4 and 6 of recipes/scenariostresstestingagent.md: run every check and record each one, including deliberate
         breaks that MUST be caught. A check passes only if the observed result is the expected one. Steps 1, 3 and 5 have their own
         evidence in scenariostresstestingagent-self-test.py; this file does not repeat it.
Input: the repo (its recipe, sample corpus, verified files and the step 4 and step 6 scripts). Python standard library only.
Output: logs/scenariostresstestingagent/report-self-test-results.json and report-self-test-results.md.
Side effects: writes those two files. Every break works on a temporary copy of the tree; the repo's own files are never touched.
Idempotent: Yes (no clock in the results).
Errors: exit 1 if any check does not come out as expected.
Recipe: recipes/scenariostresstestingagent.md
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SLUG = "scenariostresstestingagent"
REPO = Path(__file__).resolve().parents[2]
Q = f"scripts/gigo/{SLUG}-transform-quality-check.py"
R = f"scripts/tools/{SLUG}-produce-human-report.py"
NOW = "2026-11-01T09:00:00Z"
SECTIONS = ["Run summary", "Purpose", "Source inventory", "Inputs used", "Phase-gate results", "Steps completed", "Records seen", "Rejects",
            "Duplicates", "Flags", "Typed TODOs", "Human approvals", "Verified findings", "Inferred findings", "Decision recommendation"]
LOG_FIELDS = ["workflow", "run_id", "mode", "steps_completed", "records_seen", "rejects", "duplicates", "flags", "stop_conditions", "todo_items",
              "source_files", "gate_decisions", "generated_at", "raw_output_paths", "verified_output_paths", "report_path"]
CLEAN = f"data/verified/{SLUG}/clean"


def tree() -> Path:
    """a temporary copy of just what the two steps need; the scripts find their repo from their own location."""
    t = Path(tempfile.mkdtemp(prefix="stress-st-"))
    for rel in ("scripts/gigo", "scripts/tools"):
        (t / rel).mkdir(parents=True)
        for p in (REPO / rel).glob(f"{SLUG}-*.py"):
            shutil.copy(p, t / rel / p.name)
    (t / "recipes").mkdir()
    shutil.copy(REPO / "recipes" / f"{SLUG}.md", t / "recipes" / f"{SLUG}.md")
    shutil.copytree(REPO / "data" / "raw" / SLUG, t / "data" / "raw" / SLUG)
    shutil.copytree(REPO / "data" / "verified" / SLUG, t / "data" / "verified" / SLUG)
    (t / "logs").mkdir()
    for p in (REPO / "logs").glob(f"{SLUG}-*-2026-10-25.json"):
        shutil.copy(p, t / "logs" / p.name)
    (t / "reports" / "generated").mkdir(parents=True)
    return t


def run(t: Path, script: str, *args: str):
    p = subprocess.run([sys.executable, str(t / script), *args], capture_output=True, text=True, cwd=str(t))
    return p.returncode, p.stdout + p.stderr


def jload(t: Path, rel: str):
    return json.loads((t / rel).read_text())


def jsave(t: Path, rel: str, doc) -> None:
    (t / rel).write_text(json.dumps(doc, indent=2) + "\n")


def mutate_results(t: Path, rid: str, fn) -> None:
    d = jload(t, f"{CLEAN}/stress-results.json")
    for r in d["results"]:
        if r["id"] == rid:
            fn(r["result"])
    jsave(t, f"{CLEAN}/stress-results.json", d)


results: list[dict] = []


def check(name: str, expected: str, observed: str, ok: bool) -> None:
    results.append({"check": name, "expected": expected, "observed": observed, "passed": bool(ok)})
    print(f"{'ok  ' if ok else 'FAIL'}  {name}")


def failures_of(t: Path) -> set[str]:
    return {f["check"] for f in jload(t, f"{CLEAN}/quality-check.json")["failures"]}


def main() -> int:
    # ------------------------------------------------------------------ step 4, as it should work
    t = tree()
    code, out = run(t, Q)
    qc = jload(t, f"{CLEAN}/quality-check.json")
    check("4 clean set: exit 0, 11 reconciled, 1 handed off, no failures, no duplicates", "exit 0; 11; 1; 0; 0",
          f"exit {code}; {len(qc['verified_records'])}; {len(qc['handed_off'])}; {len(qc['failures'])}; {len(qc['duplicates'])}",
          code == 0 and len(qc["verified_records"]) == 11 and len(qc["handed_off"]) == 1 and not qc["failures"] and not qc["duplicates"])
    kinds = {f["flag"] for f in qc["flags"]}
    want = {"default-sector", "rescaled", "majority-holding", "scenario-defaulted", "handoff", "on-threshold"}
    check("4 clean set: the corpus's designed edge cases raise their flags", ", ".join(sorted(want)), ", ".join(sorted(kinds)), kinds == want)
    first = (t / CLEAN / "quality-check.json").read_bytes()
    run(t, Q)
    check("4 idempotent: a second run gives the same bytes", "identical", "identical" if (t / CLEAN / "quality-check.json").read_bytes() == first else "different",
          (t / CLEAN / "quality-check.json").read_bytes() == first)
    code, out = run(t, Q, "--verified-dir", f"data/verified/{SLUG}/defective")
    qd = jload(t, f"data/verified/{SLUG}/defective/quality-check.json")
    check("4 defective set: exit 1, 0 verified, 10 rejects", "exit 1; 0; 10", f"exit {code}; {len(qd['verified_records'])}; {len(qd['rejects'])}",
          code == 1 and not qd["verified_records"] and len(qd["rejects"]) == 10)
    shutil.rmtree(t)

    # ------------------------------------------------------------------ step 4, deliberate breaks of a result (eight ways)
    rid = "c01-tech-crash-semiconductor-heavy"
    breaks = [
        ("a position's loss is off by 1", lambda r: r["all_positions"][0].__setitem__("loss", r["all_positions"][0]["loss"] + 1), "position-loss"),
        ("a position's shock_pct is off by 1", lambda r: r["all_positions"][0].__setitem__("shock_pct", r["all_positions"][0]["shock_pct"] + 1), "position-shock"),
        ("total_loss is off by 5", lambda r: r.__setitem__("total_loss", r["total_loss"] + 5), "total-loss"),
        ("final_portfolio_value is off by 10", lambda r: r.__setitem__("final_portfolio_value", r["final_portfolio_value"] + 10), "final-value"),
        ("risk_level says LOW for a 78% drawdown", lambda r: r.__setitem__("risk_level", "LOW"), "risk-level"),
        ("top_losers in the wrong order", lambda r: r.__setitem__("top_losers", list(reversed(r["top_losers"]))), "top-losers"),
        ("a weight changed so the book adds to 0.9", lambda r: r["all_positions"][0].__setitem__("weight", round(r["all_positions"][0]["weight"] - 0.1, 4)), "weights-sum"),
        ("scenario_name is not the template's", lambda r: r.__setitem__("scenario_name", "Tech Sector Rally"), "scenario-name"),
    ]
    for label, fn, want_check in breaks:
        t = tree()
        mutate_results(t, rid, fn)
        code, out = run(t, Q)
        got = failures_of(t)
        check(f"4 break caught: {label}", f"exit 1; failure `{want_check}` recorded", f"exit {code}; {sorted(got)}", code == 1 and want_check in got)
        shutil.rmtree(t)

    # ------------------------------------------------------------------ step 4, duplicates and a missing result
    t = tree()
    v = jload(t, f"{CLEAN}/validated.json")
    v["accepted"].append(json.loads(json.dumps(v["accepted"][0])))
    jsave(t, f"{CLEAN}/validated.json", v)
    code, out = run(t, Q)
    dups = jload(t, f"{CLEAN}/quality-check.json")["duplicates"]
    check("4 break caught: the same id twice", "exit 1; a duplicate of kind `id`", f"exit {code}; {[d['kind'] for d in dups]}", code == 1 and any(d["kind"] == "id" for d in dups))
    shutil.rmtree(t)
    t = tree()
    v = jload(t, f"{CLEAN}/validated.json")
    twin = json.loads(json.dumps(v["accepted"][0]))
    twin["id"] = "c99-same-book-another-name"
    v["accepted"].append(twin)
    jsave(t, f"{CLEAN}/validated.json", v)
    code, out = run(t, Q)
    dups = jload(t, f"{CLEAN}/quality-check.json")["duplicates"]
    check("4 break caught: the same holdings and scenario under another id", "exit 1; a duplicate of kind `content`", f"exit {code}; {[d['kind'] for d in dups]}",
          code == 1 and any(d["kind"] == "content" for d in dups))
    shutil.rmtree(t)
    t = tree()
    d = jload(t, f"{CLEAN}/stress-results.json")
    d["results"] = [r for r in d["results"] if r["id"] != rid]
    jsave(t, f"{CLEAN}/stress-results.json", d)
    code, out = run(t, Q)
    check("4 break caught: an accepted request with no step-5 result", "exit 1; failure `ran`", f"exit {code}; {sorted(failures_of(t))}", code == 1 and "ran" in failures_of(t))
    shutil.rmtree(t)
    t = tree()
    (t / CLEAN / "quality-check.json").unlink()
    (t / CLEAN / "validated.json").write_text("{not json")
    code, out = run(t, Q)
    wrote = (t / CLEAN / "quality-check.json").exists()
    check("4 refuses an unreadable validated.json: exit 2, nothing written", "exit 2; quality-check.json not written", f"exit {code}; written: {wrote}", code == 2 and not wrote and "cannot read" in out)
    shutil.rmtree(t)

    # ------------------------------------------------------------------ step 6, as it should work
    t = tree()
    run(t, Q)
    code, out = run(t, R, "--now", NOW)
    rp = t / "reports" / "generated" / f"{SLUG}-2026-11-01.md"
    lp = t / "logs" / f"{SLUG}-2026-11-01.json"
    rep = rp.read_text() if rp.exists() else ""
    heads = re.findall(r"^## (.+)$", rep, flags=re.M)
    check("6 clean report: exit 0 and the Output Contract's fifteen sections, in order", "exit 0; " + ", ".join(SECTIONS), f"exit {code}; {heads}", code == 0 and heads == SECTIONS)
    log = json.loads(lp.read_text()) if lp.exists() else {}
    check("6 agent log: the contract's sixteen fields", ", ".join(LOG_FIELDS), ", ".join(log.keys()), list(log.keys()) == LOG_FIELDS)
    qc = jload(t, f"{CLEAN}/quality-check.json")
    check("6 the report's counts equal the files' counts", f"12 requests in; {len(qc['verified_records'])} reconciled; {len(qc['flags'])} flags",
          "; ".join(re.findall(r"(\d+ request\(s\) read|\d+ reconciled|\d+ advisory flag)", rep)),
          f"12 request(s) read" in rep and f"{len(qc['verified_records'])} reconciled" in rep and f"{len(qc['flags'])} advisory flag" in rep and log["records_seen"] == 12)
    check("6 the recommendation always blocks live execution while no approval record exists", "contains 'Block live execution: YES'",
          "yes" if "Block live execution: YES" in rep else "no", "Block live execution: YES" in rep)
    check("6 gates: 4 reads 5 of 6 scripts with step 2 open; 6 passes", "5 of 6; step(s) 2; gate 6 PASS",
          ("5 of 6 step scripts exist; step(s) 2" in rep, "6 Report gate | PASS" in rep), "5 of 6 step scripts exist; step(s) 2" in rep and "6 Report gate | PASS" in rep)
    stops = log.get("stop_conditions", [])
    ev = [x.get("evidence", "") for x in stops]
    check("6 stop conditions: four judged from evidence, none triggered, each with its own evidence", "4 conditions; none triggered; four different evidence strings, none the old placeholder",
          f"{len(stops)} conditions; triggered: {[x.get('triggered') for x in stops]}; distinct evidence: {len(set(ev))}",
          len(stops) == 4 and not any(x.get("triggered") for x in stops) and len(set(ev)) == 4 and not any("not triggered in sample mode" in e for e in ev))
    check("6 the credential scan does not flag the report script itself", "condition 1 says none found and names no script", ev[0][-80:] if ev else "no evidence",
          bool(ev) and ev[0].endswith("none found") and "produce-human-report" not in ev[0])
    check("6 the person's page and the machine's page agree on stop conditions", "report: 'Stop conditions: 0 of 4 triggered'; log: 0 triggered",
          f"report line present: {'Stop conditions: 0 of 4 triggered' in rep}; log triggered: {sum(1 for x in stops if x.get('triggered'))}",
          "Stop conditions: 0 of 4 triggered" in rep and sum(1 for x in stops if x.get("triggered")) == 0)
    b1 = (rp.read_bytes(), lp.read_bytes())
    run(t, R, "--now", NOW)
    check("6 idempotent: a second run (clock pinned) gives the same bytes", "identical", "identical" if (rp.read_bytes(), lp.read_bytes()) == b1 else "different", (rp.read_bytes(), lp.read_bytes()) == b1)
    code, out = run(t, R, "--folder", "defective", "--now", NOW)
    run(t, Q, "--verified-dir", f"data/verified/{SLUG}/defective")
    code, out = run(t, R, "--folder", "defective", "--now", NOW)
    drep = (t / "reports" / "generated" / f"{SLUG}-2026-11-01-defective.md").read_text() if (t / "reports" / "generated" / f"{SLUG}-2026-11-01-defective.md").exists() else ""
    check("6 defective set: exit 0, nothing ran, nothing to approve", "exit 0; 'Approve for the next phase (sample mode only): NO'",
          f"exit {code}; {'NO' if 'sample mode only): NO' in drep else 'not NO'}", code == 0 and "sample mode only): NO" in drep and "No request was accepted" in drep)
    shutil.rmtree(t)

    # ------------------------------------------------------------------ step 6, a deliberate break of the stop-condition check
    t = tree()
    # built from pieces at run time, so that no script in the repo contains a credential-shaped literal, this one included
    planted = "api_" + "key = " + '"' + "sk" + "-" + "abcdefghijklmnopqrstuvwxyz0123" + '"' + "\n"
    (t / "scripts" / "tools" / f"{SLUG}-planted-credential.py").write_text(planted)
    run(t, Q)
    code, out = run(t, R, "--now", NOW)
    prep = (t / "reports" / "generated" / f"{SLUG}-2026-11-01.md").read_text() if (t / "reports" / "generated" / f"{SLUG}-2026-11-01.md").exists() else ""
    plog = json.loads((t / "logs" / f"{SLUG}-2026-11-01.json").read_text()) if (t / "logs" / f"{SLUG}-2026-11-01.json").exists() else {"stop_conditions": []}
    pst = plog["stop_conditions"]
    check("6 break caught: a hardcoded key planted in a script trips stop condition 1, both pages say so, and approve turns NO",
          "log: condition 1 triggered, others not; report: 'Stop conditions: 1 of 4 triggered'; 'sample mode only): NO'",
          f"exit {code}; triggered: {[x.get('triggered') for x in pst]}; report line: {'Stop conditions: 1 of 4 triggered' in prep}; approve NO: {'sample mode only): NO' in prep}",
          code == 0 and [x.get("triggered") for x in pst] == [True, False, False, False] and "Stop conditions: 1 of 4 triggered" in prep and "sample mode only): NO" in prep
          and "planted-credential" in pst[0].get("evidence", ""))
    shutil.rmtree(t)

    # ------------------------------------------------------------------ step 6, refusals (exit 2, nothing written)
    for label, setup in [
        ("step 4's output is missing", lambda t: (t / CLEAN / "quality-check.json").unlink()),
        ("step 4's output does not account for the accepted requests", lambda t: jsave(t, f"{CLEAN}/quality-check.json", dict(jload(t, f"{CLEAN}/quality-check.json"), verified_records=jload(t, f"{CLEAN}/quality-check.json")["verified_records"][1:]))),
        ("the run envelope declares live calls", lambda t: jsave(t, f"data/raw/{SLUG}/run-envelope.json", dict(jload(t, f"data/raw/{SLUG}/run-envelope.json"), live_calls=True))),
    ]:
        t = tree()
        run(t, Q)
        setup(t)
        code, out = run(t, R, "--now", NOW)
        wrote = (t / "reports" / "generated" / f"{SLUG}-2026-11-01.md").exists()
        check(f"6 refuses when {label}", "exit 2; no report written", f"exit {code}; report written: {wrote}", code == 2 and not wrote)
        shutil.rmtree(t)

    ok = all(r["passed"] for r in results)
    outdir = REPO / "logs" / SLUG
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "report-self-test-results.json").write_text(json.dumps({"recipe": SLUG, "steps": [4, 6], "checks": results, "all_passed": ok}, indent=2, ensure_ascii=False) + "\n")
    md = [f"# Self-test, steps 4 and 6: {SLUG}", "",
          f"{sum(r['passed'] for r in results)} of {len(results)} checks came out as expected. A check passes only if what was observed is what was expected; the deliberate "
          "breaks are meant to be caught. Every break ran on a temporary copy of the tree.", "", "| Check | Expected | Observed | Result |", "|---|---|---|---|"]
    md += [f"| {r['check']} | {r['expected']} | {str(r['observed']).replace('|', '/')} | {'as expected' if r['passed'] else 'NOT as expected'} |" for r in results]
    (outdir / "report-self-test-results.md").write_text("\n".join(md) + "\n")
    print(f"\n{sum(r['passed'] for r in results)}/{len(results)} checks as expected")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
