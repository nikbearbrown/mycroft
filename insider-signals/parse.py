"""
parse.py — PARSE stage of the insider-signal-agent recipe.

Reads one extracted quarter of SEC's Insider Transactions Data Sets (written by ingest.py)
and classifies every non-derivative transaction on Form 4 / 4-A.

What it does (recipe: "2. PARSE")
    - Checks provenance first: the extracted folder's ZIP hash must match manifest.json.
    - Reads each TSV by its own header. The downloaded header is authoritative: a required
      column that is missing halts the run; extra or reordered columns are fine.
    - Joins SUBMISSION ⋈ NONDERIV_TRANS on ACCESSION_NUMBER and attaches every
      REPORTINGOWNER of that accession. A joint filing stays one row per transaction, with
      its owners listed, so no transaction is counted twice.
    - Keeps DOCUMENT_TYPE 4 and 4/A. Other forms are counted, not output.
    - Classifies every row by TRANS_CODE (SEC's Trans Code List) and applies the buy filter:
      code P, TRANS_ACQUIRED_DISP_CD = A, non-derivative table, shares > 0, price > 0,
      no equity swap. Each excluded row gets exactly one reason (the first failing check,
      in the order above), and every reason is counted. A buy whose trade date is after its
      filing date is excluded last, as trans_date_after_filing.
    - Normalizes AFF10B5ONE: 1/true → plan, 0/false → no_plan, blank → unknown.
      Unrecognized values are also unknown and are counted separately.
    - Splits RPTOWNER_RELATIONSHIP on commas, case-insensitively.
    - Flags, but does not exclude, qualifying buys whose footnotes on the transaction's own
      fields (date, shares, price, code, security; not the holdings columns) suggest they
      were not open-market purchases:
        private_purchase_flag   offering / private-placement / issuer wording
        espp_or_drip_flag       employee stock purchase plan or dividend reinvestment
      This is a provisional footnote heuristic. The recipe's [TODO: DEFINE] on the
      private-purchase rule (including a price-vs-market test once ENRICH has prices, and
      whether flagged rows are excluded) is still open. Matches are listed in the audit for
      human review.
    - Records whether footnotes mention "10b5-1", as an audit finding only. It never
      changes the AFF10B5ONE normalization.

Outputs, in data/raw/parsed/
    <q>_form4_transactions.csv   every Form 4/4-A transaction row with buy_class (gitignored)
    <q>_parse_summary.json       all counts and review samples (machine customer)
    <q>_parse-audit.md           funnel, exclusions, flags, samples (human customer)

The audit reports what was found; it does not say pass. Nothing here writes to
data/verified/; that is the G2 conformance gate's job.

No network. Standard library only.

Usage
    python parse.py --quarters 2026q3
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Iterator

import ingest

csv.field_size_limit(sys.maxsize)

ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = ingest.DEFAULT_DATA_DIR
DEFAULT_OUT_DIR = ROOT / "data" / "raw" / "parsed"

FORM4_TYPES = ("4", "4/A")

# Columns this stage reads. AFF10B5ONE is optional: it exists only in 2023+ data sets.
REQUIRED = {
    "SUBMISSION": ["ACCESSION_NUMBER", "FILING_DATE", "PERIOD_OF_REPORT", "DATE_OF_ORIG_SUB",
                   "DOCUMENT_TYPE", "ISSUERCIK", "ISSUERNAME", "ISSUERTRADINGSYMBOL"],
    "REPORTINGOWNER": ["ACCESSION_NUMBER", "RPTOWNERCIK", "RPTOWNERNAME",
                       "RPTOWNER_RELATIONSHIP", "RPTOWNER_TITLE", "RPTOWNER_TXT"],
    "NONDERIV_TRANS": ["ACCESSION_NUMBER", "NONDERIV_TRANS_SK", "SECURITY_TITLE", "TRANS_DATE",
                       "DEEMED_EXECUTION_DATE", "TRANS_FORM_TYPE", "TRANS_CODE",
                       "EQUITY_SWAP_INVOLVED", "TRANS_TIMELINESS", "TRANS_SHARES",
                       "TRANS_PRICEPERSHARE", "TRANS_ACQUIRED_DISP_CD", "SHRS_OWND_FOLWNG_TRANS",
                       "DIRECT_INDIRECT_OWNERSHIP", "NATURE_OF_OWNERSHIP"],
    "FOOTNOTES": ["ACCESSION_NUMBER", "FOOTNOTE_ID", "FOOTNOTE_TXT"],
    "DERIV_TRANS": ["ACCESSION_NUMBER", "TRANS_CODE"],
}
OPTIONAL = {"SUBMISSION": ["AFF10B5ONE"]}

# SEC Trans Code List (insider_transactions_readme.pdf, Appendix 6.2) → short category.
TRANS_CODES = {
    "A": "grant_award", "C": "conversion", "D": "disposition_to_issuer",
    "E": "expiration_short_derivative", "F": "tax_or_exercise_payment", "G": "gift",
    "H": "expiration_long_derivative", "I": "discretionary_16b3f", "J": "other",
    "L": "small_acquisition", "M": "option_exercise_16b3", "O": "option_exercise_otm",
    "P": "purchase", "S": "sale", "U": "tender_change_of_control", "W": "will_or_descent",
    "X": "option_exercise_itm", "Z": "voting_trust",
}

# Exclusion reasons, in the order they are checked. One reason per row.
REASONS = (
    "code_missing",
    "code_unrecognized",
    *(f"code_{c}_{TRANS_CODES[c]}" for c in sorted(TRANS_CODES) if c != "P"),
    "p_not_acquired",
    "p_shares_missing_or_not_positive",
    "p_price_missing_or_not_positive",
    "p_equity_swap",
    "trans_date_after_filing",
)
QUALIFYING = "qualifying_buy"

_TRUE = {"1", "true", "t", "y", "yes"}
_FALSE = {"0", "false", "f", "n", "no"}

RELATIONSHIP_TOKENS = {"director": "director", "officer": "officer",
                       "tenpercentowner": "ten_percent_owner", "other": "other"}

# Footnote heuristics (provisional; see the module docstring). Case-insensitive.
PRIVATE_PATTERNS = {
    "private placement": r"private placement",
    "privately negotiated": r"privately[- ]negotiated",
    "subscription agreement": r"subscription agreement",
    "securities purchase agreement": r"securities purchase agreement",
    "registered direct": r"registered direct",
    "public offering": r"public offering",
    "underwritten": r"underwrit",
    "IPO": r"\bIPO\b|initial public offering",
    "directed share program": r"directed share",
    "rights offering": r"rights offering",
    "PIPE": r"\bPIPE\b",
    "from the issuer": r"(purchased|acquired|bought) (directly )?from the (issuer|company)",
}
ESPP_DRIP_PATTERNS = {
    "ESPP": r"employee stock purchase plan|\bESPP\b",
    "dividend reinvestment": r"dividend reinvestment",
}
# Flags read only footnotes attached to the transaction's own fields. Footnotes on the
# holdings columns (SHRS_OWND_FOLWNG_TRANS_FN, NATURE_OF_OWNERSHIP_FN, ...) often describe the
# owner's total position ("includes shares acquired through the DRIP"), not this purchase.
TRANSACTION_FN_COLUMNS = ("SECURITY_TITLE_FN", "TRANS_DATE_FN", "DEEMED_EXECUTION_DATE_FN",
                          "EQUITY_SWAP_TRANS_CD_FN", "TRANS_TIMELINESS_FN", "TRANS_SHARES_FN",
                          "TRANS_PRICEPERSHARE_FN", "TRANS_ACQUIRED_DISP_CD_FN")
TEN_B5_ONE = re.compile(r"10b5-1", re.IGNORECASE)
_PRIVATE_RE = {k: re.compile(v, re.IGNORECASE) for k, v in PRIVATE_PATTERNS.items()}
_ESPP_RE = {k: re.compile(v, re.IGNORECASE) for k, v in ESPP_DRIP_PATTERNS.items()}

OUTPUT_COLUMNS = [
    "accession_number", "nonderiv_trans_sk", "document_type", "filing_date", "filing_date_raw",
    "trans_date", "trans_date_raw", "period_of_report", "date_of_orig_sub", "issuer_cik",
    "issuer_name", "ticker_as_filed", "owner_count", "owners", "relationships",
    "security_title", "trans_form_type", "trans_code", "trans_code_category",
    "acquired_disposed", "shares", "price", "value_usd", "shares_owned_after",
    "direct_indirect", "nature_of_ownership", "equity_swap", "trans_timeliness",
    "aff10b5one_raw", "is_10b5_1", "footnote_mentions_10b5_1",
    "private_purchase_flag", "espp_or_drip_flag", "flag_evidence", "footnote_ids",
    "buy_class", "source_quarter",
]


class ParseError(Exception):
    """Input does not meet the contract; halt (exit 1)."""


# --------------------------------------------------------------------------- small helpers

def norm_bool(value: str | None) -> bool | None:
    v = (value or "").strip().lower()
    if v in _TRUE:
        return True
    if v in _FALSE:
        return False
    return None


def norm_aff10b5one(value: str | None) -> str:
    """1/true → plan · 0/false → no_plan · blank or anything else → unknown."""
    b = norm_bool(value)
    return "plan" if b is True else "no_plan" if b is False else "unknown"


def split_relationship(value: str | None) -> tuple[list[str], list[str]]:
    """'Director,Officer' → (['director', 'officer'], []). Unknown tokens returned separately."""
    known, unknown = [], []
    for token in (value or "").split(","):
        t = token.strip()
        if not t:
            continue
        mapped = RELATIONSHIP_TOKENS.get(t.replace(" ", "").replace("_", "").lower())
        if mapped:
            if mapped not in known:
                known.append(mapped)
        else:
            unknown.append(t)
    return known, unknown


def to_decimal(value: str | None) -> Decimal | None:
    v = (value or "").strip().replace(",", "")
    if not v:
        return None
    try:
        d = Decimal(v)
    except InvalidOperation:
        return None
    return d if d.is_finite() else None


def iso_date(value: str | None) -> str:
    """'15-AUG-2026' → '2026-08-15'; '' when blank or unparseable."""
    v = (value or "").strip()
    if not v:
        return ""
    try:
        return datetime.strptime(v.title(), "%d-%b-%Y").date().isoformat()
    except ValueError:
        return ""


def footnote_ids(row: dict, fn_columns: Iterable[str]) -> list[str]:
    ids: list[str] = []
    for col in fn_columns:
        for fid in re.split(r"[,\s]+", row.get(col) or ""):
            if fid and fid not in ids:
                ids.append(fid)
    return ids


def classify(row: dict, filing_date: str = "") -> str:
    """Return QUALIFYING or the first failing exclusion reason.

    `filing_date` is the submission's raw FILING_DATE. A buy whose TRANS_DATE is after it is
    excluded as trans_date_after_filing (decided 2026-11-04: such dates are filing errors).
    If either date does not parse, this check is skipped and G2's dates check decides."""
    code = (row.get("TRANS_CODE") or "").strip().upper()
    if not code:
        return "code_missing"
    if code not in TRANS_CODES:
        return "code_unrecognized"
    if code != "P":
        return f"code_{code}_{TRANS_CODES[code]}"
    if (row.get("TRANS_ACQUIRED_DISP_CD") or "").strip().upper() != "A":
        return "p_not_acquired"
    shares = to_decimal(row.get("TRANS_SHARES"))
    if shares is None or shares <= 0:
        return "p_shares_missing_or_not_positive"
    price = to_decimal(row.get("TRANS_PRICEPERSHARE"))
    if price is None or price <= 0:
        return "p_price_missing_or_not_positive"
    if norm_bool(row.get("EQUITY_SWAP_INVOLVED")) is True:
        return "p_equity_swap"
    td, fd = iso_date(row.get("TRANS_DATE")), iso_date(filing_date)
    if td and fd and td > fd:
        return "trans_date_after_filing"
    return QUALIFYING


