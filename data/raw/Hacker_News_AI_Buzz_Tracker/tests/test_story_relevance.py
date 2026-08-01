"""
Fixture tests for story_relevance.py (Week 10 attribution fix). No network calls.
The canonical Bento misattribution is reproduced as a fixture: a high-points
story that only name-drops the entities must NOT be selected as a top story.

Runs both ways:
    pytest tests/test_story_relevance.py -v
    python tests/test_story_relevance.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from story_relevance import title_matches, select_top_stories


# The real Week 9 case: Bento out-pointed everything but is about a slide tool.
BENTO = {"title": "Show HN: Bento - An entire PowerPoint in one HTML file",
         "points": 1018, "objectID": "49008211"}
OPENAI_REAL = {"title": "OpenAI releases GPT-5", "points": 300, "objectID": "1"}
ANTHROPIC_REAL = {"title": "Claude Opus 4.5 is available", "points": 250, "objectID": "2"}


def test_title_matches_basic():
    assert title_matches("OpenAI releases GPT-5", ["OpenAI", "ChatGPT"]) is True


def test_title_matches_case_insensitive():
    assert title_matches("A look at claude's context window", ["Claude"]) is True


def test_title_matches_body_only_mention_is_false():
    # Bento's title never names the entity; the mention is body-only.
    assert title_matches(BENTO["title"], ["OpenAI", "ChatGPT"]) is False
    assert title_matches(BENTO["title"], ["Anthropic", "Claude"]) is False


def test_title_matches_none_and_blank_terms():
    assert title_matches(None, ["OpenAI"]) is False
    assert title_matches("OpenAI ships", ["", "   "]) is False


def test_select_excludes_bento_even_though_highest_points():
    hits = [BENTO, OPENAI_REAL]
    top = select_top_stories(hits, ["OpenAI", "ChatGPT", "GPT-5"], n=3)
    ids = [h["objectID"] for h in top]
    assert "49008211" not in ids and ids == ["1"]


def test_select_degrades_to_empty_when_nothing_relevant():
    # Only the incidental story is present -> no relevant top story.
    top = select_top_stories([BENTO], ["Anthropic", "Claude"], n=3)
    assert top == []


def test_select_preserves_points_order_among_relevant():
    a = {"title": "Claude adds tools", "points": 100, "objectID": "a"}
    b = {"title": "Claude pricing drop", "points": 400, "objectID": "b"}
    top = select_top_stories([a, b, BENTO], ["Claude"], n=3)
    assert [h["objectID"] for h in top] == ["b", "a"]


def test_select_falls_back_when_terms_missing():
    # No terms -> cannot judge relevance -> points-ranked top-N unfiltered.
    top = select_top_stories([BENTO, OPENAI_REAL], [], n=1)
    assert top[0]["objectID"] == "49008211"


TESTS = [
    test_title_matches_basic,
    test_title_matches_case_insensitive,
    test_title_matches_body_only_mention_is_false,
    test_title_matches_none_and_blank_terms,
    test_select_excludes_bento_even_though_highest_points,
    test_select_degrades_to_empty_when_nothing_relevant,
    test_select_preserves_points_order_among_relevant,
    test_select_falls_back_when_terms_missing,
]


def run_tests():
    passed = failed = 0
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
