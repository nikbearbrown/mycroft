"""The answer-key rules on a hand-built notes-data month (no network, no real data needed)."""

import gzip

import pytest

from ai_debt_tracker.eval.answer_key import AnswerKey, level_counts

A = "0000000001-26-000010"      # 10-Q for 2026-06-30
A_AMEND = "0000000001-26-000020"  # 10-Q/A for the same period, accepted later


def _write(path, header, rows, gz=False):
    opener = gzip.open if gz else open
    with opener(path, "wt", encoding="utf-8", newline="") as f:
        f.write("\t".join(header) + "\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")


@pytest.fixture
def key(tmp_path, monkeypatch):
    monkeypatch.setenv("AI_DEBT_DATA", str(tmp_path))
    d = tmp_path / "fsn_debt" / "2026_08"
    d.mkdir(parents=True)
    sub_cols = ["adsh", "cik", "name", "sic", "countryba", "form", "period", "fy", "fp", "filed", "accepted",
                "prevrpt", "fye", "afs", "aciks"]
    _write(d / "sub.tsv", sub_cols, [
        [A, 1, "EXAMPLE CO", 3674, "US", "10-Q", "20260630", 2026, "Q2", "20260805", "2026-08-05 16:00:00.0", 0, "1231", "1-LAF", ""],
        [A_AMEND, 1, "EXAMPLE CO", 3674, "US", "10-Q/A", "20260630", 2026, "Q2", "20260901", "2026-09-01 16:00:00.0", 0, "1231", "1-LAF", ""],
    ])
    dims = {
        "0xb1": "DebtInstrument=A20329.625SeniorNotes;LongtermDebtType=SeniorNotes;",
        "0xb2": "DebtInstrument=EuroNotes3.500Due2030;",
        "0xb3": "DebtInstrument=IssuanceOfLongTermDebtEight;",
        "0xb4": "DebtInstrument=NewNotes2031;SubsequentEventType=SubsequentEvent;",
        "0xb5": "LongtermDebtType=SeniorNotes;",
        "0xb6": "LongtermDebtType=November2025Debt;",
        "0xb7": "DebtInstrument=A20329.625SeniorNotes;Range=Minimum;",
        "0xb8": "DebtInstrument=Notes1.00Due2026;",
    }
    _write(d / "dim.tsv", ["dimhash", "segments"], sorted(dims.items()))
    _write(d / "labels.tsv", ["tag", "version", "tlabel"], [
        ["A20329.625SeniorNotesMember", A, "2032 9.625% Senior Notes"],
        ["EuroNotes3.500Due2030Member", A, "3.500% Euro Notes due 2030"],
        ["IssuanceOfLongTermDebtEightMember", A, "Issuance of long term debt eight"],
        ["November2025DebtMember", A, "November 2025 Debt"],
        ["SeniorNotesMember", "us-gaap/2025", "Senior Notes [Member]"],
        ["Notes1.00Due2026Member", A, "1.00% Notes due 2026"],
    ])
    num_cols = ["adsh", "tag", "version", "ddate", "qtrs", "uom", "dimh", "coreg", "value", "dcml"]
    P = "20260630"
    _write(d / "num.tsv.gz", num_cols, [
        [A, "DebtInstrumentInterestRateStatedPercentage", "us-gaap/2025", P, 0, "pure", "0xb1", "", "0.0963", 4],
        [A, "DebtInstrumentFaceAmount", "us-gaap/2025", P, 0, "USD", "0xb1", "", "1250000000", -6],
        [A, "DebtInstrumentCarryingAmount", "us-gaap/2025", P, 0, "USD", "0xb1", "", "1231000000", -6],
        [A, "DebtInstrumentCarryingAmount", "us-gaap/2025", P, 0, "USD", "0xb1", "SUBSIDIARY LP", "999", -6],
        [A, "DebtInstrumentCarryingAmount", "us-gaap/2025", P, 0, "USD", "0xb2", "", "580000000", -6],
        [A, "DebtInstrumentFaceAmount", "us-gaap/2025", P, 0, "EUR", "0xb2", "", "500000000", -6],
        [A, "DebtInstrumentCarryingAmount", "us-gaap/2025", P, 0, "USD", "0xb3", "", "7930000000", -6],
        [A, "DebtInstrumentFaceAmount", "us-gaap/2025", P, 0, "USD", "0xb4", "", "2000000000", -6],
        [A, "LongTermDebt", "us-gaap/2025", P, 0, "USD", "0xb5", "", "9000000000", -6],
        [A, "LongTermDebt", "us-gaap/2025", P, 0, "USD", "0xb6", "", "30000000000", -6],
        [A, "DebtInstrumentInterestRateStatedPercentage", "us-gaap/2025", P, 0, "pure", "0xb7", "", "0.05", 4],
        [A, "DebtInstrumentCarryingAmount", "us-gaap/2025", P, 0, "USD", "0xb8", "", "0", -6],
        [A, "LongTermDebt", "us-gaap/2025", P, 0, "USD", "0x00000000", "", "41000000000", -6],
        [A, "LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths", "us-gaap/2025", P, 0, "USD", "0x00000000", "", "1000000000", -6],
    ], gz=True)
    _write(d / "txt.tsv.gz", ["adsh", "tag", "ddate", "qtrs", "dimh", "coreg", "value"], [], gz=True)
    (d / "_complete").write_text("test\n")
    return AnswerKey(["2026_08"], {1})