def match_flags(texts: Iterable[str]) -> tuple[list[str], list[str]]:
    joined = " ".join(texts)
    private = [k for k, rx in _PRIVATE_RE.items() if rx.search(joined)]
    espp = [k for k, rx in _ESPP_RE.items() if rx.search(joined)]
    return private, espp


# --------------------------------------------------------------------------- reading

def read_table(folder: Path, table: str) -> tuple[list[str], Iterator[dict]]:
    """Open <table>.tsv, check its header against REQUIRED, return (header, row iterator)."""
    path = folder / f"{table}.tsv"
    if not path.exists():
        raise ParseError(f"{path} not found. Run ingest.py for this quarter first.")
    fh = open(path, newline="", encoding="utf-8")
    reader = csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
    try:
        header = [h.strip() for h in next(reader)]
    except StopIteration:
        fh.close()
        raise ParseError(f"{path.name} is empty.")
    missing = [c for c in REQUIRED[table] if c not in header]
    if missing:
        fh.close()
        raise ParseError(f"{path.name}: header is missing required column(s) {missing}.")

    def rows() -> Iterator[dict]:
        with fh:
            for lineno, values in enumerate(reader, start=2):
                if len(values) != len(header):
                    raise ParseError(f"{path.name} line {lineno}: {len(values)} fields, "
                                     f"header has {len(header)}.")
                yield dict(zip(header, values))
    return header, rows()


