"""
Fixture tests for community_opinion.py's HTML-cleaning, dedup, and JSON
parsing steps (plan.md Week 9: "add fixture tests for the HTML-cleaning and
parsing steps"). No network calls — the LLM call itself is not exercised here.

Runs both ways:
    pytest tests/test_community_opinion.py -v      (assert-based)
    python tests/test_community_opinion.py         (standalone runner below)
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from community_opinion import (
    clean_comment, clean_and_dedupe, parse_and_validate, parse_sector_response,
    _degraded, _degraded_sector,
)


def test_clean_comment_strips_tags_and_entities():
    raw = "<p>We&#x27;re re-evaluating <i>our</i> stack &amp; budget.</p>"
    out = clean_comment(raw)
    assert out == "We're re-evaluating our stack & budget."


def test_clean_comment_collapses_whitespace():
    raw = "Line one.\n\n\nLine   two."
    out = clean_comment(raw)
    assert out == "Line one. Line two."


def test_clean_comment_truncates():
    raw = "x" * 900
    out = clean_comment(raw)
    assert len(out) == 500


def test_clean_comment_empty_and_none():
    assert clean_comment("") is None and clean_comment(None) is None and clean_comment("<p></p>") is None


def test_clean_and_dedupe_drops_exact_repeats():
    raw = ["<p>same thing</p>", "same thing", "<p>different thing</p>"]
    out = clean_and_dedupe(raw)
    assert out == ["same thing", "different thing"]


def test_parse_and_validate_happy_path():
    raw = json.dumps({
        "summary": "Developers are split on pricing but praise reasoning gains.",
        "sentiment": "mixed",
        "themes": ["pricing", "reasoning quality", "extra", "extra2", "extra3", "extra4"],
        "notableOpinions": ["quote one", "quote two", "quote three", "quote four"],
    })
    out = parse_and_validate(raw)
    assert (out["summary"] and out["sentiment"] == "mixed"
            and len(out["themes"]) == 5 and len(out["notableOpinions"]) == 3
            and out["enumCoerced"] is False)


def test_parse_and_validate_coerces_bad_sentiment():
    raw = json.dumps({"summary": "Some summary.", "sentiment": "very happy", "themes": []})
    out = parse_and_validate(raw)
    assert out["sentiment"] == "neutral" and out["enumCoerced"] is True


def test_parse_and_validate_strips_stray_prose():
    raw = 'Here you go:\n{"summary": "ok", "sentiment": "positive", "themes": []}\nHope that helps!'
    out = parse_and_validate(raw)
    assert out["summary"] == "ok" and out["sentiment"] == "positive"


def test_parse_and_validate_rejects_empty_summary():
    raw = json.dumps({"summary": "   ", "sentiment": "neutral", "themes": []})
    try:
        parse_and_validate(raw)
    except ValueError:
        return
    raise AssertionError("expected ValueError for empty summary")


def test_parse_sector_response_happy_path():
    raw = json.dumps({
        "sectorNarrative": "This week's discussion centered on pricing pressure across labs.",
        "crossEntityThemes": ["pricing", "reasoning quality"],
    })
    out = parse_sector_response(raw)
    assert out["sectorNarrative"] and out["crossEntityThemes"] == ["pricing", "reasoning quality"]


def test_degraded_shape_has_null_fields():
    d = _degraded("no comments available for this entity's top stories", provider="none")
    assert d["degraded"] is True and d["summary"] is None and d["sentiment"] is None


def test_degraded_sector_shape_has_null_fields():
    d = _degraded_sector("no non-degraded entity opinions this run", provider="none")
    assert d["degraded"] is True and d["sectorNarrative"] is None


TESTS = [
    test_clean_comment_strips_tags_and_entities,
    test_clean_comment_collapses_whitespace,
    test_clean_comment_truncates,
    test_clean_comment_empty_and_none,
    test_clean_and_dedupe_drops_exact_repeats,
    test_parse_and_validate_happy_path,
    test_parse_and_validate_coerces_bad_sentiment,
    test_parse_and_validate_strips_stray_prose,
    test_parse_and_validate_rejects_empty_summary,
    test_parse_sector_response_happy_path,
    test_degraded_shape_has_null_fields,
    test_degraded_sector_shape_has_null_fields,
]


def run_tests():
    """Standalone runner: a test passes if it returns without raising (asserts
    do the checking now, matching how pytest judges the same functions)."""
    passed = 0
    failed = 0
    for t in TESTS:
        try:
            t()
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL  [{t.__name__}]  {type(exc).__name__}: {exc}")
        else:
            passed += 1
            print(f"PASS  [{t.__name__}]")
    print(f"\n{passed} passed, {failed} failed")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
