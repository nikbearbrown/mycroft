"""Pre-reader validation: drop empty, tiny, or boilerplate-dominated chunks."""

from __future__ import annotations

import logging
from typing import Any

from ecis.config.settings import settings
from ecis.db.init_db import get_connection, log_agent_action
from ecis.preprocessing.boilerplate import boilerplate_token_ratio

logger = logging.getLogger(__name__)


def validate_chunk(text: str) -> tuple[bool, str | None]:
    stripped = (text or "").strip()
    if not stripped:
        return False, "empty"

    tokens = stripped.split()
    if len(tokens) < settings.min_chunk_tokens:
        return False, "below_min_tokens"

    ratio = boilerplate_token_ratio(stripped)
    if ratio > settings.max_boilerplate_ratio:
        return False, "boilerplate"

    return True, None


def filter_chunks(chunks: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for chunk in chunks:
        ok, reason = validate_chunk(chunk.get("text", ""))
        if ok:
            accepted.append(chunk)
        else:
            rejected.append({
                "chunk_index": chunk.get("chunk_index"),
                "ticker": chunk.get("ticker"),
                "transcript_date": chunk.get("transcript_date"),
                "reason": reason,
                "token_count": len((chunk.get("text") or "").split()),
            })
    return accepted, rejected


def log_rejections(rejected: list[dict[str, Any]]) -> None:
    if not rejected:
        return
    try:
        conn = get_connection("agents")
        conn.executemany(
            """INSERT INTO chunk_rejections
               (ticker, transcript_date, chunk_index, reason, token_count)
               VALUES (?, ?, ?, ?, ?)""",
            [
                (
                    r.get("ticker"),
                    r.get("transcript_date"),
                    r.get("chunk_index"),
                    r.get("reason"),
                    r.get("token_count"),
                )
                for r in rejected
            ],
        )
        conn.commit()
        conn.close()
        log_agent_action(
            "chunk_validator",
            f"{len(rejected)} chunks rejected",
            "reject_chunks",
            ",".join(sorted({r.get("reason") or "?" for r in rejected})),
        )
    except Exception as exc:
        logger.debug("Could not persist chunk rejections: %s", exc)