def check_provenance(data_dir: Path, quarter: str) -> str:
    """The extracted folder must come from the ZIP recorded in manifest.json."""
    manifest = ingest.load_manifest(data_dir)
    entry = manifest["quarters"].get(quarter)
    if not entry:
        raise ParseError(f"{quarter}: not in manifest.json. Run ingest.py first.")
    marker = data_dir / quarter / ingest.EXTRACT_MARKER
    if not marker.exists():
        raise ParseError(f"{quarter}: not extracted ({marker.name} missing). Run ingest.py.")
    extracted_sha = json.loads(marker.read_text(encoding="utf-8")).get("sha256")
    if extracted_sha != entry["sha256"]:
        raise ParseError(f"{quarter}: extracted files do not match the manifest hash.")
    zp = ingest.zip_path(data_dir, quarter)
    if zp.exists() and ingest.sha256_file(zp) != entry["sha256"]:
        raise ParseError(f"{quarter}: {zp.name} does not match the manifest hash.")
    return entry["sha256"]


# --------------------------------------------------------------------------- core

def parse_folder(folder: Path, quarter: str) -> tuple[list[dict], dict]:
    """Classify every Form 4 / 4-A non-derivative row in `folder`. Returns (rows, summary)."""
    sub_header, sub_rows = read_table(folder, "SUBMISSION")
    has_aff = "AFF10B5ONE" in sub_header
    submissions = {r["ACCESSION_NUMBER"]: r for r in sub_rows}

    _, owner_rows = read_table(folder, "REPORTINGOWNER")
    owners: dict[str, list[dict]] = defaultdict(list)
    unknown_rel = Counter()
    for r in owner_rows:
        known, unknown = split_relationship(r["RPTOWNER_RELATIONSHIP"])
        unknown_rel.update(unknown)
        owners[r["ACCESSION_NUMBER"]].append({
            "cik": r["RPTOWNERCIK"].strip(), "name": r["RPTOWNERNAME"].strip(),
            "relationship": known, "title": r["RPTOWNER_TITLE"].strip(),
            "other_text": r["RPTOWNER_TXT"].strip(),
        })

    _, fn_rows = read_table(folder, "FOOTNOTES")
    footnotes: dict[str, dict[str, str]] = defaultdict(dict)
    for r in fn_rows:
        footnotes[r["ACCESSION_NUMBER"]][r["FOOTNOTE_ID"].strip()] = r["FOOTNOTE_TXT"]

    nd_header, nd_rows = read_table(folder, "NONDERIV_TRANS")
    fn_columns = [c for c in nd_header if c.endswith("_FN")]
    tx_fn_columns = [c for c in TRANSACTION_FN_COLUMNS if c in nd_header]

    c = Counter()
    by_doc_type, code_counts, reasons = Counter(), Counter(), Counter()
    aff_raw_all, aff_raw_buys, aff_buys = Counter(), Counter(), Counter()
    flag_counts, fn10b5_by_aff, swap_raw = Counter(), Counter(), Counter()
    private_samples: list[dict] = []
    espp_samples: list[dict] = []
    out: list[dict] = []
    for sub in submissions.values():
        if sub["DOCUMENT_TYPE"].strip() in FORM4_TYPES:
            aff_raw_all[(sub.get("AFF10B5ONE") or "").strip() if has_aff else "<column absent>"] += 1

    for row in nd_rows:
        c["nonderiv_rows_total"] += 1
        acc = row["ACCESSION_NUMBER"].strip()
        sub = submissions.get(acc)
        if sub is None:
            c["nonderiv_rows_without_submission"] += 1
            continue
        doc_type = sub["DOCUMENT_TYPE"].strip()
        by_doc_type[doc_type] += 1
        if doc_type not in FORM4_TYPES:
            continue
        c["form4_rows"] += 1
        code = (row["TRANS_CODE"] or "").strip().upper()
        code_counts[code or "<blank>"] += 1
        if code == "P":
            c["form4_code_p_rows"] += 1
            swap_raw[(row["EQUITY_SWAP_INVOLVED"] or "").strip() or "<blank>"] += 1

        buy_class = classify(row, sub["FILING_DATE"])
        acc_owners = owners.get(acc, [])
        if not acc_owners:
            c["form4_rows_without_owner"] += 1
        aff_raw = (sub.get("AFF10B5ONE") or "").strip() if has_aff else ""
        is_plan = norm_aff10b5one(aff_raw) if has_aff else "unknown"
        ids = footnote_ids(row, fn_columns)
        texts = [footnotes[acc].get(i, "") for i in ids]
        mentions_10b5 = any(TEN_B5_ONE.search(t) for t in texts)          # all footnotes
        tx_texts = [footnotes[acc].get(i, "") for i in footnote_ids(row, tx_fn_columns)]
        private, espp = match_flags(tx_texts) if buy_class == QUALIFYING else ([], [])

        if buy_class == QUALIFYING:
            c["qualifying_buys"] += 1
            aff_buys[is_plan] += 1
            aff_raw_buys[aff_raw or "<blank>"] += 1
            if mentions_10b5:
                fn10b5_by_aff[is_plan] += 1
            if len(acc_owners) > 1:
                flag_counts["joint_filing"] += 1
            if private:
                flag_counts["private_purchase_flag"] += 1
                flag_counts.update(f"private:{p}" for p in private)
                if len(private_samples) < 10:
                    private_samples.append(_sample(acc, sub, private, tx_texts))
            if espp:
                flag_counts["espp_or_drip_flag"] += 1
                flag_counts.update(f"espp_drip:{p}" for p in espp)
                if len(espp_samples) < 5:
                    espp_samples.append(_sample(acc, sub, espp, tx_texts))
            if private and espp:
                flag_counts["both_flags"] += 1
            if is_plan == "plan" and (private or espp):
                flag_counts["plan_and_footnote_flag"] += 1
        else:
            reasons[buy_class] += 1

        shares, price = to_decimal(row["TRANS_SHARES"]), to_decimal(row["TRANS_PRICEPERSHARE"])
        out.append({
            "accession_number": acc,
            "nonderiv_trans_sk": row["NONDERIV_TRANS_SK"].strip(),
            "document_type": doc_type,
            "filing_date": iso_date(sub["FILING_DATE"]), "filing_date_raw": sub["FILING_DATE"],
            "trans_date": iso_date(row["TRANS_DATE"]), "trans_date_raw": row["TRANS_DATE"],
            "period_of_report": iso_date(sub["PERIOD_OF_REPORT"]),
            "date_of_orig_sub": iso_date(sub["DATE_OF_ORIG_SUB"]),
            "issuer_cik": sub["ISSUERCIK"].strip(), "issuer_name": sub["ISSUERNAME"].strip(),
            "ticker_as_filed": sub["ISSUERTRADINGSYMBOL"].strip(),
            "owner_count": len(acc_owners),
            "owners": json.dumps(acc_owners, ensure_ascii=False),
            "relationships": ";".join(sorted({r for o in acc_owners for r in o["relationship"]})),
            "security_title": row["SECURITY_TITLE"].strip(),
            "trans_form_type": row["TRANS_FORM_TYPE"].strip(),
            "trans_code": code, "trans_code_category": TRANS_CODES.get(code, ""),
            "acquired_disposed": row["TRANS_ACQUIRED_DISP_CD"].strip(),
            "shares": "" if shares is None else str(shares),
            "price": "" if price is None else str(price),
            "value_usd": str(shares * price) if buy_class == QUALIFYING else "",
            "shares_owned_after": row["SHRS_OWND_FOLWNG_TRANS"].strip(),
            "direct_indirect": row["DIRECT_INDIRECT_OWNERSHIP"].strip(),
            "nature_of_ownership": row["NATURE_OF_OWNERSHIP"].strip(),
            "equity_swap": row["EQUITY_SWAP_INVOLVED"].strip(),
            "trans_timeliness": row["TRANS_TIMELINESS"].strip(),
            "aff10b5one_raw": aff_raw, "is_10b5_1": is_plan,
            "footnote_mentions_10b5_1": str(mentions_10b5).lower(),
            "private_purchase_flag": str(bool(private)).lower(),
            "espp_or_drip_flag": str(bool(espp)).lower(),
            "flag_evidence": ";".join(private + espp),
            "footnote_ids": ";".join(ids),
            "buy_class": buy_class,
            "source_quarter": quarter,
        })

    _, deriv_rows = read_table(folder, "DERIV_TRANS")
    for row in deriv_rows:
        sub = submissions.get(row["ACCESSION_NUMBER"].strip())
        if sub and sub["DOCUMENT_TYPE"].strip() in FORM4_TYPES and \
                (row["TRANS_CODE"] or "").strip().upper() == "P":
            c["form4_derivative_code_p_rows"] += 1

    if c["form4_rows"] != c["qualifying_buys"] + sum(reasons.values()):
        raise ParseError("internal: funnel does not add up")   # every row has exactly one class

    summary = {
        "quarter": quarter,
        "aff10b5one_column_present": has_aff,
        "funnel": {
            "nonderiv_rows_total": c["nonderiv_rows_total"],
            "form4_rows": c["form4_rows"],
            "form4_code_p_rows": c["form4_code_p_rows"],
            "qualifying_buys": c["qualifying_buys"],
        },
        "nonderiv_rows_by_document_type": dict(sorted(by_doc_type.items())),
        "nonderiv_rows_without_submission": c["nonderiv_rows_without_submission"],
        "form4_rows_by_trans_code": dict(code_counts.most_common()),
        "exclusions_by_reason": {r: reasons[r] for r in REASONS if reasons[r]},
        "qualifying_buys_by_is_10b5_1": {k: aff_buys[k] for k in ("plan", "no_plan", "unknown")},
        "qualifying_buys_aff10b5one_raw_values": dict(aff_raw_buys.most_common()),
        "form4_submissions_aff10b5one_raw_values": dict(aff_raw_all.most_common()),
        "qualifying_buys_footnote_mentions_10b5_1_by_is_10b5_1": dict(fn10b5_by_aff),
        "qualifying_buy_flags": dict(sorted(flag_counts.items())),
        "context": {
            "form4_derivative_table_code_p_rows": c["form4_derivative_code_p_rows"],
            "form4_rows_without_reporting_owner": c["form4_rows_without_owner"],
            "code_p_equity_swap_raw_values": dict(swap_raw.most_common()),
            "unrecognized_relationship_tokens": dict(unknown_rel.most_common()),
        },
        "private_purchase_samples": private_samples,
        "espp_or_drip_samples": espp_samples,
    }
    return out, summary


