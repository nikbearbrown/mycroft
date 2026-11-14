import pytest

from gateway.policy import Policy
from gateway.tiers import TierConfig
from gateway.validators import VALIDATOR_NAMES, UnknownValidator, check

SENTIMENT = ["positive", "negative", "neutral"]
VERDICTS = ["contradiction", "consistent", "insufficient_evidence"]


def run(validator, text, **kwargs):
    kwargs.setdefault("tokens_out", 40)
    kwargs.setdefault("max_tokens", 512)
    return check(validator, text, **kwargs)


# -- checks that run before any task-specific one ------------------------

def test_truncation_is_reported_before_emptiness():
    """A cut-off answer is often empty too; truncation is the useful reason."""
    result = run("label_in_set", "", tokens_out=512, max_tokens=512, labels=SENTIMENT)
    assert (result["passed"], result["reason"]) == (False, "truncated")


def test_an_empty_answer_fails():
    result = run("label_in_set", "   ", labels=SENTIMENT)
    assert (result["passed"], result["reason"]) == (False, "empty")


# -- label_in_set --------------------------------------------------------

def test_an_exact_label_passes():
    result = run("label_in_set", "positive", labels=SENTIMENT)
    assert result["passed"] and result["label"] == "positive"


def test_a_label_wrapped_in_prose_is_recovered_and_recorded():
    result = run("label_in_set", "The sentiment is **positive**.", labels=SENTIMENT)
    assert result["passed"]
    assert result["reason"] == "recovered_single_label"


def test_two_labels_in_one_answer_is_ambiguous_and_fails():
    result = run("label_in_set", "could be positive or negative", labels=SENTIMENT)
    assert (result["passed"], result["reason"]) == (False, "label_not_in_set")


def test_a_label_outside_the_set_fails():
    result = run("label_in_set", "bullish", labels=SENTIMENT)
    assert (result["passed"], result["reason"]) == (False, "label_not_in_set")


# -- required_keys -------------------------------------------------------

def test_all_required_keys_present_passes():
    text = '{"metric": "revenue", "direction": "up", "period": "FY"}'
    assert run("required_keys", text,
               required_keys=["metric", "direction", "period"])["passed"]


def test_json_inside_a_code_fence_is_parsed():
    text = '```json\n{"metric": "revenue", "direction": "up", "period": "FY"}\n```'
    assert run("required_keys", text,
               required_keys=["metric", "direction", "period"])["passed"]


def test_a_missing_or_null_key_fails():
    text = '{"metric": "revenue", "direction": null}'
    result = run("required_keys", text,
                 required_keys=["metric", "direction", "period"])
    assert (result["passed"], result["reason"]) == (False, "missing_keys")
    assert result["missing"] == ["direction", "period"]


def test_prose_instead_of_json_fails():
    result = run("required_keys", "Revenue is going up.", required_keys=["metric"])
    assert (result["passed"], result["reason"]) == (False, "not_a_json_object")


# -- verdict_with_quote --------------------------------------------------

STATEMENTS = 'Statement A: "We have no plans to raise prices."\nStatement B: "We raised prices in July."'


def test_a_contradiction_quoting_the_input_passes():
    text = '{"verdict": "contradiction", "quote": "We raised prices in July."}'
    assert run("verdict_with_quote", text, labels=VERDICTS,
               input_text=STATEMENTS)["passed"]


def test_a_contradiction_with_an_invented_quote_fails():
    text = '{"verdict": "contradiction", "quote": "We doubled prices in June."}'
    result = run("verdict_with_quote", text, labels=VERDICTS, input_text=STATEMENTS)
    assert (result["passed"], result["reason"]) == (False, "quote_not_in_input")


def test_a_non_contradiction_needs_no_quote():
    text = '{"verdict": "insufficient_evidence"}'
    assert run("verdict_with_quote", text, labels=VERDICTS,
               input_text=STATEMENTS)["passed"]


def test_a_verdict_outside_the_set_fails():
    text = '{"verdict": "maybe"}'
    result = run("verdict_with_quote", text, labels=VERDICTS, input_text=STATEMENTS)
    assert (result["passed"], result["reason"]) == (False, "verdict_not_in_set")


# -- numbers_grounded ----------------------------------------------------

SOURCE = "Revenue of $412 million, up 9% year over year. Operating margin was 18%."


def test_a_summary_using_only_the_inputs_numbers_passes():
    text = "Revenue reached $412 million, 9% higher, at an 18% margin."
    assert run("numbers_grounded", text, input_text=SOURCE)["passed"]


def test_a_number_not_in_the_input_fails_even_when_the_answer_is_right():
    """summ-004's trap: a correct unit conversion invents a number."""
    source = "Operating margin expanded 150 basis points to 19.5%."
    text = "Operating margin rose 1.5 percentage points to 19.5%."
    result = run("numbers_grounded", text, input_text=source)
    assert (result["passed"], result["reason"]) == (False, "ungrounded_numbers")
    assert 1.5 in result["numbers"]


# -- cites_context -------------------------------------------------------

PASSAGES = ["A dividend is paid out of profits.", "A coupon is a bond's interest."]


def test_a_valid_citation_passes():
    result = run("cites_context", "A bond's coupon is its interest [1].", context=PASSAGES)
    assert result["passed"] and result["cited"] == [1]


def test_a_citation_out_of_range_fails():
    result = run("cites_context", "See [7].", context=PASSAGES)
    assert (result["passed"], result["reason"]) == (False, "citation_out_of_range")


def test_an_answer_with_no_citation_fails():
    result = run("cites_context", "It is the annual interest.", context=PASSAGES)
    assert (result["passed"], result["reason"]) == (False, "no_citation")


# -- fullwidth citation brackets (2026-09-24 judge run) ------------------

def test_a_citation_in_fullwidth_brackets_still_counts():
    """The mid tier wrote 【0】 and was failed for having no citation at all."""
    result = run("cites_context", "A dividend is paid out of profits. 【0】",
                 context=PASSAGES)
    assert result["passed"]
    assert result["cited"] == [0]


def test_ascii_and_fullwidth_citations_are_counted_together():
    result = run("cites_context", "Profits 【0】, and interest [1].", context=PASSAGES)
    assert result["cited"] == [0, 1]


def test_a_fullwidth_citation_out_of_range_is_still_out_of_range():
    """Widening the brackets must not widen what counts as a valid passage."""
    result = run("cites_context", "The answer is no 【7】", context=PASSAGES)
    assert (result["passed"], result["reason"]) == (False, "citation_out_of_range")


# -- wiring --------------------------------------------------------------

def test_an_unknown_validator_raises():
    with pytest.raises(UnknownValidator):
        run("vibes_check", "anything")


def test_every_validator_policy_names_exists_here():
    """Pins policy.json and this module together so they cannot drift."""
    policy = Policy.load(TierConfig.load())
    named = {policy.rule_for(t)["validator"] for t in policy.task_types}
    assert named <= VALIDATOR_NAMES