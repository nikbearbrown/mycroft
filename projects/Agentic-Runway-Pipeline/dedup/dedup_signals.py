"""
dedup/dedup_signals.py  —  Sprint 5a: embedding-based deduplication.

When two news sources report the SAME event ("OpenAI raised $2B" from TechCrunch
AND VentureBeat), they should count ONCE, not twice. This uses sentence-transformers
to embed each signal's text and group near-duplicates by cosine similarity.

Requires: pip install sentence-transformers

Run:
    python -m dedup.dedup_signals data/extracted/signals.json --out data/deduped/signals.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

SIM_THRESHOLD = 0.80  # two signals above this cosine similarity = same event


def dedup(signals: list[dict], threshold: float = SIM_THRESHOLD):
    """Group near-duplicate signals; keep the highest-confidence one from each group."""
    from sentence_transformers import SentenceTransformer, util

    if not signals:
        return [], []

    model = SentenceTransformer("all-MiniLM-L6-v2")  # small, fast, ~90MB
    texts = [f"{s.get('company_id','')} {s.get('signal_title','')}" for s in signals]
    embeddings = model.encode(texts, convert_to_tensor=True)

    kept = []
    dropped = []
    used = set()
    for i in range(len(signals)):
        if i in used:
            continue
        group = [i]
        for j in range(i + 1, len(signals)):
            if j in used:
                continue
            sim = float(util.cos_sim(embeddings[i], embeddings[j]))
            # same company AND high text similarity = same event
            if sim >= threshold and signals[i].get("company_id") == signals[j].get("company_id"):
                group.append(j)
                used.add(j)
        used.add(i)
        # keep the highest-confidence signal in the group
        best = max(group, key=lambda k: signals[k].get("score", 0))
        rep = dict(signals[best])
        if len(group) > 1:
            rep["merged_from"] = [signals[k].get("signal_id") for k in group]
            dropped.extend(signals[k] for k in group if k != best)
        kept.append(rep)
    return kept, dropped


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("signals_path")
    ap.add_argument("--out", default=None)
    ap.add_argument("--threshold", type=float, default=SIM_THRESHOLD)
    args = ap.parse_args()

    signals = json.load(open(args.signals_path))
    kept, dropped = dedup(signals, args.threshold)

    print("EMBEDDING DEDUP (sentence-transformers)")
    print("=" * 52)
    print(f"Input signals:  {len(signals)}")
    print(f"After dedup:    {len(kept)}  (removed {len(dropped)} duplicate(s))")
    print()
    for s in kept:
        merged = f"  [merged {len(s['merged_from'])} sources]" if s.get("merged_from") else ""
        print(f"  {s.get('company_id')}: {s.get('signal_title','')[:55]}{merged}")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        json.dump(kept, open(args.out, "w"), indent=2)
        print(f"\n[saved] {len(kept)} deduped signals -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
