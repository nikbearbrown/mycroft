"""Purpose: Evidence for steps 1, 3 and 5 of recipes/what-if-simulation-agent.md. Run every check on a scratch copy and
         record what was run, what was seen and what was expected, including deliberate attempts to break it.
Input: the repository (read only); every run happens on a temporary copy of the files each step needs.
Output: logs/what-if-simulation-agent/self-test-results.json and .md.
Side effects: writes those two files. No network, no credentials, nothing in the repository is modified by a check.
Idempotent: Yes (the results hold no times or paths that change).
Errors: exit 1 if any check does not come out as expected. A deliberate break that is NOT caught is a failed check.
Recipe: recipes/what-if-simulation-agent.md
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SLUG = "what-if-simulation-agent"
REPO = Path(__file__).resolve().parents[2]
WORKFLOW = "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/What-If_Simulation_Agent/What-If Simulation Agent.json"
PORT = f"scripts/tools/{SLUG}-run-approved-tools.py"
SCRIPTS = {"prov": f"scripts/tools/{SLUG}-verify-provenance.py", "valid": f"scripts/gigo/{SLUG}-validate-data-shape.py",
           "tools": PORT, "parity": f"scripts/tools/{SLUG}-parity-check.py"}
EXPECT_WHY = {"d01": "revenue_growth must be between", "d02": "sentiment_score must be 0", "d03": "risk_appetite must be", "d04": "pe_ratio must be positive",
              "d05": "debt_equity must be positive", "d06": "revenue_growth must be between", "d07": "not a finite number", "d08": "not a finite number",
              "d09": "must be a JSON object", "d10": "does not parse"}
rows: list[dict] = []
_manifest = json.loads((REPO / f"data/raw/{SLUG}/sample/manifest.json").read_text())
N_CLEAN, N_DEF = _manifest["counts"]["clean"], _manifest["counts"]["defective"]
N_OBJ_DEF = sum(1 for rel, m in _manifest["files"].items() if m["kind"] == "defective" and rel.endswith(".json")
                and isinstance(json.loads((REPO / f"data/raw/{SLUG}/sample" / rel).read_text()), dict))


def record(name: str, ran: str, saw: str, expected: str, ok: bool, kind: str = "check") -> None:
    rows.append({"name": name, "kind": kind, "ran": ran, "saw": saw, "expected": expected, "as_expected": ok})


def workspace() -> Path:
    """A scratch repo holding just what the steps read: the recipe, the workflow, the scripts and the sample corpus."""
    t = Path(tempfile.mkdtemp(prefix="whatif-selftest-"))
    for rel in [f"recipes/{SLUG}.md", WORKFLOW, *SCRIPTS.values()]:
        (t / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, t / rel)
    shutil.copytree(REPO / f"data/raw/{SLUG}", t / f"data/raw/{SLUG}")
    return t


def run(ws: Path, script: str, *args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, "-I", str(ws / script), *args], capture_output=True, text=True, cwd=ws)
    return r.returncode, (r.stdout + r.stderr).strip()


def jload(p: Path):
    return json.loads(p.read_text())


def main() -> int:
    # ---- step 1: provenance
    ws = workspace()
    rc, out = run(ws, SCRIPTS["prov"], "--now", "2026-10-17T00:00:00+00:00")
    rec = jload(ws / "logs" / f"{SLUG}-provenance-2026-10-17.json")
    record("provenance as declared", "verify-provenance on the declared workflow", f"exit {rc}; node table {rec['node_table_match']}, chain {rec['chain_match']}, fixtures {rec['fixtures_ok']}",
           "exit 0; all True", rc == 0 and rec["node_table_match"] and rec["chain_match"] and rec["fixtures_ok"])
    wf_path = ws / WORKFLOW
    wf = wf_path.read_text()
    wf_path.write_text(wf.replace("📈 Sim 1 — Growth vs Sentiment Tradeoff", "📈 Sim 1 renamed", 1))
    rc, out = run(ws, SCRIPTS["prov"], "--now", "2026-10-17T00:00:00+00:00")
    rec = jload(ws / "logs" / f"{SLUG}-provenance-2026-10-17.json")
    record("BREAK: a node renamed in the workflow", "rename 'Sim 1' in a copy of the workflow, run verify-provenance", f"exit {rc}; node table {rec['node_table_match']}; findings {len(rec['findings'])}",
           "exit 1; node table False", rc == 1 and rec["node_table_match"] is False, "break")
    w = json.loads(wf)
    w["connections"]["⚖️ Sim 2 — Risk Appetite Simulator"]["main"][0][0]["node"] = "🧠 Aggregate & Score All Simulations"   # skip Sim 3
    wf_path.write_text(json.dumps(w, ensure_ascii=False))
    rc, out = run(ws, SCRIPTS["prov"], "--now", "2026-10-17T00:00:00+00:00")
    rec = jload(ws / "logs" / f"{SLUG}-provenance-2026-10-17.json")
    record("BREAK: Sim 3 skipped in the connections", "rewire Sim 2 straight to Aggregate in a copy, run verify-provenance", f"exit {rc}; chain {rec['chain_match']}",
           "exit 1; chain False", rc == 1 and rec["chain_match"] is False, "break")
    shutil.rmtree(ws)
    ws = workspace()
    fx = ws / f"data/raw/{SLUG}/sample/clean/c01-strong-buy-on-the-thresholds.json"
    fx.write_text(fx.read_text().replace("48.2", "48.3"))
    rc, out = run(ws, SCRIPTS["prov"], "--now", "2026-10-17T00:00:00+00:00")
    rec = jload(ws / "logs" / f"{SLUG}-provenance-2026-10-17.json")
    record("BREAK: a fixture changed after it was frozen", "change one digit in c01, run verify-provenance", f"exit {rc}; fixtures {rec['fixtures_ok']}",
           "exit 1; fixtures False", rc == 1 and rec["fixtures_ok"] is False, "break")
    rc, out = run(ws, SCRIPTS["valid"])
    record("BREAK: the validator on the changed fixture", "same copy, run validate-data-shape", f"exit {rc}; validated.json written: {(ws / 'data/verified').exists()}",
           "exit 2; nothing written", rc == 2 and not (ws / "data/verified").exists(), "break")
    shutil.rmtree(ws)

    # ---- step 3: data shape
    ws = workspace()
    rc, out = run(ws, SCRIPTS["valid"])
    clean = jload(ws / f"data/verified/{SLUG}/clean/validated.json")
    record("clean set validates", "validate-data-shape on sample/clean", f"exit {rc}; {len(clean['accepted'])} accepted, {len(clean['rejected'])} rejected, record_count {clean['record_count']}",
           f"exit 0; {N_CLEAN} accepted, 0 rejected", rc == 0 and len(clean["accepted"]) == N_CLEAN and not clean["rejected"])
    rc, out = run(ws, SCRIPTS["valid"], "--sample-dir", str(ws / f"data/raw/{SLUG}/sample/defective"))
    bad = jload(ws / f"data/verified/{SLUG}/defective/validated.json")
    by = {r["id"].split("-")[0]: " ; ".join(r["reasons"]) for r in bad["rejected"]}
    wrong = [k for k, v in EXPECT_WHY.items() if v not in by.get(k, "")]
    record("every catalogued defect rejected, for its own reason", "validate-data-shape on sample/defective", f"exit {rc}; {len(bad['rejected'])}/{N_DEF} rejected; wrong or missing reasons: {wrong or 'none'}",
           f"exit 1 (by design); {N_DEF}/{N_DEF} rejected, each for its catalogued reason", rc == 1 and len(bad["rejected"]) == N_DEF and not wrong)
    msgs = re.findall(r"errors\.push\('([^']+)'\)", json.loads((ws / WORKFLOW).read_text())["nodes"][1]["parameters"]["jsCode"])
    spec_rules = re.search(r"RULES = \[(.*?)\n\]", (ws / SCRIPTS["valid"]).read_text(), re.S).group(1)
    ours = re.findall(r'"([^"]+)"', spec_rules)
    record("the contract has not drifted from the workflow's own rules", "compare the validator's five messages with the errors.push() messages in the Parse & Validate Input node", f"workflow {len(msgs)} messages, validator {len(ours)}; equal: {msgs == ours}",
           "the same five messages in the same order", msgs == ours)

    # ---- step 5: tools
    rc, out = run(ws, SCRIPTS["tools"], "--now", "2026-10-17")
    res = jload(ws / f"data/verified/{SLUG}/clean/simulation-results.json")
    ok_all = all("ai_prompt" in r["result"] and "aggregate" in r["result"] for r in res["results"])
    record("approved tools run on the clean set", "run-approved-tools on the validated clean set", f"exit {rc}; {res['count']} results, each with an aggregate and a prompt: {ok_all}",
           f"exit 0; {N_CLEAN} results", rc == 0 and res["count"] == N_CLEAN and ok_all)
    cells = {f"{r['result']['sim1_growth_sentiment']['inputs']['growth_level']}_{r['result']['sim1_growth_sentiment']['inputs']['sentiment_level']}" for r in res["results"]}
    risks = {r["result"]["risk_appetite"] for r in res["results"]}
    hz = {r["result"]["time_horizon"] for r in res["results"]}
    finals = {r["result"]["aggregate"]["final_recommendation"] for r in res["results"]}
    record("the clean set reaches every branch", "read the results: matrix cells, risk appetites, horizons, final recommendations", f"{len(cells)}/9 matrix cells; {len(risks)}/3 risk appetites; {len(hz)}/3 horizons; {len(finals)}/5 final recommendations",
           "9/9; 3/3; 3/3; 5/5", len(cells) == 9 and len(risks) == 3 and len(hz) == 3 and len(finals) == 5)
    first = (ws / f"data/verified/{SLUG}/clean/simulation-results.json").read_bytes()
    run(ws, SCRIPTS["tools"], "--now", "2026-10-17")
    record("rerun is byte-identical", "run-approved-tools twice", f"identical: {first == (ws / f'data/verified/{SLUG}/clean/simulation-results.json').read_bytes()}", "identical", first == (ws / f"data/verified/{SLUG}/clean/simulation-results.json").read_bytes())
    shutil.rmtree(ws)
    ws = workspace()
    run(ws, SCRIPTS["valid"], "--sample-dir", str(ws / f"data/raw/{SLUG}/sample/defective"))
    rc, out = run(ws, SCRIPTS["tools"], "--input", str(ws / f"data/verified/{SLUG}/defective/validated.json"), "--now", "2026-10-17")
    wrote = (ws / f"data/verified/{SLUG}/defective/simulation-results.json").exists() or (ws / "logs").exists()
    record("BREAK: the tools are handed rejected requests", "run-approved-tools on the defective validated.json", f"exit {rc}; anything written: {wrote}", "exit 1; nothing written", rc == 1 and not wrote, "break")
    run(ws, SCRIPTS["valid"])
    vp = ws / f"data/verified/{SLUG}/clean/validated.json"
    doc = jload(vp)
    doc["rejected"] = [{"id": "x", "reasons": ["smuggled"]}]
    vp.write_text(json.dumps(doc))
    rc, out = run(ws, SCRIPTS["tools"], "--input", str(vp), "--now", "2026-10-17")
    record("BREAK: a clean file hand-edited to hold a rejected request", "add one rejected entry to the clean validated.json, run-approved-tools", f"exit {rc}", "exit 1", rc == 1, "break")
    shutil.rmtree(ws)

    # ---- the port against the original JavaScript, and four deliberate breaks of the port
    ws = workspace()
    rc, out = run(ws, SCRIPTS["parity"], "--no-write")
    record("parity with the original JavaScript", f"parity-check: original JS vs the port, {N_CLEAN + N_OBJ_DEF} requests ({N_CLEAN} clean, {N_OBJ_DEF} object-shaped defective)", out.splitlines()[0], f"{N_CLEAN + N_OBJ_DEF}/{N_CLEAN + N_OBJ_DEF} identical", rc == 0 and f"{N_CLEAN + N_OBJ_DEF}/{N_CLEAN + N_OBJ_DEF}" in out)
    src = (ws / PORT).read_text()
    breaks = [
        ("rounding with Python's round() (half goes to even)", "    f = math.floor(x)\n    return float(f + 1) if (x - f) >= 0.5 else float(f)", "    return float(round(x))"),
        ("toFixed with Python's format (ties go to even)", "    q = Decimal(abs(x)).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)\n    s = format(q, \"f\")\n    return (\"-\" + s) if neg and q != 0 else s", "    return format(x, f\".{digits}f\")"),
        ("Math.min/Math.max replaced by Python's min/max (NaN is not contagious)", "    return NAN if any(isinstance(x, float) and math.isnan(x) for x in xs) else min(xs)", "    return min(xs)"),
        ("numbers printed the Python way (100.0 for 100)", "def jn(x: float) -> str:\n    return js_num_str(x)", "def jn(x: float) -> str:\n    return str(x)"),
    ]
    for label, old, new in breaks:
        if old not in src:
            record(f"BREAK: {label}", "patch a copy of the port", "the patch target was not found in the port", "patch applied", False, "break")
            continue
        broken = ws / "broken-port.py"
        broken.write_text(src.replace(old, new, 1))
        rc, out = run(ws, SCRIPTS["parity"], "--no-write", "--port", str(broken))
        record(f"BREAK: {label}", "parity-check on a copy of the port with that one change", out.splitlines()[0], "exit 1; the parity check must catch it", rc == 1 and "different" in out, "break")
    shutil.rmtree(ws)

    n_ok = sum(r["as_expected"] for r in rows)
    outdir = REPO / "logs" / SLUG
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "self-test-results.json").write_text(json.dumps({"slug": SLUG, "checks": len(rows), "as_expected": n_ok, "breaks": sum(r["kind"] == "break" for r in rows), "rows": rows}, indent=2, ensure_ascii=False) + "\n")
    md = [f"# Self-test: {SLUG}", "", f"{n_ok}/{len(rows)} checks came out as expected; {sum(r['kind'] == 'break' for r in rows)} of them are deliberate attempts to break it.",
          "Written by `scripts/tools/what-if-simulation-agent-self-test.py`. Each row pairs what was run with what was seen and what was expected.", "",
          "| Ran | Saw | Expected | As expected |", "|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['name']}: {r['ran']} | {r['saw']} | {r['expected']} | {'yes' if r['as_expected'] else '**NO**'} |")
    (outdir / "self-test-results.md").write_text("\n".join(m.replace("\n", " ") for m in md) + "\n")
    print(f"self-test: {n_ok}/{len(rows)} as expected")
    for r in rows:
        if not r["as_expected"]:
            print("  NOT AS EXPECTED:", r["name"], "|", r["saw"])
    return 0 if n_ok == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
