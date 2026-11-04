"""
conformance.py — GIGO stage (gate G2) of the insider-signal-agent recipe.

Checks the parsed buys against the raw SEC tables and promotes them to data/verified/ only
when every halting check passes.

Halting checks (verification stack, layer 1). Any failure → exit 1, nothing in data/verified/
changes, and the failure audit goes to data/raw/conformance/ instead.
    hash              ZIP, extracted folder and parse summary all carry the manifest's SHA-256
    required_columns  every field named in DATA_CONTRACT.md is in each raw table's header
                      (AFF10B5ONE included: the study period is 2023+); the parsed CSV has
                      exactly parse.OUTPUT_COLUMNS
    keys              ACCESSION_NUMBER non-null in every table; (ACCESSION_NUMBER,
                      NONDERIV_TRANS_SK) unique in NONDERIV_TRANS and in the buys file
    dates             for every buy to be promoted, raw FILING_DATE and TRANS_DATE are
                      DD-MON-YYYY and TRANS_DATE ≤ FILING_DATE
    codes             for every buy, raw TRANS_CODE is in SEC's list and
                      TRANS_ACQUIRED_DISP_CD is A or D
    buy_filter_purity every buys-file row meets the buy filter on its own fields; it matches its
                      raw source row; and the set of raw rows meeting the filter (re-derived
                      here, independently of parse.classify) equals the buys file exactly
    identity          ISSUERCIK and every RPTOWNERCIK non-null and numeric; ≥ 1 owner per buy

Date and code checks apply to the rows being promoted. Problems in rows that are not buys
(e.g. a sale dated after its filing) are reported in the audit, not halted on: they never
enter data/verified/.

Findings (layer 2, the audit; reported, never halted on): rows in/out, exclusions by reason and
code, the effect of PRE_REGISTRATION.md Rule 1, amendments, blank symbols, late filings,
joint filings, the TRANS_DATE → FILING_DATE lag, and the filing spot-check.

Spot-check: N buys (default 25) drawn at random with a seed derived from the source ZIP
hashes, so the sample cannot be hand-picked and can be reproduced. Each filing's full text
(<accession>.txt in EDGAR Archives) is fetched through ingest.SecClient (SEC_USER_AGENT
required, 1 request/second, logged) and its Form 4 XML is compared with the data set on
code, shares, price and date. Mismatches are listed for the human; nothing is corrected.
Fetched filings are cached in data/raw/filings/ and not fetched again. If SEC refuses
(403/429 after backoff) the run halts (exit 3) and nothing is promoted.

Outputs on pass (data/verified/)
    insider_buys.csv           one row per qualifying buy, with its flags (VERIFIED_COLUMNS)
    conformance-audit.md       the audit (human customer)
    conformance_summary.json   every check, count and spot-check row (machine customer)

Exit codes: 0 promoted · 1 halting check failed · 2 configuration refused · 3 halted by SEC.

Usage
    SEC_USER_AGENT="Name email" python conformance.py --quarters 2026q3
    python conformance.py --quarters 2026q3 --no-spot-check     # offline; audit says NOT RUN
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import random
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path
from typing import Callable, Iterable, Mapping

import ingest
import parse

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = ingest.DEFAULT_DATA_DIR
DEFAULT_PARSED_DIR = parse.DEFAULT_OUT_DIR
DEFAULT_VERIFIED_DIR = ROOT / "data" / "verified"
DEFAULT_STAGING_DIR = ROOT / "data" / "raw" / "conformance"
DEFAULT_FILINGS_DIR = ROOT / "data" / "raw" / "filings"
SPOT_CHECK_N = 25
EDGAR_ARCHIVES = "https://www.sec.gov/Archives/edgar/data"

BUYS_NAME = "insider_buys.csv"
AUDIT_NAME = "conformance-audit.md"
SUMMARY_NAME = "conformance_summary.json"

# Fields DATA_CONTRACT.md says this module uses, per raw table (written out here on purpose,
# not imported from parse.py, so the gate checks the contract rather than the parser).
CONTRACT_FIELDS = {
    "SUBMISSION": ["ACCESSION_NUMBER", "FILING_DATE", "PERIOD_OF_REPORT", "DATE_OF_ORIG_SUB",
                   "DOCUMENT_TYPE", "ISSUERCIK", "ISSUERNAME", "ISSUERTRADINGSYMBOL",
                   "AFF10B5ONE"],
    "REPORTINGOWNER": ["ACCESSION_NUMBER", "RPTOWNERCIK", "RPTOWNERNAME",
                       "RPTOWNER_RELATIONSHIP", "RPTOWNER_TITLE", "RPTOWNER_TXT"],
    "NONDERIV_TRANS": ["ACCESSION_NUMBER", "NONDERIV_TRANS_SK", "SECURITY_TITLE", "TRANS_DATE",
                       "DEEMED_EXECUTION_DATE", "TRANS_FORM_TYPE", "TRANS_CODE",
                       "EQUITY_SWAP_INVOLVED", "TRANS_TIMELINESS", "TRANS_SHARES",
                       "TRANS_PRICEPERSHARE", "TRANS_ACQUIRED_DISP_CD", "SHRS_OWND_FOLWNG_TRANS",
                       "DIRECT_INDIRECT_OWNERSHIP", "NATURE_OF_OWNERSHIP"],
    "FOOTNOTES": ["ACCESSION_NUMBER", "FOOTNOTE_ID", "FOOTNOTE_TXT"],
}
SEC_TRANS_CODES = frozenset("A C D E F G H I J L M O P S U W X Z".split())
FORM4_TYPES = frozenset({"4", "4/A"})
_SEC_DATE = re.compile(r"^\d{2}-[A-Za-z]{3}-\d{4}$")
_CIK = re.compile(r"^\d{1,10}$")
_SWAP_TRUE = {"1", "true", "t", "y", "yes"}

VERIFIED_COLUMNS = [
    "accession_number", "nonderiv_trans_sk", "document_type", "filing_date", "trans_date",
    "period_of_report", "date_of_orig_sub", "issuer_cik", "issuer_name", "ticker_as_filed",
    "owner_count", "rptowner_ciks", "rptowner_names", "relationships", "titles", "owners",
    "security_title", "trans_code", "acquired_disposed", "equity_swap", "shares", "price",
    "value_usd", "shares_owned_after", "direct_indirect", "nature_of_ownership",
    "trans_timeliness", "is_10b5_1", "private_purchase_flag", "espp_or_drip_flag",
    "flag_evidence", "footnote_mentions_10b5_1", "source_quarter", "filing_index_url",
]
HALTING_CHECKS = ("hash", "required_columns", "keys", "dates", "codes", "buy_filter_purity",
                  "identity")


class ConformanceError(Exception):
    """Inputs missing or unreadable (exit 1)."""


# --------------------------------------------------------------------------- small helpers

def dec(value: str | None) -> Decimal | None:
    v = (value or "").strip().replace(",", "")
    if not v:
        return None
    try:
        d = Decimal(v)
    except InvalidOperation:
        return None
    return d if d.is_finite() else None


def sec_date(value: str | None) -> date | None:
    """Strict DD-MON-YYYY → date; None if it does not have that form."""
    v = (value or "").strip()
    if not _SEC_DATE.match(v):
        return None
    try:
        return datetime.strptime(v.title(), "%d-%b-%Y").date()
    except ValueError:
        return None


def meets_buy_filter(doc_type: str, code: str, acquired: str, shares: str, price: str,
                     equity_swap: str) -> bool:
    """The recipe's buy filter, written independently of parse.classify."""
    s, p = dec(shares), dec(price)
    return (doc_type.strip() in FORM4_TYPES and code.strip().upper() == "P"
            and acquired.strip().upper() == "A" and s is not None and s > 0
            and p is not None and p > 0 and equity_swap.strip().lower() not in _SWAP_TRUE)


