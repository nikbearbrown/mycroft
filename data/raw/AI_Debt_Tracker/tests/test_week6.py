"""Week 6 on hand-made inputs (no network, no model): the merge fixes P56–P58, loans (capacity vs drawn), the
investigators' amendments, the triage fixes P53–P54, the answer-key and grader fixes P47 and P49, and the
opening-ledger reader's table reading."""

from ai_debt_tracker.documents.parse import Document, Table
from ai_debt_tracker.graph.nodes import investigator as inv
from ai_debt_tracker.graph.nodes import opening as op
from ai_debt_tracker.graph.nodes import reader as rd
from ai_debt_tracker.graph.nodes import triage as tr
from ai_debt_tracker.ledger import engine

from test_ledger_engine import OPEN, ev


# ------------------------------------------------------------------------------------ P56–P58 and loans
def test_p57_a_launch_without_coupon_folds_into_the_priced_bond_that_follows():
    launch = ev("new_issue", "new", None, 2030, 2.0e9, acc="launch", accepted="2025-02-18T08:00:00")
    priced = ev("new_issue", "new", 0.0, 2030, 2.3e9, acc="priced", accepted="2025-02-19T08:00:00")
    led = engine.closing_ledger(OPEN, {"total_debt": 3.5e9}, [launch, priced], "2025-03-31")
    new = [i for i in led["instruments"] if str(i["id"]).startswith("new-")]
    assert len(new) == 1 and new[0]["principal"] == 2.3e9 and len(led["meta"]["launches_folded"]) == 1


def test_p57_a_launch_with_no_pricing_is_a_question_and_a_floating_tranche_is_left_alone():
    launch = ev("new_issue", "new", None, 2031, 1.0e9, acc="launch")
    frn = ev("new_issue", "new", None, 2028, 5e8, acc="pricing") | {"floating": True}
    fixed = ev("new_issue", "new", 4.8, 2028, 1.5e9, acc="pricing")
    led = engine.closing_ledger(OPEN, {}, [launch, frn, fixed], "2025-06-30")
    assert [q["type"] for q in led["meta"]["questions"]] == ["launch_not_priced"]
    assert sorted((i["coupon_pct"] or -1, i["maturity_year"]) for i in led["instruments"]
                  if str(i["id"]).startswith("new-")) == [(-1, 2028), (4.8, 2028)]


def test_p56_a_bond_with_no_amount_is_a_question_not_an_addition():
    led = engine.closing_ledger(OPEN, {}, [ev("new_issue", "new", 0.25, 2027, None)], "2025-06-30")
    assert not [i for i in led["instruments"] if str(i["id"]).startswith("new-")]
    assert led["meta"]["questions"][0]["type"] == "new_without_amount"


def test_p58_the_banks_option_is_not_a_bond():
    base = ev("new_issue", "new", 2.75, 2030, 3.0e8, acc="a")
    option = ev("new_issue", "new", 2.75, 2030, 4.5e7, acc="b") | {"option": True}
    led = engine.closing_ledger(OPEN, {}, [base, option], "2025-06-30")
    new = [i for i in led["instruments"] if str(i["id"]).startswith("new-")]
    assert len(new) == 1 and new[0]["principal"] == 3.0e8           # the option's amount does not win the vote
    alone = engine.closing_ledger(OPEN, {}, [option], "2025-06-30")
    assert not [i for i in alone["instruments"] if str(i["id"]).startswith("new-")]


def test_p58_marker_reads_the_cited_sentence():
    s = ("The Company granted the initial purchasers an option to purchase up to an additional $45 million aggregate "
         "principal amount of the notes.")
    assert rd.is_option_amount(s, "$45 million")
    s2 = ("The Company issued $2.3 billion in aggregate principal amount of notes, which includes $300 million in "
          "aggregate principal amount of the notes issued pursuant to the exercise in full of the initial purchasers' "
          "option to purchase additional notes.")
    assert rd.is_option_amount(s2, "$300 million") and not rd.is_option_amount(s2, "$2.3 billion")
    doc = Document(key="k", sentences=[{"id": "s1", "text": s, "section": None, "order": 0}])
    evs = rd.mark_options([{"action_class": "new", "cites": {"principal": {"id": "d0:s1", "text": "$45 million"}}}], [doc])
    assert evs[0]["option"]


