"""Purpose: Evidence for steps 1, 3 and 5 of recipes/scenariostresstestingagent.md: run every check and record each one,
         including deliberate breaks that MUST be caught. A check passes only if the observed result is the expected one.
Input: the repo (its recipe, workflow, sample corpus and the three step scripts plus the parity check). Needs `node`
       for the checks that compare against the original JavaScript; without it those checks are marked SKIPPED.
Output: logs/scenariostresstestingagent/self-test-results.json and self-test-results.md.
Side effects: writes those two files; works on temporary copies for the breaks (the repo's files are never touched).
Idempotent: Yes (no clock in the results).
Errors: exit 1 if any check does not come out as expected; exit 2 if node is missing and checks were skipped.
Recipe: recipes/scenariostresstestingagent.md
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SLUG = "scenariostresstestingagent"
REPO = Path(__file__).resolve().parents[2]
T = REPO / "scripts" / "tools"
G = REPO / "scripts" / "gigo"
PORT = T / f"{SLUG}-run-approved-tools.py"
VALIDATOR = G / f"{SLUG}-validate-data-shape.py"
PROV = T / f"{SLUG}-verify-provenance.py"
PARITY = T / f"{SLUG}-parity-check.py"
SAMPLE = REPO / "data" / "raw" / SLUG / "sample"
WORKFLOW = REPO / "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, cwd=REPO)


def main() -> int:
    port, validator, prov, parity = load(PORT, "p_ok"), load(VALIDATOR, "v_ok"), load(PROV, "pr_ok"), load(PARITY, "pa_ok")
    have_node = shutil.which("node") is not None
    checks: list[dict] = []

    def record(group, name, expected, observed, ok=None, skipped=False):
        checks.append({"group": group, "check": name, "expected": expected, "observed": observed,
                       "as_expected": (observed == expected) if ok is None else ok, "skipped": skipped})

    # ------------------------------------------------------------------ straight checks
    rec, ok = prov.verify(REPO, "2026-10-25T00:00:00+00:00")
    record("provenance", "recipe node table = workflow nodes; connections = the wiring the port assumes; ported nodes have the language the port copies; fixtures intact", "OK", "OK" if ok else f"PROBLEM {rec['findings']}")

    clean = sorted((SAMPLE / "clean").glob("*.json"))
    defective = sorted((SAMPLE / "defective").glob("*.json"))
    j_clean = [validator.judge(p, port) for p in clean]
    j_def = [validator.judge(p, port) for p in defective]
    record("validator", f"clean set: all {len(clean)} accepted", len(clean), sum(j["accepted"] for j in j_clean))
    record("validator", f"defective set: all {len(defective)} rejected, each with a reason", len(defective), sum((not j["accepted"]) and bool(j["reasons"]) for j in j_def))
    want = {"d01-portfolio-missing": "Portfolio must have holdings array", "d03-holding-without-ticker": "Each holding must have a ticker",
            "d04-holdings-is-an-object": "not iterable", "d05-weight-is-a-string": "not a number", "d06-all-weights-zero": "weights total",
            "d07-negative-weight": "negative weight", "d08-unknown-scenario-type": "meltdown", "d09-empty-holdings": "empty", "d10-weight-missing": "no weight"}
    got = {j["id"]: " ; ".join(j["reasons"]) for j in j_def}
    record("validator", "each defect is rejected for its own reason", True, all(v in got[k] for k, v in want.items()))

    results = [(j["id"], port.run_chain(j["request"])) for j in j_clean]
    stressed = [t for _, t in results if t["stress_test_engine"] is not None]
    handoffs = [t for _, t in results if t["stress_test_engine"] is None]
    record("port", "12 clean requests: 11 stress-tested, 1 stopped at the Groq handoff", (11, 1), (len(stressed), len(handoffs)))
    names = {t["stress_test_engine"]["scenario_name"] for t in stressed}
    record("coverage", "all five template scenarios reached", 5, len(names))
    record("coverage", "all four risk levels reached", ["CRITICAL", "HIGH", "LOW", "MODERATE"], sorted({t["stress_test_engine"]["risk_level"] for t in stressed}))
    normalised = {i for i, t in results if t["edit_fields"] and any(h.get("weight") != v.get("weight") for h, v in zip(t["edit_fields"]["portfolio"]["holdings"], t["validate_portfolio"]["portfolio"]["holdings"]))}
    record("coverage", "both sides of the rescale rule: some requests rescaled, some left alone", (True, True), (len(normalised) > 0, len(normalised) < len(results)))
    tickers = {h["ticker"] for _, t in results for h in t["validate_portfolio"]["portfolio"]["holdings"]}
    record("coverage", "tickers both inside and outside the workflow's sector map", (True, True), (bool(tickers & set(port.SECTOR_MAP)), bool(tickers - set(port.SECTOR_MAP))))
    record("coverage", "the 10-percent threshold is hit exactly (and is LOW: the rule is 'above 10')", ("LOW", -10.0),
           next(((t["stress_test_engine"]["risk_level"], t["stress_test_engine"]["drawdown_pct"]) for i, t in results if "c11" in i), None))
    record("port", "a handoff is recorded for each live service, none approved or performed", True,
           all(h["approved_for_live_action"] is False and h["live_call_performed"] is False for h in port.HANDOFFS) and len(port.HANDOFFS) == 3)
    with tempfile.TemporaryDirectory() as td:
        rc = run(PORT, "--sample-dir", SAMPLE / "defective", "--no-write").returncode
    record("port", "rejected data is refused: the tools exit 1 and write nothing", (1, False), (rc, (REPO / "data/verified" / SLUG / "defective" / "stress-results.json").exists()))
    stubs = ["scripts/gigo/scenariostresstestingagent-parse-input.py", "scripts/ingest/scenariostresstestingagent-fetch-data.py",
             "scripts/tools/scenariostresstestingagent-basic-llm-chain.py", "scripts/tools/scenariostresstestingagent-groq-chat-model.py",
             "scripts/tools/scenariostresstestingagent-parse-llm-response.py", "scripts/tools/scenariostresstestingagent-save-portfolio-before-llm.py",
             "scripts/tools/scenariostresstestingagent-stress-test-engine.py", "scripts/tools/scenariostresstestingagent-webhook-trigger.py"]
    g = subprocess.run(["git", "-C", str(REPO), "diff", "--name-only", "upstream/main", "--", *stubs], capture_output=True, text=True)
    if g.returncode == 0:
        record("untouched", "the 8 generated per-node scripts are byte-identical to upstream/main", [], g.stdout.split())
    else:
        record("untouched", "the 8 generated per-node scripts are byte-identical to upstream/main", "checked", "SKIPPED (no upstream/main ref here)", ok=True, skipped=True)

    # ------------------------------------------------------------------ parity (needs node for the JavaScript node)
    ctx = parity.prepare(REPO)
    if have_node:
        res = parity.compare(port, ctx)
        record("parity", "port = original code on every request and every node (compared cases mismatching)", 0, res["mismatching"])
        record("parity", "cases compared (21 requests + 3 direct engine inputs; 1 not modelled and refused by the gate)", (24, 1), (res["requests"], res["not_modelled"]))
    else:
        record("parity", "port = original code (needs node)", "n/a", "SKIPPED: node not found", ok=True, skipped=True)

    # ------------------------------------------------------------------ deliberate breaks: each MUST be caught
    src = PORT.read_text()
    tmp = Path(tempfile.mkdtemp())

    def patched(old, new, label):
        assert old in src, f"break does not apply: {label}"
        p = tmp / f"port_{abs(hash(label))}.py"
        p.write_text(src.replace(old, new, 1))
        return load(p, f"p_{abs(hash(label))}")

    py_breaks = [
        ("a port that skips the weight rescale", 'if abs(total - 1.0) > 0.01:', 'if False:'),
        ("a port with a wrong CRITICAL threshold (25, not 30)", '("CRITICAL", 30)', '("CRITICAL", 25)'),
        ("a port that treats exactly 10.0 as MODERATE ('>=' for '>')", 'if abs(drawdown_pct) > bound:', 'if abs(drawdown_pct) >= bound:'),
        ("a port that rounds positions to 1 decimal, not 2", 'round(position_value, 2)', 'round(position_value, 1)'),
        ("a port that also applies the all_sectors shock the engine never reads", 'total_shock = shocks.get("market", 0)', 'total_shock = shocks.get("market", 0) + shocks.get("all_sectors", 0)'),
        ("a port whose default scenario is rate_hike, not tech_crash", 'DEFAULT_TEMPLATE = "tech_crash"', 'DEFAULT_TEMPLATE = "rate_hike"'),
        ("a port with NVDA in the wrong sector", '"NVDA": "semiconductor"', '"NVDA": "big_tech"'),
        ("a port that sends a custom scenario down the template branch", 'return "custom_llm" if len(v) > 0 else "template"', 'return "template" if len(v) > 0 else "custom_llm"'),
    ]
    for label, old, new in py_breaks:
        if have_node:
            bad = parity.compare(patched(old, new, label), ctx)
            record("deliberate break", f"{label}: parity must catch it", True, bad["mismatching"] > 0)
        else:
            record("deliberate break", f"{label}: parity must catch it", "n/a", "SKIPPED: node not found", ok=True, skipped=True)

    # a renamed node, a tampered fixture, a holding without a ticker, a changed edge
    wf = json.loads(WORKFLOW.read_text())
    wf2 = json.loads(json.dumps(wf))
    next(n for n in wf2["nodes"] if n["name"] == "Stress_Test_Engine")["name"] = "Stress_Test_Engine_RENAMED"
    p = tmp / "renamed.json"
    p.write_text(json.dumps(wf2))
    r2, ok2 = prov.verify(REPO, "x", workflow_override=p)
    record("deliberate break", "a renamed node: provenance must fail", False, ok2)
    wf3 = json.loads(json.dumps(wf))
    wf3["connections"]["Merge1"]["main"][0][0]["node"] = "Respond to Webhook"       # the engine is skipped
    p = tmp / "rewired.json"
    p.write_text(json.dumps(wf3))
    r3, ok3 = prov.verify(REPO, "x", workflow_override=p)
    record("deliberate break", "a rewired connection (the engine skipped): provenance must fail", False, ok3)
    shutil.copytree(SAMPLE, tmp / "sample")
    c = tmp / "sample" / "clean" / "c01-tech-crash-semiconductor-heavy.json"
    d = json.loads(c.read_text())
    d["body"]["portfolio"]["holdings"][0]["weight"] = 0.41
    c.write_text(json.dumps(d))
    r4, ok4 = prov.verify(REPO, "x", sample_override=tmp / "sample")
    rc4 = run(VALIDATOR, "--sample-dir", tmp / "sample" / "clean", "--out", tmp / "out").returncode
    record("deliberate break", "a tampered fixture: provenance must fail and the validator must stop (exit 2)", (False, 2), (ok4, rc4))
    nt = tmp / "no-ticker.json"
    nt.write_text(json.dumps({"body": {"portfolio": {"holdings": [{"weight": 1.0}]}, "scenario_type": "tech_crash"}}))
    jn = validator.judge(nt, port)
    record("deliberate break", "a holding without a ticker: the gate must reject it with the node's own message", True,
           (not jn["accepted"]) and "Each holding must have a ticker" in jn["reasons"][0])
    shutil.rmtree(tmp, ignore_errors=True)

    # ------------------------------------------------------------------ write
    ok_all = all(c["as_expected"] for c in checks)
    skipped = sum(c["skipped"] for c in checks)
    breaks = [c for c in checks if c["group"] == "deliberate break"]
    out = {"slug": SLUG, "node_found": have_node, "checks": len(checks), "as_expected": sum(c["as_expected"] for c in checks), "skipped": skipped,
           "deliberate_breaks": len(breaks), "deliberate_breaks_caught": sum(c["as_expected"] for c in breaks), "results": checks}
    d = REPO / "logs" / SLUG
    d.mkdir(parents=True, exist_ok=True)
    (d / "self-test-results.json").write_text(json.dumps(out, indent=2, ensure_ascii=False, default=str) + "\n")
    lines = [f"# Self-test: {SLUG}", "", "Written by `scripts/tools/scenariostresstestingagent-self-test.py`. A check passes when what was seen is what was expected; "
             "each deliberate break must be caught.", "",
             f"- Checks: {out['as_expected']}/{out['checks']} as expected ({skipped} skipped); deliberate breaks caught: {out['deliberate_breaks_caught']}/{out['deliberate_breaks']}",
             f"- node found: {have_node}", "", "| Group | Check | Expected | Observed | As expected |", "|---|---|---|---|---|"]
    for c in checks:
        esc = lambda v: str(v).replace("|", "\\|").replace("\n", " ")[:110]
        lines.append(f"| {c['group']} | {esc(c['check'])} | {esc(c['expected'])} | {esc(c['observed'])} | {'yes' if c['as_expected'] else 'NO'}{' (skipped)' if c['skipped'] else ''} |")
    (d / "self-test-results.md").write_text("\n".join(lines) + "\n")
    print(f"self-test: {out['as_expected']}/{out['checks']} checks as expected, {out['deliberate_breaks_caught']}/{out['deliberate_breaks']} deliberate breaks caught, {skipped} skipped")
    for c in checks:
        if not c["as_expected"]:
            print(f"  NOT AS EXPECTED: {c['group']}: {c['check']} (expected {c['expected']!r}, saw {c['observed']!r})")
    if not have_node:
        return 2
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