DATASET_DECIMALS = Decimal("0.01")   # SEC's data set carries at most 2 decimals (see the audit)


def rounds_to(dataset: Decimal | None, filed: Decimal | None) -> bool:
    """True if the filed value, rounded half-up to 2 decimals, equals the data-set value."""
    if dataset is None or filed is None:
        return False
    return filed.quantize(DATASET_DECIMALS, rounding=ROUND_HALF_UP) == dataset


def business_days(start: date, end: date) -> int:
    """Weekdays after `start` up to and including `end` (no holiday calendar)."""
    n, d = 0, start
    while d < end:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def percentile(sorted_values: list[int], q: float) -> int | None:
    if not sorted_values:
        return None
    k = max(0, min(len(sorted_values) - 1, round(q * (len(sorted_values) - 1))))
    return sorted_values[k]


def filing_url(cik: str, accession: str, filename: str = "") -> str:
    return f"{EDGAR_ARCHIVES}/{int(cik)}/{accession.replace('-', '')}/{filename}"


def _check(name: str, problems: list[str], detail: str = "", not_run: str = "") -> dict:
    return {"name": name, "passed": not problems and not not_run, "violations": len(problems),
            "examples": problems[:5], "detail": detail, "not_run": not_run}


def _header(path: Path) -> list[str]:
    with open(path, newline="", encoding="utf-8") as fh:
        first = fh.readline().rstrip("\r\n")
    return [h.strip() for h in first.split("\t")] if first else []


# --------------------------------------------------------------------------- one quarter

