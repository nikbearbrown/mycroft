"""The frozen signal contract, the commentary guards, and the scheduler.

The contract tests are the ones that matter longest. `schema_version` 1.0 is
a promise to a consumer this project does not control, and the cheapest way to
break it is to add a field in passing. These tests are what makes that fail
loudly instead of quietly.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.signal import commentary as C  # noqa: E402
from src.signal import contract  # noqa: E402


def minimal() -> dict:
    return contract.envelope(
        period={"latest_period_end": "2026-04-30",
                "first_period_end": "2022-11-30", "periods": 55},
        coverage={"companies": 2, "managers": 5, "marks": 100,
                  "marks_published": 95},
        companies=[{
            "company": "Databricks, Inc.", "status": "full", "marks": 80,
            "managers": 5, "latest_period_end": "2026-04-30",
            "latest_price_min": 169.12, "latest_price_max": 198.01,
            "remark_rate": 0.802,
            "dispersion": {"groups": 12, "median_spread": 0.2193,
                           "max_spread": 1.1186, "suppressed_reason": None},
            "propagation": {"events": 9, "median_days_to_half": 30,
                            "max_days_to_half": 92, "suppressed_reason": None},
        }],
        guards={"change_blocked": 301, "unadjudicated_splits": 0,
                "incomplete_runs": 0, "unresolved_reviews": 0},
    )


# ------------------------------------------------------------- the contract

def test_a_well_formed_signal_validates():
    assert contract.validate(minimal())["schema_version"] == "1.0"


def test_the_version_is_frozen_at_1_0():
    signal = minimal()
    signal["schema_version"] = "1.1"
    with pytest.raises(contract.SignalInvalid):
        contract.validate(signal)


def test_an_unknown_top_level_field_is_rejected():
    """The cheapest way to break a contract is to add a field in passing."""
    signal = minimal()
    signal["extra_insight"] = {"anything": 1}
    with pytest.raises(contract.SignalInvalid, match="extra_insight"):
        contract.validate(signal)


def test_an_unknown_nested_field_is_rejected():
    signal = minimal()
    signal["companies"][0]["confidence"] = 0.9
    with pytest.raises(contract.SignalInvalid):
        contract.validate(signal)


def test_a_missing_required_field_is_rejected():
    signal = minimal()
    del signal["guards"]
    with pytest.raises(contract.SignalInvalid, match="guards"):
        contract.validate(signal)


def test_an_unknown_coverage_status_is_rejected():
    signal = minimal()
    signal["companies"][0]["status"] = "partial"
    with pytest.raises(contract.SignalInvalid):
        contract.validate(signal)


@pytest.mark.parametrize("field", [
    "valuation", "company_valuation", "implied_valuation", "market_cap",
    "post_money", "pre_money", "shares_outstanding", "irr", "moic",
])
def test_the_signal_may_never_carry_a_valuation_field(field):
    """N-PORT gives a fund's share count, never the company's.

    A field for this would invite a consumer to fill it from elsewhere and
    inherit that source's error. The name scan is a standing prohibition,
    independent of what the schema happens to allow today.
    """
    signal = minimal()
    signal["companies"][0][field] = 1
    with pytest.raises(contract.SignalInvalid):
        contract.validate(signal)


@pytest.mark.parametrize("field", [
    "valuation", "implied_valuation", "market_cap", "shares_outstanding",
])
def test_the_name_scan_catches_a_valuation_the_schema_would_allow(field):
    """Defence in depth, and the two layers catch different things.

    `additionalProperties: false` rejects an unknown field wherever the
    schema reaches, so it catches the case above first. The name scan is the
    standing prohibition for anywhere the schema does not reach -- a free
    string, or an object a future version adds deliberately. This test
    exercises the scan directly, because the schema would otherwise mask it.
    """
    found = contract._scan_forbidden({"companies": [{field: 1}]})
    assert found == [f"$.companies[0].{field}"]


def test_the_limits_travel_inside_the_payload():
    """A consumer parsing the signal gets the caveats, not a README."""
    signal = minimal()
    blob = " ".join(signal["not_supported"]).lower()
    assert "shares outstanding" in blob
    assert "lag" in blob
    assert len(signal["not_supported"]) >= 4


def test_commentary_is_always_marked_as_model_output():
    signal = minimal()
    signal["commentary"] = {
        "text": "anything", "is_model_output": False,
        "model": "x", "generated_at": "2026-04-30T00:00:00Z"}
    with pytest.raises(contract.SignalInvalid):
        contract.validate(signal)


def test_a_signal_is_validated_before_it_reaches_disk(tmp_path):
    """There is no path from this module to a file that skips the contract."""
    bad = minimal()
    bad["schema_version"] = "2.0"
    target = tmp_path / "signal.json"
    with pytest.raises(contract.SignalInvalid):
        contract.write(bad, target)
    assert not target.exists()


def test_suppression_is_a_value_not_a_missing_key():
    """"We did not publish this" and "there was nothing" are different."""
    signal = minimal()
    signal["companies"][0]["dispersion"] = {
        "groups": 0, "median_spread": None, "max_spread": None,
        "suppressed_reason": "only 2 managers priced this company"}
    contract.validate(signal)
    assert signal["companies"][0]["dispersion"]["suppressed_reason"]


# ------------------------------------------------------- commentary guards

FACTS = {"companies": [
    {"company": "A", "marks": 2151, "managers": 28, "remark_rate": 0.802},
    {"company": "B", "marks": 31, "managers": 2, "remark_rate": 0.99},
]}


def test_a_fabricated_number_is_caught():
    assert C.check_grounding("A moved 47.3% of the time.", FACTS) == ["47.3"]


def test_a_number_from_the_facts_is_accepted_in_several_renderings():
    """A model given 0.802 will write 80.2%. Both are faithful."""
    for text in ("the rate is 0.802", "the rate is 80.2%", "the rate is 0.80"):
        assert C.check_grounding(text, FACTS) == [], text


def test_small_integers_are_free():
    """"one of the two" is English, not a claim about the data."""
    assert C.check_grounding("Two of the three managers agreed.", FACTS) == []


def test_a_wrong_ranking_is_caught_even_though_every_number_is_real():
    """The failure the first real run actually produced.

    Grounding passed -- every number was one the model had been given -- and
    the prose still said "A has the lowest number of marks, at 2151" while B
    has 31. The number was real; the ranking was invented.
    """
    text = "A has the lowest number of marks, at 2151."
    assert C.check_grounding(text, FACTS) == []
    assert C.check_superlatives(text, FACTS) == ["lowest … 2151"]


def test_a_correct_ranking_passes():
    assert C.check_superlatives("B has the fewest marks, at 31.", FACTS) == []
    assert C.check_superlatives("A has the most marks, at 2151.", FACTS) == []


def test_a_correct_ranking_passes_as_a_percentage():
    assert C.check_superlatives("B has the highest rate, at 99%.", FACTS) == []


def test_the_superlative_check_does_not_cry_wolf_on_sentence_ends():
    """An earlier version captured "30." out of "30. The next" and reported
    it as a failed ranking. A check that cries wolf gets switched off."""
    assert C.check_superlatives("The median was 30. The most was 2151.",
                                FACTS) == []


def test_no_backend_refuses_rather_than_templating():
    """A templated paragraph carrying is_model_output would be
    indistinguishable from model output while not being any."""
    import os

    saved = os.environ.pop("GROQ_API_KEY", None)
    try:
        out = C.write_commentary(FACTS, call=None, backend=None) \
            if not C.available_backends() else {"refused": None}
    finally:
        if saved:
            os.environ["GROQ_API_KEY"] = saved
    if out["refused"] is None:
        pytest.skip("a backend is reachable in this environment")
    assert out["refused"] is True
    assert out["text"] == ""
    assert out["is_model_output"] is True
    assert "no commentary backend" in out["refusal_reason"]


def test_a_refused_commentary_still_says_it_is_model_output():
    """The key's meaning must not depend on whether a model was reachable."""
    out = C.write_commentary(FACTS, call=lambda _: (_ for _ in ()).throw(
        RuntimeError("boom")))
    assert out["refused"] is True
    assert out["is_model_output"] is True
    assert "boom" in out["refusal_reason"]


