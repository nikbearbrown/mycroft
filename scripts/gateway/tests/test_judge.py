import pytest

from gateway.adapters.fake import FakeAdapter
from gateway.bench.judge import (
    Comparison, build_prompt, compare, parse_verdict, summarize,
)
from gateway.client import GatewayClient
from gateway.logbook import Logbook
from gateway.report import read_records

TIERS = {
    "cheap":  {"provider": "groq", "model": "small"},
    "strong": {"provider": "anthropic", "model": "strong"},
}

PAIR = dict(
    fixture_id="summ-001",
    asks="Summarize the statement in one sentence.",
    input_text="Revenue rose and margins held.",
    answer_a="Revenue rose; margins held.",
    answer_b="Things went well.",
    a_label="cheap",
    b_label="mid",
)


def make_client(log_path, prices):
    judge = FakeAdapter(provider="anthropic")
    client = GatewayClient(
        logbook=Logbook(log_path, prices),
        adapters={"groq": FakeAdapter(provider="groq"), "anthropic": judge},
        tiers=TIERS, policy_version="0.1.0", clock=lambda: 0.0,
    )
    return client, judge


# -- reading a verdict ----------------------------------------------------

@pytest.mark.parametrize("text, expected", [
    ("FIRST", "first"),
    ("second", "second"),
    ("Tie", "tie"),
    ("  SECOND  \n", "second"),
    ("Both are close, but I would say\nFIRST", "first"),
])
def test_a_clear_verdict_is_read(text, expected):
    assert parse_verdict(text) == expected


@pytest.mark.parametrize("text", [
    "", "   ", "I cannot decide.",
    "FIRST is wrong and SECOND is wrong",  # names two -- not a verdict
])
def test_an_unclear_reply_is_not_guessed_at(text):
    assert parse_verdict(text) is None


# -- the swap -------------------------------------------------------------

def test_the_two_runs_show_the_answers_in_opposite_orders(log_path, prices_v1):
    client, judge = make_client(log_path, prices_v1)
    judge.queue_response("FIRST").queue_response("SECOND")

    compare(client, **PAIR)

    assert len(judge.calls) == 2
    first_prompt, second_prompt = (c["prompt"] for c in judge.calls)
    assert first_prompt.index(PAIR["answer_a"]) < first_prompt.index(PAIR["answer_b"])
    assert second_prompt.index(PAIR["answer_b"]) < second_prompt.index(PAIR["answer_a"])


def test_a_judge_that_always_says_first_is_recorded_as_inconsistent(log_path, prices_v1):
    """The point of the swap. Position bias must not be able to look like a win."""
    client, judge = make_client(log_path, prices_v1)
    judge.queue_response("FIRST").queue_response("FIRST")

    result = compare(client, **PAIR)

    assert result.result == "inconsistent"
    assert [v.verdict for v in result.votes] == ["a", "b"]


def test_both_runs_agreeing_on_the_same_answer_is_a_win(log_path, prices_v1):
    client, judge = make_client(log_path, prices_v1)
    judge.queue_response("FIRST").queue_response("SECOND")  # answer A, both ways

    result = compare(client, **PAIR)

    assert result.result == "a"
    assert [v.verdict for v in result.votes] == ["a", "a"]


def test_both_runs_agreeing_on_a_tie_is_a_tie(log_path, prices_v1):
    client, judge = make_client(log_path, prices_v1)
    judge.queue_response("TIE").queue_response("TIE")

    assert compare(client, **PAIR).result == "tie"


def test_a_reply_with_no_verdict_is_unparsed_not_a_tie(log_path, prices_v1):
    client, judge = make_client(log_path, prices_v1)
    judge.queue_response("I think both are fine").queue_response("SECOND")

    result = compare(client, **PAIR)

    assert result.result == "unparsed"
    assert result.votes[0].verdict is None


# -- what it costs and what it records ------------------------------------

def test_both_judging_calls_are_logged_and_the_cost_is_their_sum(log_path, prices_v1):
    client, judge = make_client(log_path, prices_v1)
    judge.queue_response("FIRST").queue_response("SECOND")

    result = compare(client, **PAIR)

    rows = read_records(log_path)
    assert len(rows) == 2
    assert {r["caller"] for r in rows} == {"bench.judge"}
    assert {r["task_type"] for r in rows} == {"judge_pairwise"}
    assert {r["routing_reason"] for r in rows} == {"override"}
    assert {r["tier"] for r in rows} == {"strong"}
    assert result.cost_usd == pytest.approx(sum(r["cost_usd"] for r in rows))


def test_each_run_is_its_own_request(log_path, prices_v1):
    """Two independent judgments, not one request retried."""
    client, judge = make_client(log_path, prices_v1)
    judge.queue_response("FIRST").queue_response("SECOND")

    result = compare(client, **PAIR)

    assert result.votes[0].request_id != result.votes[1].request_id
    assert {r["attempt_no"] for r in read_records(log_path)} == {1}


def test_a_verdict_travels_labeled_as_a_judgment(log_path, prices_v1):
    client, judge = make_client(log_path, prices_v1)
    judge.queue_response("FIRST").queue_response("SECOND")

    record = compare(client, **PAIR).to_record()

    assert record["kind"] == "model_judgment"
    assert record["judged_by"] == "strong"
    assert len(record["votes"]) == 2


# -- the summary ----------------------------------------------------------

def _comparison(result: str) -> Comparison:
    return Comparison(fixture_id="x", a_label="cheap", b_label="mid",
                      result=result, votes=(), cost_usd=0.001,
                      judged_by="strong", judged_at="2026-09-24T00:00:00+00:00")


def test_the_summary_counts_every_outcome_including_the_awkward_ones():
    summary = summarize([_comparison(r) for r in
                         ("a", "a", "b", "tie", "inconsistent", "unparsed")])

    assert summary["comparisons"] == 6
    assert summary["counts"] == {"a": 2, "b": 1, "tie": 1,
                                 "inconsistent": 1, "unparsed": 1}
    assert summary["decided"] == 4
    assert summary["cost_usd"] == pytest.approx(0.006)


def test_the_summary_says_out_loud_that_these_are_judgments():
    assert summarize([])["kind"] == "model_judgment"