def check_quarter(data_dir: Path, parsed_dir: Path, quarter: str) -> dict:
    """Run every halting check on one quarter. Returns checks, promotable rows and findings."""
    checks: dict[str, dict] = {}
    folder = data_dir / quarter

    # hash ---------------------------------------------------------------------------------
    problems: list[str] = []
    entry = ingest.load_manifest(data_dir)["quarters"].get(quarter)
    sha = entry.get("sha256") if entry else None
    if not entry:
        problems.append(f"{quarter}: no manifest.json entry")
    else:
        zp = ingest.zip_path(data_dir, quarter)
        if not zp.exists():
            problems.append(f"{zp.name} is missing; the hash cannot be checked")
        elif ingest.sha256_file(zp) != sha:
            problems.append(f"{zp.name} SHA-256 does not match manifest.json")
        marker = folder / ingest.EXTRACT_MARKER
        if not marker.exists():
            problems.append(f"{quarter}/{marker.name} missing (folder not extracted by ingest.py)")
        elif json.loads(marker.read_text(encoding="utf-8")).get("sha256") != sha:
            problems.append(f"{quarter}/ was extracted from a different ZIP than manifest.json")
    summary_path = parsed_dir / f"{quarter}_parse_summary.json"
    parse_summary: dict = {}
    if not summary_path.exists():
        problems.append(f"{summary_path.name} missing; run parse.py first")
    else:
        parse_summary = json.loads(summary_path.read_text(encoding="utf-8"))
        if sha and parse_summary.get("source_sha256") != sha:
            problems.append(f"{summary_path.name} was produced from a different ZIP")
    checks["hash"] = _check("hash", problems, f"manifest SHA-256 {sha or 'n/a'}")

    # required columns ----------------------------------------------------------------------
    problems = []
    for table, fields in CONTRACT_FIELDS.items():
        path = folder / f"{table}.tsv"
        if not path.exists():
            problems.append(f"{table}.tsv missing")
            continue
        missing = [f for f in fields if f not in _header(path)]
        if missing:
            problems.append(f"{table}.tsv lacks {missing}")
    csv_path = parsed_dir / f"{quarter}_form4_transactions.csv"
    if not csv_path.exists():
        problems.append(f"{csv_path.name} missing; run parse.py first")
    else:
        with open(csv_path, newline="", encoding="utf-8") as fh:
            got = next(csv.reader(fh), [])
        if got != parse.OUTPUT_COLUMNS:
            problems.append(f"{csv_path.name} columns differ from parse.OUTPUT_COLUMNS")
    checks["required_columns"] = _check("required_columns", problems,
                                        "DATA_CONTRACT.md fields in 4 raw tables + parsed CSV header")

    if problems or not checks["hash"]["passed"]:
        why = "an input check (hash or required_columns) failed"
        for name in HALTING_CHECKS[2:]:
            checks[name] = _check(name, [], not_run=why)
        return {"quarter": quarter, "sha256": sha, "checks": checks, "rows": [],
                "findings": {}, "parse_summary": parse_summary}

    # read raw tables ----------------------------------------------------------------------
    try:
        subs = {}
        acc_null = Counter()
        _, it = parse.read_table(folder, "SUBMISSION")
        for r in it:
            if not r["ACCESSION_NUMBER"].strip():
                acc_null["SUBMISSION"] += 1
            subs[r["ACCESSION_NUMBER"].strip()] = r
        owners_raw: dict[str, list[dict]] = defaultdict(list)
        _, it = parse.read_table(folder, "REPORTINGOWNER")
        for r in it:
            if not r["ACCESSION_NUMBER"].strip():
                acc_null["REPORTINGOWNER"] += 1
            owners_raw[r["ACCESSION_NUMBER"].strip()].append(r)
        _, it = parse.read_table(folder, "FOOTNOTES")
        for r in it:
            if not r["ACCESSION_NUMBER"].strip():
                acc_null["FOOTNOTES"] += 1
        nd: dict[tuple[str, str], dict] = {}
        nd_dupes: list[str] = []
        _, it = parse.read_table(folder, "NONDERIV_TRANS")
        for r in it:
            acc = r["ACCESSION_NUMBER"].strip()
            if not acc:
                acc_null["NONDERIV_TRANS"] += 1
            k = (acc, r["NONDERIV_TRANS_SK"].strip())
            if k in nd:
                nd_dupes.append(f"duplicate key {k}")
            nd[k] = r
    except parse.ParseError as err:
        raise ConformanceError(f"{quarter}: {err}") from err

    with open(csv_path, newline="", encoding="utf-8") as fh:
        parsed = [r for r in csv.DictReader(fh) if r["buy_class"] == parse.QUALIFYING]

    # keys ---------------------------------------------------------------------------------
    problems = [f"{t}: {n} row(s) with blank ACCESSION_NUMBER" for t, n in acc_null.items() if n]
    problems += nd_dupes
    seen: set[tuple[str, str]] = set()
    for r in parsed:
        k = (r["accession_number"], r["nonderiv_trans_sk"])
        if k in seen:
            problems.append(f"buys file: duplicate key {k}")
        seen.add(k)
    checks["keys"] = _check("keys", problems, f"{len(nd):,} NONDERIV_TRANS keys, {len(parsed):,} buys")

    # dates, codes, identity, purity (row by row) --------------------------------------------
    p_dates, p_codes, p_ident, p_pure = [], [], [], []
    rows = []
    for r in parsed:
        k = (r["accession_number"], r["nonderiv_trans_sk"])
        raw, sub = nd.get(k), subs.get(r["accession_number"])
        tag = f"{k[0]} sk {k[1]}"
        if raw is None or sub is None:
            p_pure.append(f"{tag}: not found in the raw tables")
            continue
        fd, td = sec_date(sub["FILING_DATE"]), sec_date(raw["TRANS_DATE"])
        if fd is None or td is None:
            p_dates.append(f"{tag}: FILING_DATE {sub['FILING_DATE']!r} / TRANS_DATE "
                           f"{raw['TRANS_DATE']!r} not DD-MON-YYYY")
        elif td > fd:
            p_dates.append(f"{tag}: TRANS_DATE {td} after FILING_DATE {fd}")
        code = raw["TRANS_CODE"].strip().upper()
        if code not in SEC_TRANS_CODES:
            p_codes.append(f"{tag}: TRANS_CODE {code!r} not in SEC's list")
        if raw["TRANS_ACQUIRED_DISP_CD"].strip().upper() not in ("A", "D"):
            p_codes.append(f"{tag}: TRANS_ACQUIRED_DISP_CD {raw['TRANS_ACQUIRED_DISP_CD']!r}")
        if not _CIK.match(sub["ISSUERCIK"].strip()):
            p_ident.append(f"{tag}: ISSUERCIK {sub['ISSUERCIK']!r}")
        raw_owner_ciks = [o["RPTOWNERCIK"].strip() for o in owners_raw.get(k[0], [])]
        if not raw_owner_ciks:
            p_ident.append(f"{tag}: no REPORTINGOWNER row")
        for c in raw_owner_ciks:
            if not _CIK.match(c):
                p_ident.append(f"{tag}: RPTOWNERCIK {c!r}")
        owners = json.loads(r["owners"])
        # purity: the row on its own fields, and against its raw source
        if not meets_buy_filter(r["document_type"], r["trans_code"], r["acquired_disposed"],
                                r["shares"], r["price"], r["equity_swap"]):
            p_pure.append(f"{tag}: buys-file row fails the buy filter")
        if not meets_buy_filter(sub["DOCUMENT_TYPE"], raw["TRANS_CODE"],
                                raw["TRANS_ACQUIRED_DISP_CD"], raw["TRANS_SHARES"],
                                raw["TRANS_PRICEPERSHARE"], raw["EQUITY_SWAP_INVOLVED"]):
            p_pure.append(f"{tag}: raw source row fails the buy filter")
        diffs = [f for f, a, b in (
            ("shares", dec(r["shares"]), dec(raw["TRANS_SHARES"])),
            ("price", dec(r["price"]), dec(raw["TRANS_PRICEPERSHARE"])),
            ("trans_date", r["trans_date"], td.isoformat() if td else ""),
            ("filing_date", r["filing_date"], fd.isoformat() if fd else ""),
            ("issuer_cik", r["issuer_cik"], sub["ISSUERCIK"].strip()),
            ("document_type", r["document_type"], sub["DOCUMENT_TYPE"].strip()),
            ("owners", [o["cik"] for o in owners], raw_owner_ciks)) if a != b]
        if diffs:
            p_pure.append(f"{tag}: differs from raw on {diffs}")
        rows.append(_verified_row(r, owners))

    raw_buy_keys = {k for k, raw in nd.items() if k[0] in subs and meets_buy_filter(
        subs[k[0]]["DOCUMENT_TYPE"], raw["TRANS_CODE"], raw["TRANS_ACQUIRED_DISP_CD"],
        raw["TRANS_SHARES"], raw["TRANS_PRICEPERSHARE"], raw["EQUITY_SWAP_INVOLVED"])}
    missing = sorted(raw_buy_keys - seen)
    extra = sorted(seen - raw_buy_keys)
    p_pure += [f"raw buy {k} missing from the buys file" for k in missing]
    p_pure += [f"buys-file row {k} is not a buy in the raw tables" for k in extra]

    checks["dates"] = _check("dates", p_dates, "promoted rows: DD-MON-YYYY, TRANS_DATE ≤ FILING_DATE")
    checks["codes"] = _check("codes", p_codes, "promoted rows: SEC code list, A/D")
    checks["buy_filter_purity"] = _check(
        "buy_filter_purity", p_pure,
        f"independent filter on raw: {len(raw_buy_keys):,} buys; buys file: {len(seen):,}")
    checks["identity"] = _check("identity", p_ident, "ISSUERCIK and RPTOWNERCIK, numeric")

    findings = _findings(rows, subs, owners_raw, nd, parse_summary)
    return {"quarter": quarter, "sha256": sha, "checks": checks, "rows": rows,
            "findings": findings, "parse_summary": parse_summary}


