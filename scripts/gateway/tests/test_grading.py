import pytest

from gateway.bench.grading import grade_answer, normalize, value_matches

KEYS = ["metric", "direction", "period"]
VALUES = {
    "metric": ["revenue"],
    "direction": ["up", "above", "higher", "raise"],
    "period": ["full year", "full-year", "fy"],
}
EXTRACTION = {"required_keys": KEYS, "values": VALUES}
PASSED_KEYS = {"validator": "required_keys", "passed": True, "keys": sorted(KEYS)}


# -- matching ------------------------------------------------------------

def test_punctuation_and_case_do_not_decide_correctness():
    assert normalize("Full-Year, 2026") == "full year 2026"
    assert value_matches("Full-Year 2026", ["full year"])


def test_a_value_counts_when_the_accepted_wording_appears_inside_it():
    """The labeller lists what they would accept, not what the model will say."""
    assert value_matches("revenue guidance", ["revenue"])
    assert value_matches("raised above the prior range", ["above"])


def test_a_value_that_says_something_else_does_not_count():
    assert not value_matches("gross margin", ["revenue"])
    assert not value_matches("down", ["up", "above"])


def test_a_missing_value_does_not_count():
    assert not value_matches(None, ["revenue"])


# -- extraction ----------------------------------------------------------

def test_a_correct_extraction_is_graded_correct():
    text = '{"metric": "revenue", "direction": "above prior range", "period": "FY2026"}'
    result = grade_answer(EXTRACTION, PASSED_KEYS, text)

    assert result["graded"] and result["correct"]
    assert result["wrong_fields"] == []


def test_an_invented_value_is_caught_even_though_the_check_passed():
    """The whole reason acceptable values exist: present is not the same as right."""
    text = '{"metric": "revenue", "direction": "down", "period": "Q3"}'
    result = grade_answer(EXTRACTION, PASSED_KEYS, text)

    assert result["graded"] and not result["correct"]
    assert result["wrong_fields"] == ["direction", "period"]
    assert result["fields"]["direction"]["got"] == "down"


def test_an_extraction_with_no_acceptable_values_is_not_graded():
    result = grade_answer({"required_keys": KEYS}, PASSED_KEYS, "{}")

    assert result["graded"] is False
    assert result["correct"] is None


def test_unparseable_json_grades_wrong_rather_than_ungraded():
    result = grade_answer(EXTRACTION, PASSED_KEYS, "Revenue is going up.")

    assert result["graded"] and result["correct"] is False
    assert result["reason"] == "not_a_json_object"


def test_json_inside_a_fence_is_graded_the_same_way_the_check_parsed_it():
    text = '```json\n{"metric": "revenue", "direction": "up", "period": "fy"}\n```'
    assert grade_answer(EXTRACTION, PASSED_KEYS, text)["correct"]


def test_the_no_guidance_fixture_grades_on_the_word_none():
    none_key = {"required_keys": KEYS,
                "values": {k: ["none", "n/a", "not given"] for k in KEYS}}
    text = '{"metric": "none", "direction": "none", "period": "none"}'
    assert grade_answer(none_key, PASSED_KEYS, text)["correct"]


# -- the other task types ------------------------------------------------

def test_a_label_is_graded_against_the_key():
    checked = {"validator": "label_in_set", "passed": True, "label": "positive"}
    assert grade_answer({"label": "positive"}, checked, "positive")["correct"]
    assert not grade_answer({"label": "negative"}, checked, "positive")["correct"]


def test_a_citation_is_graded_on_whether_the_right_passage_was_cited():
    checked = {"validator": "cites_context", "passed": True, "cited": [1]}
    assert grade_answer({"cite": 1}, checked, "answer [1]")["correct"]
    assert not grade_answer({"cite": 0}, checked, "answer [1]")["correct"]


def test_prose_is_reported_as_ungraded_and_says_why():
    result = grade_answer({}, {}, "A summary.")

    assert result["graded"] is False
    assert result["correct"] is None
    assert "kappa 0.00" in result["reason"]