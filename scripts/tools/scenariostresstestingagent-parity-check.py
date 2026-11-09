"""Purpose: Evidence for step 5 of recipes/scenariostresstestingagent.md. Run the ORIGINAL code of the ported nodes, extracted
         from the workflow JSON at run time (Validate Portfolio under Node; Load_Template_Scenario,
         Save_Portfolio_Before_LLM and Stress_Test_Engine as Python inside a small shim that provides _input.item.json,
         _input.all() and the {json: ...} return shape), beside the port, on every sample request, and compare the result of
         every node. Where the original fails (it throws, or a Python error), the port must fail with the same message.
Input: the workflow JSON declared in the recipe, the sample requests (clean and defective), and the port
       (scripts/tools/scenariostresstestingagent-run-approved-tools.py, or --port <path>). Needs `node` for the one
       JavaScript node; without it that node is not compared (said so, and the three Python nodes are compared on the
       port's validated item).
Output: logs/scenariostresstestingagent/parity-results.json and a summary on stdout.
Side effects: writes that file and a temporary runner under the system temp folder. No network, no clock, no randomness.
Idempotent: Yes.
Errors: exit 1 if any node output of any request differs; exit 2 if the workflow is missing.
Notes: not compared, and counted separately, are requests where the port raises NotModelled (JavaScript string arithmetic:
       the step-3 gate refuses them first). NaN is compared as JSON.stringify writes it (null). The Fetch_Data branch is
       never taken in sample mode, so the Merge after Validate Portfolio carries only that one item; that, and the IF node's
       'notEmpty' condition on custom_scenario (read from the workflow), are the two statements the harness takes on trust.
Recipe: recipes/scenariostresstestingagent.md
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

SLUG = "scenariostresstestingagent"
REPO = Path(__file__).resolve().parents[2]
WORKFLOW = "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json"

RUNNER = r"""
const fs = require('fs');
const cfg = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const out = [];
for (const req of cfg.items) {
  try {
    const fn = new Function('$input', cfg.code);
    const res = fn({ item: { json: req.item } });
    out.push({ id: req.id, ok: true, result: JSON.parse(JSON.stringify(res.json)) });
  } catch (e) {
    out.push({ id: req.id, ok: false, error: String(e && e.message || e) });
  }
}
fs.writeFileSync(cfg.outPath, JSON.stringify(out));
"""


class _Item:
    def __init__(self, j):
        self.json = j


class _Input:
    """n8n's Python code-node input: _input.item for the current item, _input.all() for every item."""
    def __init__(self, items):
        self._items = [_Item(i) for i in items]
        self.item = self._items[0]

    def all(self):
        return self._items


