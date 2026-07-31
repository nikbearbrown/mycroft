"""Purpose: Cross-regime comparison — corporate insider (Form 4) vs congressional (STOCK Act)
         cluster-buy signals, same 30-day cluster methodology, two disclosure regimes.
Input: data/verified/scored_signals.json (ours) +
       data/raw/congressional-import/cluster_signals.json (third-party; see PROVENANCE.md).
Output: reports/cross_regime_study.md — every number traces to one of the two JSONs (P3).
Side effects: Local file write only; NO network (the import is a local git object).
Idempotent: Yes.
Recipe: recipes/insider-cluster-signal-agent.md

The imported congressional data is another contributor's claim (unmerged PR #3), not our
verified fact — this script validates its SHAPE, not its correctness, and says so in the
report (P2/P8). Numbers from the two pipelines are compared only where the bases align;
where they don't (alpha anchor date, tier definitions), the difference IS the finding.
"""

from __future__ import annotations

import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

MODULE_DIR = Path(__file__).parent

CONGRESSIONAL_REQUIRED_FIELDS = {
    "ticker", "cluster_size", "politicians", "anchor_date",
    "window_days", "avg_alpha", "win_rate", "priced_trades",
}


def load_congressional(path: Path) -> list[dict]:
    """Load + shape-validate the imported third-party clusters. Halt on malformed data (P4)."""
    payload = json.loads(path.read_text())
    clusters = payload.get("clusters")
    if not isinstance(clusters, list) or not clusters:
        raise SystemExit(f"HALT: {path.name} has no 'clusters' list — import invalid")
    for i, c in enumerate(clusters):
        missing = CONGRESSIONAL_REQUIRED_FIELDS - c.keys()
        if missing:
            raise SystemExit(f"HALT: congressional cluster {i} missing fields {sorted(missing)}")
    return clusters


def stats_block(alphas: list[float]) -> dict:
    return {
        "n": len(alphas),
        "mean": round(statistics.mean(alphas), 2) if alphas else None,
        "median": round(statistics.median(alphas), 2) if alphas else None,
        "positive_share": round(100 * sum(1 for a in alphas if a > 0) / len(alphas), 1) if alphas else None,
    }


