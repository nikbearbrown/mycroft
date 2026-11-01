"""The `timeline` and `triage` nodes, offline (no SEC, no Ollama)."""

import pytest

from ai_debt_tracker.graph.nodes import timeline as tl
from ai_debt_tracker.graph.nodes import triage as tr

COVER = "UNITED STATES SECURITIES AND EXCHANGE COMMISSION FORM 8-K Example Corp. Check the appropriate box ... "


def t(body: str) -> str:
    return COVER + body


# ------------------------------------------------------------------------------------ rules
@pytest.mark.parametrize("form,items,texts,relevant,event,rule", [
    ("8-K", ["2.03", "9.01"], {"8-K": t("Item 2.03 Creation of a Direct Financial Obligation. The notes ...")},
     True, None, "rule R1"),
    ("424B5", [], {"424B5": "Prospectus Supplement $1,500,000,000 4.200% Notes due 2029 Oracle Corporation is offering"},
     True, "new_bond_issue", "rule R2"),
    ("424B5", [], {"424B5": "Prospectus Supplement 12,000,000 Shares of Common Stock offered by the selling stockholders"},
     False, "not_debt", "rule R2"),
    ("FWP", [], {"FWP": "Final Pricing Term Sheet 5.800% Senior Notes due 2035 Issuer: Micron"},
     True, "new_bond_issue", "rule R3"),
    ("8-K", ["8.01", "9.01"], {"8-K": t("Item 8.01 Other Events. On May 21, 2025, the Company priced its offering of "
                                         "$2,000 million aggregate principal amount of 9.250% senior notes due 2030.")},
     True, "new_bond_issue", "rule R4"),
    ("8-K", ["8.01"], {"8-K": t("Item 8.01 Other Events. The Company delivered a notice of redemption to holders of its "
                                 "3.150% Notes due 2025.")}, True, "redemption_or_repayment", "rule R4"),
    ("8-K", ["1.01"], {"8-K": t("Item 1.01 Entry into a Material Definitive Agreement. The Company entered into a "
                                 "Third Amended and Restated Credit Agreement with the lenders.")},
     True, "facility_amendment", "rule R4"),
    ("8-K", ["5.02"], {"8-K": t("Item 5.02 Departure of Directors. Jane Doe resigned as Chief Financial Officer.")},
     False, "not_debt", "rule R5"),
])
def test_rules(form, items, texts, relevant, event, rule):
    r = tr.triage(form, items, texts, "acc", ask=lambda *a: pytest.fail("the model must not be asked"))
    assert (r.relevant, r.decided_by) == (relevant, rule)
    if event:
        assert r.event_type == event
    assert r.model_judgment is False


def test_doubtful_filings_go_to_the_model_and_are_labelled_as_judgments():
    """An earnings release that mentions notes outside its lead is doubtful."""
    text = t("Item 2.02 Results of Operations. " + "Revenue grew. " * 300 + "Long-term debt includes our senior notes.")
    calls = []

    def fake(form, items, texts, model, host):
        calls.append(form)
        return {"relevant": False, "event_type": "not_debt", "evidence": "", "evidence_found": True}, 1.2

    r = tr.triage("8-K", ["2.02", "9.01"], {"8-K": text, "EX-99.1": "Example Corp reports results. " + "x " * 2000
                                            + "The Company has senior notes outstanding."}, "acc", ask=fake)
    assert calls == ["8-K"] and r.decided_by == "model" and r.model_judgment and not r.relevant


def test_model_quote_not_in_the_text_is_flagged():
    def fake(form, items, texts, model, host):
        return {"relevant": True, "event_type": "new_bond_issue", "evidence": "invented", "evidence_found": False}, 1.0
    r = tr.triage("8-K", ["8.01"], {"8-K": t("Item 8.01 Other Events. " + "x " * 1500 + "debt")}, "acc", ask=fake)
    assert r.evidence.startswith("[quote not found in the text]")


def test_a_model_answer_that_does_not_parse_keeps_the_filing(monkeypatch):
    """A runaway answer cut off mid-string is not a 'no': triage keeps it for the reader, flagged."""
    import io
    import json as _json

    class Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    cut = _json.dumps({"message": {"content": '{"relevant": true, "event_type": "new_bond_issue", "evidence": "the No'}})
    monkeypatch.setattr(tr.urllib.request, "urlopen", lambda *a, **k: Resp(cut.encode()))
    r = tr.triage("8-K", ["8.01"], {"8-K": t("Item 8.01 Other Events. " + "x " * 1500 + "debt")}, "acc", host="http://x")
    assert r.relevant and r.decided_by == "model" and r.model_judgment
    assert r.evidence.startswith("[model answer did not parse")


def test_note_words_do_not_fire_on_notes_to_financial_statements():
    assert not tr.DEBT_WORDS.search("See the Notes to the Condensed Consolidated Financial Statements.")
    assert tr.DEBT_WORDS.search("the 2030 senior notes")


# ------------------------------------------------------------------------------------ timeline
class FakePit:
    def timeline(self, cik, start, end, forms):
        if cik == 2:   # the subsidiary
            return [{"accession": "0000000002-25-000001", "form": "FWP", "filing_date": "2025-02-01",
                     "accepted": "2025-02-01T10:00:00", "items": "", "primary_document": "fwp.htm"},
                    {"accession": "0000000001-25-000002", "form": "424B2", "filing_date": "2025-02-02",
                     "accepted": "2025-02-02T10:00:00", "items": "", "primary_document": "p.htm"}]
        return [{"accession": "0000000001-25-000002", "form": "424B2", "filing_date": "2025-02-02",
                 "accepted": "2025-02-02T10:00:00", "items": "", "primary_document": "p.htm"},
                {"accession": "0000000001-25-000003", "form": "8-K", "filing_date": "2025-03-01",
                 "accepted": "2025-03-01T10:00:00", "items": "8.01,9.01", "primary_document": "k.htm"}]

    def exhibits(self, cik, accession):
        return [{"document": "k.htm", "type": "8-K"}, {"document": "ex991.htm", "type": "EX-99.1"},
                {"document": "ex41.htm", "type": "EX-4.1"}, {"document": "logo.jpg", "type": "GRAPHIC"},
                {"document": "x.xsd", "type": "EX-101.SCH"}, {"document": "p.htm", "type": "424B2"},
                {"document": "fwp.htm", "type": "FWP"}]


def test_timeline_covers_subsidiaries_and_deduplicates_co_filings():
    c = tl.timeline(FakePit(), 1, "2025-01-01", "2025-12-31", subsidiaries=[2])
    assert [x.accession for x in c] == ["0000000002-25-000001", "0000000001-25-000002", "0000000001-25-000003"]
    assert [x.family for x in c] == ["FWP", "424B", "8-K"]
    assert c[0].cik == 2 and c[0].company_cik == 1
    k = c[2]
    assert k.items == ["8.01", "9.01"]
    assert [d["type"] for d in k.documents][0] == "8-K"                # main document first
    assert {d["type"] for d in k.documents} >= {"EX-99.1", "EX-4.1"}
    assert not any(d["document"].endswith((".jpg", ".xsd")) for d in k.documents)