def test_a_draft_with_a_fabricated_number_is_retried_then_refused():
    attempts = []

    def always_lies(prompt):
        attempts.append(prompt)
        return "The spread was 47.3 percent."

    out = C.write_commentary(FACTS, call=always_lies)
    assert out["refused"] is True
    assert len(attempts) == C.MAX_ATTEMPTS
    assert "47.3" in out["refusal_reason"]


# A draft long enough to clear MIN_WORDS, using only figures from FACTS, so a
# test about the retry loop is not also a test about the length guard.
GOOD_DRAFT = (
    "A reported 2151 marks across 28 managers this period, and its remark "
    "rate stands at 0.802 of consecutive observations. B reported 31 marks "
    "from 2 managers, with a remark rate of 0.99. The gap in coverage between "
    "the two is large enough that the smaller of them cannot be characterised "
    "with any confidence, and this note does not attempt to do so. Nothing "
    "here is a verified claim; the figures are as filed and are reported "
    "without adjustment or interpretation beyond what the panel states."
)


def test_the_retry_hands_the_model_its_own_failure():
    """A specific mechanical complaint is what a model can act on."""
    seen = []

    def improves(prompt):
        seen.append(prompt)
        return ("The spread was 47.3 percent." if len(seen) == 1
                else GOOD_DRAFT)

    out = C.write_commentary(FACTS, call=improves)
    assert out["refused"] is False
    assert len(seen) == 2
    assert "47.3" in seen[1] and "rejected" in seen[1]