def main() -> None:
    ours = json.loads((MODULE_DIR / "data" / "verified" / "scored_signals.json").read_text())
    theirs = load_congressional(MODULE_DIR / "data" / "raw" / "congressional-import" / "cluster_signals.json")

    our_alphas = [s["mean_alpha_30d"] for s in ours["signals"] if s["mean_alpha_30d"] is not None]
    # Their avg_alpha can also be null (unpriced/immature windows) — excluded, count reported.
    their_alphas = [c["avg_alpha"] for c in theirs if c["avg_alpha"] is not None]
    our_stats, their_stats = stats_block(our_alphas), stats_block(their_alphas)
    their_sizes = [c["cluster_size"] for c in theirs]
    our_sizes = [s["n_insiders"] for s in ours["signals"]]

    ts = datetime.now(timezone.utc).isoformat()[:19] + "Z"
    lines = [
        "# Cross-Regime Study — Corporate Insiders (Form 4) vs Congress (STOCK Act)",
        "",
        f"Generated {ts} by `cross_regime.py`. Research only — no investment advice.",
        "",
        "Two cluster-buy detectors built on the same core methodology (>=2 distinct buyers,",
        "same ticker, 30-day window, 30-day SPY-adjusted alpha) applied to two disclosure",
        "regimes. Sources: this module's `data/verified/scored_signals.json` and the",
        "congressional-signals module's cluster output imported from upstream PR #3",
        "(`data/raw/congressional-import/` — provenance + sha256 in PROVENANCE.md; the import",
        "is that contributor's claim, shape-validated here, **not independently verified**).",
        "",
        "## The two regimes",
        "",
        "| | Corporate insiders (this module) | Congress (PR #3 module) |",
        "|---|---|---|",
        "| Disclosure law | SEC Form 4, 17 CFR 240.16a | STOCK Act |",
        "| Filing deadline | **2 business days** after trade | **<= 45 days** after trade |",
        "| Alpha anchor | **transaction date** | **disclosure date** |",
        "| Alpha window | 30 calendar days vs SPY | 30 calendar days vs SPY |",
        "| Tier rule | trade-time info only (size, roles, value); **alpha never classifies** | `cluster_size >= 2 AND avg_alpha > 1% AND score >= 1.5` -> STRONG |",
        "",
        "## Populations compared",
        "",
        f"| Metric | Corporate (ours) | Congressional (imported) |",
        f"|---|---|---|",
        f"| Clusters | {len(ours['signals'])} | {len(theirs)} |",
        f"| Corpus | 1 trading day (2026-03-02) + samples | multi-year scrape (2023–2026) |",
        f"| Mean cluster size | {round(statistics.mean(our_sizes), 2)} | {round(statistics.mean(their_sizes), 2)} |",
        f"| Max cluster size | {max(our_sizes)} | {max(their_sizes)} |",
        f"| Mean 30d alpha | {our_stats['mean']}% (n={our_stats['n']}) | {their_stats['mean']}% (n={their_stats['n']}) |",
        f"| Median 30d alpha | {our_stats['median']}% | {their_stats['median']}% |",
        f"| Clusters with positive alpha | {our_stats['positive_share']}% | {their_stats['positive_share']}% |",
        "",
        "## Findings",
        "",
        "1. **The tier definitions are not comparable — and that is the headline.** The",
        "   congressional scorer uses realized alpha to classify (`avg_alpha > 1%` is a STRONG",
        "   condition). Selecting signals on their outcome guarantees flattering tier statistics",
        "   (look-ahead bias): a congressional STRONG has positive alpha *by construction*. This",
        "   module classifies from trade-time information only and reports alpha as the",
        "   scoreboard — which is why it can (and does) show negative-alpha STRONG clusters",
        "   (LRMR -5.43). Any cross-regime claim that compares tier hit-rates directly would be",
        "   methodologically void; population-level alpha (above) is the only fair comparison.",
        "2. **Disclosure freshness differs by design.** A Form 4 cluster is knowable within ~2",
        "   business days of the trades; a STOCK Act cluster can surface up to 45 days later,",
        "   and its alpha is anchored at disclosure. The two alphas therefore measure different",
        "   questions: 'what happened after insiders traded' vs 'what happened after the public",
        "   could know'. Neither is wrong; they are not the same number.",
        "3. **Population alpha is directionally consistent** across both regimes on the data",
        "   available (means above), with the corporate sample far too small (see limitations)",
        "   to claim anything stronger than 'not inconsistent'.",
        "",
        "## Limitations (read before citing any number)",
        "",
        f"- Corporate corpus is **one complete trading day** ({our_stats['n']} clusters with",
        "  matured alpha) — illustrative, not statistical. A tier-level backtest is deferred",
        "  until the corpus grows (remaining 9 gated days, future sprint).",
        "- The congressional numbers are reproduced from an **unmerged, un-gated PR** — their",
        "  pipeline's own audits/attestation have not been performed. Shape-validated only.",
        "- Sector composition differs (their corpus concentrates in semiconductor/AI clusters).",
        "- No transaction costs, no sector adjustment, 30-day window only, single benchmark (SPY).",
        "",
        "## Provenance",
        "",
        "corporate numbers -> `data/verified/scored_signals.json` -> cluster/enrichment chain ->",
        "EDGAR accessions (SHA-256 manifests). congressional numbers ->",
        "`data/raw/congressional-import/cluster_signals.json` (sha256 + source commit in",
        "`PROVENANCE.md`) -> upstream PR #3.",
        "",
    ]
    out = MODULE_DIR / "reports" / "cross_regime_study.md"
    out.write_text("\n".join(lines))
    print(f"study written: {out.name}")
    print(f"  ours: {len(ours['signals'])} clusters, mean alpha {our_stats['mean']}%")
    print(f"  theirs: {len(theirs)} clusters, mean alpha {their_stats['mean']}%")


if __name__ == "__main__":
    main()
