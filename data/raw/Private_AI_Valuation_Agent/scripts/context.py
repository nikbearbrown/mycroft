"""Week 9's reports: the exposure map, the timelines, and the context coverage.

    python -m scripts.context --report     # docs/context.md + docs/_context.json
    python -m scripts.context --json       # machine view only

Two customers, twice (P5). `docs/context.md` is for the person who wants to
know who holds what and when they bought it; `docs/_context.json` is the same
content for anything downstream, and is what the Week 9 figures are drawn
from.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db.connect import connect  # noqa: E402
from src.ingest import form_d, ncsr  # noqa: E402
from src.resolve.identity import summary as identity_summary  # noqa: E402
from src.signal.exposure import (  # noqa: E402
    NOT_COMPUTED, corroboration, exposure_map,
    summary as exposure_summary, timeline,
)

REPORT = ROOT / "docs" / "context.md"
DATA = ROOT / "docs" / "_context.json"

# plan.md scopes the N-CSR work to "the top three companies by coverage".
TOP_THREE = list(ncsr.TOP_THREE)


def build(conn) -> dict:
    return {
        "form_d": form_d.coverage(conn),
        "identity": identity_summary(conn),
        "ncsr": ncsr.coverage(conn),
        "exposure_summary": exposure_summary(conn),
        "exposure_map": exposure_map(conn),
        "corroboration": corroboration(conn),
        "timelines": {name: timeline(conn, name) for name in TOP_THREE},
        "not_computed": list(NOT_COMPUTED),
    }


def _money(value) -> str:
    if value in (None, ""):
        return "—"
    value = float(value)
    for cut, suffix in ((1e9, "bn"), (1e6, "m"), (1e3, "k")):
        if abs(value) >= cut:
            return f"${value / cut:,.1f}{suffix}"
    return f"${value:,.0f}"


def render(data: dict) -> str:
    fd, ident, nc = data["form_d"], data["identity"], data["ncsr"]
    pooled = next((b["rows"] for b in fd["by_class"]
                   if b["vehicle_class"] == "pooled_vehicle"), 0)
    candidates = next((b["rows"] for b in fd["by_class"]
                       if b["vehicle_class"] == "candidate_operating"), 0)

    out = [
        "# Context: Form D, N-CSR and the exposure map",
        "",
        "Week 9 adds two sources beside the N-PORT marks panel. Neither of them "
        "produces a price, and neither can produce a valuation; both answer "
        "questions the marks panel structurally cannot.",
        "",
        "| Source | Answers | Cannot answer |",
        "|---|---|---|",
        "| N-PORT (weeks 1–8) | what a position is worth on a period end | when "
        "it was bought, what was paid |",
        "| **N-CSR / N-CSRS** footnote (Reg S-X 12-12) | acquisition date, and "
        "cost where the filer gives it per position | anything about the company "
        "as a whole |",
        "| **Form D** | when an offering was made and how much was sold | any "
        "price — it carries no share count |",
        "",
        "---",
        "",
        "## 1. Form D: why a name join would have been wrong",
        "",
        f"The scan covers **{fd['quarters_scanned']} quarters**, "
        f"`{fd['first_quarter']}` → `{fd['last_quarter']}`, and returns "
        f"**{fd['rows']} issuer rows** whose entity name matches a universe "
        f"pattern, filed between {fd['first_filing_date']} and "
        f"{fd['last_filing_date']}.",
        "",
        f"**{pooled} of those {fd['rows']} rows are pooled investment "
        f"vehicles.** Not "
        "a near-miss, not a long tail: the overwhelming majority. "
        "\"Anthropic Jan 2026 a Series of CGF2021 LLC\", \"SpaceX Tender Dec "
        "2025 a Series of CGF2021 LLC\", \"HII Cerebras V, a Series of HII "
        "Cerebras, LLC\" — feeder vehicles raising money from accredited "
        "investors to buy existing shares on the secondary market. Their "
        "`TOTALAMOUNTSOLD` is the feeder's raise and has nothing to do with a "
        "round by the company.",
        "",
        "Summing them per company and labelling the result \"round timing and "
        "amounts\" would have produced a clean-looking table of numbers that no "
        "universe company's filing ever produced. That is the P3 failure with a "
        "plausible chart attached.",
        "",
        "So the classification uses the **filer's own declaration** — the "
        "offering's `ISPOOLEDINVESTMENTFUNDTYPE` flag — rather than an inference "
        "from the name. A filed fact, not a guess.",
        "",
        f"That leaves **{candidates} rows across "
        f"{sum(1 for _ in ident.get('by_verdict', [])) or ident['outstanding'] + len(ident.get('operating_companies', []))} "
        "distinct CIKs** for a human, and the machine stops there. The reason it "
        "has to stop is in `docs/identity_queue.md`; three examples:",
        "",
        "- **`x.ai, inc.` (CIK 1609052)** normalises to exactly the same string "
        "as **`X.AI CORP.` (CIK 2002695)**. One is a Delaware company in New "
        "York that filed four Form Ds between 2014 and 2017; the other is a "
        "Nevada company in Palo Alto that started filing in 2023. No amount of "
        "string work separates them.",
        "- **`Community Philanthropic Ventures, LLC`** matches `%ANTHROPIC%`, "
        "because *phil-anthropic* contains it.",
        "- **`Gaingels Databricks 2024 LLC`** is a feeder with no pooling token "
        "in its name and no pooled-fund flag set. A rule wide enough to catch it "
        "would catch operating companies that file as LLCs.",
        "",
    ]

    if ident["operating_companies"]:
        out += ["**Affirmed identities:**", "",
                "| Company | CIK | Filed as |", "|---|---|---|"]
        out += [f"| {r['company']} | `{r['cik']}` | {r['entity_name']} |"
                for r in ident["operating_companies"]]
        out.append("")
    else:
        out += [
            f"**No identity has been affirmed yet** — {ident['outstanding']} "
            "candidate CIKs are waiting on a named reviewer, so "
            "`form_d.resolved()` returns nothing and every timeline's Form D "
            "leg is empty. That is the designed state before a review, not a "
            "gap: the join does not exist until a human creates it (P1, P4).",
            "",
        ]

    out += [
        f"> **Archive note.** {fd['archive_gap']}",
        "",
        "### What the archive says about the largest issuers",
        "",
        "**Anthropic, OpenAI, Anduril and Cerebras have filed no Form D under "
        "their own identity** anywhere in the published archive. Every hit on "
        "their names is a vehicle. Cerebras has an EDGAR filer record, but it "
        "was created by the S-1 registration path — its first filing is a DRS "
        "in June 2024, and there is no `D` among them.",
        "",
        "Two explanations fit and this project cannot distinguish them from "
        "filings alone: either those rounds relied on the statutory Section "
        "4(a)(2) private-placement exemption, which requires no Form D, or they "
        "were filed in a form or quarter the archive does not carry. The "
        "observation is reported; the cause is not.",
        "",
        "---",
        "",
        "## 2. N-CSR: the entry dates N-PORT does not have",
        "",
        f"**{nc['filings']['filings']} filings** fetched across "
        f"**{nc['filings']['registrants']} registrants** "
        f"({int(nc['filings']['bytes_fetched']) / 1e9:.2f} GB), of which "
        f"**{nc['filings']['with_footnote']}** disclose restricted securities "
        f"and **{nc['filings']['with_lots']}** yielded a universe lot.",
        "",
        "There is no bulk data set for N-CSR and no prescribed layout — Reg S-X "
        "names the required contents, not the columns. Five filers write it five "
        "ways, so the parser maps columns by reading the **header** rather than "
        "by knowing the filer. A sixth filer with a labelled header works without "
        "a code change.",
        "",
        "| Filer | Layout |",
        "|---|---|",
        "| Baron | table · Name of Issuer, Acquisition Date(s), Value · cost "
        "given once **per fund** |",
        "| Fidelity | table · Security, Acquisition Date, Acquisition Cost ($) |",
        "| Lincoln | table · Investment, Date of Acquisition, Cost, Value |",
        "| Neuberger | table · + Value and Percentage of Net Assets |",
        "| **BlackRock** | **no table** · `(Acquired 10/22/19, cost $3,030,010)` "
        "inline in the Schedule of Investments line item |",
        "",
    ]

    if nc["by_company"]:
        out += ["| Company | Lots | Registrants | Position cost | Date ranges | "
                "Earliest entry | Latest entry |", "|---|---|---|---|---|---|---|"]
        for row in nc["by_company"]:
            out.append(
                f"| {row['company']} | {row['lots']} | {row['registrants']} | "
                f"{row['with_position_cost']} | {row['date_ranges']} | "
                f"{row['earliest_entry']} | {row['latest_entry']} |")
        out.append("")

    out += [
        "Two properties of the filed format are carried as columns rather than "
        "flattened away:",
        "",
        "- **Acquisition dates are often ranges.** Baron files "
        "`11/15/2017-8/4/2020` for a SpaceX preferred position built across "
        "three years. Both ends are stored; collapsing to one would invent a "
        "precision the filing does not have.",
        "- **Cost is not always per position.** Baron reports one cost for all "
        "restricted securities in a fund and says so — \"See Portfolios of "
        "Investments for cost of individual securities\". "
        "`cost_basis_scope` records `position`, `fund_total` or `absent`, so a "
        "fund total is never read as an entry price.",
        "",
        "---",
        "",
        "## 3. The exposure map",
        "",
        "One row per (manager, company) at the latest period end that manager "
        "reported, with how long they have held it. `max_pct_net_assets` is the "
        "filer's own figure from N-PORT, not value divided by a net-asset number "
        "this project computed.",
        "",
        "| Company | Manager | As of | Positions | Value | Max % of net assets | "
        "First held | Periods |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in data["exposure_map"][:40]:
        pct = row["max_pct_net_assets"]
        out.append(
            f"| {row['company']} | {row['manager']} | {row['as_of']} | "
            f"{row['positions']} | {_money(row['value_usd'])} | "
            f"{float(pct):.2f}% | {row['first_period']} | "
            f"{row['periods_held']} |" if pct is not None else
            f"| {row['company']} | {row['manager']} | {row['as_of']} | "
            f"{row['positions']} | {_money(row['value_usd'])} | — | "
            f"{row['first_period']} | {row['periods_held']} |")
    if len(data["exposure_map"]) > 40:
        out.append(f"| … | _{len(data['exposure_map']) - 40} more rows in "
                   "`docs/_context.json`_ | | | | | | |")
    out.append("")

    corr = data["corroboration"]
    counted = corr["dates_in_window"]
    exact = corr["hits"].get(0, corr["hits"].get("0", 0))
    week = corr["hits"].get(7, corr["hits"].get("7", 0))

    out += [
        "---",
        "",
        "## 4. The two sources agree, and neither cites the other",
        "",
        "This is what joining them was for. The issuer files Form D because it "
        "sold securities; the fund files N-CSR because it owns them. Neither "
        "references the other, so agreement between the two is evidence rather "
        "than arithmetic.",
        "",
        f"**{exact} of {counted} fund acquisition dates fall on the exact day "
        f"an issuer reported a first sale** ({exact / counted * 100:.0f}%), and "
        f"{week} of {counted} fall within a week.",
        "",
        "| Company | Acquired | Funds | Days to nearest filed round |",
        "|---|---|---|---|",
    ]
    for row in sorted(corr["pairs"],
                      key=lambda r: (int(r["gap_days"]), -int(r["registrants"]))):
        out.append(f"| {row['company']} | {row['acquired']} | "
                   f"{row['registrants']} | {row['gap_days']} |")
    out += [
        "",
        "**The denominator is the method.** Only acquisitions *inside* a "
        "company's Form D filing window are counted. SpaceX stopped filing "
        "Form D in July 2022 and 9 of its 13 single-date acquisitions come "
        "after that; measured against the nearest round they give gaps of 873, "
        "911, 1090 and 1293 days, and every one of those numbers is the "
        "distance to the end of the archive rather than anything about when a "
        "fund bought. Left in, a real 56% agreement reads as 33%.",
        "",
        "Date ranges are excluded for the same reason: a position built across "
        "three years has no single acquisition date, and picking an endpoint "
        "would manufacture either the match or the miss.",
        "",
        "| Company | Form D window | Single dates outside it |",
        "|---|---|---|",
    ]
    for row in corr["by_company"]:
        out.append(f"| {row['company']} | {row['first_round']} → "
                   f"{row['last_round']} | {row['dates_outside_window']} of "
                   f"{row['dates_total']} |")
    out += [
        "",
        f"> **What this is not.** {corr['caveat']}",
        "",
    ]

    out += ["---", "", "## 5. Timelines for the top three by coverage", ""]
    for name in TOP_THREE:
        tl = data["timelines"][name]
        out += [
            f"### {name}",
            "",
            f"- **N-PORT:** {tl['n_port']['periods']} period ends, "
            f"{tl['n_port']['first_period']} → {tl['n_port']['last_period']}.",
            f"- **N-CSR:** {tl['n_csr']['lots']} restricted lots, "
            f"{tl['n_csr']['with_position_cost']} with a position-level cost; "
            f"earliest acquisition {tl['n_csr']['earliest_entry']}.",
            f"- **Form D:** {tl['form_d']['filings']} filings — "
            f"{tl['form_d']['note']}",
            "",
        ]
        lots = tl["n_csr"]["entries"][:10]
        if lots:
            # `Reported` is the filing's period end, not the acquisition
            # date. Without it the same lot appears twice with no explanation
            # -- a registrant's annual and semi-annual both disclose it, and
            # both are real filings.
            out += ["| Registrant | Fund | Reported | Acquired | Cost | Scope | "
                    "Value | Cost→value |",
                    "|---|---|---|---|---|---|---|---|"]
            for lot in lots:
                ratio = lot["cost_to_value"]
                out.append(
                    f"| {lot['registrant'][:32]} | {lot['fund_name'] or '—'} | "
                    f"{lot['report_date']} ({lot['form_type']}) | "
                    f"{lot['acquisition_date_raw']} | {_money(lot['cost_usd'])} | "
                    f"`{lot['cost_basis_scope']}` | {_money(lot['value_usd'])} | "
                    f"{f'{ratio:.2f}×' if ratio else '—'} |")
            if len(tl["n_csr"]["entries"]) > 10:
                out.append(f"| … | _{len(tl['n_csr']['entries']) - 10} more_ | "
                           "| | | | | |")
            out.append("")

    out += [
        "---",
        "",
        "## What none of this computes",
        "",
    ]
    out += [f"{i}. {line}" for i, line in enumerate(data["not_computed"], 1)]
    out += [
        "",
        "The first one is the tempting one. Holding an entry cost and a current "
        "mark, dividing them looks like a return — and it is not, because the "
        "cost belongs to a number of shares that may have changed since. Week 7 "
        "confirmed seven splits and blocked 301 marks for exactly that reason. "
        "Where one filed row carries both a position cost and a position value, "
        "that ratio is reported as `cost→value`, because it is a comparison the "
        "filer made.",
        "",
    ]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    conn = connect()
    try:
        data = build(conn)
    finally:
        conn.close()

    if args.json:
        print(json.dumps(data, indent=2, default=str))
    if args.report or not args.json:
        DATA.write_text(json.dumps(data, indent=2, default=str),
                        encoding="utf-8", newline="\n")
        REPORT.write_text(render(data), encoding="utf-8", newline="\n")
        print(f"wrote {REPORT}")
        print(f"wrote {DATA}")


if __name__ == "__main__":
    main()
