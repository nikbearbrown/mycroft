"""Purpose: run every check on steps 4 and 6 of recipes/portfolio-price-fetcher.md and record what happened, including
deliberate attempts to break each one, and one comparison that shows what step 4 catches that steps 3 and 5 do not.
Each check states what it ran, what it saw and what was expected (SNICKERDOODLE's attestation shape).
Break tests work on temporary copies; nothing in the repository is modified except the two results files below.
Output: logs/portfolio-price-fetcher/quality-report-self-test-results.json and quality-report-self-test-results.md.
Side effects: writes those two files. No network, no clock (the report runs use a pinned --now).
Errors: exit 1 if any check does not behave as expected.
Recipe: recipes/portfolio-price-fetcher.md
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SLUG = "portfolio-price-fetcher"
REPO = Path(__file__).resolve().parents[2]
PY = sys.executable
NOW = "2026-11-17T12:00:00+00:00"
S3 = REPO / "scripts" / "gigo" / f"{SLUG}-validate-data-shape.py"
S4 = REPO / "scripts" / "gigo" / f"{SLUG}-transform-quality-check.py"
S5 = REPO / "scripts" / "tools" / f"{SLUG}-run-approved-tools.py"
S6 = REPO / "scripts" / "tools" / f"{SLUG}-produce-human-report.py"
SAMPLE = REPO / "data" / "raw" / SLUG / "sample"
ENVELOPE = REPO / "data" / "raw" / SLUG / "run-envelope.json"
OUT = REPO / "logs" / SLUG
results: list[dict] = []


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([PY, *args], capture_output=True, text=True, cwd=REPO)


TMP: list[str] = []


def record(section: str, ran: str, saw: str, expected: str, ok: bool) -> None:
    for t in TMP:
        saw = saw.replace(t, "<tmp>")                       # temp paths are random; keep the committed results reproducible
    results.append({"section": section, "ran": ran, "saw": saw, "expected": expected, "as_expected": bool(ok)})
    print(f"{'ok  ' if ok else 'FAIL'} [{section}] {ran}: {saw}")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def stage(tmp: Path, name: str, sets: list[str]) -> dict[str, str]:
    """A temp raw/ and verified/ tree; step 3 is run on each set so step 4 starts from real step-3 output."""
    raw, ver = tmp / name / "raw", tmp / name / "verified"
    for s in sets:
        shutil.copytree(SAMPLE / s, raw / "sample" / s)
    shutil.copyfile(ENVELOPE, raw / "run-envelope.json")
    for s in sets:
        run(str(S3), "--fixture-set", s, "--raw-dir", str(raw / "sample"), "--out-dir", str(ver))
    return {"raw": str(raw), "ver": str(ver)}


def q(ver: str, s: str) -> dict:
    return json.loads((Path(ver) / s / "quality-checked.json").read_text())


def codes(doc: dict) -> list[str]:
    return sorted(f"{f['ticker']}:{f['code']}" for f in doc["flags"])


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="pf-q-"))
    TMP.append(str(tmp))
    sets = ["clean", "quality-duplicate", "quality-missing", "quality-move", "quality-far", "defective"]
    st = stage(tmp, "main", sets)
    ver, raw = st["ver"], st["raw"]

    # ---- A: step 4 on the clean set
    r = run(str(S4), "--fixture-set", "clean", "--verified-dir", ver)
    d = q(ver, "clean")
    record("A step 4 clean", "step 4 on the clean set", f"exit {r.returncode}; {d['verified_count']} verified; flags {codes(d)}; rejects {len(d['rejects'])}",
           "exit 0; 5 verified; exactly the two fallbacks (GOOGL null price, META zero price); no rejects",
           r.returncode == 0 and d["verified_count"] == 5 and codes(d) == ["GOOGL:PRICE_FELL_BACK", "META:PRICE_FELL_BACK"] and not d["rejects"])
    order = [v["ticker"] for v in d["verified_records"]]
    record("A step 4 clean", "the order of verified_records", ", ".join(order), "the workflow's own order: NVDA, MSFT, GOOGL, META, AMD",
           order == ["NVDA", "MSFT", "GOOGL", "META", "AMD"])
    nv = next(v for v in d["verified_records"] if v["ticker"] == "NVDA")
    record("A step 4 clean", "NVDA's derived numbers", f"day {nv['day_change_pct']}%, price/buy {nv['price_vs_buy']}", "day +1.32% (504.5625 / 498), price/buy 1.121 (504.5625 / 450)",
           nv["day_change_pct"] == 1.32 and nv["price_vs_buy"] == 1.121)

    # ---- B: each quality defect, one set each
    r = run(str(S4), "--fixture-set", "quality-duplicate", "--verified-dir", ver)
    d = q(ver, "quality-duplicate")
    record("B defects", "step 4 on quality-duplicate (two NVDA responses that disagree, each valid alone; step 3 passed both)",
           f"exit {r.returncode}; rejects {sorted(x['file'] for x in d['rejects'])}; flags {codes(d)}",
           "exit 1; BOTH NVDA files rejected (nothing says which is right); NVDA reported HOLDING_MISSING; output still written",
           r.returncode == 1 and sorted(x["file"] for x in d["rejects"]) == ["NVDA-restated.json", "NVDA.json"] and "NVDA:HOLDING_MISSING" in codes(d))
    r = run(str(S4), "--fixture-set", "quality-missing", "--verified-dir", ver)
    d = q(ver, "quality-missing")
    hm = [f for f in d["flags"] if f["code"] == "HOLDING_MISSING"]
    record("B defects", "step 4 on quality-missing (no AMD response)", f"exit {r.returncode}; {[(f['ticker'], f['severity']) for f in hm]}; coverage missing {d['coverage']['missing']}",
           "exit 0; AMD HOLDING_MISSING, severity high, cost basis 7,200.00 named; coverage.missing = [AMD]",
           r.returncode == 0 and [(f["ticker"], f["severity"]) for f in hm] == [("AMD", "high")] and "7,200.00" in hm[0]["detail"] and d["coverage"]["missing"] == ["AMD"])
    r = run(str(S4), "--fixture-set", "quality-move", "--verified-dir", ver)
    d = q(ver, "quality-move")
    record("B defects", "step 4 on quality-move (AMD 40% under its previous close)", f"exit {r.returncode}; flags {codes(d)}",
           "exit 0; AMD DAY_MOVE_LARGE added to the two fallbacks", r.returncode == 0 and "AMD:DAY_MOVE_LARGE" in codes(d) and len(d["flags"]) == 3)
    r = run(str(S4), "--fixture-set", "quality-far", "--verified-dir", ver)
    d = q(ver, "quality-far")
    record("B defects", "step 4 on quality-far (META 3.44x its buy price)", f"exit {r.returncode}; flags {codes(d)}",
           "exit 0; META FAR_FROM_BUY_PRICE; META's own fallback flag gone (its price is live)",
           r.returncode == 0 and "META:FAR_FROM_BUY_PRICE" in codes(d) and "META:PRICE_FELL_BACK" not in codes(d))

    # ---- C: identical duplicate collapses
    sid = tmp / "ident"
    shutil.copytree(SAMPLE / "clean", sid / "raw" / "sample" / "clean")
    shutil.copyfile(SAMPLE / "clean" / "NVDA.json", sid / "raw" / "sample" / "clean" / "NVDA-copy.json")
    shutil.copyfile(ENVELOPE, sid / "raw" / "run-envelope.json")
    run(str(S3), "--fixture-set", "clean", "--raw-dir", str(sid / "raw" / "sample"), "--out-dir", str(sid / "ver"))
    r = run(str(S4), "--fixture-set", "clean", "--verified-dir", str(sid / "ver"))
    d = json.loads((sid / "ver" / "clean" / "quality-checked.json").read_text())
    record("C identical duplicate", "a byte-identical second NVDA response", f"exit {r.returncode}; duplicates {[(x['ticker'], x['identical']) for x in d['duplicates']]}; verified {d['verified_count']}; rejects {len(d['rejects'])}",
           "exit 0; one identical duplicate collapsed to the first file; 5 verified; no rejects",
           r.returncode == 0 and [(x["ticker"], x["identical"]) for x in d["duplicates"]] == [("NVDA", True)] and d["verified_count"] == 5 and not d["rejects"])

    # ---- D: break step 4
    r = run(str(S4), "--fixture-set", "defective", "--verified-dir", ver)
    nothing = not (Path(ver) / "defective" / "quality-checked.json").exists()
    record("D break step 4", "step 4 on the defective set (step 3 rejected five responses)", f"exit {r.returncode}; quality-checked.json written: {not nothing}",
           "exit 1; nothing written (quality checks read promoted data only)", r.returncode == 1 and nothing)
    r = run(str(S4), "--fixture-set", "no-such-set", "--verified-dir", ver)
    record("D break step 4", "step 4 where step 3 never ran", f"exit {r.returncode}", "exit 2 and a message naming step 3", r.returncode == 2 and "run step 3 first" in r.stdout)
    a1 = sha(Path(ver) / "clean" / "quality-checked.json")
    run(str(S4), "--fixture-set", "clean", "--verified-dir", ver)
    record("D break step 4", "step 4 run twice on the clean set", "output hash same" if a1 == sha(Path(ver) / "clean" / "quality-checked.json") else "output changed",
           "byte-identical", a1 == sha(Path(ver) / "clean" / "quality-checked.json"))

    # ---- E: what step 4 catches that steps 3 and 5 do not
    run(str(S5), "--fixture-set", "quality-duplicate", "--verified-dir", ver, "--envelope", str(Path(raw) / "run-envelope.json"), "--log-dir", str(tmp / "main" / "logs"))
    summ = json.loads((Path(ver) / "quality-duplicate" / "portfolio-summary.json").read_text())
    nv = next(s for s in summ["stocks"] if s["ticker"] == "NVDA")
    record("E what step 4 adds", "steps 3 and 5 on quality-duplicate (both NVDA responses valid), then step 4's verdict on the same set",
           f"step 5 priced NVDA at {nv['currentPrice']}, one of the two prices, with no complaint; step 4 rejected {len(q(ver, 'quality-duplicate')['rejects'])} records",
           "step 5 uses one of the two prices (504.5625 or 530) without noticing (step 3 judges each file alone); step 4 is where the pair is seen",
           nv["currentPrice"] in (504.5625, 530) and len(q(ver, "quality-duplicate")["rejects"]) == 2)

    # ---- F: step 6 on the clean set
    rep, lg = tmp / "rep", tmp / "logs"
    for name in ("provenance", "run-approved-tools"):                       # the earlier steps' logs, read-only copies
        for p in (REPO / "logs").glob(f"{SLUG}-{name}-*.json"):
            lg.mkdir(exist_ok=True)
            shutil.copyfile(p, lg / p.name)
    run(str(S5), "--fixture-set", "clean", "--verified-dir", ver, "--envelope", str(Path(raw) / "run-envelope.json"), "--log-dir", str(lg))
    args = [str(S6), "--fixture-set", "clean", "--now", NOW, "--verified-dir", ver, "--raw-dir", raw, "--log-dir", str(lg), "--report-dir", str(rep)]
    r = run(*args)
    md = (rep / f"{SLUG}-2026-11-17.md").read_text()
    log = json.loads((lg / f"{SLUG}-2026-11-17.json").read_text())
    heads = re.findall(r"^## (.+)$", md, re.M)
    S6_MOD = S6.read_text()
    secs = re.search(r"SECTIONS = \[(.*?)\]", S6_MOD, re.S).group(1)
    want = [x.strip().strip('"') for x in re.findall(r'"[^"]+"', secs)]
    record("F step 6 clean", "step 6 on the clean set", f"exit {r.returncode}; {len(heads)} sections", "exit 0; the fifteen contract sections, in order", r.returncode == 0 and heads == want)
    record("F step 6 clean", "the agent log's fields", f"{len(log)} fields; stop conditions triggered {sum(s['triggered'] for s in log['stop_conditions'])}; steps {log['steps_completed']}",
           "the contract's sixteen fields in order; none of the four stop conditions triggered; steps 1, 3, 4, 5, 6",
           len(log) == 16 and not any(s["triggered"] for s in log["stop_conditions"]) and log["steps_completed"] == [1, 3, 4, 5, 6])
    record("F step 6 clean", "the recommendation", "approves sample mode only" if "Approve the next phase in sample mode only" in md else "other",
           "approves the next phase in sample mode only and blocks live execution", "Approve the next phase in sample mode only" in md and "recommend: Block" in md)
    b1 = (sha(rep / f"{SLUG}-2026-11-17.md"), sha(lg / f"{SLUG}-2026-11-17.json"))
    run(*args)
    record("F step 6 clean", "step 6 run twice with --now pinned", "same" if b1 == (sha(rep / f"{SLUG}-2026-11-17.md"), sha(lg / f"{SLUG}-2026-11-17.json")) else "changed",
           "byte-identical report and log", b1 == (sha(rep / f"{SLUG}-2026-11-17.md"), sha(lg / f"{SLUG}-2026-11-17.json")))

    # ---- G: step 6 on a set with rejects
    r = run(str(S6), "--fixture-set", "quality-duplicate", "--now", NOW, "--verified-dir", ver, "--raw-dir", raw, "--log-dir", str(lg), "--report-dir", str(rep))
    md2 = (rep / f"{SLUG}-2026-11-17-quality-duplicate.md").read_text()
    record("G step 6 flagged", "step 6 on quality-duplicate", f"exit {r.returncode}; recommends fixes: {'Request source or data fixes' in md2}; mentions the conflict: {'conflicting records for NVDA' in md2}",
           "exit 0; the report recommends fixes and blocks live execution; the NVDA conflict is quoted", r.returncode == 0 and "Request source or data fixes" in md2 and "conflicting records for NVDA" in md2 and "Block live execution" in md2)

    # ---- H: break step 6
    def refuses(what: str, extra: list[str], expect: str, mutate=None, repo: Path | None = None) -> None:
        before = sorted(p.name for p in rep.glob("*")) + sorted(p.name for p in lg.glob("*"))
        r = run(*args[:1], "--fixture-set", "clean", "--now", "2027-01-01T00:00:00+00:00", *extra)
        after = sorted(p.name for p in rep.glob("*")) + sorted(p.name for p in lg.glob("*"))
        record("H break step 6", what, f"exit {r.returncode}; {r.stdout.strip()[:110]}; wrote nothing: {before == after}",
               f"exit 2, nothing written, message names {expect}", r.returncode == 2 and before == after and expect in r.stdout)
    base = ["--verified-dir", ver, "--raw-dir", raw, "--log-dir", str(lg), "--report-dir", str(rep)]
    live = tmp / "live" / "raw"
    live.mkdir(parents=True)
    env = json.loads(ENVELOPE.read_text())
    env["live_calls_approved"] = True
    (live / "run-envelope.json").write_text(json.dumps(env))
    refuses("an envelope that declares live calls approved", ["--verified-dir", ver, "--raw-dir", str(live), "--log-dir", str(lg), "--report-dir", str(rep)], "live calls")
    no4 = tmp / "no4"
    shutil.copytree(Path(ver) / "clean", no4 / "clean")
    (no4 / "clean" / "quality-checked.json").unlink()
    refuses("step 4's output removed", ["--verified-dir", str(no4), "--raw-dir", raw, "--log-dir", str(lg), "--report-dir", str(rep)], "run step 4 first")
    bad4 = tmp / "bad4"
    shutil.copytree(Path(ver) / "clean", bad4 / "clean")
    qd = json.loads((bad4 / "clean" / "quality-checked.json").read_text())
    qd["verified_records"][0]["effective_price"] = 1.0
    (bad4 / "clean" / "quality-checked.json").write_text(json.dumps(qd))
    refuses("step 4's verified NVDA price tampered to 1.0", ["--verified-dir", str(bad4), "--raw-dir", raw, "--log-dir", str(lg), "--report-dir", str(rep)], "does not match step 3")
    bad5 = tmp / "bad5"
    shutil.copytree(Path(ver) / "clean", bad5 / "clean")
    sd = json.loads((bad5 / "clean" / "portfolio-summary.json").read_text())
    sd["summary"]["totalCurrentValue"] = "70000.00"
    (bad5 / "clean" / "portfolio-summary.json").write_text(json.dumps(sd))
    refuses("step 5's total value tampered to 70000.00", ["--verified-dir", str(bad5), "--raw-dir", raw, "--log-dir", str(lg), "--report-dir", str(rep)], "do not match the sum")

    # credential scan: a hardcoded key in a copy of the repo's scripts is recorded as a triggered stop condition
    fake = tmp / "fakerepo"
    for layer in ("gigo", "tools", "ingest"):
        (fake / "scripts" / layer).mkdir(parents=True)
        for p in (REPO / "scripts" / layer).glob(f"{SLUG}-*.py"):
            shutil.copyfile(p, fake / "scripts" / layer / p.name)
    (fake / "recipes").mkdir()
    shutil.copyfile(REPO / "recipes" / f"{SLUG}.md", fake / "recipes" / f"{SLUG}.md")
    wf_rel = re.search(r"^\| Original workflow JSON \| JSON \| `([^`]+)` \|", (REPO / "recipes" / f"{SLUG}.md").read_text(), re.M).group(1)
    (fake / wf_rel).parent.mkdir(parents=True)
    shutil.copyfile(REPO / wf_rel, fake / wf_rel)
    with open(fake / "scripts" / "tools" / f"{SLUG}-run-approved-tools.py", "a") as f:
        f.write("\nAPI_" + 'KEY = "abcdef0123456789abcdef"\n')       # built at run time so this file does not itself match the scan
    r = run(str(S6), "--fixture-set", "clean", "--now", NOW, "--repo", str(fake), "--verified-dir", ver, "--raw-dir", raw, "--log-dir", str(lg), "--report-dir", str(tmp / "rep2"))
    log2 = json.loads((tmp / "rep2" / ".." / "logs" / f"{SLUG}-2026-11-17.json").read_text()) if False else json.loads((lg / f"{SLUG}-2026-11-17.json").read_text())
    trig = log2["stop_conditions"][0]["triggered"]
    record("H break step 6", "a hardcoded key planted in a copy of one of this recipe's scripts", f"exit {r.returncode}; credential stop condition triggered: {trig}",
           "the report is still written, and the agent log records stop condition 1 as triggered, naming the file", r.returncode == 0 and trig and "run-approved-tools.py" in log2["stop_conditions"][0]["evidence"])
    appr = tmp / "apprepo"
    shutil.copytree(fake, appr)
    (appr / "logs" / "gate-decisions").mkdir(parents=True)
    (appr / "logs" / "gate-decisions" / f"{SLUG}-approval.json").write_text("{}")
    r = run(str(S6), "--fixture-set", "clean", "--now", NOW, "--repo", str(appr), "--verified-dir", ver, "--raw-dir", raw, "--log-dir", str(lg), "--report-dir", str(tmp / "rep3"))
    record("H break step 6", "an approval record present (the script reports sample runs only)", f"exit {r.returncode}; {r.stdout.strip()[:90]}",
           "exit 2 and a message naming the approval record", r.returncode == 2 and "approval record exists" in r.stdout)

    # ---- the existing steps are untouched
    r1 = run(str(S3), "--fixture-set", "clean", "--raw-dir", str(SAMPLE), "--out-dir", str(tmp / "chk3"))
    same = sha(tmp / "chk3" / "clean" / "validated.json") == sha(REPO / "data" / "verified" / SLUG / "clean" / "validated.json")
    record("I existing steps", "step 3 rerun into a temp folder against the committed clean output", "byte-identical" if same else "differs", "byte-identical (this contribution changes no existing file)", same)

    shutil.rmtree(tmp, ignore_errors=True)
    ok = all(x["as_expected"] for x in results)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "quality-report-self-test-results.json").write_text(json.dumps({"recipe": SLUG, "steps": [4, 6], "checks": results,
                                                                         "all_as_expected": ok}, indent=1) + "\n")
    md = [f"# Self-test results: {SLUG}, steps 4 and 6", "",
          f"{sum(x['as_expected'] for x in results)} of {len(results)} checks behaved as expected. Each row says what was run, what was seen and what was expected; "
          "the break tests are the rows in sections D and H.", "", "| Section | Ran | Saw | Expected | As expected |", "|---|---|---|---|---|"]
    md += [f"| {x['section']} | {x['ran']} | {x['saw'].replace('|', '/')} | {x['expected']} | {'yes' if x['as_expected'] else 'NO'} |" for x in results]
    md += ["", "## Did not test", "",
           "- Any live call (there is no approval record, and the Yahoo Finance request is never made).",
           "- Any real market data: every price in the sample corpus is invented.",
           "- Whether the three numeric lines in step 4 (15% day move, 3x and one third of the buy price) are the right lines for a real portfolio; they are labelled our judgment.",
           "- Step 2 (ingest), which has no script yet, and the recipe's status and TODO markers, which this contribution did not edit."]
    (OUT / "quality-report-self-test-results.md").write_text("\n".join(md) + "\n")
    print(f"\n{sum(x['as_expected'] for x in results)}/{len(results)} as expected → logs/{SLUG}/quality-report-self-test-results.{{json,md}}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
