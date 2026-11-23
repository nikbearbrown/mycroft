"""Purpose: run every check on step 2 of recipes/portfolio-price-fetcher.md and record what happened, including deliberate
attempts to break it, and a comparison that shows what step 2 leaves to step 3 (it ingests; it does not judge).
Each check states what it ran, what it saw and what was expected (SNICKERDOODLE's attestation shape).
Break tests work on a temporary copy of the repository's inputs; nothing in the repository is modified except the two
results files below.
Output: logs/portfolio-price-fetcher/ingest-self-test-results.json and ingest-self-test-results.md.
Side effects: writes those two files. No network, no clock (every ingest run pins its own time or reads the envelope's).
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
S2 = REPO / "scripts" / "ingest" / f"{SLUG}-ingest-inputs.py"
S3 = REPO / "scripts" / "gigo" / f"{SLUG}-validate-data-shape.py"
RAW = REPO / "data" / "raw" / SLUG
OUT = REPO / "logs" / SLUG
results: list[dict] = []
TMP: list[str] = []


def record(section: str, ran: str, saw: str, expected: str, ok: bool) -> None:
    for t in TMP:
        saw = saw.replace(t, "<tmp>")                       # temp paths are random; keep the committed results reproducible
    results.append({"section": section, "ran": ran, "saw": saw, "expected": expected, "as_expected": bool(ok)})
    print(f"{'ok  ' if ok else 'FAIL'} [{section}] {ran}: {saw}")


def stage(tmp: Path, name: str) -> tuple[Path, Path]:
    """A scratch repository root holding only what step 2 reads: the recipe, the workflow it declares, the raw data, step 1's record."""
    root = tmp / name
    (root / "recipes").mkdir(parents=True)
    shutil.copyfile(REPO / "recipes" / f"{SLUG}.md", root / "recipes" / f"{SLUG}.md")
    wf = re.search(r"^\| Original workflow JSON \| JSON \| `([^`]+)` \|", (REPO / "recipes" / f"{SLUG}.md").read_text(), re.M).group(1)
    (root / wf).parent.mkdir(parents=True)
    shutil.copyfile(REPO / wf, root / wf)
    (root / "data" / "raw").mkdir(parents=True)
    shutil.copytree(RAW / "sample", root / "data" / "raw" / SLUG / "sample")
    shutil.copyfile(RAW / "run-envelope.json", root / "data" / "raw" / SLUG / "run-envelope.json")
    (root / "logs").mkdir()
    for p in sorted((REPO / "logs").glob(f"{SLUG}-provenance-*.json")):
        shutil.copyfile(p, root / "logs" / p.name)
    return root, root / "data" / "raw" / SLUG


