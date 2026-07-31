"""Purpose: Classify insider buy clusters into STRONG / WATCH / SKIP research signals.
Input: data/verified/cluster_signals.json (from cluster_analyzer.py).
Output: data/verified/scored_signals.json — every cluster classified, with the rule that fired.
Side effects: Local file write only; no network.
Idempotent: Yes; deterministic rules, no randomness, no model calls.
Recipe: recipes/insider-cluster-signal-agent.md

Classification uses ONLY trade-time information — cluster size, member roles, conviction,
dollar value. 30-day alpha is deliberately excluded from classification (it is the outcome
being studied; classifying on it would be look-ahead bias) and is reported alongside as the
scoreboard.

Rules (DEFINE closure, recipe v0.3.0), evaluated in order:
  SKIP   — total value < $25k (noise floor), or no officer/director member (pure fund /
           10%-owner clusters skew mechanical, Cohen/Malloy/Pomorski 2012).
  STRONG — >= 3 distinct insiders, or (conviction >= 2.5 and value >= $100k).
  WATCH  — every remaining >= 2-insider cluster.
rank_score = weighted_conviction + log10(total_value_usd)/2, for ordering within tiers.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

MIN_VALUE_USD = 25_000
STRONG_MIN_INSIDERS = 3
STRONG_MIN_CONVICTION = 2.5
STRONG_MIN_VALUE_USD = 100_000


def classify(cluster: dict) -> tuple[str, str]:
    """Return (tier, reason) for one cluster. Trade-time information only."""
    has_operator = any(m["role"] in ("officer", "director") for m in cluster["members"])
    if cluster["total_value_usd"] < MIN_VALUE_USD:
        return "SKIP", f"total value ${cluster['total_value_usd']:,.0f} below ${MIN_VALUE_USD:,} noise floor"
    if not has_operator:
        return "SKIP", "no officer/director member — pure holder clusters skew mechanical"
    if cluster["n_insiders"] >= STRONG_MIN_INSIDERS:
        return "STRONG", f"{cluster['n_insiders']} distinct insiders in one {cluster['window']['start']}..{cluster['window']['end']} window"
    if cluster["weighted_conviction"] >= STRONG_MIN_CONVICTION and cluster["total_value_usd"] >= STRONG_MIN_VALUE_USD:
        return "STRONG", (
            f"conviction {cluster['weighted_conviction']} >= {STRONG_MIN_CONVICTION} "
            f"and value ${cluster['total_value_usd']:,.0f} >= ${STRONG_MIN_VALUE_USD:,}"
        )
    return "WATCH", "2-insider cluster above the noise floor without a STRONG trigger"


def rank_score(cluster: dict) -> float:
    return round(cluster["weighted_conviction"] + math.log10(max(cluster["total_value_usd"], 1)) / 2, 4)


def score(clusters_path: Path, verified_dir: Path) -> dict:
    payload = json.loads(clusters_path.read_text())
    signals = []
    for cluster in payload["clusters"]:
        tier, reason = classify(cluster)
        signals.append({**cluster, "signal": tier, "signal_reason": reason, "rank_score": rank_score(cluster)})
    tier_order = {"STRONG": 0, "WATCH": 1, "SKIP": 2}
    signals.sort(key=lambda s: (tier_order[s["signal"]], -s["rank_score"]))

    summary = {
        "scored_at": datetime.now(timezone.utc).isoformat(),
        "clusters_in": len(signals),
        "strong": sum(1 for s in signals if s["signal"] == "STRONG"),
        "watch": sum(1 for s in signals if s["signal"] == "WATCH"),
        "skip": sum(1 for s in signals if s["signal"] == "SKIP"),
        "rules": {
            "noise_floor_usd": MIN_VALUE_USD,
            "strong_min_insiders": STRONG_MIN_INSIDERS,
            "strong_min_conviction": STRONG_MIN_CONVICTION,
            "strong_min_value_usd": STRONG_MIN_VALUE_USD,
            "alpha_used_in_classification": False,
        },
    }
    verified_dir.mkdir(parents=True, exist_ok=True)
    (verified_dir / "scored_signals.json").write_text(
        json.dumps({"summary": summary, "signals": signals}, indent=2) + "\n"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify buy clusters into STRONG/WATCH/SKIP signals.")
    module_dir = Path(__file__).parent
    parser.add_argument("--clusters", default=str(module_dir / "data" / "verified" / "cluster_signals.json"))
    parser.add_argument("--verified-dir", default=str(module_dir / "data" / "verified"))
    args = parser.parse_args()
    print(json.dumps(score(Path(args.clusters), Path(args.verified_dir)), indent=2))


if __name__ == "__main__":
    main()
