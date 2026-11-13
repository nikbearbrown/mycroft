"""The `ledger` tool surface (DESIGN.md §6), without MCP: read a company's ledger as of a date, check a proposed
change, list the open questions. The MCP server (`ledger.py`) is a thin binding of this class.

The agent proposes; plain code validates. `propose` runs the proposed event through the same engine that builds
ledgers (`ledger/engine.py`) against a copy of the current ledger and returns the diff and the self-check
results. **Nothing is written**: applying changes is the graph's `ledger` node, and promoting a ledger to
`data/verified/` is a human gate (P4).

Ledgers are the closing ledgers the episode runs saved (`$AI_DEBT_DATA/week5/episodes/<episode>.json`). `get`
returns the latest one whose quarter ended on or before `as_of`, so it can never show a ledger from the future
of the question being asked.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..ledger import checks as ck
from ..ledger import engine

PAGE = 50


class LedgerStore:
    def __init__(self, episodes_dir: Path):
        self.dir = Path(episodes_dir)

    def _episodes(self, cik: int) -> list[dict]:
        out = []
        for p in sorted(self.dir.glob(f"{int(cik)}-*.json")):
            d = json.loads(p.read_text(encoding="utf-8"))
            if d.get("cik") == int(cik) and d.get("ledger"):
                out.append(d)
        return sorted(out, key=lambda d: d["quarter_end"])

    def get(self, cik: int, as_of: str, offset: int = 0) -> dict:
        eps = [d for d in self._episodes(cik) if d["quarter_end"] <= as_of[:10]]
        if not eps:
            return {"cik": cik, "as_of": as_of, "found": False, "summary": "no closing ledger on or before this date"}
        d = eps[-1]
        insts = d["ledger"]["instruments"]
        page = [{k: i.get(k) for k in ("id", "kind", "currency", "principal", "coupon_pct", "maturity_year", "status")}
                | {"sources": sorted({s["accession"] for e in i.get("events", []) for s in e.get("sources", [])
                                      if s.get("accession")})}
                for i in insts[offset: offset + PAGE]]
        bonds = [i for i in insts if i.get("kind") == "bond"]
        return {"cik": cik, "as_of": as_of, "found": True, "episode": d["episode"], "quarter_end": d["quarter_end"],
                "summary": (f"{len(insts)} instruments ({len(bonds)} bonds) at {d['quarter_end']}; total debt "
                            f"{d['ledger'].get('totals', {}).get('total_debt')}; {len(d['checks']['flags'])} self-check "
                            f"flags; {len(d['checks']['questions'])} open questions"),
                "instruments": page, "next_offset": offset + PAGE if offset + PAGE < len(insts) else None}

    def propose(self, cik: int, as_of: str, event: dict) -> dict:
        eps = [d for d in self._episodes(cik) if d["quarter_end"] <= as_of[:10]]
        if not eps:
            return {"valid": False, "why": "no ledger to apply it to"}
        d = eps[-1]
        if not engine.cited(event):
            return {"valid": False, "why": "a change must cite its filing and passage (DESIGN.md §7.1 rule 3)"}
        before = d["ledger"]["instruments"]
        res = engine.apply_events(before, [event], d["quarter_end"])
        after = {"instruments": [i for i in res["instruments"] if i["status"] == "outstanding"],
                 "meta": {"log": res["log"], "questions": res["questions"], "rejected": res["rejected"]}}
        return {"valid": not res["rejected"], "applied": False, "diff": res["log"], "questions": res["questions"],
                "checks": ck.run_checks(after, d["quarter_end"])}

    def open_questions(self, cik: int) -> dict:
        eps = self._episodes(cik)
        qs = [{"episode": d["episode"], "type": q["type"], "question": q["question"],
               "accession": (q.get("event") or {}).get("accession")} for d in eps for q in d["checks"]["questions"]]
        return {"cik": cik, "summary": f"{len(qs)} open questions across {len(eps)} episodes", "questions": qs[:PAGE]}
