"""
SHARE TYPES — classify each verified buy's SECURITY_TITLE by instrument type (proposed Rule 10).

Status: **proposal only.** Rule 10 is not registered in PRE_REGISTRATION.md and is not applied by
any pipeline stage. This script only counts; it changes nothing in data/verified/.

The rule is on principle (instrument type), set by Gomathy S. on 2026-11-12:
  in scope   common stock, ordinary shares, LP common units, depositary / ADR shares representing
             common or ordinary shares, shares of beneficial interest
  out        preferred (including depositary shares for preferred), notes, debentures, bonds,
             warrants, rights, options, titles with a foreign-exchange suffix such as (2330.TW),
             and titles that cannot be classified

Matching: the title is upper-cased and whitespace-collapsed; the first rule in RULES that matches
wins. Every pattern uses word boundaries, so UNITED is not UNITS and CYANOTECH is not NOTE.
Out-of-scope instruments are tested first, so "WARRANTS TO PURCHASE COMMON STOCK" and
"DEPOSITARY SHARES FOR SERIES B PREFERRED STOCK" are out.

Owner decisions of 2026-11-13 (Gomathy S.) on the AI's readings of "cannot be classified":
`depositary_underlying_unstated` and `units_not_lp_common` stay out; titles that name a company
only stay `unclassifiable` (out); ADS / ADR without a stated underlying count as common
(`depositary_common`); `share_equivalent_named` moves SUBORDINATE VOTING SHARES, REGISTERED SHARES
and titles ending in STOCK into scope (but CONVERTIBLE titles are out, as `convertible`), while fund share classes (Class I, Z, Advisor, A1/A2/A3 …)
stay out as `share_class_not_named_common`.

No returns: only READ_COLUMNS are read from enriched_buys.csv (no entry, exit or return column).

Run:  python share_types.py            → data/raw/share_types/share_types_summary.json + -audit.md
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE / "data" / "verified" / "enriched_buys.csv"
DEFAULT_ENRICH_SUMMARY = HERE / "data" / "verified" / "enrich_summary.json"
DEFAULT_OUT = HERE / "data" / "raw" / "share_types"

READ_COLUMNS = ("security_title", "source_quarter", "price_status", "filing_price_check")

# Misspellings of COMMON seen in the study's titles, matched as whole words.
COMMON_SPELLINGS = ("COMMON", "COMMOM", "CAMMON", "COMMMON", "CMMON", "COMON", "COMMPN",
                    "COMMN", "COMMONS", "COMMONSTOCK")
_COMMON = r"\b(" + "|".join(COMMON_SPELLINGS) + r")\b"

_PREF = r"\b(PREFERRED|PREFERENCE|PREF|PFD)\b|\b(NON-)?CUMM?ULATIVE\b|\bPERPETUAL\b"
_DEPOSITARY = r"\bDEPOSIT[AO]RY\b|\bDEP\.?\s+SHARES?\b|\bADSS?\b|\bADRS?\b"
_AMERICAN_DEP = r"\bAMERICAN\s+DEPOSIT[AO]RY\b|\bADSS?\b|\bADRS?\b"
_BENEFICIAL = r"\bSHARES?\s+OF\s+(BENEFICIAL|BEN\.)\s*(INTEREST|OWNERSHIP)?\b"
_LLC = r"\bLIMITED\s+LIABILI\w*\b|\bLLC\b"

IN, OUT = "in", "out"

# (reason, decision, test). First match wins.
RULES = [
    ("warrants", OUT, lambda t: re.search(r"\bWARRANTS?\b", t)),
    ("debt", OUT, lambda t: re.search(r"\b(NOTES?|DEBENTURES?|BONDS?)\b", t)),
    ("options", OUT, lambda t: re.search(r"\bOPTIONS?\b", t)),
    ("rights", OUT, lambda t: re.search(r"\bRIGHTS?\b", t)),
    ("depositary_preferred", OUT, lambda t: re.search(_DEPOSITARY, t) and re.search(_PREF, t)),
    ("preferred", OUT, lambda t: re.search(_PREF, t)),
    # Owner decision 2026-11-13: convertible securities are usually preferred → out.
    ("convertible", OUT, lambda t: re.search(r"\bCONVERTIBLE\b", t)),
    ("foreign_exchange_suffix", OUT, lambda t: re.search(r"\([0-9A-Z]+\.[A-Z]{1,3}\)", t)),
    ("depositary_common", IN, lambda t: re.search(_DEPOSITARY, t) and (
        re.search(_AMERICAN_DEP, t) or re.search(_COMMON, t) or re.search(r"\bORDINARY\b", t))),
    ("depositary_underlying_unstated", OUT, lambda t: re.search(_DEPOSITARY, t)),
    ("lp_common_units", IN, lambda t: re.search(_COMMON + r"\s+UNITS?\b", t) and not re.search(_LLC, t)),
    ("units_not_lp_common", OUT, lambda t: re.search(r"\bUNITS?\b", t)),
    ("beneficial_interest", IN, lambda t: re.search(_BENEFICIAL, t)),
    ("ordinary", IN, lambda t: re.search(r"\bORDINARY\b", t)),
    ("common", IN, lambda t: re.search(_COMMON, t)),
    ("share_equivalent_named", IN, lambda t: re.search(
        r"\bSUBORDINATE\s+VOTING\s+SHARES?\b|\bREGISTERED\s+SHARES?\b|\bSTOCK[.\s]*$", t)),
    ("share_class_not_named_common", OUT, lambda t: re.search(r"\b(SHARES?|STOCK)\b", t)),
    ("unclassifiable", OUT, lambda t: True),
]
IN_REASONS = [r for r, d, _ in RULES if d == IN]
OUT_REASONS = [r for r, d, _ in RULES if d == OUT]
# Reasons that began as the AI's reading; each was decided by the owner on 2026-11-13.
OWNER_DECIDED_REASONS = ("depositary_underlying_unstated", "units_not_lp_common",
                         "share_class_not_named_common", "share_equivalent_named")


def normalize(title: str) -> str:
    return " ".join((title or "").split()).upper()


def classify(title: str) -> tuple[str, str]:
    """Return (decision, reason) for one SECURITY_TITLE."""
    t = normalize(title)
    for reason, decision, test in RULES:
        if test(t):
            return decision, reason
    raise AssertionError("unreachable: the last rule always matches")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def count(rows) -> dict:
    """rows: iterable of dicts with READ_COLUMNS. Returns every count; no return figures."""
    total = 0
    by_reason = collections.Counter()
    priced = collections.Counter()
    mismatch = collections.Counter()
    titles = collections.defaultdict(collections.Counter)
    q_all = collections.Counter()
    q_in = collections.Counter()
    q_priced_all = collections.Counter()
    q_priced_in = collections.Counter()
    for r in rows:
        total += 1
        decision, reason = classify(r["security_title"])
        q = r["source_quarter"]
        is_priced = r["price_status"] == "priced"
        by_reason[reason] += 1
        titles[reason][normalize(r["security_title"])] += 1
        priced[reason] += is_priced
        mismatch[reason] += r["filing_price_check"] == "mismatch"
        q_all[q] += 1
        q_priced_all[q] += is_priced
        if decision == IN:
            q_in[q] += 1
            q_priced_in[q] += is_priced

    def pct(a, b):
        return round(100.0 * a / b, 2) if b else None

    n_in = sum(by_reason[r] for r in IN_REASONS)
    p_in = sum(priced[r] for r in IN_REASONS)
    p_all = sum(priced.values())

    def examples(reason):
        c = titles[reason]
        top = [t for t, _ in c.most_common(5)]
        rare = [t for t, _ in sorted(c.items(), key=lambda x: (x[1], x[0])) if t not in top][:5]
        return [[t, c[t]] for t in top + rare]

    return {
        "rows": total,
        "in_scope": n_in,
        "out_of_scope": total - n_in,
        "by_reason": {r: {"decision": d, "buys": by_reason[r], "priced": priced[r],
                          "rule9_mismatch": mismatch[r], "distinct_titles": len(titles[r]),
                          "examples": examples(r)} for r, d, _ in RULES},
        "coverage": {
            "current_all_buys": {"priced": p_all, "of": total, "pct": pct(p_all, total)},
            "rule10_over_all_buys": {"priced": p_in, "of": total, "pct": pct(p_in, total)},
            "rule10_over_in_scope": {"priced": p_in, "of": n_in, "pct": pct(p_in, n_in)},
        },
        "by_quarter": {q: {"buys": q_all[q], "in_scope": q_in[q], "priced_in_scope": q_priced_in[q],
                           "priced_all": q_priced_all[q],
                           "pct_over_all_buys": pct(q_priced_in[q], q_all[q]),
                           "pct_over_in_scope": pct(q_priced_in[q], q_in[q])}
                       for q in sorted(q_all)},
    }


def read_rows(path: Path):
    csv.field_size_limit(1 << 30)
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in READ_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"share_types: missing columns {missing} in {path}")
        for r in reader:
            yield {c: r[c] for c in READ_COLUMNS}


def render_audit(s: dict) -> str:
    def q(label):
        return label[:4] + " Q" + label[-1]

    L = ["# Share types — proposed Rule 10 (audit)", "",
         "**Proposal only: Rule 10 is not registered and not applied.** Counts, not outcomes: no "
         "entry, exit or return column was read.", "",
         f"- Input: `{s['input']}` SHA-256 `{s['input_sha256']}` (matches `enrich_summary.json`: "
         f"{s['input_matches_enrich_summary']})",
         f"- Run at: {s['run_at']} · script `share_types.py`",
         f"- Buys: {s['rows']:,} · in scope {s['in_scope']:,} · out of scope {s['out_of_scope']:,}", "",
         "## Counts by decision", "",
         "| Decision | Reason | Buys | Priced | Rule 9 mismatch | Distinct titles |",
         "|---|---|---|---|---|---|"]
    for r, v in s["by_reason"].items():
        flag = " (owner-decided 2026-11-13)" if r in OWNER_DECIDED_REASONS else ""
        L.append(f"| {v['decision']} | `{r}`{flag} | {v['buys']:,} | {v['priced']:,} | "
                 f"{v['rule9_mismatch']:,} | {v['distinct_titles']:,} |")
    c = s["coverage"]
    L += ["", "## Coverage (both denominators are shown, always)", "",
          "| Measure | Priced | Of | Coverage |", "|---|---|---|---|",
          f"| Current (no Rule 10), all buys | {c['current_all_buys']['priced']:,} | "
          f"{c['current_all_buys']['of']:,} | {c['current_all_buys']['pct']}% |",
          f"| Rule 10, over all buys | {c['rule10_over_all_buys']['priced']:,} | "
          f"{c['rule10_over_all_buys']['of']:,} | {c['rule10_over_all_buys']['pct']}% |",
          f"| Rule 10, over in-scope buys | {c['rule10_over_in_scope']['priced']:,} | "
          f"{c['rule10_over_in_scope']['of']:,} | {c['rule10_over_in_scope']['pct']}% |",
          "", "### By quarter", "",
          "| Quarter | Buys | In scope | Priced in scope | Over all buys | Over in-scope |",
          "|---|---|---|---|---|---|"]
    for k, v in s["by_quarter"].items():
        L.append(f"| {q(k)} | {v['buys']:,} | {v['in_scope']:,} | {v['priced_in_scope']:,} | "
                 f"{v['pct_over_all_buys']}% | {v['pct_over_in_scope']}% |")
    L += ["", "## Example titles (5 most frequent, then up to 5 rarest)", ""]
    for r, v in s["by_reason"].items():
        L.append(f"**{v['decision']} · `{r}`**")
        L += [f"- {t} [{n:,}]" for t, n in v["examples"]] or ["- (none)"]
        L.append("")
    return "\n".join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--enrich-summary", type=Path, default=DEFAULT_ENRICH_SUMMARY)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    a = ap.parse_args(argv)
    digest = sha256(a.input)
    expected = json.loads(a.enrich_summary.read_text())["enriched_buys_sha256"]
    if digest != expected:
        print(f"share_types: input SHA-256 {digest} ≠ enrich_summary {expected}; halting", file=sys.stderr)
        return 1
    s = count(read_rows(a.input))
    s = {"run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "input": str(a.input.relative_to(HERE)) if a.input.is_relative_to(HERE) else str(a.input),
         "input_sha256": digest, "input_matches_enrich_summary": True,
         "rule10_status": "proposed, not registered", **s}
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "share_types_summary.json").write_text(json.dumps(s, indent=1, ensure_ascii=False) + "\n")
    (a.out / "share_types-audit.md").write_text(render_audit(s) + "\n")
    c = s["coverage"]
    print(f"share_types: {s['rows']:,} buys · in scope {s['in_scope']:,} · coverage over all buys "
          f"{c['rule10_over_all_buys']['pct']}% · over in-scope {c['rule10_over_in_scope']['pct']}% "
          f"· audit {a.out / 'share_types-audit.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
