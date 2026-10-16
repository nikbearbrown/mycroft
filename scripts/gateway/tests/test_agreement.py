import json

import pytest

from gateway.bench.agreement import VERDICTS, analyse, kappa
from gateway.bench.score import (
    load_scores, resolve_pick, save_scores, scores_path, shown_order,
)


def row(pair_id, result, task_type="summarization", fixture_id=None):
    """One judged pair, as judge_run.py writes it."""
    return {"pair_id": pair_id, "id": fixture_id or pair_id.split("#")[0],
            "task_type": task_type, "result": result,
            "a_label": "cheap", "b_label": "mid"}


def score(pair_id, pick, task_type="summarization", shown="a", note=""):
    """One human score, as score.py writes it."""
    position = "first" if shown == "a" else "second"
    return {"pair_id": pair_id, "fixture_id": pair_id.split("#")[0],
            "task_type": task_type, "shown_first": shown,
            "picked_position": position if pick != "tie" else "tie",
            "pick": pick, "note": note}


# -- kappa ---------------------------------------------------------------

def test_perfect_agreement_is_one():
    pairs = [("a", "a"), ("b", "b"), ("tie", "tie"), ("a", "a")]
    k, po, _, _ = kappa(pairs)
    assert po == 1.0
    assert k == pytest.approx(1.0)


def test_a_judge_that_always_says_tie_scores_zero():
    """The Sprint 6 result, in miniature.

    The human separates two pairs, the judge separates none. They happen to
    agree on the two ties, which is 50% raw -- and exactly what chance
    predicts, so kappa is 0.
    """
    pairs = [("a", "tie"), ("b", "tie"), ("tie", "tie"), ("tie", "tie")]
    k, po, pe, _ = kappa(pairs)
    assert po == pytest.approx(0.5)
    assert pe == pytest.approx(0.5)
    assert k == pytest.approx(0.0)


def test_raw_agreement_alone_would_have_looked_fine():
    """Why kappa is reported at all: 50% raw on the case above is meaningless."""
    pairs = [("a", "tie"), ("b", "tie"), ("tie", "tie"), ("tie", "tie")]
    _, po, _, _ = kappa(pairs)
    assert po > 0  # a raw figure that flatters an instrument measuring nothing


def test_both_raters_using_one_category_is_undefined_not_perfect():
    """100% raw agreement, zero information. Reported as undefined, with a reason."""
    k, po, pe, note = kappa([("tie", "tie")] * 6)
    assert po == 1.0
    assert pe == pytest.approx(1.0)
    assert k is None
    assert "undefined" in note


def test_systematic_disagreement_is_negative():
    pairs = [("a", "b"), ("b", "a"), ("a", "b"), ("b", "a")]
    k, po, _, _ = kappa(pairs)
    assert po == 0.0
    assert k == pytest.approx(-1.0)


def test_no_pairs_yields_no_kappa():
    k, po, pe, note = kappa([])
    assert (k, po, pe) == (None, 0.0, 0.0)
    assert note


# -- joining human scores to judge verdicts ------------------------------

def test_a_judge_non_verdict_is_not_counted_as_a_disagreement():
    """`inconsistent` is a failure to judge, not a judgment that differs."""
    rows = [row("x#1", "inconsistent"), row("x#2", "unparsed"), row("x#3", "tie")]
    scores = [score("x#1", "a"), score("x#2", "b"), score("x#3", "tie")]

    report = analyse(scores, rows)

    assert report["scored"] == 3
    assert report["comparable"] == 1
    assert report["not_a_verdict"] == 2
    assert report["disagreed"] == 0
    assert len(report["judge_non_verdicts"]) == 2


def test_a_scored_pair_missing_from_the_results_is_reported_not_dropped():
    report = analyse([score("ghost#1", "a")], [row("x#1", "tie")])

    assert report["scored"] == 0
    assert report["missing_from_results"] == ["ghost#1"]


def test_agreement_is_split_per_task_type():
    rows = [row("s#1", "tie", "summarization"), row("s#2", "tie", "summarization"),
            row("r#1", "a", "rag_answer"), row("r#2", "tie", "rag_answer")]
    scores = [score("s#1", "a", "summarization"), score("s#2", "b", "summarization"),
              score("r#1", "a", "rag_answer"), score("r#2", "tie", "rag_answer")]

    per_task = analyse(scores, rows)["per_task"]

    assert per_task["summarization"]["agreed"] == 0
    assert per_task["rag_answer"]["agreed"] == 2
    assert per_task["summarization"]["human"] == {"a": 1, "b": 1, "tie": 0}


def test_pairs_both_called_a_tie_are_not_decisive():
    """A pair nobody separated says nothing about either rater's discrimination."""
    rows = [row("x#1", "tie"), row("x#2", "tie")]
    scores = [score("x#1", "tie"), score("x#2", "a")]

    assert analyse(scores, rows)["decisive_pairs"] == 1


def test_human_order_bias_counts_only_the_pairs_they_separated():
    rows = [row("x#1", "tie"), row("x#2", "tie"), row("x#3", "tie")]
    scores = [score("x#1", "a", shown="a"),    # picked the first shown
              score("x#2", "a", shown="b"),    # picked the second shown
              score("x#3", "tie")]             # no preference, no bias to record

    bias = analyse(scores, rows)["human_order_bias"]

    assert bias["picked_the_first_shown"] == 1
    assert bias["picked_the_second_shown"] == 1


def test_counts_cover_every_verdict_category():
    report = analyse([score("x#1", "a")], [row("x#1", "a")])
    assert set(report["human_picks"]) == set(VERDICTS)
    assert set(report["judge_picks"]) == set(VERDICTS)


# -- blind scoring mechanics ---------------------------------------------

def test_a_pick_is_recorded_against_the_answer_not_the_position():
    """The whole point of the swap: position 1 is not always answer A."""
    assert resolve_pick("first", ("a", "b")) == "a"
    assert resolve_pick("second", ("a", "b")) == "b"
    assert resolve_pick("first", ("b", "a")) == "b"
    assert resolve_pick("second", ("b", "a")) == "a"
    assert resolve_pick("tie", ("b", "a")) == "tie"


def test_the_order_a_pair_is_shown_in_is_stable_across_sessions():
    """A resumed session must not re-shuffle, or a saved pick would mean something else."""
    assert shown_order("summ-001#1", "Simba") == shown_order("summ-001#1", "Simba")


def test_different_pairs_do_not_all_get_the_same_order():
    orders = {shown_order(f"x#{n}", "Simba") for n in range(30)}
    assert len(orders) == 2  # both orders occur across a run


def test_scores_round_trip_through_the_file(tmp_path):
    path = scores_path("2026-10-01T061158", "Simba", scores_dir=tmp_path)
    rows = {"x#1": score("x#1", "a"), "x#2": score("x#2", "tie")}

    save_scores(path, run_id="2026-10-01T061158", by="Simba",
                results_file="r.json", scores=rows)
    loaded = load_scores(path)

    assert set(loaded) == {"x#1", "x#2"}
    assert loaded["x#1"]["pick"] == "a"
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["blind"] is True  # the file states the conditions it was made under


def test_loading_scores_that_do_not_exist_yet_is_empty_not_an_error(tmp_path):
    assert load_scores(tmp_path / "nothing.json") == {}