def load_port(path: Path):
    spec = importlib.util.spec_from_file_location("stress_port_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def norm(v):
    """Comparable with JSON.parse(JSON.stringify(...)): NaN and Infinity -> None."""
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    if isinstance(v, dict):
        return {k: norm(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [norm(x) for x in v]
    return v


def diff(a, b, path=""):
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


def original_code(workflow: dict) -> dict:
    """The original code of the ported nodes, plus the IF node's condition, from the workflow JSON."""
    by = {n["name"]: n for n in workflow["nodes"]}
    code = {"Validate Portfolio": by["Validate Portfolio"]["parameters"]["jsCode"]}
    for name in ("Load_Template_Scenario", "Save_Portfolio_Before_LLM", "Stress_Test_Engine"):
        code[name] = by[name]["parameters"]["pythonCode"]
    cond = by["Custom Scenario?"]["parameters"]["conditions"]["conditions"][0]
    code["_if"] = {"left": cond["leftValue"], "operation": cond["operator"]["operation"]}
    return code


def run_py(code: str, items: list[dict]):
    """Run an original Python node. Returns ('ok', json) or ('error', 'Type: message')."""
    src = "def _node():\n" + textwrap.indent(code, "    ") + "\n"
    ns: dict = {"_input": _Input(copy.deepcopy(items))}
    try:
        exec(src, ns)
        res = ns["_node"]()
        return "ok", json.loads(json.dumps(res["json"]))
    except Exception as e:      # the original failing is a result to compare, not a crash of the check
        return "error", f"{e.__class__.__name__}: {e}"


def run_js(code: str, items: list[dict]) -> list[dict] | None:
    node = shutil.which("node")
    if not node:
        return None
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        cfg = {"code": code, "items": items, "outPath": str(td / "out.json")}
        (td / "cfg.json").write_text(json.dumps(cfg))
        (td / "runner.js").write_text(RUNNER)
        r = subprocess.run([node, str(td / "runner.js"), str(td / "cfg.json")], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f"the JavaScript run failed: {r.stderr[-400:]}")
        return json.loads((td / "out.json").read_text())


def requests_from(sample_root: Path) -> list[dict]:
    reqs = []
    for kind in ("clean", "defective"):
        for p in sorted((sample_root / kind).glob("*.json")):
            reqs.append({"id": f"{kind}/{p.stem}", "payload": json.loads(p.read_text(encoding="utf-8"))})
    return reqs


def prepare(repo: Path, workflow_path: Path | None = None) -> dict:
    """Everything that does not depend on the port: the original code, the Edit Fields items and the JavaScript run.
    Computed once so the self-test can compare many deliberately broken ports against it."""
    wf = json.loads((workflow_path or repo / WORKFLOW).read_text())
    code = original_code(wf)
    sample_root = repo / "data" / "raw" / SLUG / "sample"
    reqs = requests_from(sample_root)
    stub = load_port(repo / "scripts" / "tools" / f"{SLUG}-run-approved-tools.py")     # only for edit_fields: a set node, not code
    items = []
    for r in reqs:
        try:
            items.append({"id": r["id"], "item": stub.edit_fields(r["payload"])})
        except Exception:
            items.append({"id": r["id"], "item": None})
    js = run_js(code["Validate Portfolio"], [i for i in items if i["item"] is not None])
    return {"code": code, "requests": reqs, "items": items, "js": js}


def original_outcome(ctx: dict, req_id: str, item: dict, js_row: dict | None, port) -> dict:
    """What the original nodes do with one request: a dict of per-node ('ok', value) or ('error', message)."""
    code = ctx["code"]
    out: dict = {}
    if js_row is not None:
        out["validate"] = ("ok", js_row["result"]) if js_row["ok"] else ("error", js_row["error"])
    else:   # no node: take the port's validated item as the input to the Python nodes (the JavaScript node is not compared)
        try:
            out["validate"] = ("ok", port.validate_portfolio(copy.deepcopy(item)))
        except (port.ValidationFailed, port.JSTypeError) as e:
            out["validate"] = ("error", str(e))
    if out["validate"][0] != "ok":
        return out
    v = out["validate"][1]
    custom = v.get("custom_scenario")
    route = "custom_llm" if isinstance(custom, str) and len(custom) > 0 else "template"    # the IF node: notEmpty on custom_scenario
    out["route"] = ("ok", route)
    if route == "template":
        st, res = run_py(code["Load_Template_Scenario"], [v])
        out["load_template_scenario"] = (st, res)
        if st == "ok":
            out["stress_test_engine"] = run_py(code["Stress_Test_Engine"], [res])
    else:
        out["save_portfolio_before_llm"] = run_py(code["Save_Portfolio_Before_LLM"], [v])
    return out


def port_outcome(port, item: dict) -> dict:
    """The same per-node record from the port. Raises port.NotModelled if the port declines the request."""
    out: dict = {}
    try:
        v = port.validate_portfolio(copy.deepcopy(item))
        out["validate"] = ("ok", v)
    except (port.ValidationFailed, port.JSTypeError) as e:
        out["validate"] = ("error", str(e))
        return out
    out["route"] = ("ok", port.route_for(v))
    if out["route"][1] == "template":
        try:
            loaded = port.to_json_boundary(port.load_template_scenario([copy.deepcopy(v)]))
            out["load_template_scenario"] = ("ok", loaded)
            out["stress_test_engine"] = ("ok", port.to_json_boundary(port.stress_test_engine([copy.deepcopy(loaded)])))
        except Exception as e:
            step = "stress_test_engine" if "load_template_scenario" in out else "load_template_scenario"
            out[step] = ("error", f"{e.__class__.__name__}: {e}")
    else:
        out["save_portfolio_before_llm"] = ("ok", port.to_json_boundary(port.save_portfolio_before_llm([copy.deepcopy(v)])))
    return out


DIRECT_ENGINE_CASES = {
    "engine: no scenario in the item": [{"portfolio": {"holdings": [{"ticker": "NVDA", "weight": 1.0}]}}],
    "engine: no portfolio anywhere": [{"scenario": {"name": "n", "description": "d", "shocks": {"market": -0.1}}}],
    "engine: portfolio without holdings": [{"scenario": {"name": "n", "description": "d", "shocks": {"market": -0.1}}, "portfolio": {"name": "x"}}],
}


def compare(port, ctx: dict) -> dict:
    rows, mismatches, not_modelled = [], 0, 0
    js_by_id = {r["id"]: r for r in (ctx["js"] or [])}
    for it in ctx["items"]:
        if it["item"] is None:
            continue
        rid = it["id"]
        row = {"id": rid}
        try:
            theirs = port_outcome(port, it["item"])
        except port.NotModelled as e:
            row.update(match=None, note=f"not modelled by the port ({e}); refused by the step-3 gate")
            not_modelled += 1
            rows.append(row)
            continue
        except Exception as e:
            row.update(match=False, note=f"the port crashed: {e.__class__.__name__}: {str(e)[:80]}")
            mismatches += 1
            rows.append(row)
            continue
        ours = original_outcome(ctx, rid, it["item"], js_by_id.get(rid), port)
        d = []
        for step in sorted(set(ours) | set(theirs)):
            a, b = ours.get(step), theirs.get(step)
            if a is None or b is None:
                d.append((step, "present" if a else "(absent)", "present" if b else "(absent)"))
            elif a[0] != b[0]:
                d.append((step, f"{a[0]}: {str(a[1])[:70]}", f"{b[0]}: {str(b[1])[:70]}"))
            else:
                d += [(f"{step}{p}", x, y) for p, x, y in diff(norm(a[1]), norm(b[1]))]
        row["original"] = {k: ("error: " + v[1]) if v[0] == "error" else "ok" for k, v in ours.items() if k != "route"}
        row["route"] = ours.get("route", (None, None))[1]
        row["match"] = not d
        if d:
            row["differences"] = d[:8]
            mismatches += 1
        rows.append(row)
    for name, items in DIRECT_ENGINE_CASES.items():
        a = run_py(ctx["code"]["Stress_Test_Engine"], items)
        try:
            b = ("ok", port.to_json_boundary(port.stress_test_engine(copy.deepcopy(items))))
        except Exception as e:
            b = ("error", f"{e.__class__.__name__}: {e}")
        d = [("result", x, y) for _, x, y in diff(norm(a[1]), norm(b[1]))] if a[0] == b[0] else [("kind", a[0], b[0])]
        rows.append({"id": name, "match": not d, **({"differences": d[:4]} if d else {})})
        mismatches += 1 if d else 0
    compared = [r for r in rows if r["match"] is not None]
    return {"requests": len(compared), "matching": len([r for r in compared if r["match"]]), "mismatching": mismatches,
            "not_modelled": not_modelled, "javascript_compared": ctx["js"] is not None, "rows": rows}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--port", default=None, help="port under test (default: the repo's step-5 script)")
    ap.add_argument("--workflow", default=None)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo)
    wf = Path(args.workflow) if args.workflow else repo / WORKFLOW
    if not wf.exists():
        print(f"workflow missing: {wf}", file=sys.stderr)
        return 2
    port_path = Path(args.port) if args.port else repo / "scripts" / "tools" / f"{SLUG}-run-approved-tools.py"
    ctx = prepare(repo, wf)
    if ctx["js"] is None:
        print("node not found: the JavaScript node (Validate Portfolio) is not compared; the three Python nodes are compared "
              "on the port's own validated item", file=sys.stderr)
    res = compare(load_port(port_path), ctx)
    out = {"slug": SLUG, "original": "extracted from the workflow JSON at run time: Validate Portfolio under node; the three Python nodes by exec inside a small _input shim",
           "if_node_condition": ctx["code"]["_if"], **res}
    if not args.no_write:
        p = repo / "logs" / SLUG / "parity-results.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"parity: {res['matching']}/{res['requests']} compared cases identical to the original code, {res['mismatching']} different; "
          f"{res['not_modelled']} not modelled (refused by the gate); javascript node compared: {res['javascript_compared']}")
    for r in res["rows"]:
        if r["match"] is False:
            print(f"  DIFF {r['id']}: {r.get('differences', r.get('note'))}")
    return 0 if res["mismatching"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