def test_a_placeholder_in_the_prose_is_rejected():
    out = C.write_commentary(FACTS, call=lambda _: "A had a spread of null.")
    assert out["refused"] is True
    assert "placeholder" in out["refusal_reason"]


def test_the_prompt_forbids_ranking_and_valuation():
    prompt = C.SYSTEM_PROMPT.lower()
    assert "do not rank" in prompt
    assert "shares outstanding" in prompt
    assert "verified" in prompt
    assert "coverage is thin" in prompt


def test_the_model_is_given_figures_and_nothing_else():
    """No database, no tools, no retrieval, so a number it did not get is
    a number it invented."""
    source = Path(C.__file__).read_text(encoding="utf-8")
    assert "connect(" not in source
    assert "SELECT" not in source


# ----------------------------------------------------------- the n8n lane

WORKFLOW = ROOT / "n8n" / "quarterly_digest.json"


def test_the_workflow_is_valid_json_with_the_expected_shape():
    flow = json.loads(WORKFLOW.read_text(encoding="utf-8"))
    assert flow["nodes"] and flow["connections"]
    kinds = {n["type"] for n in flow["nodes"]}
    assert "n8n-nodes-base.scheduleTrigger" in kinds
    assert "n8n-nodes-base.emailSend" in kinds


def test_the_workflow_embeds_no_secret():
    """Credentials are referenced from the n8n store, never inlined.

    Checked against node parameters and credential blocks rather than the
    whole file, because the file's own notes contain the sentence "this file
    carries no password" and a naive substring scan fails on its own
    documentation.
    """
    flow = json.loads(WORKFLOW.read_text(encoding="utf-8"))
    suspicious = ("password", "apikey", "api_key", "secret", "token",
                  "postgres://", "postgresql://")
    for node in flow["nodes"]:
        blob = json.dumps(node.get("parameters", {})).lower()
        for needle in suspicious:
            assert needle not in blob, f"{node['name']}: {needle}"
        for cred in (node.get("credentials") or {}).values():
            assert set(cred) <= {"id", "name"}, node["name"]


def test_the_workflow_refuses_an_unknown_schema_version():
    """A contract change is not a digest to send."""
    flow = json.loads(WORKFLOW.read_text(encoding="utf-8"))
    blob = json.dumps(flow)
    assert "schema_version" in blob
    assert "n8n-nodes-base.stopAndError" in {n["type"] for n in flow["nodes"]}