def _sample(acc: str, sub: dict, matched: list[str], texts: list[str]) -> dict:
    """Audit sample: accession, issuer, and a short footnote snippet. No reporting-owner name
    fields; the snippet is public filing text and may still mention a person."""
    joined = " ".join(t for t in texts if t)
    rx = next((r for k, r in {**_PRIVATE_RE, **_ESPP_RE}.items() if k in matched), None)
    m = rx.search(joined) if rx else None
    start = max(0, (m.start() if m else 0) - 60)
    snippet = re.sub(r"\s+", " ", joined[start:start + 180]).strip()
    return {"accession_number": acc, "issuer": sub["ISSUERNAME"].strip(),
            "matched": matched, "snippet": snippet}


# --------------------------------------------------------------------------- outputs

def write_outputs(out_dir: Path, quarter: str, rows: list[dict], summary: dict) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "csv": out_dir / f"{quarter}_form4_transactions.csv",
        "summary": out_dir / f"{quarter}_parse_summary.json",
        "audit": out_dir / f"{quarter}_parse-audit.md",
    }
    tmp = paths["csv"].with_name(paths["csv"].name + ".tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=OUTPUT_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    tmp.replace(paths["csv"])
    paths["summary"].write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    paths["audit"].write_text(render_audit(summary), encoding="utf-8")
    return paths


def _pct(n: int, d: int) -> str:
    return f"{100 * n / d:.1f}%" if d else "n/a"


def render_audit(s: dict) -> str:
    f = s["funnel"]
    lines = [
        f"# PARSE audit — {s['quarter']}",
        "",
        f"Source: SEC Insider Transactions Data Set {s['quarter']} (ZIP SHA-256 "
        f"`{s.get('source_sha256', 'n/a')}`). Produced by `parse.py`. This audit reports what "
        "was found. It does not say pass, and nothing here has entered `data/verified/`.",
        "",
        "## Funnel",
        "",
        "| Step | Rows | Share of Form 4 rows |",
        "|---|---:|---:|",
        f"| Non-derivative transaction rows, all forms | {f['nonderiv_rows_total']:,} | |",
        f"| Form 4 / 4-A rows | {f['form4_rows']:,} | 100.0% |",
        f"| … with code P | {f['form4_code_p_rows']:,} | {_pct(f['form4_code_p_rows'], f['form4_rows'])} |",
        f"| … qualifying buys | {f['qualifying_buys']:,} | {_pct(f['qualifying_buys'], f['form4_rows'])} |",
        "",
        "Rows by document type (all forms): " + ", ".join(
            f"{k}: {v:,}" for k, v in s["nonderiv_rows_by_document_type"].items()) + ".",
        "",
        "## Exclusions by reason (Form 4 / 4-A rows)",
        "",
        "Each excluded row has exactly one reason: the first check it fails, in this order.",
        "",
        "| Reason | Rows |",
        "|---|---:|",
        *(f"| `{r}` | {n:,} |" for r, n in s["exclusions_by_reason"].items()),
        f"| **Total excluded** | **{sum(s['exclusions_by_reason'].values()):,}** |",
        "",
        "## Flags on qualifying buys (flagged, not excluded)",
        "",
        "| Flag | Buys | Share of qualifying |",
        "|---|---:|---:|",
    ]
    q = f["qualifying_buys"]
    a = s["qualifying_buys_by_is_10b5_1"]
    fl = s["qualifying_buy_flags"]
    for label, n in [("10b5-1 plan (AFF10B5ONE = 1/true)", a["plan"]),
                     ("No plan (AFF10B5ONE = 0/false)", a["no_plan"]),
                     ("Unknown (AFF10B5ONE blank or unrecognized)", a["unknown"]),
                     ("Likely private / issuer purchase (footnote heuristic)", fl.get("private_purchase_flag", 0)),
                     ("ESPP or dividend reinvestment (footnote heuristic)", fl.get("espp_or_drip_flag", 0)),
                     ("Joint filing (more than one reporting owner)", fl.get("joint_filing", 0))]:
        lines.append(f"| {label} | {n:,} | {_pct(n, q)} |")
    lines += [
        "",
        "Raw `AFF10B5ONE` values on qualifying buys: " + ", ".join(
            f"`{k}` {v:,}" for k, v in s["qualifying_buys_aff10b5one_raw_values"].items()) + ".",
        "Footnotes mentioning \"10b5-1\" on qualifying buys, by normalized flag: " + (", ".join(
            f"{k} {v:,}" for k, v in s["qualifying_buys_footnote_mentions_10b5_1_by_is_10b5_1"].items())
            or "none") + ". This is a finding only and does not change the flag.",
        "",
        "Footnote phrases matched: " + ", ".join(
            f"{k.split(':', 1)[1]} {v:,}" for k, v in fl.items() if ":" in k) + ".",
        "",
        "Flags read only footnotes on the transaction's own fields (date, shares, price, code, "
        "security), not those on the holdings columns. The footnote heuristic is provisional. The recipe's private-purchase rule is still a "
        "`[TODO: DEFINE]`: a price-vs-market test needs ENRICH, and whether flagged buys are "
        "excluded is undecided. Review the samples below.",
        "",
        "## Context",
        "",
        f"- Form 4 code P rows in the derivative table (excluded by design, not counted above): "
        f"{s['context']['form4_derivative_table_code_p_rows']:,}",
        f"- Form 4 rows whose accession has no reporting owner: "
        f"{s['context']['form4_rows_without_reporting_owner']:,}",
        f"- Non-derivative rows with no matching submission: {s['nonderiv_rows_without_submission']:,}",
        "- `EQUITY_SWAP_INVOLVED` raw values on code P rows: " + ", ".join(
            f"`{k}` {v:,}" for k, v in s["context"]["code_p_equity_swap_raw_values"].items()),
        "- Unrecognized `RPTOWNER_RELATIONSHIP` tokens: " + (", ".join(
            f"`{k}` {v:,}" for k, v in s["context"]["unrecognized_relationship_tokens"].items())
            or "none"),
        f"- `AFF10B5ONE` column present: {s['aff10b5one_column_present']}",
        "",
        "## Samples for review — likely private / issuer purchases (first 10)",
        "",
        "| Accession | Issuer | Matched | Footnote snippet |",
        "|---|---|---|---|",
        *(f"| {x['accession_number']} | {_md(x['issuer'])} | {', '.join(x['matched'])} | {_md(x['snippet'])} |"
          for x in s["private_purchase_samples"]),
        "",
        "## Samples for review — ESPP / dividend reinvestment (first 5)",
        "",
        "| Accession | Issuer | Matched | Footnote snippet |",
        "|---|---|---|---|",
        *(f"| {x['accession_number']} | {_md(x['issuer'])} | {', '.join(x['matched'])} | {_md(x['snippet'])} |"
          for x in s["espp_or_drip_samples"]),
        "",
    ]
    return "\n".join(lines)


def _md(text: str) -> str:
    return text.replace("|", "\\|")


# --------------------------------------------------------------------------- CLI

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PARSE: classify Form 4 transactions.")
    ap.add_argument("--quarters", required=True, help="e.g. 2026q3 or 2023q1:2026q3")
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = ap.parse_args(argv)
    try:
        for q in ingest.parse_quarters(args.quarters):
            sha = check_provenance(args.data_dir, q)
            rows, summary = parse_folder(args.data_dir / q, q)
            summary = {"source_sha256": sha, **summary}
            paths = write_outputs(args.out_dir, q, rows, summary)
            f = summary["funnel"]
            print(f"parse {q}: {f['form4_rows']:,} Form 4 rows → {f['form4_code_p_rows']:,} code P → "
                  f"{f['qualifying_buys']:,} qualifying buys · audit {paths['audit'].name}")
        return 0
    except (ParseError, ingest.IngestError) as err:
        print(f"parse: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