def _verified_row(r: dict, owners: list[dict]) -> dict:
    return {
        **{c: r[c] for c in ("accession_number", "nonderiv_trans_sk", "document_type",
                             "filing_date", "trans_date", "period_of_report", "date_of_orig_sub",
                             "issuer_cik", "issuer_name", "ticker_as_filed", "owner_count",
                             "owners", "security_title", "trans_code", "shares", "price",
                             "value_usd", "shares_owned_after", "direct_indirect",
                             "nature_of_ownership", "trans_timeliness", "is_10b5_1",
                             "private_purchase_flag", "espp_or_drip_flag", "flag_evidence",
                             "footnote_mentions_10b5_1", "source_quarter")},
        "acquired_disposed": r["acquired_disposed"],
        "equity_swap": r["equity_swap"],
        "rptowner_ciks": ";".join(o["cik"] for o in owners),
        "rptowner_names": ";".join(o["name"] for o in owners),
        "relationships": r["relationships"],
        "titles": ";".join(sorted({o["title"] for o in owners if o["title"]})),
        "filing_index_url": filing_url(r["issuer_cik"], r["accession_number"]),
    }


# --------------------------------------------------------------------------- findings

def _findings(rows: list[dict], subs: dict, owners_raw: dict, nd: dict, ps: dict) -> dict:
    f: dict = {}
    # Pre-registration Rule 1 (counts only; nothing about outcomes)
    excl = [r for r in rows if r["private_purchase_flag"] == "true" or r["espp_or_drip_flag"] == "true"]
    f["prereg_rule1"] = {
        "excluded_from_clustering": len(excl),
        "private_flag": sum(r["private_purchase_flag"] == "true" for r in rows),
        "espp_or_drip_flag": sum(r["espp_or_drip_flag"] == "true" for r in rows),
        "both_flags": sum(r["private_purchase_flag"] == "true" and r["espp_or_drip_flag"] == "true" for r in rows),
        "plan_buys_strong_ineligible": sum(r["is_10b5_1"] == "plan" and r["private_purchase_flag"] != "true"
                                           and r["espp_or_drip_flag"] != "true" for r in rows),
        "plan_buys_also_excluded": sum(r["is_10b5_1"] == "plan" for r in excl),
        "unknown_10b5_1": sum(r["is_10b5_1"] == "unknown" for r in rows),
        "cluster_eligible": len(rows) - len(excl),
    }
    # amendments
    owner_set = {acc: frozenset(o["RPTOWNERCIK"].strip() for o in os_) for acc, os_ in owners_raw.items()}
    originals = defaultdict(list)
    for acc, s in subs.items():
        if s["DOCUMENT_TYPE"].strip() == "4":
            originals[(s["ISSUERCIK"].strip(), owner_set.get(acc, frozenset()),
                       parse.iso_date(s["FILING_DATE"]))].append(acc)
    buys_by_acc = defaultdict(list)
    for r in rows:
        buys_by_acc[r["accession_number"]].append(r)
    am = [r for r in rows if r["document_type"] == "4/A"]
    am_accs = sorted({r["accession_number"] for r in am})
    match = Counter()
    dup_buys = 0
    for acc in am_accs:
        s = subs[acc]
        cands = originals.get((s["ISSUERCIK"].strip(), owner_set.get(acc, frozenset()),
                               parse.iso_date(s["DATE_OF_ORIG_SUB"])), [])
        match["no DATE_OF_ORIG_SUB" if not s["DATE_OF_ORIG_SUB"].strip() else
              "unique" if len(cands) == 1 else "multiple" if cands else "none_in_quarter"] += 1
        orig_buys = {(b["trans_date"], dec(b["shares"]), dec(b["price"]))
                     for c in cands for b in buys_by_acc.get(c, [])}
        dup_buys += sum((b["trans_date"], dec(b["shares"]), dec(b["price"])) in orig_buys
                        for b in buys_by_acc[acc])
    f["amendments"] = {"amendment_buys": len(am), "amendment_accessions": len(am_accs),
                       "original_candidates_in_quarter": dict(match),
                       "amendment_buys_repeating_an_original_buy": dup_buys}
    # symbols
    sym = Counter()
    sym_issuers = defaultdict(set)
    for r in rows:
        t = r["ticker_as_filed"].strip().upper()
        label = "blank" if not t else t if t in ("NONE", "N/A", "NA", "-", "--") else None
        if label:
            sym[label] += 1
            sym_issuers[label].add(r["issuer_cik"])
    f["symbols"] = {"buys": dict(sym), "issuers": {k: len(v) for k, v in sym_issuers.items()}}
    # timeliness and lag
    lags, bdays = [], []
    for r in rows:
        td, fd = date.fromisoformat(r["trans_date"]), date.fromisoformat(r["filing_date"])
        lags.append((fd - td).days)
        bdays.append(business_days(td, fd))
    lags.sort()
    buckets = Counter()
    for d in lags:
        buckets["0" if d == 0 else "1-2" if d <= 2 else "3-5" if d <= 5 else "6-30" if d <= 30
                else "31-365" if d <= 365 else ">365"] += 1
    f["timeliness"] = {
        "TRANS_TIMELINESS": dict(Counter(r["trans_timeliness"] or "<blank: on time>" for r in rows)),
        "more_than_2_business_days": sum(b > 2 for b in bdays),
        "more_than_2_business_days_and_not_marked_L": sum(
            b > 2 and r["trans_timeliness"] != "L" for b, r in zip(bdays, rows)),
    }
    f["lag_calendar_days"] = {
        "n": len(lags), "min": percentile(lags, 0), "p25": percentile(lags, .25),
        "median": percentile(lags, .5), "p75": percentile(lags, .75),
        "p90": percentile(lags, .9), "p99": percentile(lags, .99), "max": percentile(lags, 1),
        "buckets": {b: buckets[b] for b in ("0", "1-2", "3-5", "6-30", "31-365", ">365")},
    }
    # joint filings
    joint = [r for r in rows if int(r["owner_count"]) > 1]
    f["joint_filings"] = {
        "buys": len(joint), "accessions": len({r["accession_number"] for r in joint}),
        "owner_count_distribution": dict(sorted(Counter(int(r["owner_count"]) for r in rows).items())),
    }
    # whole-Form-4 anomalies outside the promoted rows (not halted on)
    late_dated = bad_dates = bad_codes = bad_ad = 0
    for (acc, _), raw in nd.items():
        s = subs.get(acc)
        if not s or s["DOCUMENT_TYPE"].strip() not in FORM4_TYPES:
            continue
        fd, td = sec_date(s["FILING_DATE"]), sec_date(raw["TRANS_DATE"])
        if fd is None or td is None:
            bad_dates += 1
        elif td > fd:
            late_dated += 1
        if raw["TRANS_CODE"].strip().upper() not in SEC_TRANS_CODES:
            bad_codes += 1
        if raw["TRANS_ACQUIRED_DISP_CD"].strip().upper() not in ("A", "D"):
            bad_ad += 1
    f["form4_rows_not_promoted"] = {"trans_date_after_filing_date": late_dated,
                                    "unparseable_dates": bad_dates,
                                    "code_blank_or_unrecognized": bad_codes,
                                    "acquired_disposed_not_A_or_D": bad_ad}
    prices = [dec(r["price"]) for r in rows]
    f["precision"] = {
        "max_decimals_price": max((-p.as_tuple().exponent for p in prices if p), default=0),
        "max_decimals_shares": max((-dec(r["shares"]).as_tuple().exponent for r in rows), default=0),
        "buys_price_below_1": sum(p < 1 for p in prices),
        "buys_price_at_most_0_05": sum(p <= Decimal("0.05") for p in prices),
    }
    f["parse"] = {"funnel": ps.get("funnel", {}), "exclusions_by_reason": ps.get("exclusions_by_reason", {})}
    return f


