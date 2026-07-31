"""Purpose: Build the self-contained signal dashboard (reports/dashboard.html) from verified data.
Input: data/verified/scored_signals.json + latest logs/run_*.json + data/raw/fetch-manifest-*.json
       + dashboard_template.html.
Output: reports/dashboard.html — one shareable file, opens via file://, no server, no framework.
Side effects: Local file write only; no network.
Idempotent: Yes; same inputs yield the same page (run metadata comes from the run log, not now()).
Recipe: recipes/insider-cluster-signal-agent.md

Second human-customer artifact (P5) beside the markdown report. Visuals follow
brutalist/DESIGN.md: the 6 palette tokens only; red = emphasis/brand (STRONG badge),
never valence — alpha bars are ink (positive) / secondary (negative).
"""

from __future__ import annotations

import json
from pathlib import Path

MODULE_DIR = Path(__file__).parent
PLACEHOLDER = "/*__DATA__*/"


def manifest_index(raw_dir: Path) -> dict:
    """accession -> manifest entry (same mapping audit_signals.py uses)."""
    index = {}
    for manifest_path in raw_dir.glob("fetch-manifest-*.json"):
        for entry in json.loads(manifest_path.read_text()).get("fetched", []):
            accession = entry["file_name"].rsplit("/", 1)[-1].removesuffix(".txt")
            index[accession] = entry
    return index


def latest_run(logs_dir: Path) -> dict:
    runs = sorted(logs_dir.glob("run_*.json"))
    if not runs:
        raise SystemExit("HALT: no logs/run_*.json — run pipeline.py before building the dashboard")
    return json.loads(runs[-1].read_text())


def build() -> Path:
    scored = json.loads((MODULE_DIR / "data" / "verified" / "scored_signals.json").read_text())
    run = latest_run(MODULE_DIR / "logs")
    by_accession = manifest_index(MODULE_DIR / "data" / "raw")

    def evidence(accessions: list[str]) -> list[dict]:
        rows = []
        for a in accessions:
            entry = by_accession.get(a)
            rows.append({
                "accession": a,
                "url": entry["xml_url"] if entry else "",
                "sha256": (entry["sha256"][:16] + "...") if entry else "n/a",
            })
        return rows

    signals = [{**s, "evidence": evidence(s["accessions"])} for s in scored["signals"]]
    audit = [
        {"accession": e["accession"], "url": e["url"], "ticker": s["ticker"]}
        for s in signals for e in s["evidence"]
    ]
    data = {
        "run": {
            "run_id": run["run_id"],
            "generated_at": run["generated_at"][:19].replace("T", " ") + "Z",
            "strong": run["strong"], "watch": run["watch"], "skip": run["skip"],
            "research_mode": run["research_mode"],
            "corpus": "2026-03-02 (complete trading day) + July samples",
        },
        "signals": signals,
        "audit": audit,
    }

    template = (MODULE_DIR / "dashboard_template.html").read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        raise SystemExit("HALT: template missing /*__DATA__*/ placeholder")
    # </script> inside JSON strings would terminate the script block; escape defensively.
    payload = json.dumps(data, default=str).replace("</", "<\\/")
    html = template.replace(PLACEHOLDER, payload)

    out = MODULE_DIR / "reports" / "dashboard.html"
    out.write_text(html, encoding="utf-8")
    print(f"dashboard written: {out.name} ({len(signals)} cards, {len(audit)} audit rows)")
    return out


if __name__ == "__main__":
    build()