def test_the_schedule_is_not_the_quarter_end():
    """Firing on 31 March produces a digest about December.

    Verified lag is ~55-60 days from period end to filing, so the schedule is
    the 20th of the second month after each quarter.
    """
    from scripts import schedule

    assert schedule.DAY_OF_MONTH == 20
    assert schedule.MONTHS == ("FEB", "MAY", "AUG", "NOV")
    assert schedule.CRON == "0 7 20 2,5,8,11 *"

    flow = json.loads(WORKFLOW.read_text(encoding="utf-8"))
    crons = [i["expression"] for n in flow["nodes"]
             for i in n.get("parameters", {}).get("rule", {}).get("interval", [])
             if "expression" in i]
    assert crons == [schedule.CRON], "n8n and the local scheduler disagree"


# ------------------------------- guards added after the first Groq run

def test_a_spelled_out_number_is_checked():
    """The hole a real Groq run exposed.

    It wrote "Dispersion is measured across sixty-one groups". That was
    correct, and it would have passed identically if it had been wrong,
    because the grounding check only read digits. An unchecked figure is the
    whole problem.
    """
    facts = {"companies": [{"groups": 61, "managers": 28}]}
    assert C.check_grounding("across sixty-one groups", facts) == []
    assert C.check_grounding("across seventy-one groups", facts) == ["71"]


@pytest.mark.parametrize("text,expected", [
    ("sixty-one groups", {"61"}),
    ("twenty-eight managers", {"28"}),
    ("twelve managers", {"12"}),
    ("ninety-nine", {"99"}),
])
def test_number_words_convert(text, expected):
    assert C.words_to_numbers(text) == expected


def test_prose_counting_words_are_not_read_as_claims():
    """"one of the two" is English. Only a unit word alone is a figure."""
    assert C.words_to_numbers("one of the best things") == {"1"}
    assert C.words_to_numbers("five three") == set()


def test_an_empty_note_is_refused_not_accepted():
    """The bug: an empty draft passes every content check trivially.

    Nothing to fabricate, nothing to rank, no placeholder. One real run
    reported "0 words" as a success, because a reasoning model spent its
    whole token budget on a hidden channel and returned no prose.
    """
    out = C.write_commentary(FACTS, call=lambda _: "")
    assert out["refused"] is True
    assert "words" in out["refusal_reason"]


def test_a_too_short_note_is_refused():
    out = C.write_commentary(FACTS, call=lambda _: "Marks were published.")
    assert out["refused"] is True
    assert str(C.MIN_WORDS) in out["refusal_reason"]


def test_the_groq_model_is_a_preference_list_not_a_pin():
    """plan.md pins llama-3.3-70b-versatile, which Groq has since retired.

    A valid key plus a retired model name produced HTTP 404 "model does not
    exist or you do not have access to it" -- which reads like a credentials
    problem and is not one. Hosted model names are not stable, so the plan's
    choice stays first in a list rather than being the only option.
    """
    assert isinstance(C.GROQ_MODELS, tuple)
    assert C.GROQ_MODELS[0] == "llama-3.3-70b-versatile"
    assert len(C.GROQ_MODELS) > 1
    assert not hasattr(C, "GROQ_MODEL")


def test_the_prompt_defines_the_term_models_misread():
    """A real run glossed median_days_to_half as "halve the price impact"."""
    prompt = C.SYSTEM_PROMPT
    assert "median_days_to_half" in prompt
    assert "HALF THE MANAGERS WHO EVENTUALLY ADOPTED" in prompt
    assert "not a half-life" in prompt
    assert "digits, not words" in prompt


def test_commentary_loads_its_own_env():
    """An earlier version read GROQ_API_KEY from os.environ and worked only
    because src.db.connect happened to be imported first."""
    source = Path(C.__file__).read_text(encoding="utf-8")
    assert "load_dotenv" in source
