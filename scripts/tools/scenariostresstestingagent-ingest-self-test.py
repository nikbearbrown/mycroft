#!/usr/bin/env python3
"""Purpose: Evidence for step 2 of recipes/scenariostresstestingagent.md: run every check and record each one, including deliberate
         breaks that MUST be caught. A check passes only if the observed result is the expected one. Steps 1, 3 and 5 have their own
         evidence in scenariostresstestingagent-self-test.py and steps 4 and 6 in scenariostresstestingagent-report-self-test.py; this file
         does not repeat it.
Input: the repo (its recipe, run envelope, sample corpus with its frozen manifest, the workflow JSON the recipe declares, and the step-2
       script). Python standard library only.
Output: logs/scenariostresstestingagent/ingest-self-test-results.json and ingest-self-test-results.md.
Side effects: writes those two files. Every check works on a temporary copy of the tree; the repo's own files are never touched.
Idempotent: Yes (no clock in the results).
Errors: exit 1 if any check does not come out as expected.
Recipe: recipes/scenariostresstestingagent.md
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SLUG = "scenariostresstestingagent"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "ingest" / f"{SLUG}-ingest-inputs.py"
NOW = "2026-11-09T00:00:00+00:00"
INGEST = f"data/raw/{SLUG}/ingest"
# dummy values, assembled at run time so no credential-shaped text sits in this file
CREDS = {"GROQ_API_KEY": "-".join(["dummy", "groq", "value", "0123456789"]), "ALPHA_VANTAGE_API_KEY": "-".join(["dummy", "alpha", "value", "9876543210"])}
results: list[dict] = []


def declared_workflow() -> str:
    text = (REPO / "recipes" / f"{SLUG}.md").read_text(encoding="utf-8")
    return re.search(r"^\| Original workflow JSON \| JSON \| `([^`]+)` \|", text, re.M).group(1)


def tree() -> Path:
    """A scratch repo: the recipe, the run envelope and sample corpus (without any earlier ingest output), the workflow, nothing else."""
    t = Path(tempfile.mkdtemp(prefix="stress-st2-"))
    (t / "recipes").mkdir()
    shutil.copy(REPO / "recipes" / f"{SLUG}.md", t / "recipes" / f"{SLUG}.md")
    shutil.copytree(REPO / "data" / "raw" / SLUG, t / "data" / "raw" / SLUG, ignore=shutil.ignore_patterns("ingest"))
    wf = declared_workflow()
    (t / wf).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(REPO / wf, t / wf)
    return t


def clean_env() -> dict:
    return {k: v for k, v in os.environ.items() if k not in CREDS}


def run(t: Path, *args: str, env: dict | None = None):
    return subprocess.run([sys.executable, str(SCRIPT), "--repo", str(t), "--now", NOW, *args], capture_output=True, text=True, env=env or clean_env())


def files(t: Path) -> set[str]:
    return {str(p.relative_to(t)) for p in t.rglob("*") if p.is_file()}


def jload(t: Path, rel: str):
    return json.loads((t / rel).read_text(encoding="utf-8"))


def jsave(t: Path, rel: str, doc) -> None:
    (t / rel).write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def check(name: str, expected: str, observed: str, ok: bool) -> None:
    results.append({"check": name, "expected": expected, "observed": observed, "passed": bool(ok)})


def sample(t: Path) -> Path:
    return t / "data" / "raw" / SLUG / "sample"


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def reasons(r) -> str:
    return r.stdout


def main() -> int:
    # ---- the clean run -------------------------------------------------------------------------------------------------------
    t = tree()
    before = files(t)
    r = run(t)
    out = {f: jload(t, f"{INGEST}/{f}/ingested.json") for f in ("clean", "defective")} if r.returncode == 0 else {}
    sc = jload(t, f"{INGEST}/source-check.json") if r.returncode == 0 else {}
    manifest = jload(t, f"data/raw/{SLUG}/sample/manifest.json")
    check("2 run on the sample corpus: exit 0 and the four files written", "exit 0; 4 files under ingest/",
          f"exit {r.returncode}; {len(files(t) - before)} new files", r.returncode == 0 and len(files(t) - before) == 4)
    check("2 every request is ingested: 12 clean, 10 defective, no rejects", "12; 10; 0; 0",
          f"{out['clean']['record_count']}; {out['defective']['record_count']}; {len(out['clean']['rejects'])}; {len(out['defective']['rejects'])}",
          out["clean"]["record_count"] == 12 and out["defective"]["record_count"] == 10 and not out["clean"]["rejects"] and not out["defective"]["rejects"])
    field_ok = all({"records", "source_name", "source_type", "fetched_at", "sample_mode", "rejects"} <= set(d) for d in out.values())
    check("2 the recipe's six step-2 output fields are present in both files", "records, source_name, source_type, fetched_at, sample_mode, rejects",
          "all present" if field_ok else "missing", field_ok)
    check("2 sample_mode is true and fetched_at is the pinned clock", "true; " + NOW, f"{out['clean']['sample_mode']}; {out['clean']['fetched_at']}",
          out["clean"]["sample_mode"] is True and out["clean"]["fetched_at"] == NOW)
    same_bytes = all(rec["body"] == json.loads((sample(t) / rec["record_id"]).read_text()) and rec["sha256"] == digest(sample(t) / rec["record_id"]) == manifest["files"][rec["record_id"]]["sha256"]
                     for d in out.values() for rec in d["records"])
    check("2 each record is its fixture, unchanged: body equal, SHA-256 equal to the manifest's", "22 of 22 equal", "22 of 22 equal" if same_bytes else "a record differs", same_bytes)
    ids = [rec["record_id"] for d in out.values() for rec in d["records"]]
    check("2 record ids are unique and listed in order", "22 unique, sorted per folder", f"{len(set(ids))} unique",
          len(set(ids)) == 22 and all([r_["record_id"] for r_ in d["records"]] == sorted(r_["record_id"] for r_ in d["records"]) for d in out.values()))
    defect_ok = all(rec["record_id"].startswith("defective/") for rec in out["defective"]["records"])
    check("2 a defective request ingests like any other (valid JSON); its shape is step 3's work", "10 read, none judged here", f"{out['defective']['record_count']} read", defect_ok and out["defective"]["record_count"] == 10)
    by = {s["node"]: s for s in sc["sources"]}
    stat = {k: by[k]["status"] for k in by}
    check("2 the four sources: webhook available, chat skipped, Alpha Vantage and Groq approval-required",
          "Webhook Trigger available; When chat message received skipped; Fetch_Data approval-required; Groq Chat Model approval-required",
          "; ".join(f"{k} {v}" for k, v in sorted(stat.items())),
          stat == {"Webhook Trigger": "available", "When chat message received": "skipped", "Fetch_Data": "approval-required", "Groq Chat Model": "approval-required"})
    check("2 every source carries a reason, and none was contacted or approved", "reasons; live_call_performed false; approved_for_live_action false",
          "yes" if all(s["reason"] and s["live_call_performed"] is False and s["approved_for_live_action"] is False for s in sc["sources"]) else "no",
          all(s["reason"] and s["live_call_performed"] is False and s["approved_for_live_action"] is False for s in sc["sources"]))
    check("2 the handoff condition is met and no problems are listed", "true; none", f"{sc['handoff_condition_met']}; {sc['problems']}", sc["handoff_condition_met"] is True and not sc["problems"])
    check("2 credential names are reported as not set when the environment has none", "False; False",
          f"{by['Fetch_Data']['credential_env']} {by['Fetch_Data']['credential_present']}; {by['Groq Chat Model']['credential_env']} {by['Groq Chat Model']['credential_present']}",
          by["Fetch_Data"]["credential_env"] == "ALPHA_VANTAGE_API_KEY" and by["Groq Chat Model"]["credential_env"] == "GROQ_API_KEY"
          and by["Fetch_Data"]["credential_present"] is False and by["Groq Chat Model"]["credential_present"] is False)
    created = files(t) - before
    check("2 only files under data/raw/<slug>/ingest/ were created", "4 files, all under ingest/", f"{len(created)} files; outside: {sorted(p for p in created if not p.startswith(INGEST))}",
          created and all(p.startswith(INGEST) for p in created))
    a = {p: (t / p).read_bytes() for p in created}
    run(t)
    check("2 idempotent: a second run with the clock pinned gives the same bytes", "identical", "identical" if all((t / p).read_bytes() == a[p] for p in created) else "differs",
          all((t / p).read_bytes() == a[p] for p in created))
    t2 = tree(); b2 = files(t2); r2 = run(t2, "--no-write")
    check("2 --no-write writes nothing", "exit 0; no new file", f"exit {r2.returncode}; {len(files(t2) - b2)} new", r2.returncode == 0 and files(t2) == b2)
    r3 = run(t2, "--sample", "--no-write")
    check("2 --sample is accepted and changes nothing; an unknown flag is refused by argparse (exit 2)", "exit 0; exit 2",
          f"exit {r3.returncode}; exit {run(t2, '--live').returncode}", r3.returncode == 0 and run(t2, "--live").returncode == 2)

    # ---- no network, no credential value ------------------------------------------------------------------------------------
    src = SCRIPT.read_text(encoding="utf-8")
    mod = ast.parse(src)
    banned = {"socket", "urllib", "http", "requests", "ssl", "subprocess", "ftplib", "smtplib", "asyncio", "shutil"}
    imported = {a_.name.split(".")[0] for n in ast.walk(mod) if isinstance(n, ast.Import) for a_ in n.names} | {n.module.split(".")[0] for n in ast.walk(mod) if isinstance(n, ast.ImportFrom) and n.module}
    check("2 the script imports nothing that can reach a network or start a process", "none of socket, urllib, http, requests, ssl, subprocess, ftplib, smtplib, asyncio, shutil",
          f"imports: {sorted(imported)}", not (imported & banned))
    parents = {c: p for p in ast.walk(mod) for c in ast.iter_child_nodes(p)}
    gets = [n for n in ast.walk(mod) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get"
            and isinstance(n.func.value, ast.Attribute) and n.func.value.attr == "environ"]
    subs = [n for n in ast.walk(mod) if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Attribute) and n.value.attr == "environ"]
    only_bool = bool(gets) and all(isinstance(parents.get(g), ast.Call) and getattr(parents[g].func, "id", "") == "bool" for g in gets)
    check("2 the environment is only asked whether a name is set: every os.environ.get sits inside bool(), none is read by subscript", "bool(os.environ.get(...)) only",
          f"{len(gets)} get call(s), all inside bool(): {only_bool}; subscripts: {len(subs)}", only_bool and not subs)
    t3 = tree(); r4 = run(t3, env={**clean_env(), **CREDS})
    sc3 = jload(t3, f"{INGEST}/source-check.json")
    by3 = {s["node"]: s for s in sc3["sources"]}
    check("2 with both credentials set, each is reported as set", "True; True", f"{by3['Fetch_Data']['credential_present']}; {by3['Groq Chat Model']['credential_present']}",
          by3["Fetch_Data"]["credential_present"] is True and by3["Groq Chat Model"]["credential_present"] is True and r4.returncode == 0)
    blob = "".join((t3 / p).read_text(errors="ignore") for p in files(t3) if p.startswith(INGEST)) + r4.stdout + r4.stderr
    leaked = [k for k, v in CREDS.items() if v in blob or v[:12] in blob]
    check("2 the credential values appear in no output file and not on the screen", "no value anywhere", f"found: {leaked or 'none'}", not leaked)

    # ---- deliberate breaks, each on its own copy ---------------------------------------------------------------------------
    def broken(name: str, expected: str, mutate, want: str, codes=(1,)):
        t_ = tree()
        mutate(t_)
        r_ = run(t_)
        check(f"2 break caught: {name}", expected, f"exit {r_.returncode}; {'reason named' if want in r_.stdout else 'reason NOT named'}",
              r_.returncode in codes and want in r_.stdout)
        return t_, r_

    def flip(t_: Path):
        p = sample(t_) / "clean" / "c01-tech-crash-semiconductor-heavy.json"
        p.write_bytes(p.read_bytes().replace(b"NVDA", b"NVDB", 1))
    tb, rb = broken("a fixture changed by one letter", "exit 1; 'differs from the SHA-256 frozen'", flip, "differs from the SHA-256 frozen")
    cb = jload(tb, f"{INGEST}/clean/ingested.json")
    check("2 the changed fixture is left out of the records and named in rejects; the other 11 still ingest", "11 records; 1 reject named c01",
          f"{cb['record_count']} records; rejects {[x['source_name'] for x in cb['rejects']]}", cb["record_count"] == 11 and [x["source_name"] for x in cb["rejects"]] == ["c01-tech-crash-semiconductor-heavy.json"])
    broken("a fixture deleted", "exit 1; 'listed in the frozen manifest but not on disk'", lambda t_: (sample(t_) / "defective" / "d03-holding-without-ticker.json").unlink(), "not on disk")
    broken("an unlisted fixture added", "exit 1; 'not in the frozen manifest'", lambda t_: (sample(t_) / "clean" / "c99-extra.json").write_text('{"body": {}}\n'), "not in the frozen manifest")

    def corrupt(t_: Path):
        p = sample(t_) / "clean" / "c02-rate-hike-mixed-book.json"
        p.write_text("{not json", encoding="utf-8")
        m = jload(t_, f"data/raw/{SLUG}/sample/manifest.json")
        m["files"]["clean/c02-rate-hike-mixed-book.json"]["sha256"] = digest(p)
        jsave(t_, f"data/raw/{SLUG}/sample/manifest.json", m)
    broken("a fixture that is not JSON, with the manifest updated to match", "exit 1; 'not valid JSON'", corrupt, "not valid JSON")
    broken("the manifest removed", "exit 1; 'frozen manifest is missing'", lambda t_: (sample(t_) / "manifest.json").unlink(), "frozen manifest is missing")

    def envelope(**kw):
        def m(t_: Path):
            e = jload(t_, f"data/raw/{SLUG}/run-envelope.json"); e.update(kw); jsave(t_, f"data/raw/{SLUG}/run-envelope.json", e)
        return m
    tl, _ = broken("the run envelope says mode live", "exit 1; 'sample mode only'", envelope(mode="live"), "sample mode only")
    check("2 a refused scope writes nothing", "no ingest folder", f"ingest folder exists: {(tl / INGEST).exists()}", not (tl / INGEST).exists())
    broken("the run envelope allows network", "exit 1; 'network'", envelope(network=True), "network")
    broken("the run envelope allows live calls", "exit 1; 'live_calls'", envelope(live_calls=True), "live_calls")
    broken("the run envelope removed", "exit 1; 'run envelope is missing'", lambda t_: (t_ / "data" / "raw" / SLUG / "run-envelope.json").unlink(), "run envelope is missing")
    broken("the declared workflow removed", "exit 1; 'workflow JSON is missing'", lambda t_: (t_ / declared_workflow()).unlink(), "workflow JSON is missing")

    def edit_workflow(fn):
        def m(t_: Path):
            p = t_ / declared_workflow(); wf = json.loads(p.read_text()); fn(wf); p.write_text(json.dumps(wf, indent=2))
        return m
    broken("the workflow declares no webhook trigger", "exit 1; 'declares no webhook trigger'",
           edit_workflow(lambda wf: wf.__setitem__("nodes", [n for n in wf["nodes"] if n["type"] != "n8n-nodes-base.webhook"])), "declares no webhook trigger")

    def add_db(wf):
        wf["nodes"].append({"name": "Save Results", "type": "n8n-nodes-base.postgres", "parameters": {}, "credentials": {"postgres": {"id": "x", "name": "database"}}})
    t5 = tree(); edit_workflow(add_db)(t5); r5 = run(t5); s5 = {s["node"]: s for s in jload(t5, f"{INGEST}/source-check.json")["sources"]}
    check("2 a credentialed node of an unrecognised type is held back as approval-required, never passed as available", "exit 0; Save Results approval-required; reason says 'unrecognised'",
          f"exit {r5.returncode}; {s5.get('Save Results', {}).get('status')}; {'unrecognised' in s5.get('Save Results', {}).get('reason', '')}",
          r5.returncode == 0 and s5.get("Save Results", {}).get("status") == "approval-required" and "unrecognised" in s5["Save Results"]["reason"])

    def other_host(wf):
        for n in wf["nodes"]:
            if n["name"] == "Fetch_Data":
                n["parameters"]["url"] = "https://example.org/data"
    t6 = tree(); edit_workflow(other_host)(t6); run(t6); s6 = {s["node"]: s for s in jload(t6, f"{INGEST}/source-check.json")["sources"]}
    check("2 an HTTP request to another host is still approval-required, with no credential name guessed", "approval-required; 'none known'",
          f"{s6['Fetch_Data']['status']}; {s6['Fetch_Data']['credential_env']}", s6["Fetch_Data"]["status"] == "approval-required" and s6["Fetch_Data"]["credential_env"] == "none known")
    t7 = tree(); (t7 / "logs" / "gate-decisions").mkdir(parents=True); jsave(t7, f"logs/gate-decisions/{SLUG}-approval.json", {"note": "a test approval"})
    r7 = run(t7); s7 = jload(t7, f"{INGEST}/source-check.json")
    check("2 an approval record is noticed, but sample mode stays sample: still approval-required, nothing performed", "approval_record_present true; statuses unchanged; live_call_performed false",
          f"{s7['approval_record_present']}; {[s['status'] for s in s7['sources']]}; {[s['live_call_performed'] for s in s7['sources']]}",
          r7.returncode == 0 and s7["approval_record_present"] is True and [s["status"] for s in s7["sources"]].count("approval-required") == 2 and not any(s["live_call_performed"] for s in s7["sources"]))

    # ---- the recipe and the script agree on the flags (the CLI's own contract) -------------------------------------------------
    recipe = (REPO / "recipes" / f"{SLUG}.md").read_text(encoding="utf-8")
    row = next((ln for ln in recipe.splitlines() if ln.startswith("| Ingest declared inputs | `snickerdoodle run")), "")
    declared = set(re.findall(r"`(--[a-z][a-z0-9-]*)`", row.split("|")[3])) if row else set()
    implemented = set(re.findall(r"add_argument\(\s*['\"](--[a-z][a-z0-9-]*)['\"]", src)) - {"--input", "--output", "--help"}
    check("2 the recipe's Flags cell for this step lists exactly the flags the script implements", ", ".join(sorted(implemented)), ", ".join(sorted(declared)) or "no row found", declared == implemented and bool(declared))
    check("2 the recipe's Script Locations row points at this script, and the file exists", "scripts/ingest/scenariostresstestingagent-ingest-inputs.py",
          "present" if f"| Ingest declared inputs | `scripts/ingest/{SLUG}-ingest-inputs.py` | ingest |" in recipe and SCRIPT.exists() else "missing",
          f"| Ingest declared inputs | `scripts/ingest/{SLUG}-ingest-inputs.py` | ingest |" in recipe and SCRIPT.exists())

    ok = all(c["passed"] for c in results)
    outdir = REPO / "logs" / SLUG
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "ingest-self-test-results.json").write_text(json.dumps({"recipe": SLUG, "steps": [2], "checks": results, "all_passed": ok}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md = [f"# Self-test, step 2: {SLUG}", "",
          f"{sum(c['passed'] for c in results)} of {len(results)} checks came out as expected. A check passes only if what was observed is what was expected; the deliberate breaks are meant to be caught. Every check ran on a temporary copy of the tree.", "",
          "| Check | Expected | Observed | Result |", "|---|---|---|---|"]
    md += [f"| {c['check']} | {c['expected']} | {c['observed']} | {'as expected' if c['passed'] else '**NOT AS EXPECTED**'} |" for c in results]
    (outdir / "ingest-self-test-results.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"{sum(c['passed'] for c in results)}/{len(results)} checks as expected")
    for c in results:
        if not c["passed"]:
            print("NOT AS EXPECTED:", c["check"], "| expected:", c["expected"], "| observed:", c["observed"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
