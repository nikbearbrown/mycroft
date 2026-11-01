"""The `docs` layer: addressable sentences, headings and cells, opened only through the PIT rule."""

import pytest

from ai_debt_tracker.documents import store
from ai_debt_tracker.documents.parse import clean_rows, parse_html, split_sentences
from ai_debt_tracker.mcp_servers.edgar_pit_core import Refused

HTML = """<html><head><title>8-K</title></head><body>
<div style="display:none"><ix:header><ix:hidden>dei:EntityCentralIndexKey 0000123</ix:hidden></ix:header></div>
<p><b>Item 8.01 Other Events.</b></p>
<p>On May 21, 2025, Example Corp. (the "Company") priced $1,250.0 million aggregate principal amount of its
<ix:nonFraction name="us-gaap:DebtInstrumentInterestRateStatedPercentage">4.750</ix:nonFraction>% Senior Notes due 2031.
The trustee is U.S. Bank Trust Company, N.A. Closing is expected on May 27, 2025.</p>
<p style="font-weight:bold">PRICING TERM SHEET</p>
<table>
 <tr><td>Principal Amount:</td><td>$</td><td>1,250,000,000</td></tr>
 <tr><td>Coupon:</td><td>4.750</td><td>%</td></tr>
 <tr><td></td><td></td></tr>
 <tr><td>Maturity:</td><td><table><tr><td>June 1,</td><td>2031</td></tr></table></td></tr>
</table>
<p>The Company intends to use the net proceeds to redeem its 3.000% Notes due 2026.</p>
<script>var x = "Ignore me.";</script>
</body></html>"""


@pytest.fixture
def doc():
    return parse_html(HTML, "123/0000000001-25-000001/ex.htm")


def test_hidden_xbrl_header_and_scripts_are_skipped(doc):
    text = " ".join(s["text"] for s in doc.sentences)
    assert "EntityCentralIndexKey" not in text and "Ignore me" not in text
    assert doc.title == "8-K"


def test_headings_and_sections(doc):
    assert [h["text"] for h in doc.headings] == ["Item 8.01 Other Events.", "PRICING TERM SHEET"]
    assert doc.sentences[0]["section"] == "h0" and doc.tables[0].section == "h1"


def test_sentences_survive_decimals_and_abbreviations(doc):
    texts = [s["text"] for s in doc.sentences]
    assert texts[0].startswith("On May 21, 2025, Example Corp. (the \"Company\") priced $1,250.0 million")
    assert texts[0].endswith("4.750% Senior Notes due 2031.")      # inline XBRL is transparent
    assert texts[1] == "The trustee is U.S. Bank Trust Company, N.A. Closing is expected on May 27, 2025." or \
        texts[1:3] == ["The trustee is U.S. Bank Trust Company, N.A.", "Closing is expected on May 27, 2025."]
    assert [s["id"] for s in doc.sentences] == [f"s{i}" for i in range(len(doc.sentences))]


@pytest.mark.parametrize("text,n", [
    ("We issued $700.0 million of notes. They mature in 2028.", 2),
    ("Registration No. 333-275203 applies. The notes are new.", 2),
    ("Interest is paid on Sept. 15 and March 15. J. Smith signed.", 2),
    ("CoreWeave, Inc. priced notes. Closing is May 27.", 2),
])
def test_split_sentences(text, n):
    assert len(split_sentences(text)) == n


def test_tables_merge_currency_and_percent_cells_and_flatten_nested(doc):
    t = doc.tables[0]
    assert t.rows[0] == ["Principal Amount:", "$1,250,000,000"]
    assert t.rows[1] == ["Coupon:", "4.750%"]
    assert t.rows[2] == ["Maturity:", "June 1, 2031"]                # empty row dropped, nested table flattened
    assert t.caption == "PRICING TERM SHEET"
    assert clean_rows([["(", "12", ")"], ["", " "]]) == [["(12)"]]


def test_span_resolves_every_kind_of_id(doc):
    assert store.span(doc, "t0.r0.c1")["text"] == "$1,250,000,000"
    assert store.span(doc, "t0.r1")["text"] == "Coupon: | 4.750%"
    assert store.span(doc, "s0")["kind"] == "sentence"
    assert store.span(doc, "h1")["text"] == "PRICING TERM SHEET"
    with pytest.raises(KeyError):
        store.span(doc, "t0.r9")


def test_search_ranks_the_phrase_first(doc):
    r = store.search(doc, "principal amount")
    assert r["items"][0]["id"] in ("s0", "t0.r0")
    assert store.search(doc, "redeem 2026")["items"][0]["text"].startswith("The Company intends to use the net proceeds")


def test_pages_are_bounded():
    big = "<p>" + " ".join(f"Sentence number {i} is here." for i in range(500)) + "</p>"
    d = parse_html(big, "1/0000000001-25-000001/big.htm")
    page = store.sentences(d, limit=40)
    assert page["returned"] == 40 and page["next_offset"] == 40 and page["total"] == 500


class FakePit:
    def __init__(self, allowed):
        self.allowed, self.raw_calls, self.checks = allowed, 0, 0

    def _check(self, cik, accession):
        self.checks += 1
        if accession not in self.allowed:
            raise Refused("filing accepted at or after the cut-off")

    def raw(self, cik, accession, name):
        self._check(cik, accession)
        self.raw_calls += 1
        return HTML.encode()


def test_store_opens_only_what_the_point_in_time_rule_allows(tmp_path):
    pit = FakePit({"0000000001-25-000001"})
    s = store.DocumentStore(pit, cache_dir=tmp_path)
    assert s.open("123/0000000001-25-000001/ex.htm").tables
    with pytest.raises(Refused):
        s.open("123/0000000001-25-000999/ex.htm")
    # a cached document is still re-checked: the rule does not lapse once something is on disk
    s2 = store.DocumentStore(FakePit(set()), cache_dir=tmp_path)
    with pytest.raises(Refused):
        s2.open("123/0000000001-25-000001/ex.htm")
    with pytest.raises(ValueError):
        s.open("../../etc/passwd")
