"""The grader and baseline B0 on hand-built records (DESIGN.md §9.1–9.3)."""

import pytest

from ai_debt_tracker.eval.baselines.carry_forward import carry_forward, opening_report
from ai_debt_tracker.eval.grader import grade_episode, grade_l1, grade_l2, grade_l3, summarise


def inst(member, rate, year, face, klass="bond", currency="USD", outstanding=True, issued=None, usd=None):
    return {"member": member, "klass": klass, "outstanding": outstanding, "rate": rate, "maturity_year": year,
            "face": face, "face_uom": currency, "carrying": None, "carrying_uom": None, "currency": currency,
            "amount_usd": usd if usd is not None else (face if currency == "USD" else None), "issued": issued}


def rec(instruments, totals=None, adsh="A", period="20250630"):
    return {"adsh": adsh, "period": period, "instruments": instruments,
            "totals": totals if totals is not None else {"long_term_debt": sum(i["face"] or 0 for i in instruments)}}


def bond(rate, year, principal, currency="USD", issued=None):
    return {"kind": "bond", "currency": currency, "principal": principal, "coupon_pct": rate,
            "maturity_year": year, "issued": issued, "amount_usd": principal}


TARGET = rec([inst("Notes2030", 4.75, 2030, 1e9), inst("Notes2035", 5.3, 2035, 2e9),
              inst("EuroNotes2031", 3.5, 2031, 5e8, currency="EUR", usd=5.4e8)])


def test_perfect_ledger_scores_full():
    led = {"instruments": [bond(4.75, 2030, 1e9), bond(5.3, 2035, 2e9), bond(3.5, 2031, 5e8, "EUR")]}
    g = grade_l1(TARGET, led)
    assert (g["matched"], g["truth"], g["ledger"], g["principal_ok"]) == (3, 3, 3, 3)


def test_rounded_coupon_matches_but_a_different_coupon_does_not():
    assert grade_l1(TARGET, {"instruments": [bond(4.755, 2030, 1e9)]})["matched"] == 1   # P17: 4.75 vs 4.755
    assert grade_l1(TARGET, {"instruments": [bond(4.80, 2030, 1e9)]})["matched"] == 0


def test_currency_must_agree():
    assert grade_l1(TARGET, {"instruments": [bond(3.5, 2031, 5e8, "USD")]})["matched"] == 0


def test_wrong_principal_still_matches_but_fails_principal_accuracy():
    g = grade_l1(TARGET, {"instruments": [bond(4.75, 2030, 1.5e9)]})
    assert g["matched"] == 1 and (g["principal_scored"], g["principal_ok"]) == (1, 0)


def test_assignment_is_one_to_one_and_uses_principal_to_break_ties():
    """Intel-style twin keys: two bonds with one coupon and year, told apart by amount."""
    target = rec([inst("A", 5.0, 2033, 1e9), inst("B", 5.0, 2033, 2e9)])
    led = {"instruments": [bond(5.0, 2033, 2e9), bond(5.0, 2033, 1e9)]}
    g = grade_l1(target, led)
    assert g["matched"] == 2 and g["principal_ok"] == 2
    assert grade_l1(target, {"instruments": [bond(5.0, 2033, 1e9)]})["matched"] == 1   # never claims both


def test_bond_without_tagged_coupon_matches_on_year_and_principal():
    target = rec([inst("NotesDue2029", None, 2029, 7.5e8)])
    assert grade_l1(target, {"instruments": [bond(4.1, 2029, 7.5e8)]})["matched"] == 1
    assert grade_l1(target, {"instruments": [bond(4.1, 2029, 9e8)]})["matched"] == 0


def test_subtotal_members_are_not_truth_but_one_large_bond_is():
    """Digital Realty's subtotal has no maturity; TeraWulf's one bond is 60% of its debt."""
    target = rec([inst("UnsecuredSeniorNotes", None, None, 9e9), inst("Notes2030", 4.75, 2030, 1e9)],
                 totals={"long_term_debt": 1e10})
    assert grade_l1(target, {"instruments": []})["truth"] == 1
    big = rec([inst("SeniorSecured2030", 7.75, 2030, 3.2e9), inst("Convert2031", 1.0, 2031, 2.1e9)])
    assert grade_l1(big, {"instruments": []})["truth"] == 2


