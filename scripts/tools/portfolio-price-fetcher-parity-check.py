"""Purpose: prove the step-5 Python port computes what the original workflow computes.
Runs the ORIGINAL JavaScript of the Calculate Metrics and Aggregate Summary nodes (extracted from the declared
workflow JSON at run time, never copied into this repository) under a small Node shim that plays n8n's $input,
feeds it the same raw sample responses in the portfolio's order, and compares every field with the port's
portfolio-summary.json.
Input: data/raw/portfolio-price-fetcher/sample/<set>/*.json, the declared workflow, the run envelope's as_of
       (the shim pins `new Date()` to it), data/verified/portfolio-price-fetcher/<set>/portfolio-summary.json.
Output: stdout, one line per holding plus the summary; --json writes the comparison to a file.
Excluded from comparison: summary.lastUpdatedFormatted (toLocaleString depends on the host's locale).
Side effects: none beyond the optional --json file. Needs `node` on PATH. No network.
Errors: exit 1 on any difference; exit 2 if node is missing.
Recipe: recipes/portfolio-price-fetcher.md
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SLUG = "portfolio-price-fetcher"
REPO = Path(__file__).resolve().parents[2]
EXCLUDED = {"lastUpdatedFormatted"}

SHIM = r"""
const fs = require('fs');
const calcCode = fs.readFileSync(process.argv[2], 'utf8');   // the two node bodies, from files
const aggCode = fs.readFileSync(process.argv[3], 'utf8');
const raw = JSON.parse(process.argv[4]);                     // the raw responses, inline JSON
const asOf = process.argv[5];
const RealDate = Date;
global.Date = class extends RealDate { constructor(...a) { a.length ? super(...a) : super(asOf); } };
const calc = new Function('$input', calcCode);            // runOnceForEachItem: one call per item
const perItem = raw.map(json => calc({ item: { json } }).json);
const agg = new Function('$input', aggCode);              // runOnceForAllItems
const items = perItem.map(json => ({ json }));
const out = agg({ all: () => items, item: items[0] });
process.stdout.write(JSON.stringify(out[0].json));
"""


def declared_workflow() -> Path:
    text = (REPO / "recipes" / f"{SLUG}.md").read_text()
    return REPO / re.search(r"^\| Original workflow JSON \| JSON \| `([^`]+)` \|", text, re.M).group(1)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fixture-set", default="clean")
    ap.add_argument("--summary", help="port output to compare (default: the verified portfolio-summary.json)")
    ap.add_argument("--json", help="write the comparison here")
    a = ap.parse_args()
    if not shutil.which("node"):
        print("parity stop: node is not on PATH")
        return 2

    wf = json.loads(declared_workflow().read_text())
    code = {n["name"]: n["parameters"].get("jsCode", "") for n in wf["nodes"]}
    order = re.findall(r"ticker:\s*'([^']+)'", code["Define Portfolio"])
    raw_dir = REPO / "data" / "raw" / SLUG / "sample" / a.fixture_set
    raw = [json.loads((raw_dir / f"{t}.json").read_text()) for t in order if (raw_dir / f"{t}.json").exists()]
    envelope = json.loads((REPO / "data" / "raw" / SLUG / "run-envelope.json").read_text())

    with tempfile.TemporaryDirectory() as d:
        paths = []
        for name, text in (("calc.js", code["Calculate Metrics"]), ("agg.js", code["Aggregate Summary"]),
                           ("shim.js", SHIM)):
            p = Path(d) / name
            p.write_text(text)
            paths.append(str(p))
        r = subprocess.run(["node", paths[2], paths[0], paths[1], json.dumps(raw), envelope["as_of"]],
                           capture_output=True, text=True)
    if r.returncode != 0:
        print(f"parity stop: the original JavaScript failed: {r.stderr.strip()[-400:]}")
        return 1
    js = json.loads(r.stdout)
    port_path = Path(a.summary) if a.summary else REPO / "data" / "verified" / SLUG / a.fixture_set / "portfolio-summary.json"
    port = json.loads(port_path.read_text())

    diffs = []
    if len(js["stocks"]) != len(port["stocks"]):
        diffs.append(f"holding count: original {len(js['stocks'])}, port {len(port['stocks'])}")
    for o, p in zip(js["stocks"], port["stocks"]):
        for k in o:
            if o[k] != p.get(k):
                diffs.append(f"{o.get('ticker')}.{k}: original {o[k]!r}, port {p.get(k)!r}")
        print(f"  {o['ticker']:5} value {o['currentValue']:>10} gain {o['gainLoss']:>9} pct {o['gainLossPct']:>7}"
              f"  {'agree' if all(o[k] == p.get(k) for k in o) else 'DIFFER'}")
    for k, v in js["summary"].items():
        if k not in EXCLUDED and v != port["summary"].get(k):
            diffs.append(f"summary.{k}: original {v!r}, port {port['summary'].get(k)!r}")
    print(f"  summary  {js['summary']['totalCurrentValue']} / {js['summary']['totalCostBasis']} / "
          f"{js['summary']['totalGainLoss']} / {js['summary']['totalReturn']}%")
    if a.json:
        Path(a.json).write_text(json.dumps({"fixture_set": a.fixture_set, "holdings": len(js["stocks"]),
                                            "excluded": sorted(EXCLUDED), "differences": diffs}, indent=1) + "\n")
    if diffs:
        print("parity FAIL:")
        for x in diffs:
            print(f"  - {x}")
        return 1
    print(f"parity pass: {len(js['stocks'])}/{len(js['stocks'])} holdings and the summary agree with the original JavaScript "
          f"(excluded: {', '.join(sorted(EXCLUDED))})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
