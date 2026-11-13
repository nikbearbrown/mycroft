"""The ledger engine, the self-checks and the episode supervisor on hand-made events (no network, no model)."""

import threading

from ai_debt_tracker.ledger import checks, engine

CITE = {"principal": {"id": "d0:s3", "text": "$1,000,000,000", "found": "cited"}}


def ev(action, cls, coupon, year, principal, acc="a1", accepted="2025-05-01T16:00:00", currency="USD", cites=CITE):
    return {"action": action, "action_class": cls, "kind": "notes", "currency": currency, "principal": principal,
            "coupon_pct": coupon, "floating": False, "maturity_year": year, "cites": cites, "accession": acc,
            "accepted": accepted, "form": "8-K"}


def bond(coupon, year, principal, currency="USD"):
    return {"kind": "bond", "currency": currency, "principal": principal, "coupon_pct": coupon, "maturity_year": year,
            "amount_usd": principal if currency == "USD" else None}


OPEN = [bond(3.0, 2027, 1e9), bond(4.5, 2030, 2e9), bond(2.0, 2024, 5e8)]


def test_same_bond_in_three_filings_is_one_event_with_every_source():
    es = [ev("new_issue", "new", 5.25, 2035, 1.5e9, "pricing", "2025-05-01"),
          ev("new_issue", "new", 5.250, 2035, None, "fwp", "2025-05-02"),
          ev("new_issue", "new", 5.25, 2035, 1.5e9, "closing", "2025-05-07")]
    (m,) = engine.merge_events(es)
    assert m["principal"] == 1.5e9 and m["merged_from"] == 3 and len(m["sources"]) == 3


def test_closing_ledger_adds_removes_sweeps_and_moves_the_total():
    es = [ev("new_issue", "new", 5.25, 2035, 1.5e9), ev("redemption", "exit", 3.0, 2027, None, "r1", "2025-06-01")]
    led = engine.closing_ledger(OPEN, {"total_debt": 3.5e9}, es, "2025-06-30")
    keys = sorted((i["coupon_pct"], i["maturity_year"]) for i in led["instruments"])
    assert keys == [(4.5, 2030), (5.25, 2035)]                 # 2027 redeemed, 2024 swept, 2035 added
    assert led["totals"]["total_debt"] == 3.5e9 - 5e8 + 1.5e9 - 1e9
    assert led["meta"]["swept"] == 1


def test_partial_redemption_reduces_and_add_on_adds():
    es = [ev("tender_offer", "exit", 4.5, 2030, 5e8), ev("add_on", "new", 3.0, 2027, 2.5e8, "t2", "2025-06-02")]
    led = engine.closing_ledger(OPEN, {}, es, "2025-06-30")
    p = {(i["coupon_pct"], i["maturity_year"]): i["principal"] for i in led["instruments"]}
    assert p[(4.5, 2030)] == 1.5e9 and p[(3.0, 2027)] == 1.25e9


def test_a_bond_already_in_the_opening_ledger_is_not_added_twice():
    led = engine.closing_ledger(OPEN, {}, [ev("new_issue", "new", 4.5, 2030, 2e9)], "2025-06-30")
    assert len(led["instruments"]) == 2 and led["meta"]["log"][0]["change"] == "already held"


def test_unknown_exit_and_new_bond_without_year_become_questions_not_changes():
    es = [ev("redemption", "exit", 7.0, 2029, 3e8), ev("new_issue", "new", 6.0, None, 5e8, "n2", "2025-06-02")]
    led = engine.closing_ledger(OPEN, {}, es, "2025-06-30")
    assert {q["type"] for q in led["meta"]["questions"]} == {"exit_of_unknown", "new_without_maturity"}
    assert len(led["instruments"]) == 2
    res = checks.run_checks(led, "2025-06-30", 3.5e9)
    assert any(f["check"] == "exits_known" for f in res["flags"]) and "cited" in res["passed"]


def test_a_change_without_a_citation_is_rejected():
    led = engine.closing_ledger(OPEN, {}, [ev("new_issue", "new", 6.0, 2033, 5e8, cites={})], "2025-06-30")
    assert len(led["instruments"]) == 2 and led["meta"]["rejected"]
    assert any(f["check"] == "cited" for f in checks.run_checks(led, "2025-06-30")["flags"])