# --------------------------------------------------------------------------- spot-check

def spot_check_seed(shas: Iterable[str]) -> int:
    return int(hashlib.sha256(",".join(sorted(shas)).encode()).hexdigest()[:16], 16)


def ownership_xml(text: str) -> ET.Element | None:
    """The <ownershipDocument> inside an EDGAR full-submission .txt file."""
    for m in re.finditer(r"<XML>(.*?)</XML>", text, re.S | re.I):
        body = m.group(1).strip()
        if "<ownershipDocument" in body:
            body = re.sub(r"^<\?xml[^>]*\?>", "", body).strip()
            return ET.fromstring(body)
    return None


def _v(el: ET.Element, path: str) -> str:
    node = el.find(path)
    if node is None:
        return ""
    value = node.find("value")
    return ((value.text if value is not None else node.text) or "").strip()


def compare_filing(row: dict, doc: ET.Element) -> dict:
    """Compare one data-set buy with the Form 4 XML. Picks the XML transaction that matches
    the most of code, shares, price, date (data-set surrogate keys are not in the XML)."""
    want = {"code": row["trans_code"].upper(), "shares": dec(row["shares"]),
            "price": dec(row["price"]), "date": row["trans_date"]}
    best, best_score, cands = None, -1, doc.findall("nonDerivativeTable/nonDerivativeTransaction")
    for t in cands:
        got = {"code": (t.findtext("transactionCoding/transactionCode") or "").strip().upper(),
               "shares": dec(_v(t, "transactionAmounts/transactionShares")),
               "price": dec(_v(t, "transactionAmounts/transactionPricePerShare")),
               "date": _v(t, "transactionDate")[:10]}
        ok = {k: got[k] == want[k] for k in want}
        if sum(ok.values()) > best_score:
            best, best_score = (got, ok), sum(ok.values())
    issuer = (doc.findtext("issuer/issuerCik") or "").strip()
    result = {
        "xml_transactions": len(cands),
        "document_type_xml": (doc.findtext("documentType") or "").strip(),
        "document_type_match": (doc.findtext("documentType") or "").strip() == row["document_type"],
        "issuer_cik_match": issuer.isdigit() and int(issuer) == int(row["issuer_cik"]),
    }
    if best is None:
        return {**result, "status": "no_nonderivative_transactions", "match": False,
                "fields": {k: False for k in want}, "xml": {}}
    got, ok = best
    off = [k for k, v in ok.items() if not v]
    rounding_only = bool(off) and all(k in ("shares", "price") and rounds_to(want[k], got[k])
                                      for k in off)
    return {**result, "status": "compared", "match": all(ok.values()),
            "rounding_only": rounding_only, "fields": ok,
            "xml": {k: (str(v) if v is not None else "") for k, v in got.items()}}


def fetch_filing(client: ingest.SecClient, row: dict, filings_dir: Path,
                 now: Callable[[], datetime]) -> dict:
    """Full-submission text for a buy, from the cache or EDGAR (issuer CIK path first, then
    each reporting owner's). Returns {text, url, sha256, cached} or {text: None, tried}."""
    acc = row["accession_number"]
    cache, meta = filings_dir / f"{acc}.txt", filings_dir / f"{acc}.json"
    if cache.exists() and meta.exists():
        m = json.loads(meta.read_text(encoding="utf-8"))
        data = cache.read_bytes()
        if hashlib.sha256(data).hexdigest() == m.get("sha256"):
            return {"text": data.decode("utf-8", "replace"), "url": m["url"],
                    "sha256": m["sha256"], "cached": True}
    tried = []
    for cik in dict.fromkeys([row["issuer_cik"], *row["rptowner_ciks"].split(";")]):
        if not cik:
            continue
        url = filing_url(cik, acc, f"{acc}.txt")
        tried.append(url)
        resp = client.get(url, allow_404=True)
        if resp is None:
            continue
        try:
            data = b"".join(ingest.iter_body(resp))
        finally:
            ingest._close(resp)
        filings_dir.mkdir(parents=True, exist_ok=True)
        sha = hashlib.sha256(data).hexdigest()
        cache.write_bytes(data)
        meta.write_text(json.dumps({"url": url, "sha256": sha, "bytes": len(data),
                                    "retrieved_at": ingest._iso(now())}, indent=2) + "\n",
                        encoding="utf-8")
        return {"text": data.decode("utf-8", "replace"), "url": url, "sha256": sha,
                "cached": False, "issuer_path": cik == row["issuer_cik"]}
    return {"text": None, "tried": tried}