def ingest(root: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run([PY, str(S2), "--repo", str(root), "--raw-dir", str(root / "data" / "raw" / SLUG), *extra],
                          capture_output=True, text=True)


def load(root: Path, s: str) -> dict:
    return json.loads((root / "data" / "raw" / SLUG / "ingest" / s / "ingested.json").read_text())


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="pf-s2-"))
    TMP.append(str(tmp))
    env = json.loads((RAW / "run-envelope.json").read_text())

    # 1. the clean set, end to end
    root, raw = stage(tmp, "clean")
    p = ingest(root)
    d = load(root, "clean")
    ok = p.returncode == 0 and d["record_count"] == 5 and not d["rejects"] and d["sample_mode"] is True
    record("clean set", "step 2 on the clean set (the envelope's fixture_set)", f"exit {p.returncode}; {d['record_count']} ingested, {len(d['rejects'])} rejected; sample_mode {d['sample_mode']}",
           "exit 0; 5 ingested; 0 rejected; sample_mode true", ok)
    same = all(json.loads((raw / "sample" / r["file"]).read_text()) == r["body"] for r in d["records"])
    manifest = json.loads((raw / "sample" / "manifest.json").read_text())["files"]
    hashes = all(r["sha256"] == manifest[r["file"]]["sha256"] == sha(raw / "sample" / r["file"]) for r in d["records"])
    record("clean set", "compare each ingested body and SHA-256 with the file on disk and the frozen manifest", f"bodies identical: {same}; hashes agree: {hashes}", "both true: the body is kept unchanged", same and hashes)
    record("clean set", "read fetched_at", f"{d['fetched_at']} (the envelope's as_of is {env['as_of']})", "equal, so reruns are byte-identical", d["fetched_at"] == env["as_of"])

    # 2. every set, with the counts each one should give
    root, raw = stage(tmp, "all")
    p = ingest(root, "--set", "all")
    want = {"clean": (5, 0), "defective": (4, 1), "quality-duplicate": (6, 0), "quality-far": (5, 0), "quality-missing": (4, 0), "quality-move": (5, 0)}
    got = {s: (load(root, s)["record_count"], len(load(root, s)["rejects"])) for s in want}
    record("all sets", "step 2 with --set all", f"exit {p.returncode}; (ingested, rejected) by set: {got}", f"exit 1 (the defective set has one file that is not JSON); counts {want}", p.returncode == 1 and got == want)
    rej = load(root, "defective")["rejects"]
    record("all sets", "the one reject in the defective set", f"{rej}", "truncated-json.txt, not valid JSON", len(rej) == 1 and rej[0]["file"].endswith("truncated-json.txt") and "not valid JSON" in rej[0]["reason"])

    # 3. what step 2 leaves to step 3 and step 4
    ver = tmp / "ver"
    pop: dict[str, tuple[set, set, int]] = {}
    for s in want:
        subprocess.run([PY, str(S3), "--fixture-set", s, "--raw-dir", str(raw / "sample"), "--out-dir", str(ver)], capture_output=True, text=True)
        v = json.loads((ver / s / "validated.json").read_text())
        pop[s] = ({r["file"] for r in v["records"]} | {r["file"] for r in v["rejects"]}, {r["file"] for r in v["records"]}, v["promoted_count"])
    same_pop = all(pop[s][0] == {Path(r["file"]).name for r in load(root, s)["records"]} | {Path(r["file"]).name for r in load(root, s)["rejects"]} for s in want)
    record("against step 3", "the files step 3 reads in each set versus the files step 2 ingests or rejects", f"identical in all {len(want)} sets: {same_pop}", "the same file population in every set (step 2 neither adds nor loses a file)", same_pop)
    dfx = load(root, "defective")
    record("against step 3", "the defective set: records step 2 ingests versus records step 3 promotes", f"step 2 ingests {dfx['record_count']}; step 3 promotes {pop['defective'][2]} of the same files",
           "step 2 ingests the four that are valid JSON and step 3 promotes none (ingest does not judge a response)", dfx["record_count"] == 4 and pop["defective"][2] == 0)
    dup = load(root, "quality-duplicate")
    nv = [Path(r["file"]).name for r in dup["records"] if r["body"]["chart"]["result"][0]["meta"]["symbol"] == "NVDA"]
    record("against step 3", "the quality-duplicate set: two valid NVDA responses", f"ingested {len(nv)} ({', '.join(nv)}); rejects {len(dup['rejects'])}", "both ingested, no reject: choosing between them is step 4's work", len(nv) == 2 and not dup["rejects"])

    # 4. the naming ledger
    mi = load(root, "quality-missing")["naming_ledger"]
    record("naming ledger", "the quality-missing set", f"holdings with no named file: {mi['holdings_with_no_named_file']}; files named for no holding: {load(root, 'quality-missing')['naming_ledger']['files_named_for_no_holding']}",
           "AMD has no file; no stray file", mi["holdings_with_no_named_file"] == ["AMD"])
    nd = dup["naming_ledger"]["files_by_holding"]["NVDA"]
    record("naming ledger", "the quality-duplicate set, files named for NVDA", f"{nd}", "NVDA.json and NVDA-restated.json (both claim NVDA by name)", sorted(nd) == ["NVDA-restated.json", "NVDA.json"])

    # 5. the source check
    sc = json.loads((root / "data" / "raw" / SLUG / "ingest" / "source-check.json").read_text())
    rows = {r["node"]: r for r in sc["sources"]}
    fetch = rows["Fetch Stock Prices"]
    record("source check", "every source-bearing node the workflow names", f"{ {k: v['status'] for k, v in rows.items()} }",
           "Manual Trigger and Define Portfolio available; Fetch Stock Prices approval-required",
           rows["Manual Trigger"]["status"] == "available" and rows["Define Portfolio"]["status"] == "available" and fetch["status"] == "approval-required")
    record("source check", "the live request row", f"live_call_performed {fetch['live_call_performed']}; approved_for_live_action {fetch['approved_for_live_action']}; approval record present {fetch['approval_record_present']}",
           "false; false; false (no approval record exists)", fetch["live_call_performed"] is False and fetch["approved_for_live_action"] is False and fetch["approval_record_present"] is False)
    record("source check", "the holdings Define Portfolio declares", f"{rows['Define Portfolio']['reason']}", "five holdings: AMD, GOOGL, META, MSFT, NVDA", rows["Define Portfolio"].get("records") == 5)

    # 6. attempts to break it
    r2, w2 = stage(tmp, "tamper")
    f = w2 / "sample" / "clean" / "NVDA.json"
    f.write_bytes(f.read_bytes().replace(b"504.5625", b"504.5626"))
    p = ingest(r2)
    d = load(r2, "clean")
    record("break: changed a byte", "change one digit of clean/NVDA.json, then ingest", f"exit {p.returncode}; ingested {d['record_count']}; reject: {d['rejects'][0]['reason'][:70] if d['rejects'] else 'none'}",
           "exit 1; 4 ingested; the changed file rejected for differing from its frozen SHA-256", p.returncode == 1 and d["record_count"] == 4 and "SHA-256" in (d["rejects"][0]["reason"] if d["rejects"] else ""))
    r2, w2 = stage(tmp, "delete")
    (w2 / "sample" / "clean" / "AMD.json").unlink()
    p = ingest(r2)
    d = load(r2, "clean")
    record("break: removed a file", "delete clean/AMD.json, then ingest", f"exit {p.returncode}; reject: {d['rejects'][0]['reason'] if d['rejects'] else 'none'}", "exit 1; AMD.json reported as listed in the manifest but missing",
           p.returncode == 1 and d["rejects"] and "missing" in d["rejects"][0]["reason"])
    r2, w2 = stage(tmp, "stray")
    (w2 / "sample" / "clean" / "TSLA.json").write_text('{"chart": {"result": [], "error": null}}')
    p = ingest(r2)
    d = load(r2, "clean")
    record("break: added a file", "add clean/TSLA.json (not in any manifest), then ingest", f"exit {p.returncode}; ingested {d['record_count']}; reject: {d['rejects'][0]['reason'][:60] if d['rejects'] else 'none'}",
           "exit 1; the five frozen files ingested; the stray file rejected as not listed", p.returncode == 1 and d["record_count"] == 5 and "not listed" in (d["rejects"][0]["reason"] if d["rejects"] else ""))
    r2, w2 = stage(tmp, "badjson")
    f = w2 / "sample" / "clean" / "MSFT.json"
    f.write_text('{"chart": ')
    mpath = w2 / "sample" / "manifest.json"
    m = json.loads(mpath.read_text())
    m["files"]["clean/MSFT.json"]["sha256"] = sha(f)                # the frozen hash now matches, so only the JSON itself is wrong
    mpath.write_text(json.dumps(m))
    p = ingest(r2)
    d = load(r2, "clean")
    record("break: broken JSON with a matching hash", "replace clean/MSFT.json with truncated JSON and re-freeze its hash, then ingest", f"exit {p.returncode}; reject: {d['rejects'][0]['reason'] if d['rejects'] else 'none'}",
           "exit 1; rejected as not valid JSON (the hash check alone would not catch it)", p.returncode == 1 and d["rejects"] and "not valid JSON" in d["rejects"][0]["reason"])
    for label, edit, want_txt in (
        ("mode live", lambda e: e.update(mode="live"), "mode 'live'"),
        ("live calls approved", lambda e: e.update(live_calls_approved=True), "live_calls_approved: True"),
    ):
        r2, w2 = stage(tmp, "env-" + label.replace(" ", "-"))
        e = json.loads((w2 / "run-envelope.json").read_text())
        edit(e)
        (w2 / "run-envelope.json").write_text(json.dumps(e))
        p = ingest(r2)
        record(f"break: envelope {label}", f"set the run envelope to {label}, then ingest", f"exit {p.returncode}; {[l for l in p.stdout.splitlines() if l.startswith('STOP')][:1]}", "exit 1 with a STOP naming the envelope; no live action", p.returncode == 1 and want_txt in p.stdout)
    r2, w2 = stage(tmp, "env-missing")
    (w2 / "run-envelope.json").unlink()
    p = ingest(r2)
    record("break: no envelope", "delete the run envelope, then ingest", f"exit {p.returncode}; {[l for l in p.stdout.splitlines() if l.startswith('STOP')][:1]}", "exit 1: no scope was declared", p.returncode == 1 and "envelope is missing" in p.stdout)
    r2, w2 = stage(tmp, "no-fetch")
    wfp = next((r2 / "data" / "mycroft-main").rglob("Portfolio Price Fetcher.json"))
    wf = json.loads(wfp.read_text())
    wf["nodes"] = [n for n in wf["nodes"] if n["name"] != "Fetch Stock Prices"]
    wfp.write_text(json.dumps(wf))
    p = ingest(r2)
    record("break: workflow without the fetch node", "remove Fetch Stock Prices from the workflow copy, then ingest", f"exit {p.returncode}; {[l for l in p.stdout.splitlines() if l.startswith('STOP')][:1]}", "exit 1: the source this step must account for is gone", p.returncode == 1 and "no 'Fetch Stock Prices' node" in p.stdout)
    r2, w2 = stage(tmp, "no-manifest")
    (w2 / "sample" / "quality-manifest.json").unlink()
    p = ingest(r2, "--set", "all")
    record("break: a manifest is missing", "delete quality-manifest.json, then ingest --set all", f"exit {p.returncode}; {[l for l in p.stdout.splitlines() if l.startswith('STOP')][:1]}", "exit 1: nothing is trusted without its frozen hashes", p.returncode == 1 and "is missing" in p.stdout)
    p = ingest(stage(tmp, "unknown-set")[0], "--set", "no-such-set")
    record("break: a set that does not exist", "ingest --set no-such-set", f"exit {p.returncode}", "exit 2", p.returncode == 2)

    # 7. an approval record must not turn into a live call
    r2, w2 = stage(tmp, "approval")
    (r2 / "logs" / "gate-decisions").mkdir()
    (r2 / "logs" / "gate-decisions" / f"{SLUG}-approval.json").write_text(json.dumps({"approved_by": "a test, not a person", "scope": "live"}))
    p = ingest(r2)
    fx = {r["node"]: r for r in json.loads((w2 / "ingest" / "source-check.json").read_text())["sources"]}["Fetch Stock Prices"]
    record("approval record", "add a stand-in approval record, then ingest", f"approval_record_present {fx['approval_record_present']}; approved_for_live_action {fx['approved_for_live_action']}; live_call_performed {fx['live_call_performed']}",
           "true; false; false (this step never makes the call, with or without a record)", fx["approval_record_present"] is True and fx["approved_for_live_action"] is False and fx["live_call_performed"] is False)

    # 8. reruns, and what the script can reach
    a, b = stage(tmp, "rerun-a"), stage(tmp, "rerun-b")
    ingest(a[0], "--set", "all")
    ingest(b[0], "--set", "all")
    files = sorted(p.relative_to(a[1] / "ingest") for p in (a[1] / "ingest").rglob("*") if p.is_file())
    identical = all((a[1] / "ingest" / f).read_bytes() == (b[1] / "ingest" / f).read_bytes() for f in files)
    record("rerun", "ingest --set all twice into separate copies and compare every output file", f"{len(files)} files; byte-identical: {identical}", "byte-identical", identical)
    ingest(b[0], "--set", "all", "--now", "2030-01-01T00:00:00+00:00")
    diff = [str(f) for f in files if (a[1] / "ingest" / f).read_bytes() != (b[1] / "ingest" / f).read_bytes()]
    record("rerun", "the same with --now pinned to another time", f"{len(diff)} of {len(files)} files differ (the ones that carry the time)", "only files carrying fetched_at or checked_at change", len(diff) > 0 and all("check" in f or "ingested" in f or "audit" in f for f in diff))
    src = S2.read_text()
    reach = [w for w in ("socket", "urllib", "requests", "http.client", "subprocess", "os.environ", "getenv") if re.search(rf"\b{re.escape(w)}\b", src)]
    record("reach", "search the script for network, process and environment access", f"found: {reach or 'none'}", "none: it cannot reach the network or read a credential", not reach)

    # 9. the committed outputs are what the script writes
    committed = RAW / "ingest"
    if committed.exists():
        r3, w3 = stage(tmp, "committed")
        ingest(r3, "--set", "all")
        fresh = sorted(p.relative_to(w3 / "ingest") for p in (w3 / "ingest").rglob("*") if p.is_file())
        have = sorted(p.relative_to(committed) for p in committed.rglob("*") if p.is_file())
        eq = fresh == have and all((w3 / "ingest" / f).read_bytes() == (committed / f).read_bytes() for f in fresh)
        record("committed outputs", "regenerate data/raw/portfolio-price-fetcher/ingest/ and compare with what is committed", f"{len(fresh)} files; identical: {eq}", "identical", eq)

    OUT.mkdir(parents=True, exist_ok=True)
    bad = [r for r in results if not r["as_expected"]]
    (OUT / "ingest-self-test-results.json").write_text(json.dumps({"recipe": SLUG, "step": 2, "checks": len(results), "as_expected": len(results) - len(bad), "results": results}, indent=1) + "\n")
    md = [f"# Step 2 self-test results: {SLUG}", "", f"{len(results) - len(bad)} of {len(results)} checks behaved as expected. Each row: what was run, what was seen, what was expected.", "",
          "| Section | Ran | Saw | Expected | As expected |", "|---|---|---|---|---|"]
    md += [f"| {r['section']} | {r['ran']} | {r['saw'].replace('|', '/')} | {r['expected']} | {'yes' if r['as_expected'] else 'NO'} |" for r in results]
    md += ["", "## Did not test", "", "- Any live call: this step makes none, and no approval record exists in the repository.",
           "- Real market data: every price in the fixtures is invented and says so.",
           "- Whether the frozen manifests list the right files: that is a human judgment about the fixtures, not something this step can check.",
           "- Reading a very large response or a slow disk: the fixtures are tiny.", ""]
    (OUT / "ingest-self-test-results.md").write_text("\n".join(md))
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{len(results) - len(bad)} of {len(results)} as expected")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
