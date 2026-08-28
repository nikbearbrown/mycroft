"""Week 5 regression tests: the LLM adjudication layer.

Every test here runs against `StubBackend`. None of them needs Ollama, a model
on disk, or a GPU — a test suite that only passes on the machine with the
weights is not a regression suite. What is tested is everything around the
model: the prompt, the schema, the parsing, the refusal path, and above all the
*policy* deciding when the model is allowed to speak at all.

The measured lift is a separate artifact (docs/_adjudication_metrics.json) and
is a separate set of tests at the bottom, which skip when the cache is absent.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.resolve.adjudicate import (  # noqa: E402
    AUTO_ACCEPT,
    CANONICAL,
    POLICY_ALL,
    POLICY_BAND,
    POLICY_LLM_ONLY,
    POLICY_VETO,
    RESPONSE_SCHEMA,
    Adjudication,
    adjudicate,
    build_prompt,
    candidate_block,
    resolve_v2,
    would_consult,
)
from src.resolve.llm import Reply, StubBackend, parse_json_object  # noqa: E402
from src.resolve.match import ALIASES  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "golden_set_v1.json"
CACHE = ROOT / "docs" / "_adjudication_results.json"
METRICS = ROOT / "docs" / "_adjudication_metrics.json"


def reply(company, share_class="UNKNOWN", confidence=0.9, reason="because"):
    return json.dumps({"company": company, "share_class": share_class,
                       "confidence": confidence, "reason": reason})


# --------------------------------------------------------------------------
# The prompt
# --------------------------------------------------------------------------

def test_the_prompt_never_contains_the_answer():
    """The single most important test in this file.

    The golden set carries the label on the same record as the inputs, so it
    would be very easy to leak it into the prompt and measure nothing at all.
    Every label string is checked against the rendered prompt for every entry.
    """
    entries = json.loads(FIXTURE.read_text(encoding="utf-8"))["entries"]
    for entry in entries:
        system, user = build_prompt(
            entry["issuer_name"], entry["issuer_title"], entry.get("filer_families")
        )
        prompt = system + user
        # The candidate list legitimately names every company, so a label can
        # only leak via a field the model should not see.
        for field in ("label_reason", "evidence_class", "price_basis"):
            value = str(entry.get(field, ""))
            if len(value) > 12:
                assert value not in prompt, f"{entry['id']} leaked {field}"


def test_the_prompt_carries_what_the_plan_specifies():
    """plan.md week 5: issuer name, title, filer, candidates."""
    system, user = build_prompt("XAI CORP", "xAI Corp SER C PC PP", "Fidelity")
    assert "XAI CORP" in user
    assert "xAI Corp SER C PC PP" in user
    assert "Fidelity" in user
    for company in ALIASES:
        assert company in user, f"{company} missing from the candidate list"


def test_a_blank_field_is_labelled_not_dropped():
    """A missing title must read as absent, not as an empty string the model
    silently treats as meaningful."""
    _, user = build_prompt("SOMETHING LLC", None, None)
    assert "(blank)" in user
    assert "(not recorded)" in user


def test_the_schema_closes_the_company_list():
    allowed = set(RESPONSE_SCHEMA["properties"]["company"]["enum"])
    assert allowed == set(CANONICAL) | {"NOT_IN_UNIVERSE", "UNKNOWN"}
    assert set(RESPONSE_SCHEMA["required"]) == {
        "company", "share_class", "confidence", "reason"
    }


def test_candidate_block_lists_every_company_once():
    block = candidate_block()
    assert len(block.strip().split("\n")) == len(ALIASES)


# --------------------------------------------------------------------------
# Parsing and the refusal path
# --------------------------------------------------------------------------

def test_json_is_recovered_from_a_fenced_reply():
    """Models wrap JSON in prose and fences even when told not to. Losing the
    row over that would throw away the other 321."""
    text = 'Sure!\n```json\n{"company": "Groq, Inc.", "share_class": "COM",' \
           ' "confidence": 0.7, "reason": "x"}\n```'
    assert parse_json_object(text)["company"] == "Groq, Inc."


def test_an_empty_reply_raises_rather_than_returning_a_default():
    with pytest.raises(ValueError):
        parse_json_object("")


def test_an_off_list_company_is_an_error_not_an_answer():
    """A name outside the closed list is a schema violation. Accepting it would
    let the model invent a company that no downstream table has a row for."""
    backend = StubBackend(default=reply("Acme Rockets Inc."))
    verdict = adjudicate(backend, "SOMETHING")
    assert not verdict.ok
    assert "off-list" in verdict.error
    assert verdict.company is None


def test_a_backend_failure_is_typed_not_raised():
    class Broken:
        def chat(self, system, user):
            raise ConnectionError("server went away")

    verdict = adjudicate(Broken(), "DATABRICKS INC")
    assert not verdict.ok
    assert "backend" in verdict.error
    assert verdict.company is None


def test_unparseable_output_is_recorded_with_the_raw_text():
    """The raw reply has to survive, or a parse failure cannot be diagnosed."""
    backend = StubBackend(default="I think it is probably Databricks?")
    verdict = adjudicate(backend, "DATABRICKS INC")
    assert not verdict.ok
    assert "unparseable" in verdict.error
    assert "probably Databricks" in verdict.raw


def test_confidence_is_clamped():
    backend = StubBackend(default=reply("Groq, Inc.", confidence=7.5))
    assert adjudicate(backend, "GROQ").confidence == 1.0
    backend = StubBackend(default=reply("Groq, Inc.", confidence="banana"))
    assert adjudicate(backend, "GROQ").confidence == 0.0


def test_not_in_universe_and_unknown_are_kept_distinct():
    """'This is a different company' and 'the filing does not say' are not the
    same claim, and collapsing them would destroy the opaque-SPV count that
    every run summary reports."""
    assert adjudicate(StubBackend(default=reply("NOT_IN_UNIVERSE")), "X").company is None
    assert adjudicate(StubBackend(default=reply("UNKNOWN")), "X").company == "UNKNOWN"


# --------------------------------------------------------------------------
# The policy -- what the model is allowed to overrule
# --------------------------------------------------------------------------

def test_an_lei_match_is_never_put_to_the_model():
    """A registered identifier is identity. A model that can overrule it is not
    adding judgment, it is adding noise to the one part that was never in doubt."""
    backend = StubBackend(default=reply("Groq, Inc."))
    result = resolve_v2("SOME WRAPPER LLC", None, "984500B6DEB8CEBC4Z70",
                        backend=backend, policy=POLICY_BAND)
    assert result.company == "Anthropic PBC"
    assert result.method == "lei"
    assert result.consulted_llm is False
    assert backend.calls == [], "the model was called on an LEI match"


def test_an_exact_alias_is_never_put_to_the_model():
    backend = StubBackend(default=reply("Groq, Inc."))
    result = resolve_v2("DATABRICKS INC", None, backend=backend, policy=POLICY_BAND)
    assert result.company == "Databricks, Inc."
    assert result.consulted_llm is False
    assert backend.calls == []


def test_the_auto_accept_band_is_not_put_to_the_model():
    """0.90 and above was measured clean in Week 4. Re-litigating it can only
    lose ground."""
    backend = StubBackend(default=reply("Groq, Inc."))
    result = resolve_v2("Anthropics Technology Ltd.", "Series G",
                        backend=backend, policy=POLICY_BAND)
    assert result.deterministic_score >= AUTO_ACCEPT
    assert result.company == "Anthropic PBC"
    assert result.consulted_llm is False


def test_the_review_band_is_put_to_the_model():
    """0.80-0.90 is exactly where Week 4 found a tie no threshold could break."""
    backend = StubBackend(default=reply("NOT_IN_UNIVERSE"))
    result = resolve_v2("OPEN BAY AUTOS AI INC.", None, backend=backend, policy=POLICY_BAND)
    assert result.deterministic_company == "OpenAI Group PBC"
    assert result.deterministic_score == 0.80
    assert result.consulted_llm is True
    assert result.company is None, "the model should have been allowed to reject it"


def test_an_unresolved_name_is_put_to_the_model():
    backend = StubBackend(default=reply("Groq, Inc.", confidence=0.55))
    result = resolve_v2("GROUNDWORKS, LLC", None, backend=backend, policy=POLICY_BAND)
    assert result.consulted_llm is True
    assert result.company == "Groq, Inc."
    assert result.method == "llm"


def test_a_model_failure_falls_back_to_the_deterministic_answer():
    """No model must never mean no answer. The floor is still the floor."""
    class Broken:
        def chat(self, system, user):
            raise ConnectionError("down")

    result = resolve_v2("OPEN BAY AUTOS AI INC.", None, backend=Broken(),
                        policy=POLICY_BAND)
    assert result.company == "OpenAI Group PBC"
    assert result.method == "fuzzy"


def test_no_backend_is_a_no_op_not_a_crash():
    result = resolve_v2("OPEN BAY AUTOS AI INC.", None, backend=None, policy=POLICY_BAND)
    assert result.company == "OpenAI Group PBC"
    assert result.consulted_llm is False


def test_llm_only_policy_ignores_the_deterministic_matcher():
    backend = StubBackend(default=reply("Perplexity AI, Inc."))
    result = resolve_v2("DATABRICKS INC", None, backend=backend, policy=POLICY_LLM_ONLY)
    assert result.company == "Perplexity AI, Inc."
    assert result.deterministic_company == "Databricks, Inc."
    assert len(backend.calls) == 1


def test_all_policy_overrules_fuzzy_but_still_not_an_exact_match():
    backend = StubBackend(default=reply("Groq, Inc."))
    overruled = resolve_v2("Anthropics Technology Ltd.", "Series G",
                           backend=backend, policy=POLICY_ALL)
    assert overruled.company == "Groq, Inc.", "POLICY_ALL should reach a 0.947 fuzzy match"
    protected = resolve_v2("DATABRICKS INC", None, backend=backend, policy=POLICY_ALL)
    assert protected.company == "Databricks, Inc.", "an exact alias is never overruled"


def test_would_consult_agrees_with_what_resolve_v2_actually_does():
    """The cost estimate and the behaviour have to be the same function, or the
    throughput budget is describing a system that does not exist."""
    cases = ["DATABRICKS INC", "OPEN BAY AUTOS AI INC.", "GROUNDWORKS, LLC",
             "Anthropics Technology Ltd.", "FSOIFD TC HOLDINGS LLC",
             "U First Capital Fund III LLC (SpaceX)"]
    for name in cases:
        backend = StubBackend(default=reply("NOT_IN_UNIVERSE"))
        resolve_v2(name, None, backend=backend, policy=POLICY_BAND)
        predicted = would_consult(name, None, policy=POLICY_BAND)
        assert bool(backend.calls) == predicted, name


def test_a_cached_adjudication_is_used_instead_of_a_backend():
    """Metrics are recomputed from stored replies, so this path must work with
    no backend at all."""
    cached = Adjudication(company="Cerebras Systems Inc.", share_class="COM",
                          confidence=0.8, reason="cached")
    result = resolve_v2("GROUNDWORKS, LLC", None, backend=None,
                        policy=POLICY_BAND, adjudication=cached)
    assert result.company == "Cerebras Systems Inc."
    assert result.method == "llm"


def test_the_model_may_answer_unknown_and_that_is_not_a_company():
    backend = StubBackend(default=reply("UNKNOWN"))
    result = resolve_v2("FSOIFD TC HOLDINGS LLC", None, backend=backend,
                        policy=POLICY_BAND)
    assert result.company is None
    assert "does not disclose" in result.note


# --------------------------------------------------------------------------
# The measured result
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def metrics():
    if not METRICS.exists():
        pytest.skip("no adjudication metrics -- run scripts.run_adjudication --run")
    return json.loads(METRICS.read_text(encoding="utf-8"))


def test_the_run_records_which_weights_answered(metrics):
    """A precision figure with no model identity beside it is not reproducible."""
    run = metrics["run"]
    for field in ("model", "digest", "parameter_size", "quantization", "at", "machine"):
        assert run.get(field), f"run record has no {field}"
    assert run["temperature"] == 0, "a non-zero temperature makes the metric unrepeatable"


def test_the_llm_costs_precision_when_it_is_allowed_to_propose(metrics):
    """The Week 5 finding, pinned.

    plan.md: "Measure lift over baseline on the golden set. If there is no lift,
    keep the deterministic matcher and say so." There is no lift. Any policy
    that lets an 8B model *propose* a company loses precision, because on this
    corpus it promotes resemblances -- HYPERSCALE DATA to Scale AI, a Fidelity
    internal security code to X.AI.

    If a future model or prompt makes this test fail, that is good news and the
    recommendation in docs/entity_resolution.md section 9 has to be rewritten
    rather than the test relaxed.
    """
    baseline = metrics["subsets"]["all"]["B_matcher_v1"]["macro"]["overall"]
    band = metrics["subsets"]["all"]["C_v2_band"]["macro"]["overall"]
    llm_only = metrics["subsets"]["all"]["E_llm_only"]["macro"]["overall"]

    assert baseline["precision"] >= 0.9959 - 1e-4
    assert baseline["recall"] >= 1.0 - 1e-4
    assert band["precision"] < baseline["precision"], "the finding has reversed"
    assert band["f1"] < baseline["f1"]
    assert llm_only["f1"] < baseline["f1"]
    assert metrics["lift_vs_baseline_all_macro"]["C_v2_band"]["f1"] < 0


def test_the_damage_is_all_promotion_never_demotion(metrics):
    """Every break is None -> company. That asymmetry is the whole argument for
    the veto policy, so it is asserted rather than remembered."""
    changes = metrics["band_policy_changes"]
    assert changes["broke"], "expected the measured breaks to still be here"
    for row in changes["broke"]:
        assert row["before"] is None, f"{row['issuer_name']} broke by demotion, not promotion"
        assert row["after"] is not None
    for row in changes["fixed"]:
        assert row["after"] is None, "the only fix was a withdrawal"


def test_the_veto_policy_is_the_only_one_that_does_not_lose_ground(metrics):
    veto = metrics["subsets"]["all"]["F_v2_veto"]["macro"]["overall"]
    baseline = metrics["subsets"]["all"]["B_matcher_v1"]["macro"]["overall"]
    assert veto["precision"] >= baseline["precision"]
    assert veto["recall"] >= baseline["recall"]
    assert metrics["lift_vs_baseline_all_macro"]["F_v2_veto"]["f1"] >= 0


def test_the_veto_policy_rests_on_four_rows_and_says_so(metrics):
    """The honest size of the win.

    F_v2_veto scores 1.0000/1.0000, which looks like a solved problem and is
    not: the policy is consulted on four issuer strings in the entire golden
    set, vetoes one of them, and is right about the other three by declining.
    A perfect score on n=4 is a description of four rows, not evidence of a
    robust improvement, and section 9 says so."""
    assert metrics["veto_policy_consulted"] <= 8, (
        "the veto policy's evidence base grew; re-read whether the claim in "
        "section 9 is still proportionate"
    )


def test_model_confidence_cannot_be_used_to_triage(metrics):
    """Week 6 will want to sort a review queue by confidence. It cannot.

    The model returned 1.0 on almost everything, including most of the answers
    that were wrong."""
    cache = json.loads(CACHE.read_text(encoding="utf-8"))["results"]
    broke = {row["id"] for row in metrics["band_policy_changes"]["broke"]}
    wrong = [r["confidence"] for r in cache.values() if r["id"] in broke]
    assert wrong, "no measured breaks to check"
    assert max(wrong) >= 0.95, "a wrong answer was returned at high confidence"
    assert sum(1 for c in wrong if c >= 0.95) >= len(wrong) // 2


def test_the_confidence_prose_is_read_from_the_artifact(metrics):
    """The counts quoted in section 9.4 must be the ones the cache produces.

    This test exists because they were not. The section first claimed 1.000 on
    "308 of 322" answers with "nine of the fourteen" wrong ones above 0.95;
    recomputing from the cache gives 315, and 12 of 15 (11 of the 14 band-policy
    breaks). Both prose numbers were hand-typed, which is the P3 violation --
    the error was only caught because a figure generated from the cache
    disagreed with the text. Recompute here rather than trust the block.
    """
    conf = metrics["confidence"]
    cache = json.loads(CACHE.read_text(encoding="utf-8"))["results"]
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))["entries"]
    by_id = {r["id"]: r for r in cache.values()}

    assert conf["answers"] == len(by_id)
    assert conf["at_full_confidence"] == sum(
        1 for r in by_id.values() if r["confidence"] >= 1.0
    )

    disagree = []
    for entry in fixture:
        record = by_id.get(entry["id"])
        if record is None or entry["company"] == "UNKNOWN":
            continue
        truth = None if entry["company"] == "NOT_IN_UNIVERSE" else entry["company"]
        if (record["company"] or None) != truth:
            disagree.append(record["confidence"])
    assert conf["disagreements"] == len(disagree)
    assert conf["disagreements_at_95_plus"] == sum(1 for c in disagree if c >= 0.95)

    # The two denominators are different claims. A report that swaps them
    # understates the damage of the policy it is recommending against.
    assert conf["band_breaks"] == len(metrics["band_policy_changes"]["broke"])
    assert conf["disagreements"] >= conf["band_breaks"]

    # The finding itself: confidence carries almost no information.
    assert len(conf["distribution"]) <= 4, "confidence took more values than reported"
    assert conf["at_full_confidence"] / conf["answers"] > 0.9


def test_throughput_is_recorded(metrics):
    """plan.md week 5: 'Record throughput so the cost of a full re-resolution
    is known.'"""
    tp = metrics["throughput"]
    assert tp["mean_seconds_per_call"] > 0
    assert tp["tokens_per_second"] > 0
    assert tp["calls_measured"] >= 300
    assert tp["errors"] == 0, f"{tp['errors']} calls failed"
    assert tp["seconds_for_full_golden_set_band_policy"] > 0


