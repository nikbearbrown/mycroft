"""The free checks. Each one decides whether an answer is USABLE, not whether
it is CORRECT.

That distinction is the whole design constraint. A model that misreads a
sarcastic post still returns an allowed label, so `label_in_set` passes it and
nothing escalates. These checks catch malformed answers -- empty, cut off,
unparseable, unlabelled, ungrounded -- and nothing else. Judging correctness
needs an answer key (the benchmark has one; production does not) or a stronger
model (which costs as much as just retrying).

Every check is a pure function of text already in hand, so running them adds
no cost and no latency, which is what makes them safe to run on every call.

Two checks run before any task-specific one:
  - truncated: tokens_out hit the budget, so the answer was cut off mid-flight
  - empty: nothing came back at all
Truncation is checked first: a cut-off answer is often also empty, and
"truncated" is the more useful reason to record.
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable

NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?")
CITATION = re.compile(r"\[(\d+)\]")
FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)

# Models sometimes cite with fullwidth brackets -- 【0】 instead of [0] -- even
# though the prompt shows the ASCII form. The citation is right and only the
# glyph differs, so rejecting it escalates a correct answer to a dearer tier
# over punctuation. Seen on 3 of 8 answers in the 2026-09-24 judge run, all
# from the mid tier. Widening the check is the fix; the prompt already asks
# for [0] and asking harder did not stop it.
FULLWIDTH_BRACKETS = str.maketrans({
    "【": "[", "】": "]",
    "［": "[", "］": "]",
    "〔": "[", "〕": "]",
})


class UnknownValidator(KeyError):
    """Raised when policy names a validator this module does not implement."""


def _squash(text: str) -> str:
    """Case- and whitespace-insensitive form, for substring comparison."""
    return " ".join(text.lower().split())


def _numbers(text: str) -> list[float]:
    out = []
    for raw in NUMBER.findall(text):
        try:
            out.append(float(raw.replace(",", "")))
        except ValueError:
            continue
    return out


def _normalize_label(text: str) -> str:
    cleaned = text.strip().strip("`\"'*").strip()
    if ":" in cleaned[:12]:  # e.g. "Label: positive"
        cleaned = cleaned.split(":", 1)[1]
    return cleaned.strip().strip(".`\"'*").strip().lower()


def _extract_json(text: str) -> Any:
    """Parse JSON from a response that may be fenced or have prose around it."""
    for candidate in (text, *(m.group(1) for m in FENCE.finditer(text))):
        try:
            return json.loads(candidate.strip())
        except (json.JSONDecodeError, AttributeError):
            continue
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            return None
    return None


# -- the five task-type checks ------------------------------------------

def _label_in_set(text: str, *, labels: list[str] | None = None, **_) -> dict[str, Any]:
    if not labels:
        raise ValueError("label_in_set needs the allowed labels")

    normalized = _normalize_label(text)
    if normalized in labels:
        return {"passed": True, "reason": "", "label": normalized}

    # A model that answers "The sentiment is positive." got the answer right
    # and the format wrong. Recovering it avoids paying for an escalation over
    # punctuation -- but the recovery is recorded, so Sprint 6 can count how
    # often it was needed. Two labels in one answer is ambiguous, not recoverable.
    found = [x for x in labels if re.search(rf"\b{re.escape(x)}\b", text, re.IGNORECASE)]
    if len(found) == 1:
        return {"passed": True, "reason": "recovered_single_label", "label": found[0]}

    return {"passed": False, "reason": "label_not_in_set", "got": text[:120]}


def _required_keys(text: str, *, required_keys: list[str] | None = None, **_) -> dict[str, Any]:
    if not required_keys:
        raise ValueError("required_keys needs the key list")

    data = _extract_json(text)
    if not isinstance(data, dict):
        return {"passed": False, "reason": "not_a_json_object", "got": text[:120]}

    missing = [k for k in required_keys if data.get(k) is None]
    if missing:
        return {"passed": False, "reason": "missing_keys", "missing": missing}
    return {"passed": True, "reason": "", "keys": sorted(data)}


def _verdict_with_quote(text: str, *, labels: list[str] | None = None,
                        input_text: str = "", **_) -> dict[str, Any]:
    if not labels:
        raise ValueError("verdict_with_quote needs the allowed verdicts")

    data = _extract_json(text)
    if not isinstance(data, dict):
        return {"passed": False, "reason": "not_a_json_object", "got": text[:120]}

    verdict = str(data.get("verdict", "")).strip().lower()
    if verdict not in labels:
        return {"passed": False, "reason": "verdict_not_in_set", "got": verdict[:60]}

    # Only a claimed contradiction has to point at the conflicting words.
    if verdict == "contradiction":
        quote = str(data.get("quote") or "").strip()
        if not quote:
            return {"passed": False, "reason": "quote_missing", "verdict": verdict}
        if _squash(quote) not in _squash(input_text):
            return {"passed": False, "reason": "quote_not_in_input", "quote": quote[:120]}
    return {"passed": True, "reason": "", "verdict": verdict}


def _numbers_grounded(text: str, *, input_text: str = "", **_) -> dict[str, Any]:
    source = set(_numbers(input_text))
    ungrounded = [n for n in _numbers(text) if n not in source]
    if ungrounded:
        return {"passed": False, "reason": "ungrounded_numbers",
                "numbers": ungrounded[:5]}
    return {"passed": True, "reason": "", "numbers_checked": len(_numbers(text))}


def _cites_context(text: str, *, context: list[str] | None = None, **_) -> dict[str, Any]:
    passages = context or []
    cited = [int(n) for n in CITATION.findall(text.translate(FULLWIDTH_BRACKETS))]
    if not cited:
        return {"passed": False, "reason": "no_citation"}
    valid = [c for c in cited if 0 <= c < len(passages)]
    if not valid:
        return {"passed": False, "reason": "citation_out_of_range", "cited": cited}
    return {"passed": True, "reason": "", "cited": valid}


_VALIDATORS: dict[str, Callable[..., dict[str, Any]]] = {
    "label_in_set": _label_in_set,
    "required_keys": _required_keys,
    "verdict_with_quote": _verdict_with_quote,
    "numbers_grounded": _numbers_grounded,
    "cites_context": _cites_context,
}

VALIDATOR_NAMES = frozenset(_VALIDATORS)


def check(validator: str, text: str, *, tokens_out: int, max_tokens: int,
          labels: list[str] | None = None, required_keys: list[str] | None = None,
          input_text: str = "", context: list[str] | None = None) -> dict[str, Any]:
    """Run one validator. Returns a dict ready to store as `validator_result`."""
    if validator not in _VALIDATORS:
        raise UnknownValidator(
            f"no validator named {validator!r}; known: {sorted(VALIDATOR_NAMES)}")

    result: dict[str, Any] = {"validator": validator}

    if tokens_out >= max_tokens:
        return {**result, "passed": False, "reason": "truncated",
                "tokens_out": tokens_out, "max_tokens": max_tokens}
    if not (text or "").strip():
        return {**result, "passed": False, "reason": "empty"}

    return {**result, **_VALIDATORS[validator](
        text.strip(), labels=labels, required_keys=required_keys,
        input_text=input_text, context=context)}