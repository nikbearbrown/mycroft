import json

import pytest

from gateway.bench import fixtures as fx
from gateway.bench.label import apply_label, save
from gateway.policy import Policy
from gateway.tiers import TierConfig

ROWS = [
    {"id": "s-1", "task_type": "sentiment_classification", "input": "A beats estimates.",
     "expected": {"label": "positive"}, "difficulty": "easy", "provenance": "synthetic",
     "labeled_by": "UNREVIEWED", "expected_tier": None, "labeled_on": None},
    {"id": "s-2", "task_type": "sentiment_classification", "input": "A recalls units.",
     "expected": {"label": "negative"}, "difficulty": "easy", "provenance": "synthetic",
     "labeled_by": "UNREVIEWED", "expected_tier": None, "labeled_on": None},
]


@pytest.fixture
def policy():
    return Policy.load(TierConfig.load())


def seed(tmp_path):
    folder = tmp_path / "fx"
    folder.mkdir()
    (folder / "sentiment_classification.jsonl").write_text(
        "\n".join(json.dumps(r) for r in ROWS) + "\n", encoding="utf-8")
    return folder


def test_save_round_trips_without_bookkeeping_fields(tmp_path):
    folder = seed(tmp_path)
    save(fx.load(folder), folder)

    text = (folder / "sentiment_classification.jsonl").read_text(encoding="utf-8")
    assert "_file" not in text
    assert [f["id"] for f in fx.load(folder)] == ["s-1", "s-2"], "order preserved"


def test_a_labeled_fixture_validates_and_the_rest_are_untouched(tmp_path, policy):
    folder = seed(tmp_path)
    fixtures = fx.load(folder)
    apply_label(fixtures[0], policy=policy, tier="cheap", by="Tester", on="2026-09-10")
    save(fixtures, folder)

    reloaded = fx.validate(fx.load(folder), policy)
    assert (reloaded[0]["expected_tier"], reloaded[0]["labeled_by"]) == ("cheap", "Tester")
    assert reloaded[1]["labeled_by"] == fx.UNREVIEWED


def test_a_corrected_answer_is_kept(tmp_path, policy):
    fixtures = fx.load(seed(tmp_path))
    apply_label(fixtures[0], policy=policy, tier="mid", by="Tester",
                on="2026-09-10", expected={"label": "neutral"})
    assert fixtures[0]["expected"] == {"label": "neutral"}


def test_a_bad_tier_or_an_anonymous_label_is_refused(policy):
    fixture = dict(ROWS[0])
    with pytest.raises(ValueError, match="tier"):
        apply_label(fixture, policy=policy, tier="premium", by="Tester", on="2026-09-10")
    with pytest.raises(ValueError, match="your name"):
        apply_label(fixture, policy=policy, tier="cheap", by="UNREVIEWED", on="2026-09-10")