# --------------------------------------------------------------------------
# The veto policy, under the stub
# --------------------------------------------------------------------------

def test_veto_policy_never_promotes_an_unresolved_name():
    """The failure mode that cost 14 holdings. Whatever the model says, a name
    the deterministic matcher could not resolve stays unresolved."""
    backend = StubBackend(default=reply("Scale AI, Inc.", confidence=1.0))
    result = resolve_v2("HYPERSCALE DATA INC", None, backend=backend, policy=POLICY_VETO)
    assert result.company is None
    assert result.consulted_llm is False
    assert backend.calls == [], "no call is worth making; there is nothing to veto"


def test_veto_policy_withdraws_a_weak_wrong_claim():
    backend = StubBackend(default=reply("NOT_IN_UNIVERSE"))
    result = resolve_v2("OPEN BAY AUTOS AI INC.", None, backend=backend, policy=POLICY_VETO)
    assert result.deterministic_company == "OpenAI Group PBC"
    assert result.company is None
    assert result.method == "llm_veto"


def test_veto_policy_keeps_the_claim_when_the_model_disagrees_differently():
    """If the model names a *different* company, that is a proposal, not a veto,
    and proposals are what it is bad at. The deterministic answer stands."""
    backend = StubBackend(default=reply("Groq, Inc."))
    # The real blended-SPV string, which scores 0.80 because the two class
    # percentages leave sponsor tokens unexplained. A shortened version scores
    # 0.90 and never reaches the model at all.
    result = resolve_v2(
        "MWAM VC SPACEX-II, LLC (ECONOMIC EXPOSURE TO SPACE EXPLORATION "
        "TECHNOLOGIES CORP., 55% CLASS A COMMON STOCK AND 45% CLASS C COMMON STOCK)",
        None, backend=backend, policy=POLICY_VETO,
    )
    assert result.deterministic_score == 0.80
    assert result.company == "Space Exploration Technologies Corp."
    assert result.consulted_llm is True
    assert "did not object" in result.note


def test_veto_policy_does_not_touch_the_auto_accept_band():
    backend = StubBackend(default=reply("NOT_IN_UNIVERSE"))
    result = resolve_v2("Anthropics Technology Ltd.", "Series G",
                        backend=backend, policy=POLICY_VETO)
    assert result.company == "Anthropic PBC"
    assert backend.calls == []
