"""Join signals from separate model runs on (ticker, transcript_date, content_hash)."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict

from ecis.db.init_db import get_connection


def align_signals() -> dict[str, list[dict]]:
    conn = get_connection("signals")
    try:
        rows = conn.execute(
            """SELECT signal_id, ticker, transcript_date, content_hash, llm_model,
                      direction, confidence_raw, chunk_index
               FROM signals
               WHERE content_hash IS NOT NULL AND content_hash != ''"""
        ).fetchall()
    except Exception:
        conn.close()
        return {}
    conn.close()

    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        key = f"{row['ticker']}|{row['transcript_date']}|{row['content_hash']}"
        groups[key].append(dict(row))
    return {k: v for k, v in groups.items() if len(v) > 1}


def main() -> None:
    parser = argparse.ArgumentParser(description="Align cross-model signals by content hash")
    parser.parse_args()
    aligned = align_signals()
    print(json.dumps({"groups": len(aligned), "sample": list(aligned.items())[:10]}, default=str, indent=2))


if __name__ == "__main__":
    main()
