"""Fixture audit, and the freeze that locks the set.

Usage:
    python scripts/gateway/bench/audit.py            # coverage report
    python scripts/gateway/bench/audit.py --freeze   # write manifest.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gateway.bench import fixtures as fx
from gateway.policy import Policy
from gateway.tiers import TierConfig


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit or freeze the fixture set.")
    parser.add_argument("--freeze", action="store_true",
                        help="write manifest.json; refuses while labels are unreviewed")
    args = parser.parse_args()

    policy = Policy.load(TierConfig.load())
    fixtures = fx.validate(fx.load(), policy)

    table = fx.coverage(fixtures, policy)
    print(f"{'task type':<26}{'easy':>6}{'hard':>6}{'total':>7}"
          f"{'reviewed':>10}{'target':>8}{'short':>7}")
    for task_type, row in table.items():
        print(f"{task_type:<26}{row['easy']:>6}{row['hard']:>6}{row['total']:>7}"
              f"{row['reviewed']:>10}{fx.TARGET_PER_TYPE:>8}{row['short']:>7}")
    print(f"\n{len(fixtures)} fixtures, all conform. Provenance: "
          f"{sorted({f['provenance'] for f in fixtures})}")

    if not args.freeze:
        return 0
    try:
        manifest = fx.freeze(fixtures, policy)
    except fx.NotReviewed as exc:
        print(f"\nNot frozen: {exc}")
        return 1
    fx.MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"\nFrozen: {manifest['fixture_count']} fixtures -> {fx.MANIFEST_PATH.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())