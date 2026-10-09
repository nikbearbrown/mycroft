"""Token bounding and cursors, separated from the tools that use them.

`plan.md` week 10: "Every response is token-bounded with a cursor -- a tool
returning the whole marks table is useless to a model, so summary-first with
drill-down is the rule."

That sentence is the whole design, and it is a harder constraint than it
sounds. The marks table holds 5,479 rows. Serialised as JSON at roughly 55
tokens a row it is about 300,000 tokens -- more than most context windows, and
useless even where it fits, because a model handed 5,479 rows will not read
them. So every tool here answers in three parts:

  1. a **summary** the model can act on without reading any rows,
  2. a **bounded page** of rows,
  3. a **cursor** and an explicit count of what was left out.

This module exists separately from `server.py` so the bounding can be tested
without starting a server, and so a tool cannot quietly opt out of it: the
tools do not assemble their own envelopes.

--------------------------------------------------------------------------
Why the cursor is opaque and stateless
--------------------------------------------------------------------------
A cursor here is a base64 JSON blob carrying the offset and a digest of the
query arguments. It holds no server state, so the server can restart between
two pages, and the digest means a cursor cannot be replayed against different
arguments to silently page through a different result set.
"""

from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

# A page the model will actually read. Chosen from the row widths in this
# project rather than from a round number: a marks row serialises to roughly
# 55 tokens, so 50 rows is about 2,750 tokens of payload plus the summary --
# comfortably inside a tool-result budget, and small enough that a model
# treats it as a sample rather than a dataset.
DEFAULT_LIMIT = 50
MAX_LIMIT = 200

# Hard ceiling on a single response regardless of row count, measured in
# characters because that is what can be checked without a tokenizer. ~4 chars
# per token puts this near 12,000 tokens, which is the point where a tool
# result stops being useful as context and starts crowding out the
# conversation.
MAX_RESPONSE_CHARS = 48_000


class CursorError(ValueError):
    """A cursor that does not belong to this query."""


def _digest(scope: dict) -> str:
    payload = json.dumps(scope, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def encode_cursor(offset: int, scope: dict) -> str:
    blob = json.dumps({"o": offset, "d": _digest(scope)}, separators=(",", ":"))
    return base64.urlsafe_b64encode(blob.encode("utf-8")).decode("ascii")


def decode_cursor(cursor: str | None, scope: dict) -> int:
    """The offset a cursor stands for, or 0.

    Raises if the cursor was minted for different arguments. Without that
    check, a model that reused a cursor from `get_marks("Databricks")` on
    `get_marks("Anthropic")` would get Anthropic rows numbered from
    Databricks' offset and no indication anything was wrong.
    """
    if not cursor:
        return 0
    try:
        blob = json.loads(base64.urlsafe_b64decode(cursor.encode("ascii")))
        offset, digest = int(blob["o"]), str(blob["d"])
    except Exception as exc:                       # noqa: BLE001
        raise CursorError(f"malformed cursor: {exc}") from exc
    if digest != _digest(scope):
        raise CursorError(
            "this cursor was issued for different arguments. Cursors are "
            "bound to the query that produced them; start again without a "
            "cursor to page this one.")
    return max(0, offset)


def clamp(limit: int | None) -> int:
    if limit is None:
        return DEFAULT_LIMIT
    return max(1, min(int(limit), MAX_LIMIT))


def _shrink(rows: list[dict], envelope: dict) -> tuple[list[dict], bool]:
    """Drop rows until the serialised envelope fits MAX_RESPONSE_CHARS.

    The limit is enforced on the real serialised size rather than on a row
    count, because row width is not uniform -- a fund-exposure row with a long
    registrant name is several times a marks row. A tool that returned 50 rows
    of either kind would be well-behaved for one and oversized for the other.
    """
    trimmed = False
    while rows:
        probe = dict(envelope, rows=rows)
        if len(json.dumps(probe, default=str)) <= MAX_RESPONSE_CHARS:
            break
        rows = rows[: max(1, len(rows) * 3 // 4)]
        trimmed = True
        if len(rows) == 1:
            break
    return rows, trimmed


def page(rows: list[dict], *, scope: dict, cursor: str | None = None,
         limit: int | None = None, summary: dict | None = None,
         note: str | None = None) -> dict[str, Any]:
    """One token-bounded response: summary first, then a bounded page.

    `rows` is the full result. Paging in Python rather than in SQL is
    deliberate here: these result sets are thousands of rows, not millions,
    and the summary has to describe the whole set rather than the page -- a
    summary computed over page one would say "3 managers" about a company held
    by thirty.
    """
    offset = decode_cursor(cursor, scope)
    size = clamp(limit)
    window = rows[offset:offset + size]

    envelope: dict[str, Any] = {
        "summary": summary or {},
        "page": {
            "offset": offset,
            "returned": len(window),
            "total": len(rows),
            "remaining": max(0, len(rows) - offset - len(window)),
        },
        "rows": [],
    }
    window, trimmed = _shrink(window, envelope)
    envelope["rows"] = window
    envelope["page"]["returned"] = len(window)
    envelope["page"]["remaining"] = max(0, len(rows) - offset - len(window))

    if envelope["page"]["remaining"]:
        envelope["next_cursor"] = encode_cursor(offset + len(window), scope)
        envelope["page"]["note"] = (
            f"{envelope['page']['remaining']} further rows. Pass next_cursor "
            "to continue, or narrow the arguments instead -- the summary "
            "above already describes the whole result set, not this page.")
    if trimmed:
        envelope["page"]["truncated_for_size"] = True

    if note:
        envelope["note"] = note
    return envelope
