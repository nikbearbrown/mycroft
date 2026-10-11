"""Purpose: run every check on the Portfolio Visualization Agent's closed steps and record what happened,
including deliberate attempts to break each one.
Covers: step 1 of recipes/portfolio-price-fetcher.md and recipes/portfolio-dashboard.md, and steps 3 and 5
of recipes/portfolio-price-fetcher.md, plus the parity check against the original JavaScript.
Each check states what it ran, what it saw and what was expected (SNICKERDOODLE's attestation shape).
Break tests work on temporary copies; nothing in the repository is modified except the results below.
Output: logs/portfolio-price-fetcher/self-test-results.json and self-test-results.md.
Side effects: writes those two files and refreshes the clean-run outputs of steps 1, 3 and 5. Needs `node`
for the parity checks. No network.
Errors: exit 1 if any check does not behave as expected.
Recipe: recipes/portfolio-price-fetcher.md
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SLUG = "portfolio-price-fetcher"
REPO = Path(__file__).resolve().parents[2]
PY = sys.executable
NOW = "2026-10-10T00:00:00+00:00"
S1 = REPO / "scripts" / "tools" / f"{SLUG}-verify-provenance.py"
S1D = REPO / "scripts" / "tools" / "portfolio-dashboard-verify-provenance.py"
S3 = REPO / "scripts" / "gigo" / f"{SLUG}-validate-data-shape.py"
S5 = REPO / "scripts" / "tools" / f"{SLUG}-run-approved-tools.py"
PAR = REPO / "scripts" / "tools" / f"{SLUG}-parity-check.py"
WF = REPO / "data" / "mycroft-main" / "n8n-workflows" / "originals" / "n8n_Workflows" / \
    "Portfolio_Visualization_Agent" / "Portfolio Price Fetcher.json"
WF_D = WF.parent / "Portfolio_Dashboard_code.json"
SAMPLE = REPO / "data" / "raw" / SLUG / "sample"
VERIFIED = REPO / "data" / "verified" / SLUG

results: list[dict] = []


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([PY, *args], capture_output=True, text=True, cwd=REPO)


def record(section: str, ran: str, saw: str, expected: str, ok: bool) -> None:
    results.append({"section": section, "ran": ran, "saw": saw, "expected": expected, "as_expected": ok})
    print(f"{'ok  ' if ok else 'FAIL'} [{section}] {ran}: {saw}")


def last_line(cp: subprocess.CompletedProcess) -> str:
    lines = [l for l in (cp.stdout + cp.stderr).strip().splitlines() if l.strip()]
    return lines[-1].strip() if lines else ""


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="pvz-selftest-"))
    try:
        # ── A. step 1, provenance ────────────────────────────────────────────────────────────
        cp = run(str(S1), "--now", NOW)
        record("A step 1", "price fetcher provenance, as declared", f"exit {cp.returncode}", "exit 0, result pass",
               cp.returncode == 0)
        cp = run(str(S1D), "--now", NOW)
        record("A step 1", "dashboard provenance, as declared", f"exit {cp.returncode}",
               "exit 0; placeholder workflow id recorded as a note", cp.returncode == 0 and "placeholder" in cp.stdout)

        cp = run(str(S1), "--now", NOW, "--out-dir", str(tmp), "--workflow", str(tmp / "missing.json"))
        record("A step 1 break", "workflow file missing", f"exit {cp.returncode}", "exit 1 (stop)", cp.returncode == 1)

        wf = json.loads(WF.read_text())
        drift = json.loads(json.dumps(wf))
        drift["nodes"][2]["name"] = "Fetch Prices (renamed)"
        (tmp / "drift.json").write_text(json.dumps(drift))
        cp = run(str(S1), "--now", NOW, "--out-dir", str(tmp), "--workflow", str(tmp / "drift.json"))
        record("A step 1 break", "a workflow node renamed (node table drift)", f"exit {cp.returncode}; {last_line(cp)}",
               "exit 1, the renamed node named in the findings", cp.returncode == 1 and "renamed" in cp.stdout)

        twin = json.loads(json.dumps(wf))
        for n in twin["nodes"]:
            if n["name"] == "Calculate Metrics":
                n["parameters"]["jsCode"] = n["parameters"]["jsCode"].replace("'NVDA': { shares: 50", "'NVDA': { shares: 55")
        (tmp / "twin.json").write_text(json.dumps(twin))
        cp = run(str(S1), "--now", NOW, "--out-dir", str(tmp), "--workflow", str(tmp / "twin.json"))
        record("A step 1 break", "the two portfolio definitions disagree (NVDA shares 50 vs 55)",
               f"exit {cp.returncode}", "exit 1, portfolio_consistent false",
               cp.returncode == 1 and "portfolio differs" in cp.stdout)

        shutil.copytree(SAMPLE, tmp / "sample")
        bad = tmp / "sample" / "clean" / "MSFT.json"
        bad.write_text(bad.read_text().replace("412.0", "413.0"))
        cp = run(str(S1), "--now", NOW, "--out-dir", str(tmp), "--sample-dir", str(tmp / "sample"))
        record("A step 1 break", "a fixture edited after the manifest froze it", f"exit {cp.returncode}",
               "exit 1, the fixture named", cp.returncode == 1 and "clean/MSFT.json" in cp.stdout)

        dwf = json.loads(WF_D.read_text())
        for n in dwf["nodes"]:
            if n["type"].endswith("executeWorkflow"):
                n["parameters"]["workflowId"]["cachedResultName"] = "Some Other Workflow"
        (tmp / "dash.json").write_text(json.dumps(dwf))
        cp = run(str(S1D), "--now", NOW, "--out-dir", str(tmp), "--workflow", str(tmp / "dash.json"))
        record("A step 1 break", "dashboard calls a different workflow by name", f"exit {cp.returncode}",
               "exit 1, calls_price_fetcher false", cp.returncode == 1 and "Some Other Workflow" in cp.stdout)

        # ── B. step 3, data shape ────────────────────────────────────────────────────────────
        cp = run(str(S3), "--fixture-set", "clean")
        v = json.loads((VERIFIED / "clean" / "validated.json").read_text())
        record("B step 3", "clean set", f"exit {cp.returncode}; {v['promoted_count']} promoted, {v['rejected_count']} rejected",
               "exit 0; 5 promoted, 0 rejected", cp.returncode == 0 and v["promoted_count"] == 5 and v["rejected_count"] == 0)
        fallbacks = sorted(r["ticker"] for r in v["records"] if r["price_source"] == "previousClose")
        record("B step 3", "price fallback (JavaScript ||)", f"previousClose used for {fallbacks}",
               "GOOGL (null) and META (0) fall back", fallbacks == ["GOOGL", "META"])

        cp = run(str(S3), "--fixture-set", "defective")
        v = json.loads((VERIFIED / "defective" / "validated.json").read_text())
        manifest = json.loads((SAMPLE / "manifest.json").read_text())["files"]
        expected = {k.split("/", 1)[1] for k, m in manifest.items() if m["set"] == "defective"}
        caught = {r["file"] for r in v["rejects"]}
        record("B step 3", "defective set: every catalogued defect", f"exit {cp.returncode}; caught {len(caught)}/{len(expected)}",
               "exit 1; every defect in the manifest rejected, none promoted",
               cp.returncode == 1 and caught == expected and v["promoted_count"] == 0)

        # ── C. step 5, the port ──────────────────────────────────────────────────────────────
        cp = run(str(S5), "--fixture-set", "defective", "--log-dir", str(tmp))
        record("C step 5", "refuses a set step 3 rejected", f"exit {cp.returncode}", "exit 1, nothing written",
               cp.returncode == 1 and not (VERIFIED / "defective" / "portfolio-summary.json").exists())
        cp = run(str(S5))
        s = json.loads((VERIFIED / "clean" / "portfolio-summary.json").read_text())["summary"]
        record("C step 5", "clean set", f"exit {cp.returncode}; total {s['totalCurrentValue']}",
               "exit 0; 65098.125 rounds to 65098.13 as toFixed does (Python's default gives .12)",
               cp.returncode == 0 and s["totalCurrentValue"] == "65098.13")

        # ── D. parity with the original JavaScript ───────────────────────────────────────────
        if shutil.which("node"):
            cp = run(str(PAR))
            record("D parity", "port vs the original JavaScript, clean set", last_line(cp),
                   "exit 0; every holding and the summary agree", cp.returncode == 0)
            broken = tmp / "broken-port.py"
            broken.write_text(S5.read_text().replace(
                'return str(Decimal(x).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP))',
                'return f"{x:.{digits}f}"   # deliberately broken: Python rounding'))
            # only step 3's output is copied, and every input is passed explicitly: the broken copy lives
            # outside the repository, so it cannot find anything by its own location (a first version of this
            # check passed against the good summary left in a copied folder, because the broken run had failed)
            bdir = tmp / "verified"
            (bdir / "clean").mkdir(parents=True)
            shutil.copy(VERIFIED / "clean" / "validated.json", bdir / "clean" / "validated.json")
            bp = run(str(broken), "--verified-dir", str(bdir), "--log-dir", str(tmp), "--workflow", str(WF),
                     "--envelope", str(REPO / "data" / "raw" / SLUG / "run-envelope.json"))
            built = bp.returncode == 0 and (bdir / "clean" / "portfolio-summary.json").exists()
            cp = run(str(PAR), "--summary", str(bdir / "clean" / "portfolio-summary.json"))
            record("D parity break", "a port that rounds like Python, not JavaScript",
                   f"broken port ran: {built}; {last_line(cp)}",
                   "the broken port runs, then parity exits 1 naming the totalCurrentValue difference",
                   built and cp.returncode == 1 and "totalCurrentValue" in cp.stdout)
        else:
            record("D parity", "port vs the original JavaScript", "node not on PATH: not run", "needs node", False)

        # ── E. reproducibility ───────────────────────────────────────────────────────────────
        outs = [VERIFIED / "clean" / "validated.json", VERIFIED / "clean" / "portfolio-summary.json",
                VERIFIED / "clean" / "validate-audit.md"]
        before = [sha(p) for p in outs]
        run(str(S3), "--fixture-set", "clean")
        run(str(S5))
        same = [sha(p) for p in outs] == before
        record("E rerun", "steps 3 and 5 run again", "byte-identical" if same else "outputs changed",
               "byte-identical outputs", same)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    out = REPO / "logs" / SLUG
    out.mkdir(parents=True, exist_ok=True)
    passed = sum(r["as_expected"] for r in results)
    (out / "self-test-results.json").write_text(json.dumps(
        {"recipe": SLUG, "also_covers": ["portfolio-dashboard step 1"], "checks": len(results),
         "as_expected": passed, "results": results}, indent=1) + "\n")
    md = ["# Self-test: Portfolio Visualization Agent (closed steps)", "",
          f"{passed} of {len(results)} checks behaved as expected.", "",
          "| Section | Ran | Saw | Expected | As expected |", "|---|---|---|---|---|"]
    md += [f"| {r['section']} | {r['ran']} | {r['saw'].replace('|', '/')} | {r['expected']} | {'yes' if r['as_expected'] else '**no**'} |"
           for r in results]
    md += ["", "## Did not test", "",
           "- Any live call: Yahoo Finance is never fetched; the live handoff is recorded, not executed.",
           "- Steps 2, 4 and 6 of the price fetcher and steps 2–6 of the dashboard: still `[TODO: DEV]`.",
           "- `lastUpdatedFormatted` against the original: toLocaleString depends on the host's locale.",
           "- Real market data: every price in the sample corpus is invented."]
    (out / "self-test-results.md").write_text("\n".join(md) + "\n")
    print(f"\n{passed}/{len(results)} as expected → {out.relative_to(REPO)}/self-test-results.{{json,md}}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