def by_member(key, adsh=A):
    insts, skipped = key.instruments(adsh)
    return {i.member: i for i in insts}, skipped


def test_amendment_without_debt_facts_does_not_supersede(key):
    assert [r["adsh"] for r in key.reports(1)] == [A]      # the 10-Q/A here only refiled an exhibit


def test_amendment_with_debt_facts_supersedes(key):
    key.num[A_AMEND].append(dict(key.num[A][0], adsh=A_AMEND))
    assert [r["adsh"] for r in key.reports(1)] == [A_AMEND]


def test_p17_exact_coupon_beats_rounded_tag(key):
    i = by_member(key)[0]["A20329.625SeniorNotes"]
    assert i.rate == 9.625 and i.rate_from.startswith("parsed")
    assert i.key() == ("USD", 9.625, 2032)
    assert i.face == 1_250_000_000 and i.carrying == 1_231_000_000   # parent fact, not the co-registrant's


def test_currency_is_the_bonds_not_the_reporting_unit(key):
    i = by_member(key)[0]["EuroNotes3.500Due2030"]
    assert i.currency == "EUR" and i.amount_uom == "EUR" and i.key() == ("EUR", 3.5, 2030)


def test_issuance_groups_and_custom_debt_types_are_offerings(key):
    m, _ = by_member(key)
    assert m["IssuanceOfLongTermDebtEight"].klass == "offering"
    assert m["November2025Debt"].klass == "offering" and m["November2025Debt"].axis == "LongtermDebtType"


def test_subsequent_events_and_ranges_never_enter_the_key(key):
    m, skipped = by_member(key)
    assert "NewNotes2031" not in m                       # debt after the period: would leak the future
    assert skipped["non-descriptive axis: SubsequentEventType"] == 1
    assert skipped["non-descriptive axis: Range"] == 1
    assert skipped["co-registrant fact"] == 1
    assert skipped["category only"] == 1                 # standard SeniorNotes member alone


def test_zero_balance_is_not_outstanding(key):
    assert by_member(key)[0]["Notes1.00Due2026"].outstanding is False


def test_totals_and_level_counts(key):
    rec = key.filing_record(A)
    assert rec["totals"] == {"long_term_debt": 41e9, "due_next_12m": 1e9}
    assert level_counts(rec) == {"bond": 2, "bond_keyed": 2, "offering": 2}


def _rec(instruments, totals):
    base = {"outstanding": True, "klass": "bond", "maturity_year": 2030, "key": None}
    return {"totals": totals, "instruments": [base | i for i in instruments]}


def test_partial_per_bond_tagging_is_not_l1():
    """Oracle's 10-Qs tag only the bonds issued that quarter: 4 bonds, $8 bn of ~$100 bn."""
    from ai_debt_tracker.eval.answer_key import grading_level
    rec = _rec([{"amount_usd": 2e9}] * 4, {"long_term_debt": 100e9})
    g = grading_level(rec)
    assert g["level"] == "L3" and g["coverage_itemised"] == 0.08


def test_full_itemisation_is_l1_and_offerings_are_l2():
    from ai_debt_tracker.eval.answer_key import grading_level
    assert grading_level(_rec([{"amount_usd": 45e9}, {"amount_usd": 50e9, "klass": "facility"}],
                              {"long_term_debt": 100e9}))["level"] == "L1"
    offerings = _rec([{"amount_usd": 40e9, "klass": "offering"}, {"amount_usd": 45e9, "klass": "offering"}],
                     {"long_term_debt": 100e9})
    assert grading_level(offerings)["level"] == "L2"


def test_bonds_without_a_maturity_are_not_itemised():
    from ai_debt_tracker.eval.answer_key import grading_level
    rec = _rec([{"amount_usd": 50e9, "maturity_year": None}] * 2, {"long_term_debt": 100e9})
    assert grading_level(rec)["level"] == "L3"


def test_missing_total_falls_back_and_says_so():
    from ai_debt_tracker.eval.answer_key import grading_level
    g = grading_level(_rec([{"amount_usd": 1e9}, {"amount_usd": 2e9}], {}))
    assert g["level"] == "L1" and g["total_basis"].startswith("sum of tagged instruments")