def spot_check(rows: list[dict], n: int, seed: int, client: ingest.SecClient,
               filings_dir: Path, now: Callable[[], datetime]) -> dict:
    """Raises ingest.HaltError if SEC refuses; mismatches are results, not errors."""
    pool = sorted(rows, key=lambda r: (r["accession_number"], int(r["nonderiv_trans_sk"])))
    sample = random.Random(seed).sample(pool, min(n, len(pool)))
    results = []
    for r in sample:
        res = {"accession_number": r["accession_number"], "nonderiv_trans_sk": r["nonderiv_trans_sk"],
               "issuer_cik": r["issuer_cik"], "issuer_name": r["issuer_name"],
               "document_type": r["document_type"],
               "dataset": {"code": r["trans_code"], "shares": r["shares"], "price": r["price"],
                           "date": r["trans_date"]}}
        got = fetch_filing(client, r, filings_dir, now)
        if got["text"] is None:
            results.append({**res, "status": "filing_not_found", "match": False, "tried": got["tried"]})
            continue
        res.update({"url": got["url"], "filing_sha256": got["sha256"], "cached": got["cached"]})
        try:
            doc = ownership_xml(got["text"])
        except ET.ParseError as err:
            results.append({**res, "status": f"xml_parse_error: {err}", "match": False})
            continue
        if doc is None:
            results.append({**res, "status": "no_ownership_xml", "match": False})
            continue
        results.append({**res, **compare_filing(r, doc)})
    return {"run": True, "n": len(sample), "seed": seed, "results": results,
            "matched": sum(x["match"] for x in results),
            "rounding_only": sum(bool(x.get("rounding_only")) for x in results),
            "substantive_mismatch": sum(not x["match"] and not x.get("rounding_only")
                                        for x in results),
            "requests": client.requests_made}


# --------------------------------------------------------------------------- run + promote

def run(quarters: list[str], data_dir: Path, parsed_dir: Path, verified_dir: Path,
        staging_dir: Path, filings_dir: Path, client: ingest.SecClient | None,
        n: int = SPOT_CHECK_N, now: Callable[[], datetime] = lambda: datetime.now(timezone.utc)
        ) -> tuple[int, dict]:
    started = now()
    per_q = [check_quarter(data_dir, parsed_dir, q) for q in quarters]
    rows = [r for q in per_q for r in q["rows"]]
    cross = Counter((r["accession_number"], r["nonderiv_trans_sk"]) for r in rows)
    cross_dupes = [f"key {k} in more than one quarter" for k, c in cross.items() if c > 1]
    failed = [f"{q['quarter']}:{name}" for q in per_q for name, c in q["checks"].items()
              if not c["passed"]] + (["cross-quarter keys"] if cross_dupes else [])
    summary = {
        "run_at": ingest._iso(started), "quarters": quarters,
        "source_sha256": {q["quarter"]: q["sha256"] for q in per_q},
        "halting_checks": {q["quarter"]: q["checks"] for q in per_q},
        "cross_quarter_duplicate_keys": cross_dupes[:5],
        "failed_checks": failed, "promoted": False, "rows_promoted": 0,
        "findings": {q["quarter"]: q["findings"] for q in per_q},
        "spot_check": {"run": False, "reason": "halting check failed" if failed else
                       "--no-spot-check" if client is None else ""},
    }
    stamp = started.strftime("%Y%m%dT%H%M%SZ")
    if failed:
        _write_failure(staging_dir, stamp, summary, per_q)
        return 1, summary

    if client is not None:
        seed = spot_check_seed(q["sha256"] for q in per_q)
        try:
            summary["spot_check"] = spot_check(rows, n, seed, client, filings_dir, now)
        except ingest.HaltError as err:
            summary["spot_check"] = {"run": False, "reason": f"halted by SEC: {err}"}
            summary["failed_checks"] = ["spot-check halted by SEC"]
            _write_failure(staging_dir, stamp, summary, per_q)
            return 3, summary

    summary["promoted"], summary["rows_promoted"] = True, len(rows)
    _promote(verified_dir, staging_dir, stamp, rows, summary, per_q)
    return 0, summary


