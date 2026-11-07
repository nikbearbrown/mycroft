"""The answer key (D4): what each company's 10-Q / 10-K says it owed, instrument by instrument.

Reads the debt subset that `fsn.extract_month` wrote and turns one filing into:

* **instruments** (L1/L2) — one record per debt member, with its coupon, maturity year, face and
  carrying amount, whether it is outstanding at the period end, and what kind of thing it is
  (bond, offering, facility, category);
* **totals** (L3) — company-level long-term debt, current portion and the maturity ladder.

Rules that decide what counts, each traceable to DESIGN.md §3.4:

* Identity: the `DebtInstrument` member if the fact has one; otherwise a company-specific (custom)
  member on `LongtermDebtType` / `ShortTermDebtType` / `CreditFacility` (Meta tags its offerings
  as `LongtermDebtType=November2025Debt`). A *standard* us-gaap member alone (`SeniorNotes`) is a
  category, not an instrument.
* Only facts whose other axes are descriptive (recourse, rate type, legal entity, currency) are
  used. Facts on `SubsequentEventType` (debt after the period — it would leak the future into the
  key), `Range`, scenarios or fair-value hierarchies are skipped and counted.
* Parent facts only (`coreg` empty). Co-registrant facts are counted, not mixed in (P12).
* Outstanding = a positive balance fact dated at the period end (the Week 0 spike's rule).
* Rates are stored as tagged; `rate_dcml` keeps the stated precision because the bulk data
  rounds 6.125% to 6.13% (P17) — the matcher, not the key, applies the tolerance.

Grading side only: the agent graph must never import this module (P11, enforced by a test).
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import asdict, dataclass, field

from ..ledger.parsers import issue_period, parse_member, rates_match, split_camel
from .fsn import NO_DIMS, month_dir, read_tsv

IDENTITY_AXES = ("DebtInstrument", "LongtermDebtType", "ShortTermDebtType", "CreditFacility", "LineOfCreditFacility")
DESCRIPTIVE_AXES = {"RecourseStatus", "VariableRate", "LegalEntity", "Currency", "ConsolidatedEntities",
                    "LongtermDebtType", "ShortTermDebtType", "CreditFacility", "LineOfCreditFacility", "DebtInstrument",
                    "DebtInstrumentSecurityStatus", "DebtInstrumentPriorityStatus",
                    # debt assumed in an acquisition: Broadcom tags VMware's notes
                    # BusinessAcquisition=VMwareAcquisition (Week 2 hand-check; 56 facts were being dropped)
                    "BusinessAcquisition"}
BALANCE_TAGS = {
    "LongTermDebt", "DebtInstrumentCarryingAmount", "LongTermDebtNoncurrent", "LongTermDebtCurrent", "SeniorNotes",
    "ConvertibleNotesPayable", "LongTermLineOfCredit", "LineOfCredit", "SecuredDebt", "UnsecuredDebt", "NotesPayable",
    "DebtCurrent", "LongTermNotesPayable", "SeniorLongTermNotes", "ConvertibleDebtNoncurrent", "LoansPayable",
    "OtherLongTermDebt", "CommercialPaper", "ShortTermBorrowings", "SubordinatedDebt", "LongTermDebtGross",
    "ConvertibleDebt", "ConvertibleDebtGross", "ConvertibleDebtCurrent",   # TeraWulf's convertibles
}
CARRYING_ORDER = ("DebtInstrumentCarryingAmount", "LongTermDebt", "LongTermDebtGross", "SeniorNotes", "ConvertibleNotesPayable",
                  "ConvertibleDebt", "ConvertibleDebtGross", "LongTermLineOfCredit", "LineOfCredit", "NotesPayable")
# IBM tags its debt by maturity year ("Maturing 2027", "Maturing 2026-2028"): buckets, not instruments
BUCKET = re.compile(r"^(maturing|maturity|maturities|due)( in)?( (19|20)\d\d)+(( to| through| -|-)? ?(19|20)\d\d)?$", re.I)
L1_COVERAGE = 0.8
OVERALLOTMENT = re.compile(r"over-?\s?allot|greenshoe", re.I)
FACILITY_KINDS = {"revolver", "term_loan", "delayed_draw", "credit_facility", "commercial_paper"}
TOTALS = {
    "long_term_debt": "LongTermDebt", "long_term_debt_noncurrent": "LongTermDebtNoncurrent",
    "long_term_debt_current": "LongTermDebtCurrent", "debt_current": "DebtCurrent",
    "commercial_paper": "CommercialPaper", "short_term_borrowings": "ShortTermBorrowings",
    "face_total": "DebtInstrumentFaceAmount", "carrying_total": "DebtInstrumentCarryingAmount",
    "due_next_12m": "LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths",
    "due_year_2": "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearTwo",
    "due_year_3": "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearThree",
    "due_year_4": "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearFour",
    "due_year_5": "LongTermDebtMaturitiesRepaymentsOfPrincipalInYearFive",
    "due_after_5": "LongTermDebtMaturitiesRepaymentsOfPrincipalAfterYearFive",
    "cash": "CashAndCashEquivalentsAtCarryingValue",
    "debt_combined": "DebtLongtermAndShorttermCombinedAmount",
    "notes_and_loans_noncurrent": "LongTermNotesAndLoans",
    "notes_payable_current": "NotesPayableCurrent",
    "debt_incl_finance_leases": "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities",
}
# Total debt, first match wins; each entry is (basis label, keys summed). Filers name it differently.
TOTAL_DEBT_CHAIN = [
    ("LongTermDebt", ("long_term_debt",)),
    ("DebtLongtermAndShorttermCombinedAmount", ("debt_combined",)),
    ("LongTermDebtNoncurrent + current", ("long_term_debt_noncurrent", "long_term_debt_current|debt_current")),
    ("LongTermNotesAndLoans + NotesPayableCurrent", ("notes_and_loans_noncurrent", "notes_payable_current")),
    ("debt incl. finance leases", ("debt_incl_finance_leases",)),
    ("DebtInstrumentCarryingAmount (undimensioned)", ("carrying_total",)),
]
ADSH = re.compile(r"^\d{10}-\d{2}-\d{6}$")


@dataclass
class Instrument:
    member: str
    axis: str
    label: str | None
    custom: bool
    klass: str                     # bond | offering | facility | category | other | component (P38)
    kind: str | None
    outstanding: bool
    outstanding_from: str | None = None   # "balance at period end" | "face at period end"
    rate: float | None = None      # stated coupon, percent, as tagged
    rate_dcml: str | None = None
    rate_from: str | None = None   # "tagged" | "parsed" — where the coupon came from
    maturity_year: int | None = None
    maturity_from: str | None = None
    face: float | None = None
    carrying: float | None = None
    capacity: float | None = None
    currency: str | None = None    # the bond's own currency (P8)
    currency_from: str | None = None  # "label" | "face" (reliable) | "carrying" (may be a USD translation)
    amount_uom: str | None = None  # the unit the face/carrying amounts are stated in
    floating: bool = False
    amount_usd: float | None = None   # carrying (else face) in USD, for coverage against total debt
    face_uom: str | None = None       # currency the face amount is stated in
    carrying_uom: str | None = None   # currency the carrying amount is stated in
    issued: str | None = None         # offerings only: issue period 'YYYY-MM' or 'YYYY' (L2 grading)
    tags: list[str] = field(default_factory=list)
    parse_notes: list[str] = field(default_factory=list)

    def key(self):
        if self.klass != "bond" or self.rate is None or self.maturity_year is None:
            return None
        return (self.currency or "USD", round(self.rate, 3), self.maturity_year)


def _axes(segments: str) -> dict[str, str]:
    return dict(p.split("=", 1) for p in segments.split(";") if "=" in p)


class AnswerKey:
    """The debt facts of a set of filers across a set of notes-data periods."""

    def __init__(self, periods: list[str], ciks: set[int] | None = None):
        self.subs: dict[str, dict] = {}
        self.num: dict[str, list[dict]] = defaultdict(list)
        self.txt: dict[str, list[dict]] = defaultdict(list)
        self.dims: dict[str, str] = {}
        self.labels: dict[tuple[str, str], str] = {}
        self.std_labels: dict[str, str] = {}
        wanted = {str(c) for c in ciks} if ciks else None
        for p in periods:
            d = month_dir(p)
            if not (d / "_complete").exists():
                raise FileNotFoundError(f"notes period {p} not extracted (run: python -m ai_debt_tracker.eval.fsn)")
            new = set()
            for r in read_tsv(d / "sub.tsv"):
                if wanted is None or r["cik"] in wanted:
                    r["period_label"] = p
                    self.subs[r["adsh"]] = r
                    new.add(r["adsh"])
            for r in read_tsv(d / "dim.tsv"):
                self.dims[r["dimhash"]] = r["segments"]
            for r in read_tsv(d / "labels.tsv"):
                if ADSH.match(r["version"]):
                    if r["version"] in new:
                        self.labels[(r["tag"], r["version"])] = r["tlabel"]
                else:
                    self.std_labels.setdefault(r["tag"], r["tlabel"])
            for r in read_tsv(d / "num.tsv.gz"):
                if r["adsh"] in new and r["value"] not in ("", None):  # nil facts carry no value
                    self.num[r["adsh"]].append(r)
            for r in read_tsv(d / "txt.tsv.gz"):
                if r["adsh"] in new:
                    self.txt[r["adsh"]].append(r)

    # ---- filings ---------------------------------------------------------------------------
    def reports(self, cik: int) -> list[dict]:
        """10-K / 10-Q filings of a company, oldest first. When an amendment exists for the same
        period, the latest-accepted version wins (P13) — unless it carries no debt facts at all
        (many 10-Q/As only refile an exhibit), in which case the last version that does wins."""
        by_period = {}
        for s in sorted((s for s in self.subs.values() if s["cik"] == str(cik)), key=lambda s: s["accepted"]):
            if s["period"] not in by_period or self.num.get(s["adsh"]):
                by_period[s["period"]] = s
        return sorted(by_period.values(), key=lambda s: s["period"])

    # ---- one filing ------------------------------------------------------------------------
    def instruments(self, adsh: str) -> tuple[list[Instrument], dict]:
        sub = self.subs[adsh]
        period, year = sub["period"], int(sub["period"][:4])
        facts = defaultdict(lambda: defaultdict(list))  # (axis, member) -> tag -> [(n_axes, segments, row)]
        skipped = defaultdict(int)
        for r in self.num.get(adsh, []):
            seg = self.dims.get(r["dimh"])
            if seg is None:
                continue
            if r["coreg"]:
                skipped["co-registrant fact"] += 1
                continue
            axes = _axes(seg)
            extra = set(axes) - DESCRIPTIVE_AXES
            if extra:
                skipped["non-descriptive axis: " + ",".join(sorted(extra))[:60]] += 1
                continue
            ident = self._identity(axes, adsh)
            if ident is None:
                skipped["category only"] += 1
                continue
            facts[ident][r["tag"]].append((len(axes), seg, r))
        maturities = {}
        for r in self.txt.get(adsh, []):
            seg = self.dims.get(r["dimh"])
            if seg and not r["coreg"] and r["tag"] == "DebtInstrumentMaturityDate":
                ident = self._identity(_axes(seg), adsh)
                m = re.search(r"(20\d\d|19\d\d)", r["value"])
                if ident and m:
                    maturities[ident] = int(m.group(1))

        out = []
        for (axis, member), by_tag in facts.items():
            label = self.labels.get((member + "Member", adsh)) or self.std_labels.get(member + "Member")
            custom = (member + "Member", adsh) in self.labels
            parsed = parse_member(member, label, as_of_year=year, as_of_month=int(period[:6]))

            def pick(tag, at_period=True):
                rows = by_tag.get(tag, [])
                if at_period:
                    rows = [x for x in rows if x[2]["ddate"] == period and x[2]["qtrs"] == "0"]
                if not rows:
                    return None, None
                n, seg, r = min(rows, key=lambda x: (x[0], len(x[1]), -float(x[2]["value"] or 0)))
                return float(r["value"]), r

            rate, rate_row = pick("DebtInstrumentInterestRateStatedPercentage", at_period=False)
            face, face_row = pick("DebtInstrumentFaceAmount")
            if face is None:
                face, face_row = pick("DebtInstrumentFaceAmount", at_period=False)
            carrying, crow = None, None
            for t in CARRYING_ORDER:
                carrying, crow = pick(t)
                if carrying is not None:
                    break
            capacity, _ = pick("LineOfCreditFacilityMaximumBorrowingCapacity", at_period=False)
            dated = lambda x: x[2]["ddate"] == period and x[2]["qtrs"] == "0"  # noqa: E731
            balances = [float(x[2]["value"] or 0) for t in BALANCE_TAGS for x in by_tag.get(t, []) if dated(x)]
            if any(v > 0 for v in balances):
                outstanding, outstanding_from = True, "balance at period end"
            elif balances:
                # an explicit zero balance means repaid: Oracle tags its repaid July/November 2024 notes
                # with carrying 0 *and* their original $2 bn face at the period end (Week 2 hand-check)
                outstanding, outstanding_from = False, "zero balance at period end"
            elif any(dated(x) and float(x[2]["value"] or 0) > 0 for x in by_tag.get("DebtInstrumentFaceAmount", [])):
                outstanding, outstanding_from = True, "face at period end (no balance tagged)"
            else:
                outstanding, outstanding_from = False, None
            if crow is not None and crow["uom"] == "USD" and carrying:
                amount_usd = carrying
            elif face_row is not None and face_row["uom"] == "USD" and face:
                amount_usd = face
            else:
                amount_usd = None
            if rate is not None and rate < 1:
                rate = rate * 100  # stored as a fraction (0.0613) by most filers
            rate_from = "tagged" if rate is not None else ("parsed" if parsed.rate is not None else None)
            if rate is not None and parsed.rate is not None and rates_match(rate, parsed.rate) \
                    and (parsed.rate_digits or 0) > len(f"{rate:.4f}".rstrip("0").split(".")[1]):
                # P17: the bulk data stores 9.625% as 9.63; the filer's own name/label keeps 9.625
                rate, rate_from = parsed.rate, "parsed (tagged value rounded, P17)"
            unit_row = face_row or (crow if carrying is not None else None)
            amount_uom = unit_row["uom"] if unit_row else None
            # the bond's currency: named in the label/name (Equinix reports its euro notes in USD),
            # else the unit its face amount is stated in
            currency = parsed.currency or (face_row["uom"] if face_row else None) or amount_uom
            # Known only from the label or the face amount's unit. A carrying amount is often a
            # translation into dollars: Equinix's 2.875% 2028 notes are Swiss franc notes whose label
            # never says so and whose only amount is a USD carrying value (Week 2 hand-check).
            currency_from = "label" if parsed.currency else "face" if face_row else "carrying" if amount_uom else None
            if currency_from == "face" and crow is not None and crow["uom"] != face_row["uom"]:
                # P36: face and carrying tagged in different units with no currency in the label —
                # Digital Realty tags its *dollar* exchangeable notes' face in euros. Neither unit can
                # be trusted, so the currency is unknown and does not block a match.
                currency_from = "conflict"
            mat = maturities.get((axis, member))

            plain = re.sub(r"\[member\]|\bmember\b", "", label or "", flags=re.I).strip(" ,")
            if parsed.kind is None and BUCKET.match(plain or split_camel(member)):
                klass = "bucket"
            elif parsed.offering and mat is None:
                klass = "offering"
            elif parsed.kind in ("other_debt", "finance_lease"):
                klass = "other"
            elif parsed.kind in FACILITY_KINDS or capacity is not None and parsed.kind not in ("notes", "convertible"):
                klass = "facility"
            elif parsed.kind in ("notes", "convertible") or (rate is not None and (mat or parsed.maturity_year)):
                klass = "bond"
            elif axis != "DebtInstrument" and not custom:
                klass = "category"
            else:
                klass = "other"
            inst = Instrument(
                member=member, axis=axis, label=label, custom=custom, klass=klass, kind=parsed.kind,
                outstanding=outstanding, outstanding_from=outstanding_from,
                rate=round(rate, 4) if rate is not None else parsed.rate,
                rate_dcml=rate_row["dcml"] if rate_row else None,
                rate_from=rate_from,
                maturity_year=mat or parsed.maturity_year,
                maturity_from="tagged" if mat else ("parsed" if parsed.maturity_year else None),
                face=face, carrying=carrying, capacity=capacity,
                currency=currency, currency_from=currency_from, amount_uom=amount_uom, floating=parsed.floating,
                amount_usd=amount_usd,
                face_uom=face_row["uom"] if face_row else None, carrying_uom=crow["uom"] if crow else None,
                issued=issue_period(member, label) if klass == "offering" else None,
                tags=sorted(by_tag), parse_notes=parsed.notes,
            )
            out.append(inst)
        # P35: a bond known only by a face amount dated at the period end, in a report that tags
        # balances for its other debt, and due by the report's own year, has almost certainly been
        # repaid — Digital Realty's £400 m 4.250% notes (due Jan 2025) in its June 2025 10-Q, UPS's
        # 2022 notes in its 2023 10-K. Face-only bonds due later are kept: new issues are often
        # tagged only by face in the narrative (Mastercard's 2028/2032/2035 notes, Sep 2024).
        if any(i.outstanding_from == "balance at period end" for i in out):
            for i in out:
                if (i.outstanding and (i.outstanding_from or "").startswith("face") and i.maturity_year
                        and i.maturity_year <= year):
                    i.outstanding = False
                    i.outstanding_from = "face only, due by the report year, balances tagged elsewhere (P35)"
        # P38: the banks' over-allotment option is part of its base bond, not a second bond. Super
        # Micro tags "Convertible Senior Notes Due 2030, Overallotment Option" ($300 m) beside the
        # 2030 notes, whose $2.3 bn already includes it (Week 3 fresh held-out check). A member named
        # for an over-allotment (or greenshoe) with a base bond of the same maturity year is a component.
        for i in out:
            text = f"{i.member} {i.label or ''}"
            if i.klass == "bond" and OVERALLOTMENT.search(text):
                base = [b for b in out if b is not i and b.klass == "bond" and not OVERALLOTMENT.search(f"{b.member} {b.label or ''}")
                        and b.maturity_year == i.maturity_year and b.maturity_year is not None]
                if base:
                    i.klass = "component"
                    i.parse_notes = i.parse_notes + [f"over-allotment of {base[0].member} (P38)"]
        out.sort(key=lambda i: (i.klass, i.maturity_year or 0, i.rate or 0, i.member))
        return out, dict(skipped)

    def totals(self, adsh: str) -> dict:
        sub = self.subs[adsh]
        vals = {}
        for r in self.num.get(adsh, []):
            if r["dimh"] != NO_DIMS or r["coreg"] or r["ddate"] != sub["period"] or r["qtrs"] != "0":
                continue
            for k, tag in TOTALS.items():
                if r["tag"] == tag and r["uom"] == "USD":
                    vals[k] = float(r["value"])
        return vals

    def _identity(self, axes: dict, adsh: str):
        if "DebtInstrument" in axes:
            return ("DebtInstrument", axes["DebtInstrument"])
        for ax in IDENTITY_AXES[1:]:
            if ax in axes and (axes[ax] + "Member", adsh) in self.labels:
                return (ax, axes[ax])
        if "CreditFacility" in axes:  # a standard member alone ("RevolvingCreditFacility") is still one facility
            return ("CreditFacility", axes["CreditFacility"])
        return None

    def filing_record(self, adsh: str) -> dict:
        sub = self.subs[adsh]
        insts, skipped = self.instruments(adsh)
        return {
            "adsh": adsh, "cik": int(sub["cik"]), "name": sub["name"], "form": sub["form"], "period": sub["period"],
            "accepted": sub["accepted"], "fsn_period": sub["period_label"], "co_registrants": sub.get("aciks", ""),
            "totals": self.totals(adsh), "skipped_facts": skipped,
            "instruments": [asdict(i) | {"key": i.key()} for i in insts],
        }


def level_counts(record: dict) -> dict:
    """How finely one filing tags its debt: outstanding instruments by class, and how many bonds
    carry a full match key."""
    out = defaultdict(int)
    for i in record["instruments"]:
        if not i["outstanding"]:
            continue
        out[i["klass"]] += 1
        if i.get("key"):
            out["bond_keyed"] += 1
    return dict(out)


def grading_level(record: dict) -> dict:
    """The finest level one report supports, and the evidence (DESIGN.md §9.1, P2, P18, P19).

    Counting members is not enough: Oracle's 10-Qs tag only the handful of bonds issued that
    quarter (4–14 of ~56), so "≥ 2 bonds tagged" would call a partial list per-bond. The test is
    **coverage**: the USD amount of the itemised instruments divided by the company's total debt.

      L1  ≥ 2 itemised instruments (bonds with a maturity, facilities, other loans — not offerings
          or maturity buckets), covering ≥ 80% of total debt (offering members tagged alongside,
          as Broadcom does, do not count against it);
      L2  ≥ 2 itemised-or-offering members covering ≥ 80% of total debt;
      L3  otherwise — totals only.

    Total debt follows `TOTAL_DEBT_CHAIN` (filers name it differently — Oracle reports
    LongTermNotesAndLoans + NotesPayableCurrent). When a report tags none of them, the denominator
    falls back to the sum of all outstanding tagged amounts and the basis says so (a weaker check:
    it cannot see untagged debt).

    A member worth half or more of total debt is an aggregate ("Senior Notes And Other Long Term
    Borrowings", $125 bn at Oracle), not an instrument, and never counts as itemised.
    """
    tot = record["totals"]
    total, basis = None, None
    for label, keys in TOTAL_DEBT_CHAIN:
        if not tot.get(keys[0]):
            continue
        total = tot[keys[0]] + sum(next((tot[k] for k in alt.split("|") if tot.get(k)), 0) for alt in keys[1:])
        basis = label
        break
    outs = [i for i in record["instruments"] if i["outstanding"] and i["amount_usd"]]
    offerings = [i for i in outs if i["klass"] == "offering"]
    candidates = [i for i in outs if i["klass"] in ("bond", "facility", "other")
                  and (i["klass"] != "bond" or i["maturity_year"] is not None)]
    if not total:
        # Only instruments and offerings: subtotals such as Digital Realty's $16 bn "Unsecured
        # senior notes" (a bond member with no maturity) would double-count what they sum.
        total = sum(i["amount_usd"] for i in candidates) or sum(i["amount_usd"] for i in offerings)
        basis = "sum of tagged instruments (no total tagged; coverage not independently measured)"
    measured = not basis.startswith("sum of tagged")
    aggregate = lambda i: total and i["amount_usd"] >= 0.5 * total and (measured or len(outs) > 1)  # noqa: E731
    itemised = [i for i in candidates if not (i["klass"] == "other" and aggregate(i))]
    amt = lambda xs: sum(i["amount_usd"] for i in xs)  # noqa: E731
    cov_item = amt(itemised) / total if total else 0.0
    cov_off = amt(offerings) / total if total else 0.0
    if len(itemised) >= 2 and cov_item >= L1_COVERAGE:  # Broadcom tags bonds *and* offerings: still L1
        level = "L1"
    elif len(itemised) + len(offerings) >= 2 and cov_item + cov_off >= L1_COVERAGE:
        level = "L2"
    else:
        level = "L3"
    return {"level": level, "counts": level_counts(record), "itemised": len(itemised), "offerings": len(offerings),
            "coverage_itemised": round(cov_item, 3), "coverage_offerings": round(cov_off, 3),
            "total_debt": total, "total_basis": basis}
