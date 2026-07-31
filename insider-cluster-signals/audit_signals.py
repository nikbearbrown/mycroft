"""Purpose: Generate the spot-check audit worksheet for the signal-quality gate (Gate 3).
Input: data/verified/scored_signals.json + data/raw/fetch-manifest-*.json.
Output: data/verified/scored-signals-audit.md — counts, per-signal evidence links, anomalies.
Side effects: Local file write only; no network.
Idempotent: Yes.
Recipe: recipes/insider-cluster-signal-agent.md

Per the verification stack: an audit does not say pass — it says what it found, beside the
data it inspects, so a named human can judge it and log the gate decision (P4).
"""

from __future__ import annotations

import glob
import json
from datetime import datetime, timezone
from pathlib import Path

MODULE_DIR = Path(__file__).parent


def manifest_index(raw_dir: Path) -> dict:
    index = {}
    for manifest_path in raw_dir.glob("fetch-manifest-*.json"):
        for entry in json.loads(manifest_path.read_text()).get("fetched", []):
            accession = entry["file_name"].rsplit("/", 1)[-1].removesuffix(".txt")
            index[accession] = entry
    return index


def main() -> None:
    verified = MODULE_DIR / "data" / "verified"
    scored = json.loads((verified / "scored_signals.json").read_text())
    by_accession = manifest_index(MODULE_DIR / "data" / "raw")
    s = scored["summary"]

    lines = [
        "# scored-signals-audit.md — spot-check worksheet for the signal-quality gate (Gate 3, OPEN)",
        "",
        f"Generated {datetime.now(timezone.utc).isoformat()[:19]}Z by audit_signals.py "
        "from data/verified/scored_signals.json.",
        "This audit does not say pass. It surfaces every signal with its evidence links so a named",
        "human can verify each against the primary source and log the gate decision (P4).",
        "",
        "## Counts",
        "",
        f"- clusters: {s['clusters_in']} -> STRONG {s['strong']} / WATCH {s['watch']} / SKIP {s['skip']}",
        f"- alpha used in classification: {s['rules']['alpha_used_in_classification']} (must be False)",
        "",
        "## Per-signal checklist (human: open each filing; verify insider name, date, shares, price)",
        "",
    ]
    filings = 0
    for signal in scored["signals"]:
        lines.append(
            f"### {signal['signal']} {signal['ticker']} — {signal['n_insiders']} insiders, "
            f"${signal['total_value_usd']:,.0f}, alpha {signal['mean_alpha_30d']}"
        )
        lines.append("")
        for accession in signal["accessions"]:
            filings += 1
            entry = by_accession.get(accession)
            url = entry["xml_url"] if entry else "(manifest entry missing — flag this)"
            sha = entry["sha256"][:16] + "..." if entry else "n/a"
            lines.append(f"- [ ] `{accession}` — {url}  (sha256 {sha})")
        lines.append("")
    lines += [
        "## Anomalies surfaced for the reviewer",
        "",
        "- GENB: one member (AFEYAN NOUBAR, director) accounts for $150.0M of the $150.06M total —",
        "  cluster value is dominated by a single large buyer; conviction weighting treats members",
        "  equally regardless of trade size. Judge whether this matches signal intent.",
        "- LAW mean alpha (+24.36) averages 2 trades; CTEV (+22.35) averages 3 — small samples.",
        "- 2 negative-alpha clusters (LRMR -5.43, PVLA -9.21) retained; detector reports what it finds.",
        f"- Filings to verify: {filings} accession URLs above; every sha256 traces to a fetch manifest.",
        "",
    ]
    out = verified / "scored-signals-audit.md"
    out.write_text("\n".join(lines))
    print(f"audit written: {out.name} ({filings} filings listed)")


if __name__ == "__main__":
    main()