def test_a_draw_moves_total_debt_and_a_commitment_does_not_and_a_loan_repayment_reduces_it():
    draw = ev("draw", "new", None, 2029, 2e8) | {"kind": "term_loan"}
    commit = ev("new_facility", "new", None, 2030, 1e9) | {"kind": "revolving_facility"}
    repaid = ev("repayment", "exit", None, None, 7.75e7) | {"kind": "delayed_draw_facility"}
    led = engine.closing_ledger(OPEN, {"total_debt": 3.5e9}, [draw, commit, repaid], "2025-06-30")
    assert abs(led["totals"]["total_debt"] - (3.5e9 - 5e8 + 2e8 - 7.75e7)) < 1          # 5e8: the 2024 bond swept
    assert not led["meta"]["questions"]


# ------------------------------------------------------------------------------------ investigators
def test_an_amendment_drops_or_rewrites_the_event_it_names():
    e = ev("redemption", "exit", 4.5, 2030, None, currency="EUR")
    led = engine.closing_ledger(OPEN, {}, [e], "2025-06-30")
    q = led["meta"]["questions"][0]
    f = inv.investigate(q, led["instruments"], docs_for=lambda a: [])
    assert f["amendment"]["set"]["currency"] == "USD"                    # matched the held 4.5% 2030 on a looser key
    led2 = engine.closing_ledger(OPEN, {}, [e], "2025-06-30", [f["amendment"]])
    assert (4.5, 2030) not in {(i["coupon_pct"], i["maturity_year"]) for i in led2["instruments"]}
    assert not led2["meta"]["questions"]


def test_a_bond_named_without_amount_that_is_already_held_is_dropped_without_the_model():
    e = ev("new_issue", "new", 3.0, 2027, None, currency="EUR")       # printed in dollars, held in euros
    led = engine.closing_ledger(OPEN, {}, [e], "2025-06-30")
    f = inv.investigate(led["meta"]["questions"][0], led["instruments"], docs_for=lambda a: 1 / 0)
    assert f["amendment"]["drop"] and not f["model_judgment"]


def test_supervisor_investigates_and_reruns_the_ledger_within_two_rounds():
    from langgraph.checkpoint.memory import MemorySaver

    from ai_debt_tracker.graph import supervisor as sv
    rows = [{"cik": 1, "accession": "acc1", "form": "8-K", "filing_date": "2025-05-01", "accepted": "2025-05-01T16",
             "primary_document": "d.htm", "items": []}]
    calls = []

    def investigate(q, instruments):
        calls.append(q["type"])
        return inv.investigate(q, instruments, docs_for=lambda a: [])

    tools = sv.Tools(timeline=lambda c, a, b: rows, texts=lambda r: {"8-K": "x"},
                     triage=lambda r, t: {"relevant": True},
                     read=lambda r: {"events": [ev("redemption", "exit", 4.5, 2030, None, currency="EUR")]},
                     investigate=investigate)
    g = sv.build(tools, MemorySaver())
    out = g.invoke({"episode": "e", "cik": 1, "quarter_end": "2025-06-30", "window_open": "2025-03-01",
                    "cutoff_date": "2025-08-01", "opening": OPEN, "opening_totals": {}, "rounds": 0},
                   {"configurable": {"thread_id": "e"}})
    assert calls == ["exit_of_unknown"] and out["rounds"] == 1 and not out["checks"]["questions"]
    assert (4.5, 2030) not in {(i["coupon_pct"], i["maturity_year"]) for i in out["ledger"]["instruments"]}


# ------------------------------------------------------------------------------------ triage P53, P54
def test_p53_a_tender_for_shares_is_not_decided_as_a_debt_tender():
    text = ("Alphabet Inc. today announced that it has received notice of an unsolicited mini-tender offer by Tutanota "
            "LLC to purchase up to 350,000 shares of Alphabet's Class C capital stock at a price of $180 per share. ")
    assert tr.lead_event(text) is None
    assert tr.lead_event("The Company announced the commencement of a cash tender offer for any and all of its "
                         "outstanding 4.50% Senior Notes due 2027. ") == "tender_or_exchange"


def test_p54_an_fwp_for_shares_naming_the_concurrent_notes_goes_to_the_model():
    fwp = ("Free Writing Prospectus. Borrowed shares of Common Stock offered by certain investors subscribing for our "
           "1.75% convertible senior notes due 2030 (the Notes) in the Concurrent Notes Offering. No new shares of "
           "Common Stock will be issued in this offering.")
    assert tr.rules("FWP", [], {"FWP": fwp}) is None
    assert tr.rules("FWP", [], {"FWP": "Pricing Term Sheet. 5.250% Senior Notes due 2035. Issuer: X"}).relevant


