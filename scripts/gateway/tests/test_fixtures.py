import json

import pytest

from gateway.bench import fixtures as fx
from gateway.policy import Policy
from gateway.tiers import TierConfig


@pytest.fixture
def policy():
    return Policy.load(TierConfig.load())


def write(tmp_path, name, rows):
    folder = tmp_path / "fx"
    folder.mkdir(exist_ok=True)
    (folder / name).write_text("\n".join(json.dumps(r) for r in rows) + "\n",
                               encoding="utf-8")
    return folder


def row(**overrides):
    base = {"id": "s-1", "task_type": "sentiment_classification",
            "input": "Company: A. Headline: A beats estimates.",
            "expected": {"label": "positive"}, "difficulty": "easy",
            "provenance": "synthetic", "labeled_by": "UNREVIEWED",
            "expected_tier": None, "labeled_on": None}
    base.update(overrides)
    return base


def reviewed(**overrides):
    return row(labeled_by="Tester", expected_tier="cheap",
               labeled_on="2026-09-10", **overrides)


def test_the_seed_set_conforms(policy):
    fx.validate(fx.load(), policy)


def test_every_task_type_has_easy_and_hard_fixtures(policy):
    table = fx.coverage(fx.validate(fx.load(), policy), policy)
    for task_type, counts in table.items():
        assert counts["easy"] > 0 and counts["hard"] > 0, task_type


def test_duplicate_id_is_rejected(tmp_path, policy):
    folder = write(tmp_path, "sentiment_classification.jsonl", [row(), row()])
    with pytest.raises(fx.FixtureError, match="duplicate"):
        fx.validate(fx.load(folder), policy)


def test_label_outside_the_set_is_rejected(tmp_path, policy):
    folder = write(tmp_path, "sentiment_classification.jsonl",
                   [row(expected={"label": "bullish"})])
    with pytest.raises(fx.FixtureError, match="not one of"):
        fx.validate(fx.load(folder), policy)


def test_fixture_in_the_wrong_file_is_rejected(tmp_path, policy):
    folder = write(tmp_path, "topic_classification.jsonl", [row()])
    with pytest.raises(fx.FixtureError, match="belongs in"):
        fx.validate(fx.load(folder), policy)


def test_unreviewed_fixture_cannot_carry_a_tier(tmp_path, policy):
    """A drafted tier would anchor the human's judgment."""
    folder = write(tmp_path, "sentiment_classification.jsonl",
                   [row(expected_tier="cheap")])
    with pytest.raises(fx.FixtureError, match="UNREVIEWED"):
        fx.validate(fx.load(folder), policy)


def test_reviewed_fixture_needs_a_tier_and_a_date(tmp_path, policy):
    folder = write(tmp_path, "sentiment_classification.jsonl",
                   [row(labeled_by="Tester", expected_tier=None)])
    with pytest.raises(fx.FixtureError, match="expected_tier"):
        fx.validate(fx.load(folder), policy)

    folder = write(tmp_path, "sentiment_classification.jsonl",
                   [row(labeled_by="Tester", expected_tier="cheap", labeled_on="soon")])
    with pytest.raises(fx.FixtureError, match="ISO date"):
        fx.validate(fx.load(folder), policy)


def test_cite_outside_the_context_is_rejected(tmp_path, policy):
    bad = row(id="r-1", task_type="rag_answer", input="Q?",
              context=["a", "b"], expected={"cite": 5})
    folder = write(tmp_path, "rag_answer.jsonl", [bad])
    with pytest.raises(fx.FixtureError, match="cite"):
        fx.validate(fx.load(folder), policy)


def test_freeze_refuses_unreviewed_labels(tmp_path, policy):
    folder = write(tmp_path, "sentiment_classification.jsonl", [row()])
    fixtures = fx.validate(fx.load(folder), policy)
    with pytest.raises(fx.NotReviewed):
        fx.freeze(fixtures, policy, folder)


def test_freeze_locks_a_reviewed_set_and_detects_changes(tmp_path, policy):
    folder = write(tmp_path, "sentiment_classification.jsonl", [reviewed()])
    fixtures = fx.validate(fx.load(folder), policy)
    manifest = fx.freeze(fixtures, policy, folder)

    assert manifest["fixture_count"] == 1
    assert fx.check_manifest(manifest, folder) == []

    write(tmp_path, "sentiment_classification.jsonl", [reviewed(input="edited")])
    assert fx.check_manifest(manifest, folder) == [
        "sentiment_classification.jsonl: changed since it was frozen"]


def test_the_shipped_manifest_matches_the_fixtures():
    """Once frozen, any edit to a fixture file breaks this test."""
    if not fx.MANIFEST_PATH.exists():
        pytest.skip("fixture set not frozen yet")
    manifest = json.loads(fx.MANIFEST_PATH.read_text(encoding="utf-8"))
    assert fx.check_manifest(manifest) == []