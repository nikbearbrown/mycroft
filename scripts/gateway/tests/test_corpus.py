import json

import pytest

from gateway.bench.corpus import (
    check, collect, from_handoff, from_logbook, summarise,
)
from gateway.policy import Policy
from gateway.tiers import TierConfig

HANDOFF = {
    "action": "llm_review_of_flags",
    "llm_needed": True,
    "live_call_performed": False,
    "approved_for_live_action": False,
    "model_named_by_original": "llama-3.3-70b-versatile",
    "endpoint_named_by_original": "https://api.groq.com/openai/v1/chat/completions",
    "payload": {"max_tokens": 2000,
                "messages": [{"role": "system", "content": "You are an analyst."},
                             {"role": "user", "content": "Flagged: X and not X."}]},
}


def write_handoff(root, recipe="contradiction-detection-agent", run="sample-001",
                  name="FXA.json", **overrides):
    path = root / "logs" / recipe / "runs" / run / "llm-handoff" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({**HANDOFF, **overrides}), encoding="utf-8")
    return path


def write_logbook(root, rows, name="2026-11-09T000000-run.jsonl"):
    path = root / "logs" / "gateway" / "runs" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return path


def row(**overrides):
    return {"caller": "bench/baseline.py", "task_type": "sentiment_classification",
            "provider": "groq", "model": "openai/gpt-oss-20b", "tokens_in": 40,
            "tokens_out": 2, "cost_usd": 0.000063, **overrides}


# -- prepared requests ---------------------------------------------------

def test_a_prepared_request_is_recorded_as_never_sent(tmp_path):
    """The state of every recipe artifact in the repo on 2026-11-09."""
    record = from_handoff(write_handoff(tmp_path), tmp_path, with_text=False)

    assert record["live_call_performed"] is False
    assert record["source_kind"] == "llm_handoff"
    assert record["recipe"] == "contradiction-detection-agent"
    assert record["run"] == "sample-001"
    assert record["model_named"] == "llama-3.3-70b-versatile"
    assert record["max_tokens"] == 2000
    assert record["messages"] == 2


def test_prompt_text_is_not_stored_unless_asked_for(tmp_path):
    """Sizes and a hash are enough to price a request. Words are someone else's data."""
    path = write_handoff(tmp_path)

    without = from_handoff(path, tmp_path, with_text=False)
    with_text = from_handoff(path, tmp_path, with_text=True)

    assert "prompt" not in without
    assert without["prompt_chars"] > 0 and without["prompt_sha256"]
    assert with_text["prompt"].startswith("You are an analyst.")


def test_the_same_prompt_hashes_the_same_and_a_different_one_does_not(tmp_path):
    a = from_handoff(write_handoff(tmp_path, name="A.json"), tmp_path, with_text=False)
    b = from_handoff(write_handoff(tmp_path, name="B.json"), tmp_path, with_text=False)
    other = from_handoff(
        write_handoff(tmp_path, name="C.json",
                      payload={"max_tokens": 2000,
                               "messages": [{"content": "something else"}]}),
        tmp_path, with_text=False)

    assert a["prompt_sha256"] == b["prompt_sha256"]
    assert a["prompt_sha256"] != other["prompt_sha256"]


def test_an_empty_payload_is_recorded_as_incomplete_not_skipped(tmp_path):
    """5 of the 16 real handoffs have no payload. Silently dropping them would
    make the corpus look tidier than the evidence is."""
    record = from_handoff(write_handoff(tmp_path, payload={}), tmp_path, with_text=False)

    assert record["complete"] is False
    assert record["prompt_chars"] == 0
    assert record["prompt_sha256"] is None


def test_a_json_file_that_is_not_a_handoff_is_ignored(tmp_path):
    path = tmp_path / "logs" / "x" / "runs" / "r" / "llm-handoff" / "notes.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"something": "else"}), encoding="utf-8")

    assert from_handoff(path, tmp_path, with_text=False) is None


# -- calls that really happened ------------------------------------------

def test_logbook_rows_become_live_records_carrying_their_cost(tmp_path):
    path = write_logbook(tmp_path, [row(), row(cost_usd=0.000103)])

    records = list(from_logbook(path, tmp_path))

    assert len(records) == 2
    assert all(r["live_call_performed"] for r in records)
    assert records[0]["model_named"] == "groq:openai/gpt-oss-20b"
    assert records[1]["cost_usd"] == 0.000103


def test_both_sources_land_in_one_corpus(tmp_path):
    write_handoff(tmp_path)
    write_logbook(tmp_path, [row()])

    kinds = {r["source_kind"] for r in collect(tmp_path)}

    assert kinds == {"llm_handoff", "gateway_logbook"}


# -- the summary ---------------------------------------------------------

def test_the_summary_separates_intentions_from_traffic(tmp_path):
    write_handoff(tmp_path, name="A.json")
    write_handoff(tmp_path, name="B.json", payload={})
    write_logbook(tmp_path, [row(), row()])

    stats = summarise(collect(tmp_path))

    assert stats["records"] == 4
    assert stats["prepared_never_sent"] == 2
    assert stats["incomplete_payloads"] == 1
    assert stats["live_calls"] == 2
    assert stats["models_named"]["llama-3.3-70b-versatile"] == 2


# -- what the gateway could not serve ------------------------------------

def test_an_unpriced_model_and_an_oversized_budget_are_both_flagged(tmp_path, prices_v1):
    """Both real blockers, found on all 11 complete requests in the repo."""
    policy = Policy.load(TierConfig.load())
    problems = check(collect(tmp_path) + [from_handoff(write_handoff(tmp_path),
                                                       tmp_path, with_text=False)],
                     policy, prices_v1)

    kinds = {p["problem"] for p in problems}
    assert kinds == {"unpriced_model", "over_budget"}


def test_calls_that_already_happened_are_not_flagged(tmp_path, prices_v1):
    """They were served. Whether the gateway could serve them is not a question."""
    write_logbook(tmp_path, [row()])
    policy = Policy.load(TierConfig.load())

    assert check(collect(tmp_path), policy, prices_v1) == []