def test_checks_flag_a_new_bond_due_before_the_quarter_and_an_implausible_jump():
    es = [ev("new_issue", "new", 6.0, 2024, 5e8), ev("new_issue", "new", 6.5, 2040, 9e9, "big", "2025-06-03")]
    led = engine.closing_ledger(OPEN, {"total_debt": 3.5e9}, es, "2025-06-30")
    flagged = {f["check"] for f in checks.run_checks(led, "2025-06-30", 3.5e9)["flags"]}
    assert {"new_after_quarter", "plausible_change"} <= flagged


def test_supervisor_runs_an_episode_end_to_end_with_parallel_readers():
    from langgraph.checkpoint.memory import MemorySaver

    from ai_debt_tracker.graph import supervisor as sv
    rows = [{"cik": 1, "accession": f"acc{k}", "form": "8-K", "filing_date": "2025-05-0%d" % k, "accepted": f"2025-05-0{k}T16",
             "primary_document": f"d{k}.htm", "items": []} for k in (1, 2, 3)]
    active, peak, lock = [0], [0], threading.Lock()

    def read(row):
        with lock:
            active[0] += 1
            peak[0] = max(peak[0], active[0])
        import time
        time.sleep(0.2)
        with lock:
            active[0] -= 1
        if row["accession"] == "acc1":
            return {"events": [ev("new_issue", "new", 5.25, 2035, 1.5e9) | {"accession": None}]}
        return {"events": [ev("redemption", "exit", 3.0, 2027, None)]}

    tools = sv.Tools(timeline=lambda cik, a, b: rows, texts=lambda r: {"8-K": r["accession"]},
                     triage=lambda r, t: {"relevant": r["accession"] != "acc3"}, read=read)
    g = sv.build(tools, MemorySaver())
    out = g.invoke({"episode": "e1", "cik": 1, "quarter_end": "2025-06-30", "window_open": "2025-03-01",
                    "cutoff_date": "2025-08-01", "opening": OPEN, "opening_totals": {"total_debt": 3.5e9}},
                   {"configurable": {"thread_id": "e1"}})
    assert len(out["relevant"]) == 2 and len(out["readings"]) == 2 and peak[0] == 2     # the two reads overlapped
    keys = sorted((i["coupon_pct"], i["maturity_year"]) for i in out["ledger"]["instruments"])
    assert keys == [(4.5, 2030), (5.25, 2035)]
    assert out["checks"]["passed"] and g.get_state({"configurable": {"thread_id": "e1"}}).values["checks"]


def test_ledger_server_reads_as_of_and_proposes_without_writing(tmp_path):
    import json

    from ai_debt_tracker.mcp_servers.ledger_core import LedgerStore
    for q, extra in (("2025-03-31", []), ("2025-06-30", [ev("new_issue", "new", 5.25, 2035, 1.5e9)])):
        led = engine.closing_ledger(OPEN, {"total_debt": 3.5e9}, extra, q)
        (tmp_path / f"7-{q}.json").write_text(json.dumps({"episode": f"7-{q}", "cik": 7, "quarter_end": q, "ledger": led,
                                                          "checks": checks.run_checks(led, q)}))
    s = LedgerStore(tmp_path)
    assert s.get(7, "2025-05-15")["quarter_end"] == "2025-03-31"          # never a ledger from the future
    assert len(s.get(7, "2025-07-01")["instruments"]) == 3
    before = (tmp_path / "7-2025-06-30.json").read_text()
    p = s.propose(7, "2025-07-01", ev("redemption", "exit", 4.5, 2030, None))
    assert p["valid"] and not p["applied"] and p["diff"][0]["change"] == "removed"
    assert (tmp_path / "7-2025-06-30.json").read_text() == before
    assert not s.propose(7, "2025-07-01", ev("redemption", "exit", 4.5, 2030, None, cites={}))["valid"]


def test_p55_a_bond_priced_after_the_quarter_end_is_kept_out_of_that_quarter():
    es = [ev("new_issue", "new", 9.0, 2031, 1.75e9, "jul", "2025-07-28T16:00:00")]
    led = engine.closing_ledger(OPEN, {}, es, "2025-06-30")
    assert len(led["instruments"]) == 2 and len(led["meta"]["after_quarter"]) == 1
