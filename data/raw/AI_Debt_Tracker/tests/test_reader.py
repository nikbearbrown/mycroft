"""The event reader, baseline B1 and the value parsers, offline (no SEC, no Ollama)."""

import ast
import json
import pathlib

import pytest

from ai_debt_tracker.documents.parse import parse_html
from ai_debt_tracker.eval.baselines import regex_reader
from ai_debt_tracker.graph.nodes import reader as rd
from ai_debt_tracker.ledger import values as V

FWP = """<html><body><p>PRICING TERM SHEET</p>
<p>On October 1, 2024, the Issuers priced $700,000,000 aggregate principal amount of 4.350% Senior Notes due 2030
and $800,000,000 aggregate principal amount of 4.850% Senior Notes due 2035.</p>
<table><tr><td>Title of Securities:</td><td>4.350% Senior Notes due 2030</td></tr>
<tr><td>Principal Amount:</td><td>$</td><td>700,000,000</td></tr>
<tr><td>Coupon:</td><td>4.350</td><td>%</td></tr>
<tr><td>Maturity Date:</td><td>February 1, 2030</td></tr></table>
<p>The Company intends to use the proceeds to redeem its 5.850% Senior Notes due 2025.</p></body></html>"""
KEY = "1/0000000001-24-000001/x.htm"


@pytest.mark.parametrize("text,value,currency", [
    ("$1,250,000,000", 1.25e9, "USD"), ("$1.25 billion", 1.25e9, "USD"), ("US$500 million", 5e8, "USD"),
    ("€750,000,000", 7.5e8, "EUR"), ("€ 1.0 billion", 1e9, "EUR"), ("£400 million", 4e8, "GBP"),
    ("CHF 300 million", 3e8, "CHF"), ("$1.6835 billion", 1.6835e9, "USD")])
def test_amounts(text, value, currency):
    got = V.parse_amount(text)
    assert got[0] == pytest.approx(value) and got[1] == currency


def test_numbers_that_are_not_money_are_not_amounts():
    assert V.parse_amount("2031") is None and V.parse_amount("4.750") is None


def test_rates_and_years():
    assert V.parse_rate("4.750%") == 4.75 and V.parse_rate("5.80 %") == 5.8 and V.parse_rate("0.00%") == 0.0
    assert V.parse_rate("Term SOFR plus 1.25%") is None and V.is_floating("Term SOFR plus 1.25%")
    assert V.parse_year("June 1, 2031") == 2031 and V.parse_year("issued in 2024, due 2031") == 2031
    assert V.parse_year("June 1") is None


def test_grounding_forgives_spacing_around_signs_only():
    assert V.grounded("4.350%", "Coupon: | 4.350 %") and V.grounded("$700,000,000", "Principal Amount: | $ 700,000,000")
    assert not V.grounded("4.375%", "Coupon: | 4.350 %") and not V.grounded("", "anything")


def test_b1_reads_the_amount_rate_due_pattern():
    doc = parse_html(FWP, KEY)
    texts = [s["text"] for s in doc.sentences] + [" | ".join(r) for t in doc.tables for r in t.rows]
    got = {(i["principal"], i["coupon_pct"], i["maturity_year"]) for i in regex_reader.extract(texts)}
    assert got == {(7e8, 4.35, 2030), (8e8, 4.85, 2035)}


def test_reader_passages_keep_the_debt_terms_and_ids():
    ps = dict(rd.select_passages([parse_html(FWP, KEY)]))
    assert any("aggregate principal amount" in t for t in ps.values())
    assert all(pid.startswith("d0:") for pid in ps)


def test_reader_parses_only_what_is_in_the_cited_words():
    doc = parse_html(FWP, KEY)
    ps = rd.select_passages([doc])
    sent = next(pid for pid, t in ps if "aggregate principal amount" in t)
    answer = {"instruments": [
        {"action": "new_issue", "kind": "notes", "principal_text": "$700,000,000", "principal_id": sent,
         "coupon_text": "4.350%", "coupon_id": sent, "maturity_text": "2030", "maturity_id": sent, "floating": False},
        # a value the model "remembers" but no passage states is dropped, not used
        {"action": "new_issue", "kind": "notes", "principal_text": "$900,000,000", "principal_id": sent,
         "coupon_text": "4.850%", "coupon_id": "d0:s999", "maturity_text": "2035", "maturity_id": sent, "floating": False}]}
    r = rd.read_filing([doc], "acc", "FWP", ask=lambda *a: json.dumps(answer))
    e1, e2 = r.events
    assert (e1.principal, e1.currency, e1.coupon_pct, e1.maturity_year) == (7e8, "USD", 4.35, 2030)
    assert e1.cites["principal"]["found"] == "cited"
    assert e2.principal is None and "principal" in e2.dropped            # $900,000,000 is in no passage
    assert e2.coupon_pct == 4.85 and e2.cites["coupon"]["found"] == "relocated"   # wrong id, right words


def test_reader_survives_an_answer_that_does_not_parse():
    r = rd.read_filing([parse_html(FWP, KEY)], "acc", "FWP", ask=lambda *a: '{"instruments": [{"action": "new_iss')
    assert r.events == [] and r.error == "answer did not parse"


def test_a_cut_off_answer_keeps_the_instruments_it_completed():
    doc = parse_html(FWP, KEY)
    sent = next(pid for pid, t in rd.select_passages([doc]) if "aggregate principal amount" in t)
    one = {"action": "new_issue", "kind": "notes", "principal_text": "$700,000,000", "principal_id": sent,
           "coupon_text": "4.350%", "coupon_id": sent, "maturity_text": "2030", "maturity_id": sent, "floating": False}
    raw = json.dumps({"instruments": [one]})[:-2] + ', {"action": "new_issue", "kind": "no'
    r = rd.read_filing([doc], "acc", "FWP", ask=lambda *a: raw)
    assert [e.principal for e in r.events] == [7e8] and r.error.startswith("answer cut off")


def test_a_tranche_repeated_without_its_amount_is_merged():
    doc = parse_html(FWP, KEY)
    sent = next(pid for pid, t in rd.select_passages([doc]) if "aggregate principal amount" in t)
    full = {"action": "new_issue", "kind": "notes", "principal_text": "$700,000,000", "principal_id": sent,
            "coupon_text": "4.350%", "coupon_id": sent, "maturity_text": "2030", "maturity_id": sent, "floating": False}
    bare = dict(full, principal_text=None, principal_id=None)
    r = rd.read_filing([doc], "acc", "FWP", ask=lambda *a: json.dumps({"instruments": [full, bare]}))
    assert len(r.events) == 1


def test_the_reader_never_imports_the_grader_side():
    src = pathlib.Path(rd.__file__).read_text(encoding="utf-8")
    mods = [n.module or "" for n in ast.walk(ast.parse(src)) if isinstance(n, ast.ImportFrom)]
    assert not any("eval" in m for m in mods)


def test_the_word_null_is_no_value_not_a_failed_copy():
    assert rd._locate("null", "d0:s1", {"d0:s1": "anything"}) == (None, None, None)
