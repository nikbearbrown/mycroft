"""Pairwise quality judging: a stronger model compares two answers.

This is the only part of the system that tries to say an answer is GOOD, as
opposed to well-formed. The deterministic checks in validators.py catch a
malformed answer; nothing in the request path catches an answer that is
fluent, well-shaped and wrong.

Three rules this module exists to hold:

1. It never runs in the request path. A comparison costs two strong-model
   calls and changes no routing decision. It runs offline, over answers that
   have already been logged.
2. Every comparison runs twice with the two answers swapped. Models tend to
   favour whatever they read first, so a single direction measures that
   habit as much as it measures quality. When the two runs disagree the
   result is `inconsistent` -- recorded as such, never resolved by picking
   one. The disagreement IS the finding.
3. A verdict is a model judgment and is labeled as one (P8). It is not ground
   truth, and a count of verdicts is not an accuracy figure.

Sprint 6 measures how far these verdicts can be trusted, by having a human
score the same answers blind and comparing the two.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Callable

from gateway.client import GatewayClient
from gateway.schema import utc_now_iso

JUDGE_TASK_TYPE = "judge_pairwise"
JUDGE_CALLER = "bench.judge"

# "a" / "b": both runs agreed that answer won. "tie": both said equal.
# "inconsistent": the runs disagreed -- position bias, or a call too close
# to make. "unparsed": at least one reply did not name a verdict.
RESULTS = frozenset({"a", "b", "tie", "inconsistent", "unparsed"})

_VERDICT = re.compile(r"\b(FIRST|SECOND|TIE)\b")


def build_prompt(*, asks: str, input_text: str, first: str, second: str,
                 context: list[str] | None = None) -> str:
    """The judging prompt. `first` is whatever is shown first -- that is the swap."""
    parts = [
        "You are comparing two answers to the same task. Judge only how well "
        "each answer does the task. Ignore length, tone and formatting unless "
        "the task asks for them.",
        "",
        f"TASK: {asks}",
        "",
        f"INPUT:\n{input_text}",
    ]
    if context:
        parts += ["", "CONTEXT:"] + [f"[{n}] {p}" for n, p in enumerate(context)]
    parts += [
        "",
        f"ANSWER ONE:\n{first}",
        "",
        f"ANSWER TWO:\n{second}",
        "",
        "Reply with exactly one word and nothing else: FIRST if answer one "
        "does the task better, SECOND if answer two does, TIE if they are "
        "equally good.",
    ]
    return "\n".join(parts)


def parse_verdict(text: str) -> str | None:
    """"first" / "second" / "tie", or None when the reply does not say one clearly.

    The last line is read first: a model that reasons before answering puts
    its verdict at the end. A reply naming more than one verdict is not a
    verdict -- None, recorded as `unparsed`, is more honest than a coin flip.
    """
    lines = [line for line in (text or "").splitlines() if line.strip()]
    for candidate in ([lines[-1]] if lines else []) + [text or ""]:
        found = set(_VERDICT.findall(candidate.upper()))
        if len(found) == 1:
            return found.pop().lower()
    return None


def _map_back(verdict: str | None, order: str) -> str | None:
    """Turn a verdict about position into a verdict about an answer."""
    if verdict in (None, "tie"):
        return verdict
    shown_first, shown_second = ("a", "b") if order == "ab" else ("b", "a")
    return shown_first if verdict == "first" else shown_second


@dataclass(frozen=True)
class Vote:
    """One judging call: which answer won, and what it cost to ask."""

    order: str            # "ab" = answer A was shown first; "ba" = B was
    verdict: str | None   # "a" | "b" | "tie", or None if unparsed
    raw: str
    request_id: str
    cost_usd: float
    latency_ms: int


@dataclass(frozen=True)
class Comparison:
    """Two votes on one pair of answers, and what they add up to."""

    fixture_id: str
    a_label: str          # what produced answer A, e.g. "cheap"
    b_label: str
    result: str           # one of RESULTS
    votes: tuple[Vote, Vote]
    cost_usd: float
    judged_by: str        # the model that judged
    judged_at: str
    kind: str = "model_judgment"  # P8: labeled as a judgment, wherever it travels

    def to_record(self) -> dict[str, Any]:
        record = asdict(self)
        record["votes"] = [asdict(v) for v in self.votes]
        return record


def compare(client: GatewayClient, *, fixture_id: str, asks: str, input_text: str,
            answer_a: str, answer_b: str, a_label: str, b_label: str,
            context: list[str] | None = None, tier: str = "strong",
            max_tokens: int = 256,
            now: Callable[[], str] = utc_now_iso) -> Comparison:
    """Judge one pair, both ways round. Two logbook rows, one Comparison."""
    votes: list[Vote] = []
    for order in ("ab", "ba"):
        first, second = ((answer_a, answer_b) if order == "ab"
                         else (answer_b, answer_a))
        call = client.call(
            task_type=JUDGE_TASK_TYPE, caller=JUDGE_CALLER, tier=tier,
            prompt=build_prompt(asks=asks, input_text=input_text,
                                first=first, second=second, context=context),
            max_tokens=max_tokens,
            # Not a routing decision: the judge tier is named outright, so
            # these rows never look like policy traffic in the reports.
            routing_reason="override",
            notes=f"judge {fixture_id} order={order}",
        )
        votes.append(Vote(
            order=order,
            verdict=_map_back(parse_verdict(call.response.text), order),
            raw=call.response.text.strip(),
            request_id=call.request_id,
            cost_usd=float(call.record["cost_usd"]),
            latency_ms=int(call.record["latency_ms"]),
        ))

    one, two = votes
    if one.verdict is None or two.verdict is None:
        result = "unparsed"
    elif one.verdict == two.verdict:
        result = one.verdict
    else:
        result = "inconsistent"

    return Comparison(
        fixture_id=fixture_id, a_label=a_label, b_label=b_label, result=result,
        votes=(one, two), cost_usd=one.cost_usd + two.cost_usd,
        judged_by=client.tiers[tier]["model"], judged_at=now(),
    )


def summarize(comparisons: list[Comparison]) -> dict[str, Any]:
    """Counts, and what they cost. Counts only -- no quality score is implied.

    `inconsistent` is the number to read first. It is not noise to be tidied
    away: it is the share of comparisons where the judge's answer depended on
    which answer it read first.
    """
    counts = {name: 0 for name in sorted(RESULTS)}
    for comparison in comparisons:
        counts[comparison.result] += 1
    return {
        "comparisons": len(comparisons),
        "counts": counts,
        "decided": counts["a"] + counts["b"] + counts["tie"],
        "cost_usd": round(sum(c.cost_usd for c in comparisons), 6),
        "kind": "model_judgment",
        "note": "verdicts are model judgments, not ground truth; "
                "Sprint 6 measures how far they agree with a human",
    }