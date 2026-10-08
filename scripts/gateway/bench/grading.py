"""Grade an answer against the answer key -- correctness, not shape.

The checks in validators.py are free and run on every call, and they only see
whether an answer is usable. Grading needs the key, which exists in the
benchmark and does not exist in production. That asymmetry is the reason the
benchmark exists at all.

Four task types can be graded exactly: a label, a verdict, a citation index,
and -- since the answer key gained acceptable values on 2026-10-01 -- a
structured extraction. Prose cannot, and its quality is recorded as unmeasured
rather than guessed at: the model judge built for it scored kappa 0.00 against
a human (FINDINGS section 10).

A value matches if any of the labeller's acceptable answers appears inside it,
after both are lowercased and stripped of punctuation. "full-year 2026"
matches "full year", so the labeller does not have to predict the model's
phrasing -- only to list what they would accept.
"""

from __future__ import annotations

import re
from typing import Any

from gateway.validators import extract_json

# Keeps digits, percent signs and decimal points, which carry meaning in a
# financial answer. Everything else becomes a space, so "fourth-quarter" and
# "fourth quarter" compare equal.
_PUNCTUATION = re.compile(r"[^a-z0-9%.]+")


def normalize(value: Any) -> str:
    return " ".join(_PUNCTUATION.sub(" ", str(value).lower()).split())


def value_matches(got: Any, accepted: list[str]) -> bool:
    """True if the model's value contains any wording the labeller allowed."""
    if got is None:
        return False
    normalized = normalize(got)
    return any(normalize(a) in normalized for a in accepted if str(a).strip())


def grade_answer(expected: dict[str, Any], checked: dict[str, Any],
                 text: str) -> dict[str, Any]:
    """Compare one answer with the answer key. `checked` is the validator result."""
    checked = checked or {}

    if "label" in expected:  # label and verdict tasks
        got = checked.get("label") or checked.get("verdict")
        return {"graded": True, "correct": got == expected["label"],
                "expected": expected["label"], "got": got}

    if "cite" in expected:
        cited = checked.get("cited") or []
        return {"graded": True, "correct": expected["cite"] in cited,
                "expected": expected["cite"], "got": cited}

    if "required_keys" in expected:
        values = expected.get("values")
        if not values:
            return {"graded": False, "correct": None,
                    "reason": "no acceptable values in the answer key; the key "
                              "check cannot tell a right answer from an invented one"}

        data = extract_json(text)
        if not isinstance(data, dict):
            return {"graded": True, "correct": False,
                    "reason": "not_a_json_object", "got": text[:120]}

        fields = {field: {"got": data.get(field),
                          "accepted": accepted,
                          "correct": value_matches(data.get(field), accepted)}
                  for field, accepted in values.items()}
        wrong = sorted(f for f, r in fields.items() if not r["correct"])
        return {"graded": True, "correct": not wrong, "fields": fields,
                "wrong_fields": wrong}

    return {"graded": False, "correct": None,
            "reason": "open prose; no answer key can exist, and the model judge "
                      "scored kappa 0.00 against a human (FINDINGS section 10)"}