def test_change_detection():
    start = rec([inst("Old2027", 3.0, 2027, 1e9), inst("Notes2030", 4.75, 2030, 1e9)])
    target = rec([inst("Notes2030", 4.75, 2030, 1e9), inst("New2036", 5.5, 2036, 2e9)])
    carried = {"instruments": [bond(3.0, 2027, 1e9), bond(4.75, 2030, 1e9)]}
    g = grade_l1(target, carried, start)
    assert (g["added"], g["added_caught"], g["removed"], g["removed_caught"]) == (1, 0, 1, 0)
    tracked = {"instruments": [bond(4.75, 2030, 1e9), bond(5.5, 2036, 2e9)]}
    g = grade_l1(target, tracked, start)
    assert (g["added_caught"], g["removed_caught"]) == (1, 1)


def test_l2_sums_ledger_bonds_by_issue_period():
    target = rec([inst("November2025Debt", None, None, 3e10, klass="offering", issued="2025-11")])
    led = {"instruments": [bond(4.0, 2030, 1e10, issued="2025-11"), bond(4.5, 2035, 2e10, issued="2025-11")]}
    assert grade_l2(target, led)["matched"] == 1
    led_off = {"instruments": [bond(4.0, 2030, 1e10, issued="2025-11"), bond(4.5, 2035, 2.1e10, issued="2025-11")]}
    assert grade_l2(target, led_off)["matched"] == 0          # 3.1% off
    wrong_month = {"instruments": [bond(4.0, 2030, 3e10, issued="2025-08")]}
    assert grade_l2(target, wrong_month)["matched"] == 0


def test_l3_totals_within_two_percent():
    target = rec([], totals={"long_term_debt": 100e9, "long_term_debt_current": 5e9})
    g = grade_l3(target, {"instruments": [], "totals": {"total_debt": 101.5e9, "current": 6e9}})
    assert g["total_debt"]["ok"] and not g["current"]["ok"]


def test_b0_sweeps_by_year_and_keeps_the_target_year():
    opening = rec([inst("Due2024", 1.0, 2024, 5e8), inst("Due2025", 2.0, 2025, 5e8), inst("Due2030", 4.75, 2030, 1e9)],
                  period="20241231")
    led = carry_forward(opening, "20250630")
    assert [i["maturity_year"] for i in led["instruments"]] == [2025, 2030]
    assert led["totals"]["total_debt"] == pytest.approx(2e9 - 5e8)


def test_b0_walks_back_to_an_itemised_report():
    tenk = rec([inst("A", 4.0, 2030, 5e9), inst("B", 5.0, 2034, 5e9)], adsh="K", period="20241231")
    tenq = rec([], totals={"long_term_debt": 1e10}, adsh="Q", period="20250331")
    reports = [{"adsh": "K", "period": "20241231", "form": "10-K"}, {"adsh": "Q", "period": "20250331", "form": "10-Q"}]
    opening, note = opening_report(reports, "Q", "L1", {"K": tenk, "Q": tenq})
    assert opening["adsh"] == "K" and "walked back 1" in note


def test_summarise_has_intervals():
    target = rec([inst("Notes2030", 4.75, 2030, 1e9)])
    results = [grade_episode(target, {"instruments": [bond(4.75, 2030, 1e9)]}, "L1")] * 3 + \
              [grade_episode(target, {"instruments": []}, "L1")]
    s = summarise(results)
    point, lo, hi = s["l1"]["recall"]
    assert point == 0.75 and lo <= point <= hi


def test_bonds_adding_up_to_an_offering_are_not_extras():
    """Broadcom: a report tags old bonds one by one but its newest deal only as a total."""
    target = rec([inst("Notes2030", 4.75, 2030, 1e9),
                  inst("January2025SeniorNotes", None, None, 3e9, klass="offering", issued="2025-01")])
    target["instruments"][1]["carrying"], target["instruments"][1]["carrying_uom"] = 3e9, "USD"
    led = {"instruments": [bond(4.75, 2030, 1e9), bond(4.8, 2028, 1.1e9), bond(5.05, 2030, 0.8e9), bond(5.2, 2032, 1.1e9)]}
    g = grade_l1(target, led)
    assert (g["matched"], g["covered_by_offering"], g["extra"]) == (1, 3, 0)
    led_padded = {"instruments": led["instruments"] + [bond(6.0, 2040, 0.5e9)]}
    assert grade_l1(target, led_padded)["extra"] == 1


