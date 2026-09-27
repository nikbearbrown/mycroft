import copy
from pathlib import Path

import pytest

from gateway.policy import Policy, PolicyError, UnknownTaskType
from gateway.tiers import TierConfig

REPO_ROOT = Path(__file__).resolve().parents[3]

SIX_TYPES = {
    "sentiment_classification", "topic_classification", "structured_extraction",
    "contradiction_detection", "summarization", "rag_answer",
}


@pytest.fixture
def tiers():
    return TierConfig.load()


@pytest.fixture
def shipped(tiers):
    return Policy.load(tiers)


def minimal() -> dict:
    return {
        "version": "0.1.0",
        "tier_order": ["cheap", "mid", "strong"],
        "max_tokens_by_tier": {"cheap": 512, "mid": 512, "strong": 1024},
        "task_types": {
            "sentiment_classification": {
                "description": "d", "output": "label",
                "labels": ["positive", "negative", "neutral"],
                "validator": "label_in_set", "quality_check": "deterministic",
                "start_tier": "cheap", "escalate_to": "mid",
                "evidence": ["x"],
            },
        },
    }


def test_the_shipped_policy_locks_six_task_types(shipped):
    assert set(shipped.task_types) == SIX_TYPES


def test_every_evidence_path_exists_in_the_repo(shipped):
    """A task type is only 'something Mycroft does' if the file proving it exists."""
    missing = []
    for name in shipped.task_types:
        for path in shipped.rule_for(name)["evidence"]:
            if not (REPO_ROOT / path).exists():
                missing.append(f"{name}: {path}")
    assert missing == []


def test_strong_budget_clears_the_observed_truncation_risk(shipped):
    """Strong used 245 of 256 on a one-word answer (RUN_LOG 2026-09-10)."""
    assert shipped.max_tokens("strong") > 256


def test_unknown_task_type_is_refused_not_defaulted(shipped):
    with pytest.raises(UnknownTaskType):
        shipped.rule_for("something_nobody_defined")


def test_next_tier_up(shipped):
    assert shipped.next_tier_up("cheap") == "mid"
    assert shipped.next_tier_up("strong") is None


def test_label_task_without_labels_is_rejected(tiers):
    data = minimal()
    del data["task_types"]["sentiment_classification"]["labels"]
    with pytest.raises(PolicyError, match="labels"):
        Policy(data, tiers)


def test_escalating_down_or_sideways_is_rejected(tiers):
    for target in ("cheap",):
        data = minimal()
        data["task_types"]["sentiment_classification"]["escalate_to"] = target
        with pytest.raises(PolicyError, match="must go up"):
            Policy(data, tiers)


def test_a_tier_not_in_tiers_json_is_rejected(tiers):
    data = minimal()
    data["task_types"]["sentiment_classification"]["escalate_to"] = "premium"
    with pytest.raises(PolicyError, match="not in tier_order"):
        Policy(data, tiers)


def test_unknown_validator_is_rejected(tiers):
    data = minimal()
    data["task_types"]["sentiment_classification"]["validator"] = "vibes"
    with pytest.raises(PolicyError, match="validator"):
        Policy(data, tiers)


def test_tier_order_must_cover_every_configured_tier(tiers):
    data = minimal()
    data["tier_order"] = ["cheap", "strong"]
    with pytest.raises(PolicyError, match="every configured tier"):
        Policy(data, tiers)


def test_every_tier_needs_a_token_budget(tiers):
    data = copy.deepcopy(minimal())
    del data["max_tokens_by_tier"]["strong"]
    with pytest.raises(PolicyError, match="strong"):
        Policy(data, tiers)