def _write_failure(staging_dir: Path, stamp: str, summary: dict, per_q: list[dict]) -> None:
    staging_dir.mkdir(parents=True, exist_ok=True)
    (staging_dir / f"conformance-audit-FAILED-{stamp}.md").write_text(
        render_audit(summary, per_q), encoding="utf-8")
    (staging_dir / f"conformance_summary-FAILED-{stamp}.json").write_text(
        json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")


def _promote(verified_dir: Path, staging_dir: Path, stamp: str, rows: list[dict],
             summary: dict, per_q: list[dict]) -> None:
    """Write everything to a staging folder first, then move each file into place."""
    stage = staging_dir / f"stage-{stamp}"
    stage.mkdir(parents=True, exist_ok=True)
    rows = sorted(rows, key=lambda r: (r["filing_date"], r["accession_number"],
                                       int(r["nonderiv_trans_sk"])))
    with open(stage / BUYS_NAME, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=VERIFIED_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    summary["insider_buys_sha256"] = ingest.sha256_file(stage / BUYS_NAME)
    (stage / AUDIT_NAME).write_text(render_audit(summary, per_q), encoding="utf-8")
    (stage / SUMMARY_NAME).write_text(json.dumps(summary, indent=2, default=str) + "\n",
                                      encoding="utf-8")
    verified_dir.mkdir(parents=True, exist_ok=True)
    for name in (SUMMARY_NAME, AUDIT_NAME, BUYS_NAME):
        os.replace(stage / name, verified_dir / name)
    shutil.rmtree(stage)   # empty staging folder (rebuildable); the files now live in verified/


# --------------------------------------------------------------------------- audit

def _n(v) -> str:
    return f"{v:,}" if isinstance(v, int) else str(v)


def _md(text: str) -> str:
    return str(text).replace("|", "\\|")


def render_audit(s: dict, per_q: list[dict]) -> str:
    title = "Conformance audit (G2)" if s["promoted"] else "Conformance audit (G2) — NOT PROMOTED"
    L = [f"# {title} — {', '.join(s['quarters'])}", "",
         f"Run at {s['run_at']} by `conformance.py`. This audit reports what was found. "
         "The halting checks decide promotion; clearing G2 is the owner's logged decision.", ""]
    if s["promoted"]:
        L.append(f"**Promoted:** {s['rows_promoted']:,} rows → `data/verified/{BUYS_NAME}` "
                 f"(SHA-256 `{s.get('insider_buys_sha256', '')}`).")
    else:
        L.append("**Not promoted.** Failed: " + ", ".join(s["failed_checks"]) +
                 f". Nothing in `data/verified/` was changed.")
    L += ["", "## Halting checks", "", "| Quarter | Check | Result | Violations | Detail |",
          "|---|---|---|---:|---|"]
    for q, checks in s["halting_checks"].items():
        for name in HALTING_CHECKS:
            c = checks[name]
            res = "not run" if c["not_run"] else "PASS" if c["passed"] else "**FAIL**"
            L.append(f"| {q} | {name} | {res} | {c['violations']:,} | {_md(c['not_run'] or c['detail'])} |")
    for q, checks in s["halting_checks"].items():
        for name, c in checks.items():
            if c["examples"]:
                L += ["", f"Examples, {q} {name}:", *(f"- {_md(e)}" for e in c["examples"])]
    for q in per_q:
        f = q["findings"]
        if not f:
            continue
        ps = f["parse"]
        fun = ps["funnel"]
        L += ["", f"## Findings — {q['quarter']}", "", "### Rows in / out", "",
              "| Step | Rows |", "|---|---:|",
              f"| Form 4 / 4-A rows (PARSE) | {_n(fun.get('form4_rows', 'n/a'))} |",
              f"| … code P | {_n(fun.get('form4_code_p_rows', 'n/a'))} |",
              f"| … qualifying buys (PARSE) | {_n(fun.get('qualifying_buys', 'n/a'))} |",
              f"| … promoted to verified | {len(q['rows']):,} |", "",
              "Exclusions by reason (reason names carry the transaction code):", "",
              "| Reason | Rows |", "|---|---:|",
              *(f"| `{r}` | {v:,} |" for r, v in ps["exclusions_by_reason"].items()), ""]
        p = f["prereg_rule1"]
        L += ["### PRE_REGISTRATION.md Rule 1 (counts only)", "",
              "| | Buys |", "|---|---:|",
              f"| Kept in verified, **excluded from clustering and scoring** (private or ESPP/DRIP flag) | {p['excluded_from_clustering']:,} |",
              f"| … private flag | {p['private_flag']:,} |",
              f"| … ESPP/DRIP flag | {p['espp_or_drip_flag']:,} |",
              f"| … both | {p['both_flags']:,} |",
              f"| 10b5-1 plan buys that may cluster but **cannot be STRONG** | {p['plan_buys_strong_ineligible']:,} |",
              f"| 10b5-1 plan buys that are also excluded by a flag | {p['plan_buys_also_excluded']:,} |",
              f"| `is_10b5_1 = unknown` (rule not yet registered) | {p['unknown_10b5_1']:,} |",
              f"| **Eligible for cluster detection** | **{p['cluster_eligible']:,}** |", ""]
        a = f["amendments"]
        L += ["### Amendments (4/A)", "",
              f"- {a['amendment_buys']:,} promoted buys come from {a['amendment_accessions']:,} "
              "Form 4/A filings.",
              "- Original filing found in this quarter (same issuer, same owners, filed on "
              "`DATE_OF_ORIG_SUB`): " + (", ".join(f"{k} {v:,}" for k, v in
                                                     a["original_candidates_in_quarter"].items()) or "none") + ".",
              f"- Amendment buys that repeat a buy in a candidate original (same trade date, "
              f"shares and price): **{a['amendment_buys_repeating_an_original_buy']:,}**. These "
              "may be the same purchase counted twice.",
              "- Resolution: each amendment is kept as its own dated event at its own "
              "`FILING_DATE`; it is not linked to or merged with an original. The matching rule "
              "is recipe `[TODO: DEV]` 3, still open.", ""]
        sy = f["symbols"]
        L += ["### Blank or placeholder trading symbols", "",
              "| Symbol as filed | Buys | Issuers |", "|---|---:|---:|",
              *(f"| `{k}` | {v:,} | {sy['issuers'][k]:,} |" for k, v in sy["buys"].items()),
              "", "ENRICH cannot price these by symbol; they will need a `price_status` reason.", ""]
        t, lg = f["timeliness"], f["lag_calendar_days"]
        L += ["### Late filings and the TRANS_DATE → FILING_DATE lag", "",
              "`TRANS_TIMELINESS` as filed: " + ", ".join(f"`{k}` {v:,}" for k, v in t["TRANS_TIMELINESS"].items()) + ".",
              f"Filed more than 2 business days after the trade (weekdays only, no holiday "
              f"calendar, so this slightly overcounts): {t['more_than_2_business_days']:,}, of "
              f"which {t['more_than_2_business_days_and_not_marked_L']:,} are not marked `L`.", "",
              "| Calendar days | min | p25 | median | p75 | p90 | p99 | max |",
              "|---|---:|---:|---:|---:|---:|---:|---:|",
              f"| lag | {lg['min']} | {lg['p25']} | {lg['median']} | {lg['p75']} | {lg['p90']} | {lg['p99']} | {lg['max']:,} |", "",
              "| Lag bucket (days) | " + " | ".join(lg["buckets"]) + " |",
              "|---|" + "---:|" * len(lg["buckets"]),
              "| Buys | " + " | ".join(f"{v:,}" for v in lg["buckets"].values()) + " |", "",
              "Late filings are kept. The look-ahead rule uses `FILING_DATE`, so a late filing "
              "enters the backtest only when it became public.", ""]
        j = f["joint_filings"]
        L += ["### Joint filings", "",
              f"{j['buys']:,} buys from {j['accessions']:,} filings list more than one reporting "
              "owner. Each stays one row; all owners are in `owners` and `rptowner_ciks`. "
              "Owners per buy: " + ", ".join(f"{k}: {v:,}" for k, v in j["owner_count_distribution"].items()) + ".", ""]
        pr = f["precision"]
        L += ["### Precision of shares and prices", "",
              f"The most decimals on any promoted price is {pr['max_decimals_price']}, and on "
              f"any share count {pr['max_decimals_shares']}. The spot-check shows the data set "
              "rounds the filed values to 2 decimals (half-up). That matters most for low "
              f"prices: {pr['buys_price_below_1']:,} buys are priced below $1.00 and "
              f"{pr['buys_price_at_most_0_05']:,} at $0.05 or less, where rounding can move "
              "price and `value_usd` by a large fraction. The data set is not corrected here.", ""]
        o = f["form4_rows_not_promoted"]
        L += ["### Form 4 rows that were not promoted (reported, not halted on)", "",
              f"- `TRANS_DATE` after `FILING_DATE`: {o['trans_date_after_filing_date']:,}",
              f"- Unparseable dates: {o['unparseable_dates']:,}",
              f"- Code blank or not in SEC's list: {o['code_blank_or_unrecognized']:,}",
              f"- `TRANS_ACQUIRED_DISP_CD` not A or D: {o['acquired_disposed_not_A_or_D']:,}", ""]
    sc = s["spot_check"]
    L += ["## Spot-check against the individual filings", ""]
    if not sc.get("run"):
        L += [f"**Not run** ({sc.get('reason') or 'n/a'}).", ""]
    else:
        L += [f"{sc['n']} buys drawn at random (seed `{sc['seed']}`, derived from the source ZIP "
              f"hashes). Each filing's Form 4 XML was compared with the data set. "
              f"**{sc['matched']} of {sc['n']} match exactly** on code, shares, price and date; "
              f"**{sc['rounding_only']}** differ only because the data set rounds shares or "
              f"price to 2 decimals; **{sc['substantive_mismatch']}** differ in another way. "
              f"Requests to SEC this run: {sc['requests']} (1/s, logged in "
              "`data/raw/filings/request_log.jsonl`). Mismatches are listed, not corrected.", "",
              "| # | Accession | Form | Issuer | Data set (code · shares · price · date) | Filing XML | Code | Shares | Price | Date | Result |",
              "|---:|---|---|---|---|---|:-:|:-:|:-:|:-:|---|"]
        for i, x in enumerate(sc["results"], 1):
            d, fx, fl = x["dataset"], x.get("xml", {}), x.get("fields", {})
            mark = lambda k: ("✓" if fl.get(k) else "✗") if fl else "–"
            res = ("match" if x["match"] else "rounding only" if x.get("rounding_only") else
                   f"**{x.get('status') if x.get('status') != 'compared' else 'MISMATCH'}**")
            extra = [] if x.get("document_type_match", True) else [f"form {x.get('document_type_xml')}"]
            if x.get("issuer_cik_match") is False:
                extra.append("issuer CIK differs")
            if extra:
                res += " (" + ", ".join(extra) + ")"
            L.append(f"| {i} | [{x['accession_number']}]({x.get('url', '')}) | {x['document_type']} | "
                     f"{_md(x['issuer_name'])} | {d['code']} · {d['shares']} · {d['price']} · {d['date']} | "
                     f"{fx.get('code', '')} · {fx.get('shares', '')} · {fx.get('price', '')} · {fx.get('date', '')} | "
                     f"{mark('code')} | {mark('shares')} | {mark('price')} | {mark('date')} | {res} |")
        L.append("")
    return "\n".join(L)


# --------------------------------------------------------------------------- CLI

def main(argv: list[str] | None = None, env: Mapping[str, str] = os.environ) -> int:
    ap = argparse.ArgumentParser(description="GIGO / G2: conformance checks and promotion.")
    ap.add_argument("--quarters", required=True, help="e.g. 2026q3 or 2023q1:2026q3")
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    ap.add_argument("--parsed-dir", type=Path, default=DEFAULT_PARSED_DIR)
    ap.add_argument("--verified-dir", type=Path, default=DEFAULT_VERIFIED_DIR)
    ap.add_argument("--staging-dir", type=Path, default=DEFAULT_STAGING_DIR)
    ap.add_argument("--filings-dir", type=Path, default=DEFAULT_FILINGS_DIR)
    ap.add_argument("--spot-check-n", type=int, default=SPOT_CHECK_N)
    ap.add_argument("--no-spot-check", action="store_true")
    ap.add_argument("--rate", type=float, default=ingest.DEFAULT_RATE)
    args = ap.parse_args(argv)
    try:
        quarters = ingest.parse_quarters(args.quarters)
        client = None
        if not args.no_spot_check:
            client = ingest.SecClient(ingest.require_user_agent(env), args.rate,
                                      args.filings_dir / ingest.REQUEST_LOG_NAME)
        code, s = run(quarters, args.data_dir, args.parsed_dir, args.verified_dir,
                      args.staging_dir, args.filings_dir, client, args.spot_check_n)
    except ingest.ConfigError as err:
        print(f"conformance: {err}", file=sys.stderr)
        return 2
    except (ConformanceError, ingest.IngestError) as err:
        print(f"conformance: {err}", file=sys.stderr)
        return 1
    sc = s["spot_check"]
    spot = (f"spot-check {sc['matched']}/{sc['n']} exact, {sc['rounding_only']} rounding only, "
            f"{sc['substantive_mismatch']} other mismatch" if sc.get("run") else "spot-check not run")
    if code == 0:
        print(f"conformance: all halting checks pass · {s['rows_promoted']:,} buys promoted to "
              f"{args.verified_dir / BUYS_NAME} · {spot}")
    else:
        print(f"conformance: NOT PROMOTED ({', '.join(s['failed_checks'])}); audit in "
              f"{args.staging_dir}", file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
