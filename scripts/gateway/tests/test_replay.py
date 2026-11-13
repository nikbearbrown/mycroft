import pytest

from gateway.bench.replay import ACTION_TO_TASK, replay_one, summarise
from gateway.policy import Policy
from gateway.prices import PriceTable
from gateway.tiers import TierConfig


@pytest.fixture
def config():
    tiers = TierConfig.load()
    return {"policy": Policy.load(tiers), "tiers": tiers, "prices": PriceTable.load()}


def record(**overrides):
    return {"source": "logs/r/runs/s/llm-handoff/FXA.json",
            "recipe": "contradiction-detection-agent",
            "action": "llm_review_of_flags",
            "prompt_chars": 1334,
            "model_named": "llama-3.3-70b-versatile",
            "max_tokens": 2000, **overrides}


# -- mapping a recipe's words onto a policy task type --------------------

def test_a_known_action_maps_to_its_task_type(config):
    row = replay_one(record(), **config)
    assert row["task_type"] == ACTION_TO_TASK["llm_review_of_flags"]
    assert row["tier"]


def test_an_unknown_action_is_reported_not_guessed(config):
    """Guessing here would route real work by coincidence."""
    row = replay_one(record(action="summarise_everything"), **config)

    assert row["problems"] == ["unmapped_action"]
    assert row["tier"] is None


def test_an_empty_payload_is_not_routed(config):
    """5 of the 16 real handoffs have no payload at all."""
    row = replay_one(record(prompt_chars=0), **config)

    assert row["problems"] == ["empty_payload"]
    assert row["cost_upper_bound_usd"] is None


# -- what the gateway would do -------------------------------------------

def test_a_short_request_routes_to_cheap_under_policy_0_3_0(config):
    """All 11 complete requests are ~1,300 chars, far under the 4,000 threshold."""
    row = replay_one(record(), **config)

    assert row["tier"] == "cheap"
    assert row["max_tokens_served"] == config["policy"].max_tokens("cheap")


def test_a_long_request_is_promoted_by_length(config):
    row = replay_one(record(prompt_chars=5000), **config)
    assert row["tier"] == "mid"


def test_the_estimate_is_below_the_upper_bound(config):
    """One token per character is never an underestimate; four is nearer the truth."""
    row = replay_one(record(), **config)

    assert 0 < row["cost_estimate_usd"] < row["cost_upper_bound_usd"]


# -- what it could not serve as asked ------------------------------------

def test_a_budget_smaller_than_the_one_asked_for_is_flagged(config):
    """2,000 asked against a 512 budget -- the answer would be truncated."""
    row = replay_one(record(), **config)

    cut = [p for p in row["problems"] if p.startswith("budget_cut")]
    assert cut and "asked 2000" in cut[0]


def test_a_budget_within_the_tier_is_not_flagged(config):
    row = replay_one(record(max_tokens=256), **config)
    assert not any(p.startswith("budget_cut") for p in row["problems"])


def test_a_model_with_no_published_rate_is_flagged(config):
    """The gateway cannot price the model Mycroft's recipes actually name."""
    assert "named_model_unpriced" in replay_one(record(), **config)["problems"]


def test_a_priced_model_is_not_flagged(config):
    row = replay_one(record(model_named="openai/gpt-oss-20b"), **config)
    assert "named_model_unpriced" not in row["problems"]


# -- the summary ----------------------------------------------------------

def test_the_summary_counts_tiers_costs_and_problems(config):
    rows = [replay_one(record(), **config),
            replay_one(record(prompt_chars=5000), **config),
            replay_one(record(prompt_chars=0), **config)]

    stats = summarise(rows)

    assert stats["requests"] == 3
    assert stats["routable"] == 2
    assert stats["by_tier"] == {"cheap": 1, "mid": 1}
    assert stats["problems"]["empty_payload"] == 1
    assert stats["cost_estimate_usd"] < stats["cost_upper_bound_usd"]