def test_unknown_key_currency_does_not_block_a_match():
    """Equinix: a Swiss franc note whose label never says so; the key only has a USD carrying amount."""
    i = inst("TwoPointEightSevenFiveSeniorNotes2028", 2.875, 2028, None)
    i.update({"carrying": 3.3e8, "carrying_uom": "USD", "currency_from": "carrying"})
    assert grade_l1(rec([i], totals={}), {"instruments": [bond(2.875, 2028, None, "CHF")]})["matched"] == 1
    i["currency_from"] = "label"
    assert grade_l1(rec([i], totals={}), {"instruments": [bond(2.875, 2028, None, "CHF")]})["matched"] == 0


def test_old_offerings_cannot_claim_leftover_bonds():
    """Coincidental sums: a 2021 deal total must not 'cover' unrelated bonds in a 2025 report."""
    target = rec([inst("March2021SeniorNotes", None, None, 2.2e9, klass="offering", issued="2021-03")])
    target["instruments"][0]["carrying"], target["instruments"][0]["carrying_uom"] = 2.2e9, "USD"
    led = {"instruments": [bond(1.4, 2026, 1.5e9), bond(4.7, 2030, 0.7e9)]}
    assert grade_l1(target, led)["covered_by_offering"] == 0


def test_usd_tagged_face_does_not_make_a_currency_known():
    i = inst("TwoPointEightSevenFiveSeniorNotes2028", 2.875, 2028, 3.37e8)   # face tagged in USD
    i["currency_from"] = "face"
    assert grade_l1(rec([i], totals={}), {"instruments": [bond(2.875, 2028, None, "CHF")]})["matched"] == 1


def test_b0_carries_offerings_on_the_same_amount_the_key_grades():
    """Microsoft: an issuance's face is the original deal size; the key and B0 both use what is left."""
    off = inst("IssuanceOfLongTermDebtEight", None, None, 19.8e9, klass="offering")
    off.update({"carrying": 7.93e9, "carrying_uom": "USD"})
    opening = rec([off], totals={"long_term_debt": 7.93e9}, period="20250331")
    target = rec([dict(off)], totals={"long_term_debt": 7.93e9}, period="20250630")
    assert grade_l2(target, carry_forward(opening, "20250630"))["matched"] == 1


def test_p37_translated_principal_is_not_scored():
    """Digital Realty: a euro note whose face is tagged as a dollar translation, currency unknown."""
    i = inst("OnePointOneTwoFivePercentNotesDue2028", 1.125, 2028, 5.4855e8)
    i["currency_from"] = "face"                       # face tagged in USD: currency not known
    g = grade_l1(rec([i], totals={}), {"instruments": [bond(1.125, 2028, 5e8, "EUR")]})
    assert g["matched"] == 1 and g["principal_scored"] == 0
    g = grade_l1(rec([i], totals={}), {"instruments": [bond(1.125, 2028, 5.4855e8, "USD")]})
    assert g["principal_scored"] == 1 and g["principal_ok"] == 1


def test_p39_printed_bond_the_key_holds_without_a_maturity_is_set_aside():
    """Core Scientific: small notes tagged with a rate and a balance but no maturity anywhere. A ledger
    bond that is one of them (same amount and coupon) is neither a match nor an extra; one that is not
    stays an extra."""
    target = rec([inst("ConvertibleNotes2029", 3.0, 2029, 4.6e8), inst("HCMNote", 5.0, None, 1.0764e7)])
    led = {"instruments": [bond(3.0, 2029, 4.6e8), bond(5.0, 2026, 1.0764e7), bond(7.0, 2027, 2e7)]}
    g = grade_l1(target, led)
    assert (g["matched"], g["covered_by_unkeyed"], g["extra"]) == (1, 1, 1)


def test_p44_l1_episode_with_no_keyed_bond_is_graded_on_totals_only():
    """Applied Digital: graded L1, but no instrument in the key carries a maturity. Every ledger bond would be
    an extra; the grader grades totals only and says why."""
    target = rec([inst("CIMPromissoryNote", 7.0, None, 1.25e8)], totals={"long_term_debt": 1.05e8})
    g = grade_episode(target, {"instruments": [bond(7.0, 2027, 1.05e8)], "totals": {"total_debt": 1.05e8}}, "L1")
    assert "l1" not in g and "P44" in g["level_note"] and g["l3"]["total_debt"]["ok"]
