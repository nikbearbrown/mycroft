"""The Form D identity queue: print the candidates, record the decisions.

    python -m scripts.identity_queue --report            # Markdown, for a human
    python -m scripts.identity_queue --json              # the same, for a machine
    python -m scripts.identity_queue --affirm 0001587468 \
        --verdict operating_company --company "Databricks, Inc." \
        --reviewer "Om Mali" --evidence "..."

Two customers, twice (P5): `--report` writes `docs/identity_queue.md` for the
person who has to decide, and `--json` emits the same content for anything
downstream. Neither of them decides anything.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db.connect import connect  # noqa: E402
from src.ingest.form_d import candidates, coverage  # noqa: E402
from src.resolve.identity import (  # noqa: E402
    affirm, edgar_facts, outstanding, propose, summary,
)

REPORT = ROOT / "docs" / "identity_queue.md"


def build(conn, with_edgar: bool = False) -> dict:
    rows = candidates(conn)
    proposals = []
    for row in rows:
        # A CIK can hit more than one pattern; the provisional label is a
        # comma-joined set, and the first element is the one the scan wrote.
        canonical = (row["provisional"] or "").split(", ")[0]
        proposal = propose(row, canonical)
        proposal["already_decided"] = row["already_decided"]
        proposal["entity_types"] = row["entity_types"]
        proposal["industry_groups"] = row["industry_groups"]
        if with_edgar:
            proposal["edgar"] = edgar_facts(row["cik"])
        proposals.append(proposal)
    return {
        "coverage": coverage(conn),
        "summary": summary(conn),
        "candidates": proposals,
    }


def _table(rows, verdict):
    subset = [r for r in rows if r["proposed_verdict"] == verdict]
    if not subset:
        return ["_none_", ""]
    out = ["| CIK | Filed entity name | Company pattern | Filings | First → last | Decided |",
           "|---|---|---|---|---|---|"]
    for r in sorted(subset, key=lambda r: (-int(r["filings"] or 0), r["entity_name"])):
        out.append(
            f"| `{r['cik']}` | {r['entity_name']} | {r['company_provisional']} | "
            f"{r['filings']} | {r['first_filing']} → {r['last_filing']} | "
            f"{'yes' if r['already_decided'] else '**no**'} |")
    out.append("")
    return out


def render(data: dict) -> str:
    rows = data["candidates"]
    cov = data["coverage"]
    counts = {v: sum(1 for r in rows if r["proposed_verdict"] == v) for v in
              ("operating_company", "vehicle", "not_in_universe", "unresolved")}
    pooled = next((b["rows"] for b in cov["by_class"]
                   if b["vehicle_class"] == "pooled_vehicle"), 0)

    out = [
        "# Form D identity queue",
        "",
        "Which EDGAR CIK **is** a universe company. Until a named human answers "
        "that, nothing in `form_d_filings` joins to anything, because the "
        "alternative — joining on the issuer name — is wrong in a way that "
        "produces a plausible table.",
        "",
        "## What the scan holds",
        "",
        f"- **{cov['quarters_scanned']} quarters** scanned, "
        f"`{cov['first_quarter']}` → `{cov['last_quarter']}`.",
        f"- **{cov['rows']} issuer rows** carry a universe company's name, "
        f"filed {cov['first_filing_date']} → {cov['last_filing_date']}.",
        f"- **{pooled} of them are self-declared pooled investment vehicles** "
        "and are filtered out by the filer's own `ISPOOLEDINVESTMENTFUNDTYPE` "
        "flag before a human sees them.",
        f"- **{len(rows)} distinct CIKs** remain as candidates. "
        f"{data['summary']['outstanding']} of them are undecided.",
        "",
        f"> **Archive gap.** {cov['archive_gap']}",
        "",
        "## The proposals",
        "",
        "Every row below is a **model judgment** (P8) and decides nothing. The "
        "verdict is whatever a named reviewer records with `--affirm`.",
        "",
        f"### Proposed `operating_company` ({counts['operating_company']})",
        "",
        "The filed name normalises to the canonical name and carries no pooling "
        "token. These are the rows that would actually join.",
        "",
    ]
    out += _table(rows, "operating_company")
    out += [
        f"### Proposed `vehicle` ({counts['vehicle']})",
        "",
        "Real Form D filers raising real money, named after a universe company "
        "and not being it. A vehicle must never be linked to a company: its "
        "raise would land on the company's round timeline.",
        "",
    ]
    out += _table(rows, "vehicle")
    out += [
        f"### Proposed `not_in_universe` ({counts['not_in_universe']})",
        "",
        "A different company whose name collides with a frozen pattern.",
        "",
    ]
    out += _table(rows, "not_in_universe")
    if counts["unresolved"]:
        out += [f"### Proposed `unresolved` ({counts['unresolved']})", ""]
        out += _table(rows, "unresolved")

    out += ["## Evidence, per candidate", ""]
    for r in sorted(rows, key=lambda r: (r["proposed_verdict"], -int(r["filings"] or 0))):
        out.append(f"**`{r['cik']}` {r['entity_name']}** — proposed "
                   f"`{r['proposed_verdict']}`, {r['filings']} filing(s)")
        for reason in r["reasons"]:
            out.append(f"  - {reason}")
        edgar = r.get("edgar")
        if edgar and not edgar.get("error"):
            former = ", ".join(edgar["former_names"]) or "none"
            out.append(
                f"  - EDGAR: incorporated {edgar['state_of_incorporation']}, "
                f"{edgar['city']}, former names: {former}; "
                f"{edgar['form_d_count']} Form D filings "
                f"{edgar['form_d_first']} → {edgar['form_d_last']}")
        out.append("")

    decided = data["summary"]["by_verdict"]
    out += ["## Decisions recorded so far", ""]
    if decided:
        out += ["| Verdict | CIKs |", "|---|---|"]
        out += [f"| `{d['verdict']}` | {d['ciks']} |" for d in decided]
    else:
        out.append("_none — `company_identity` is empty, so `form_d.resolved()` "
                   "returns nothing. That is the correct state before a review._")
    out.append("")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true", help=f"write {REPORT.name}")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--edgar", action="store_true",
                    help="enrich each candidate with EDGAR facts (one request per CIK)")
    ap.add_argument("--affirm", metavar="CIK")
    ap.add_argument("--affirm-proposed", metavar="VERDICT",
                    help="affirm every undecided candidate the proposer gave "
                         "this verdict. Only 'vehicle' and 'not_in_universe' "
                         "are allowed: neither joins to anything, so one human "
                         "judgment covers the class. An operating_company "
                         "verdict creates a join and is decided one at a time.")
    ap.add_argument("--verdict")
    ap.add_argument("--company")
    ap.add_argument("--reviewer")
    ap.add_argument("--evidence")
    args = ap.parse_args()

    conn = connect()
    try:
        if args.affirm_proposed:
            if args.affirm_proposed not in ("vehicle", "not_in_universe"):
                raise SystemExit(
                    "--affirm-proposed takes 'vehicle' or 'not_in_universe'. "
                    "An operating_company verdict is what creates a join, and "
                    "it is affirmed one CIK at a time so that the reviewer "
                    "sees each one -- 'x.ai, inc.' and 'X.AI CORP.' normalise "
                    "to the same string and only one of them is xAI.")
            done = []
            for row in build(conn)["candidates"]:
                if row["already_decided"] or                         row["proposed_verdict"] != args.affirm_proposed:
                    continue
                done.append(affirm(
                    conn, cik=row["cik"], verdict=args.affirm_proposed,
                    reviewer=args.reviewer,
                    evidence=f"{args.evidence} | proposer reasons: "
                             + "; ".join(row["reasons"])))
            print(json.dumps({"affirmed": len(done),
                              "verdict": args.affirm_proposed,
                              "ciks": [d["cik"] for d in done]}, indent=2))
            return
        if args.affirm:
            print(json.dumps(affirm(
                conn, cik=args.affirm, verdict=args.verdict,
                reviewer=args.reviewer, evidence=args.evidence,
                company=args.company), indent=2))
            return
        data = build(conn, with_edgar=args.edgar)
        if args.json:
            print(json.dumps(data, indent=2, default=str))
        if args.report or not args.json:
            REPORT.write_text(render(data), encoding="utf-8", newline="\n")
            print(f"wrote {REPORT}")
            print(f"{len(outstanding(conn))} candidate CIKs still undecided")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