# ------------------------------------------------------------------------------------ P47, P49
def test_p47_a_convertible_only_filer_has_a_total_and_p49_no_ladder_on_10q_targets():
    from ai_debt_tracker.eval.grader import total_debt, truth_totals
    assert total_debt({"convertible_total": 488.7e6}) == (488.7e6, "ConvertibleDebt (convertible-only filer)")
    assert total_debt({"long_term_debt": 1e9, "convertible_total": 5e8})[0] == 1e9
    rec = {"form": "10-Q", "totals": {"long_term_debt": 1e9, "due_next_12m": 1e8, "due_after_5": 5e8}}
    assert set(truth_totals(rec)) == {"total_debt"}
    assert "due_next_12m" in truth_totals(rec | {"form": "10-K"})


# ------------------------------------------------------------------------------------ opening-ledger reader
def _doc():
    t = Table(id="t20", section=None, caption="The Company's total debt consisted of the following:", rows=[
        ["June 29, 2024", "December 30, 2023"], ["(In millions)"],
        ["2.95% Senior Notes Due 2024", "$—", "$750"],
        ["2.375% Senior Notes Due 2030", "750", "750"],
        ["€500 million 3.25% Notes due 2029", "540", "552"],
        ["Total debt (principal amount)", "1,290", "2,052"],
        ["Unamortized debt discount and issuance costs", "(31)", "(32)"],
        ["Total debt (net)", "1,259", "2,020"]])
    return Document(key="k", tables=[t])


def test_rules_reader_takes_the_period_end_column_skips_repaid_and_keeps_euro_principal():
    r = op.read_rules(_doc(), "2024-06-29")
    got = sorted((i["currency"], i["coupon_pct"], i["maturity_year"], i["principal"], i["amount_usd"]) for i in r["instruments"])
    assert got == [("EUR", 3.25, 2029, 5e8, 5.4e8), ("USD", 2.375, 2030, 7.5e8, 7.5e8)]
    assert r["totals"]["total_debt"] == 1.259e9


def test_model_reader_points_and_code_reads_and_refuses_a_bad_row():
    def ask(tables, form, period, model, host):
        return ('{"instruments": [{"row": "t20.r3", "amount_column": 2, "kind": "notes"},'
                ' {"row": "t20.r9", "amount_column": 1, "kind": "notes"}],'
                ' "total_debt": {"row": "t20.r7", "amount_column": 1}}')
    r = op.read_opening(_doc(), "10-Q", "2024-06-29", ask=ask)
    assert [(i["coupon_pct"], i["principal"]) for i in r["instruments"]] == [(2.375, 7.5e8)]   # header column wins
    assert r["refused"][0]["why"] == "no such row" and r["totals"]["total_debt"] == 1.259e9


def test_p61_a_header_with_one_cell_per_column_names_the_amount_and_a_rate_column_is_never_it():
    t = Table(id="t24", section=None, caption="We maintain debt obligations as follows (in millions):", rows=[
        ["Instrument", "Maturity Date", "Principal Outstanding as of January 31, 2025", "Interest Terms",
         "Contractual Interest Rate"],
        ["Credit Facility", "October 2029", "0", "Floating", "N/A"],
        ["2028 Senior Notes", "April 2028", "1,500", "Fixed", "3.70"],
        ["2031 Senior Notes", "July 2031", "1,500", "Fixed", "1.95"]])
    r = op.read_rules(Document(key="k", tables=[t]), "2025-01-31")
    assert sorted((i["maturity_year"], i["principal"]) for i in r["instruments"]) == [(2028, 1.5e9), (2031, 1.5e9)]


def test_p61_units_cut_from_a_long_caption_come_from_the_documents_other_captions():
    long_cap = "Short-term and long-term loan obligations with respect to revolving lines of credit and term loans " \
               "as of March 31, 2025 and June 30, 2024 consisted of the follo"
    t1 = Table(id="t28", section=None, caption=long_cap, rows=[["March 31,", "June 30,"], ["2025", "2024"],
                                                               ["Total term loans", "82,808", "114,557"]])
    t2 = Table(id="t29", section=None, caption="Available borrowings (in thousands except for percentages):",
               rows=[["a", "1"]])
    assert op.table_units(t1, Document(key="k", tables=[t1, t2])) == 1e3
