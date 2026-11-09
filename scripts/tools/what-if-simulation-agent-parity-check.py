"""Purpose: Evidence for step 5 of recipes/what-if-simulation-agent.md. Run the ORIGINAL JavaScript of the six ported
         nodes, extracted from the workflow JSON at run time, beside the Python port, on every sample request, and
         compare every field of every result and the whole prompt string.
Input: the workflow JSON declared in the recipe, the sample requests, and the port (scripts/tools/
       what-if-simulation-agent-run-approved-tools.py, or --port <path>). Needs `node` (any recent version).
Output: logs/what-if-simulation-agent/parity-results.json and a summary on stdout.
Side effects: writes that file and a temporary runner under the system temp folder. No network. The clock and
              Math.random are replaced inside the JavaScript run, so the simulation id and timestamp are fixed.
Idempotent: Yes.
Errors: exit 1 if any field or any character of any result differs; exit 2 if node or the workflow is missing.
Notes: the simulation id and timestamp come from the JavaScript's own (pinned) clock and are handed to the port, so
       they compare equal by construction; the id's FORMAT is checked separately. A request the workflow's own rules
       reject must be rejected by the port with the same message. NaN is compared as JSON.stringify writes it (null).
Recipe: recipes/what-if-simulation-agent.md
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SLUG = "what-if-simulation-agent"
REPO = Path(__file__).resolve().parents[2]
WORKFLOW = "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/What-If_Simulation_Agent/What-If Simulation Agent.json"
NODES = ["🔍 Parse & Validate Input", "📈 Sim 1 — Growth vs Sentiment Tradeoff", "⚖️ Sim 2 — Risk Appetite Simulator",
         "🎯 Sim 3 — Threshold Break Simulator", "🧠 Aggregate & Score All Simulations", "📝 Build AI Prompt"]
FIXED_MS = 1_700_000_000_000
FIXED_RANDOM = 0.123456789

RUNNER = r"""
const fs = require('fs');
const cfg = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const RealDate = Date;
class FakeDate extends RealDate {
  constructor(...a) { if (a.length === 0) super(cfg.fixedMs); else super(...a); }
  static now() { return cfg.fixedMs; }
}
globalThis.Date = FakeDate;
Math.random = () => cfg.fixedRandom;
const out = [];
for (const req of cfg.requests) {
  let item = req.payload;
  try {
    for (const code of cfg.nodes) {
      const fn = new Function('$input', code);
      const res = fn({ first: () => ({ json: item }) });
      item = res[0].json;
    }
    out.push({ id: req.id, ok: true, result: JSON.parse(JSON.stringify(item)) });
  } catch (e) {
    out.push({ id: req.id, ok: false, error: String(e && e.message || e) });
  }
}
fs.writeFileSync(cfg.outPath, JSON.stringify(out));
"""


def load_port(path: Path):
    spec = importlib.util.spec_from_file_location("whatif_port_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def norm(v):
    """Make a Python result comparable with JSON.parse(JSON.stringify(...)): NaN -> null, tuples -> lists."""
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, dict):
        return {k: norm(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [norm(x) for x in v]
    return v


def diff(a, b, path=""):
    """Paths where a and b differ (a = JavaScript, b = Python)."""
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append((f"{path}.{k}", "(absent)", repr(b[k])[:80]))
            elif k not in b:
                out.append((f"{path}.{k}", repr(a[k])[:80], "(absent)"))
            else:
                out += diff(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((path, f"len {len(a)}", f"len {len(b)}"))
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, f"{path}[{i}]")
    elif isinstance(a, bool) != isinstance(b, bool) or a != b:
        out.append((path, repr(a)[:120], repr(b)[:120]))
    return out


def requests_from(sample_root: Path) -> list[dict]:
    reqs = []
    for kind in ("clean", "defective"):
        for p in sorted((sample_root / kind).glob("*.json")):
            payload = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(payload, dict):          # a list or unparsable file never reaches the nodes (step 3 rejects it)
                reqs.append({"id": f"{kind}/{p.stem}", "payload": payload})
    return reqs


def run_js(repo: Path, requests: list[dict], workflow_path: Path) -> list[dict]:
    node = shutil.which("node")
    if not node:
        raise SystemExit("node not found; the parity check needs it to run the original JavaScript")
    wf = json.loads(workflow_path.read_text())
    codes = []
    for name in NODES:
        n = next(x for x in wf["nodes"] if x["name"] == name)
        codes.append(n["parameters"]["jsCode"])
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cfg = {"nodes": codes, "requests": requests, "fixedMs": FIXED_MS, "fixedRandom": FIXED_RANDOM, "outPath": str(td / "out.json")}
        (td / "cfg.json").write_text(json.dumps(cfg))
        (td / "runner.js").write_text(RUNNER)
        r = subprocess.run([node, str(td / "runner.js"), str(td / "cfg.json")], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f"the JavaScript run failed: {r.stderr[-400:]}")
        return json.loads((td / "out.json").read_text())


def compare(port, js_results: list[dict], requests: list[dict]) -> dict:
    by_id = {r["id"]: r["payload"] for r in requests}
    rows, mismatches = [], 0
    for jr in js_results:
        payload = by_id[jr["id"]]
        row = {"id": jr["id"], "js": "ok" if jr["ok"] else "threw"}
        try:
            if jr["ok"]:
                res = jr["result"]
                sid, ts = res["simulation_id"], res["timestamp"]
                if not re.fullmatch(r"SIM-\d{13}-[0-9A-Z]{1,6}", sid):
                    row["id_format"] = f"unexpected: {sid}"
                py = norm(port.run_chain(payload, sid, ts))
                d = diff(res, json.loads(json.dumps(py)))
                row["python"] = "ok"
                row["differences"] = d[:8]
                row["match"] = not d
            else:
                try:
                    port.run_chain(payload, "x", "y")
                    row["python"] = "ran (JavaScript threw)"
                    row["match"] = False
                except port.ValidationFailed as e:
                    row["python"] = "threw"
                    row["match"] = str(e) == jr["error"]
                    if not row["match"]:
                        row["differences"] = [("error message", jr["error"], str(e))]
        except Exception as e:   # the port itself failing is a mismatch, not a crash of the check
            row["python"] = f"crashed: {e.__class__.__name__}: {str(e)[:80]}"
            row["match"] = False
        mismatches += 0 if row["match"] else 1
        rows.append(row)
    return {"requests": len(rows), "matching": len(rows) - mismatches, "mismatching": mismatches, "rows": rows}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--port", default=None, help="port under test (default: the repo's step-5 script)")
    ap.add_argument("--workflow", default=None)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo)
    port_path = Path(args.port) if args.port else repo / "scripts" / "tools" / f"{SLUG}-run-approved-tools.py"
    wf_path = Path(args.workflow) if args.workflow else repo / WORKFLOW
    if not wf_path.exists():
        print(f"workflow missing: {wf_path}", file=sys.stderr)
        return 2
    reqs = requests_from(repo / "data" / "raw" / SLUG / "sample")
    js = run_js(repo, reqs, wf_path)
    res = compare(load_port(port_path), js, reqs)
    out = {"slug": SLUG, "javascript": "extracted from the workflow JSON at run time, run under node with the clock and Math.random pinned",
           "pinned": {"Date.now": FIXED_MS, "Math.random": FIXED_RANDOM}, **res}
    if not args.no_write:
        p = repo / "logs" / SLUG / "parity-results.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"parity: {res['matching']}/{res['requests']} requests identical to the original JavaScript, {res['mismatching']} different")
    for r in res["rows"]:
        if not r["match"]:
            print(f"  DIFF {r['id']}: {r.get('differences', r.get('python'))}")
    return 0 if res["mismatching"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
