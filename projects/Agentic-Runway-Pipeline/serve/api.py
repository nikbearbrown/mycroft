"""
serve/api.py  —  Sprint 7a: FastAPI endpoint serving briefs from the DuckDB store.

Exposes the stored runs (Sprint 6) over HTTP so other tools can read them.
Read-only: it serves what's stored; it never scores or decides. The human gate still
lives in the pipeline. This just makes the stored data queryable.

Requires: pip install fastapi uvicorn duckdb

Run (from the project root):
    uvicorn serve.api:app --reload
Then open http://127.0.0.1:8000/docs  for the interactive API.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException  # noqa: E402

DB_PATH = "data/runs.duckdb"
app = FastAPI(title="Runway-Risk Pipeline API", version="0.1.0")


def _db():
    import duckdb
    if not Path(DB_PATH).exists():
        raise HTTPException(status_code=404,
                            detail="No runs stored yet. Run: python -m storage.store_runs data/deduped/signals.json --store")
    return duckdb.connect(DB_PATH, read_only=True)


@app.get("/")
def root():
    return {"service": "runway-risk-pipeline",
            "note": "serves stored runs; never decides. The human gate lives in the pipeline."}


@app.get("/companies")
def companies():
    """List companies that have any stored signals."""
    con = _db()
    rows = con.execute("SELECT DISTINCT company_id FROM runs ORDER BY company_id").fetchall()
    con.close()
    return {"companies": [r[0] for r in rows]}


@app.get("/companies/{company_id}/brief")
def brief(company_id: str):
    """Latest brief for a company: signal counts, validation, distress, confidence."""
    con = _db()
    rows = con.execute("""
        SELECT signal_type, score, validated
        FROM runs WHERE company_id = ?
          AND run_id = (SELECT MAX(run_id) FROM runs WHERE company_id = ?)
    """, [company_id, company_id]).fetchall()
    con.close()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No signals for {company_id}")

    total = len(rows)
    validated = sum(1 for _, _, v in rows if v)
    distress = sum(1 for t, _, _ in rows if t in ("layoff", "security_issue", "executive_change"))
    avg = sum(s for _, s, _ in rows) / total
    coverage = min(total / 3, 1.0)
    confidence = round(avg * (0.5 + 0.5 * (validated / total)) * coverage)
    return {
        "company_id": company_id,
        "signals": total,
        "validated": validated,
        "distress_indicators": distress,
        "brief_confidence": confidence,
        "gate": "HALT-AWAITING-HUMAN",  # the API serves; it does not decide
    }


@app.get("/companies/{company_id}/trend")
def trend(company_id: str):
    """Signals / validation / distress per run over time."""
    con = _db()
    rows = con.execute("""
        SELECT run_id, COUNT(*),
               SUM(CASE WHEN validated THEN 1 ELSE 0 END),
               SUM(CASE WHEN signal_type IN ('layoff','security_issue','executive_change') THEN 1 ELSE 0 END)
        FROM runs WHERE company_id = ?
        GROUP BY run_id ORDER BY run_id
    """, [company_id]).fetchall()
    con.close()
    return {"company_id": company_id,
            "trend": [{"run": r[0], "signals": r[1], "validated": r[2] or 0, "distress": r[3] or 0} for r in rows]}
