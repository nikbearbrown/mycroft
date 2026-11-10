import pytest

from gateway.policy import Policy, UnknownTaskType
from gateway.router import InputTooLarge, PinnedTask, route
from gateway.tiers import TierConfig


@pytest.fixture
def tiers():
    return TierConfig.load()


@pytest.fixture
def policy(tiers):
    return Policy.load(tiers)


def make(limits: dict[str, int]):
    """A tier config with chosen context limits, and a one-type policy on it."""
    tiers = TierConfig({"version": "t", "tiers": {
        name: {"provider": "groq", "model": name, "status": "evidenced",
               "evidence": "test", "context_limit": lim, "capabilities": ["text"]}
        for name, lim in limits.items()}})
    policy = Policy({
        "version": "p",
        "tier_order": ["cheap", "mid", "strong"],
        "max_tokens_by_tier": {"cheap": 512, "mid": 512, "strong": 1024},
        "task_types": {"sentiment_classification": {
            "description": "d", "output": "label",
            "labels": ["positive", "negative", "neutral"],
            "validator": "label_in_set", "quality_check": "deterministic",
            "start_tier": "cheap", "escalate_to": "mid",
            "promote_above_chars": 2000, "evidence": ["x"]}}}, tiers)
    return policy, tiers


def test_short_sentiment_starts_cheap_and_escalates_to_mid(policy, tiers):
    d = route(task_type="sentiment_classification", text="Nvidia shares drop",
              policy=policy, tiers=tiers)
    assert (d.tier, d.escalate_to, d.max_tokens) == ("cheap", "mid", 512)
    assert d.routing_reason == "policy"
    assert d.policy_version == policy.version


def test_the_promotion_threshold_is_strictly_greater_than(policy, tiers):
    """Exactly 2,000 chars stays cheap -- a labeler needs the exact rule."""
    d = route(task_type="sentiment_classification", text="x" * 2000,
              policy=policy, tiers=tiers)
    assert d.tier == "cheap"


def test_long_input_is_promoted_one_tier(policy, tiers):
    d = route(task_type="sentiment_classification", text="x" * 2001,
              policy=policy, tiers=tiers)
    assert (d.tier, d.escalate_to) == ("mid", "strong")
    assert "promoted to mid" in d.explanation


def test_every_task_type_starts_cheap_since_policy_0_3_0(policy, tiers):
    """The Sprint 8 decision, pinned.

    Policy 0.2.0 started extraction, contradiction detection, summarization and
    rag_answer on mid. Replayed against the Sprint 7 baseline, always-cheap was
    the only policy to clear the August thresholds -- 31% cheaper and 31%
    faster at unchanged correctness (FINDINGS section 12). If this test fails,
    someone has reintroduced a dearer default without a new measurement.
    """
    for task_type in policy.task_types:
        d = route(task_type=task_type, text="short input", policy=policy, tiers=tiers)
        assert (d.tier, d.escalate_to) == ("cheap", "mid"), task_type


def test_strong_is_no_longer_a_default_escalation_target(policy, tiers):
    """Strong stays in tier_order for the context walk-up, not for quality.

    It costs 3.1x cheap, leads on no task type, and is less accurate than mid
    on the two that fail (FINDINGS section 11).
    """
    for task_type in policy.task_types:
        assert policy.rule_for(task_type)["escalate_to"] != "strong", task_type


def test_promoted_to_the_top_has_nowhere_to_escalate():
    """Reaching strong now happens only via the context-window walk-up.

    Length promotion moves one tier, and everything starts on cheap, so a long
    input reaches mid and stops. An input that fits neither cheap nor mid still
    walks up to strong, and there it has nowhere left to go.
    """
    policy, tiers = make({"cheap": 1000, "mid": 1000, "strong": 131072})
    # 300 chars + 256 margin + 512 budget = 1,068 > 1,000 for cheap and mid.
    d = route(task_type="sentiment_classification", text="x" * 300,
              policy=policy, tiers=tiers)

    assert (d.tier, d.escalate_to) == ("strong", None)
    assert d.max_tokens == policy.max_tokens("strong")
    assert d.max_tokens > policy.max_tokens("cheap"), "strong gets a larger budget"
    assert "context window" in d.explanation


def test_unknown_task_type_is_refused(policy, tiers):
    with pytest.raises(UnknownTaskType):
        route(task_type="something_nobody_defined", text="x",
              policy=policy, tiers=tiers)


def test_a_pinned_task_is_never_routed(policy, tiers):
    with pytest.raises(PinnedTask):
        route(task_type="embedding", text="x", policy=policy, tiers=tiers)


def test_input_too_big_for_cheap_moves_up():
    policy, tiers = make({"cheap": 1000, "mid": 131072, "strong": 131072})
    # 300 chars + 256 margin + 512 budget = 1,068 > cheap's 1,000
    d = route(task_type="sentiment_classification", text="x" * 300,
              policy=policy, tiers=tiers)
    assert (d.tier, d.escalate_to) == ("mid", "strong")
    assert "context window" in d.explanation


def test_input_that_fits_no_tier_is_refused():
    policy, tiers = make({"cheap": 1000, "mid": 1000, "strong": 1000})
    with pytest.raises(InputTooLarge):
        route(task_type="sentiment_classification", text="x" * 1000,
              policy=policy, tiers=tiers)


def test_routing_is_deterministic(policy, tiers):
    args = dict(task_type="contradiction_detection", text="A said X. B said not X.",
                policy=policy, tiers=tiers)
    assert route(**args) == route(**args)


def test_every_task_type_routes_and_explains_itself(policy, tiers):
    for task_type in policy.task_types:
        d = route(task_type=task_type, text="short input", policy=policy, tiers=tiers)
        assert d.tier in policy.tier_order
        assert d.tier in d.explanation