def test_maturity_buckets_are_not_instruments(tmp_path, monkeypatch):
    """IBM: `Maturing2027` is a year bucket of many bonds."""
    from ai_debt_tracker.eval.answer_key import BUCKET
    assert BUCKET.match("Maturing 2027") and BUCKET.match("Maturing 2026-2028") and BUCKET.match("Maturing 2026 2027")
    assert not BUCKET.match("Notes Maturing 2027")


def test_total_debt_chain_and_aggregate_members():
    """Oracle: no LongTermDebt tag; total = LongTermNotesAndLoans + NotesPayableCurrent; its one
    $125 bn 'Senior Notes And Other Long Term Borrowings' member is an aggregate, not an instrument."""
    from ai_debt_tracker.eval.answer_key import grading_level
    rec = _rec([{"amount_usd": 125e9, "klass": "other"}] + [{"amount_usd": 2e9}] * 4,
               {"notes_and_loans_noncurrent": 117.7e9, "notes_payable_current": 7.6e9})
    g = grading_level(rec)
    assert g["total_basis"] == "LongTermNotesAndLoans + NotesPayableCurrent"
    assert g["level"] == "L3" and g["itemised"] == 4


def test_subtotal_members_do_not_dilute_the_fallback_denominator():
    """Digital Realty: a $16 bn 'Unsecured senior notes' member (no maturity) next to the bonds it sums."""
    from ai_debt_tracker.eval.answer_key import grading_level
    rec = _rec([{"amount_usd": 16e9, "maturity_year": None}] + [{"amount_usd": 4e9}] * 4 + [{"amount_usd": 3e9, "klass": "facility"}], {})
    assert grading_level(rec)["coverage_itemised"] == 1.0


def test_bonds_and_offerings_tagged_side_by_side_is_l1():
    from ai_debt_tracker.eval.answer_key import grading_level
    rec = _rec([{"amount_usd": 47e9}, {"amount_usd": 47e9}, {"amount_usd": 90e9, "klass": "offering"}], {"long_term_debt": 100e9})
    assert grading_level(rec)["level"] == "L1"


def test_zero_balance_beats_a_face_amount_dated_at_period_end(key):
    """Oracle: a repaid note keeps its face amount at the period end, with carrying amount 0."""
    key.num[A].append({"adsh": A, "tag": "DebtInstrumentFaceAmount", "version": "us-gaap/2025", "ddate": "20260630",
                       "qtrs": "0", "uom": "USD", "dimh": "0xb8", "coreg": "", "value": "2000000000", "dcml": "-6"})
    i = by_member(key)[0]["Notes1.00Due2026"]
    assert i.outstanding is False and i.outstanding_from == "zero balance at period end"


def test_p35_face_only_bond_due_by_the_report_year_is_repaid(key):
    """Digital Realty: a repaid note with no balance tag, only a face dated at the period end, in a
    report that tags balances for its other debt."""
    from ai_debt_tracker.eval.answer_key import NO_DIMS  # noqa: F401
    key.dims["0xb9"] = "DebtInstrument=FourPointTwoFiveZeroPercentNotesDueTwoThousandTwentySix;"
    key.labels[("FourPointTwoFiveZeroPercentNotesDueTwoThousandTwentySixMember", A)] = "4.250% Notes due 2026"
    key.dims["0xba"] = "DebtInstrument=NewNotes5.000Due2031;"
    key.labels[("NewNotes5.000Due2031Member", A)] = "5.000% Notes due 2031"
    for dimh in ("0xb9", "0xba"):
        key.num[A].append({"adsh": A, "tag": "DebtInstrumentFaceAmount", "version": "us-gaap/2025", "ddate": "20260630",
                           "qtrs": "0", "uom": "USD", "dimh": dimh, "coreg": "", "value": "500000000", "dcml": "-6"})
    m, _ = by_member(key)
    assert m["FourPointTwoFiveZeroPercentNotesDueTwoThousandTwentySix"].outstanding is False      # due 2026 <= 2026
    assert m["NewNotes5.000Due2031"].outstanding is True                                         # a new issue, kept


def test_p36_conflicting_face_and_carrying_units_make_the_currency_unknown(key):
    key.num[A].append({"adsh": A, "tag": "DebtInstrumentFaceAmount", "version": "us-gaap/2025", "ddate": "20260630",
                       "qtrs": "0", "uom": "EUR", "dimh": "0xb3", "coreg": "", "value": "1150000000", "dcml": "-6"})
    i = by_member(key)[0]["IssuanceOfLongTermDebtEight"]
    assert i.currency_from == "conflict"
