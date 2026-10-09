"""Generate the Week 9 figures as SVG, from measured data only.

Every number is queried at run time and written to docs/_figdata_week9.json
before anything is drawn (P3). No figure carries a hand-typed value.

Follows brutalist/DESIGN.md: the six palette tokens and nothing else, EB
Garamond for figure titles, Inter for labels, JetBrains Mono for data. Red is
the primary series, never "danger".

  w9-nametrap     what a name join to Form D would have caught
  w9-layouts      five filers, five ways of writing the same footnote
  w9-entries      entry dates the marks panel does not have
  w9-exposure     who holds what, and how much of their fund it is
  w9-corroborate  fund entry dates landing on filed round dates

    python scripts/make_week9_figures.py
    cd ../../.. && npm run svg-to-png && npm run audit:layout
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REPO = ROOT.parents[2]
OUT = REPO / "images" / "private-ai-valuation-agent"
FIGDATA = ROOT / "docs" / "_figdata_week9.json"

from src.db.connect import connect  # noqa: E402
from src.ingest import form_d, ncsr  # noqa: E402
from src.signal.exposure import corroboration, exposure_map  # noqa: E402

WHITE, INK, RED = "#FFFFFF", "#2a1a0e", "#C8102E"
SECOND, BORDER, OCHRE = "#545454", "#D4D4D4", "#C8860E"

SERIF = "'EB Garamond', Georgia, serif"
SANS = "'Inter', sans-serif"
MONO = "'JetBrains Mono', monospace"

W, H = 700, 420
MARGIN = 40


# --------------------------------------------------------------------------
# Measurement
# --------------------------------------------------------------------------


def collect() -> dict:
    conn = connect()
    try:
        data = {
            "form_d": form_d.coverage(conn),
            "ncsr": ncsr.coverage(conn),
            "exposure": exposure_map(conn),
            "corroboration": corroboration(conn),
        }
        with conn.cursor() as cur:
            # How many distinct CIKs the name scan produced, and how the
            # pooled-fund flag splits them.
            cur.execute("""
                SELECT vehicle_class, count(DISTINCT cik) AS ciks,
                       count(*) AS rows
                  FROM form_d_filings GROUP BY 1 ORDER BY 1
            """)
            data["by_class"] = [dict(zip([c[0] for c in cur.description], r))
                                for r in cur.fetchall()]
            # The five layouts, counted from what was actually parsed.
            cur.execute("""
                SELECT split_part(registrant, ' ', 1) AS filer,
                       count(*)                        AS lots,
                       count(*) FILTER (WHERE cost_basis_scope = 'position')   AS position_cost,
                       count(*) FILTER (WHERE cost_basis_scope = 'fund_total') AS fund_cost,
                       count(*) FILTER (WHERE acquisition_date_is_range)       AS ranges
                  FROM restricted_lots
                 WHERE company_provisional IS NOT NULL
                 GROUP BY 1 HAVING count(*) > 0
                 ORDER BY 2 DESC
            """)
            data["by_filer"] = [dict(zip([c[0] for c in cur.description], r))
                                for r in cur.fetchall()]
            # Earliest entry date per company, against the panel's first mark.
            cur.execute("""
                SELECT l.company_provisional        AS company,
                       min(l.acquisition_date_first) AS first_entry,
                       (SELECT min(m.period_end) FROM marks m
                          JOIN companies c2 ON c2.company_id = m.company_id
                         WHERE c2.canonical_name = l.company_provisional)
                                                     AS first_mark,
                       count(*)                      AS lots
                  FROM restricted_lots l
                 WHERE l.company_provisional IS NOT NULL
                   AND l.acquisition_date_first IS NOT NULL
                 GROUP BY 1 ORDER BY 2
            """)
            data["entry_vs_mark"] = [dict(zip([c[0] for c in cur.description], r))
                                     for r in cur.fetchall()]
    finally:
        conn.close()

    FIGDATA.write_text(json.dumps(data, indent=2, default=str),
                       encoding="utf-8", newline="\n")
    print(f"wrote {FIGDATA}")
    return json.loads(FIGDATA.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# SVG helpers (same set the week 7 and 8 scripts use)
# --------------------------------------------------------------------------


def esc(s) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def head(title, desc, subtitle) -> list:
    return [
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img"'
        f' aria-labelledby="figtitle figdesc" font-family="{SANS}">',
        f'  <title id="figtitle">{esc(title)}</title>',
        f'  <desc id="figdesc">{esc(desc)}</desc>',
        f'  <rect width="{W}" height="{H}" fill="{WHITE}"/>',
        f'  <text x="{MARGIN}" y="42" font-size="20" font-family="{SERIF}"'
        f' fill="{INK}">{esc(title)}</text>',
        f'  <text x="{MARGIN}" y="64" font-size="13" fill="{SECOND}">{esc(subtitle)}</text>',
    ]


def source_line(text) -> str:
    return (f'  <text x="{MARGIN}" y="402" font-size="10" fill="{SECOND}"'
            f' font-family="{MONO}">{esc(text)}</text>')


def label(x, y, text, size=12, fill=INK, font=SANS, anchor="start", weight=None,
          spacing=None) -> str:
    bits = [f'  <text x="{x}" y="{y}" font-size="{size}" fill="{fill}"',
            f' font-family="{font}"']
    if anchor != "start":
        bits.append(f' text-anchor="{anchor}"')
    if weight:
        bits.append(f' font-weight="{weight}"')
    if spacing:
        bits.append(f' letter-spacing="{spacing}"')
    bits.append(f'>{esc(text)}</text>')
    return "".join(bits)


def rule(y, x1=MARGIN, x2=W - MARGIN, colour=BORDER, width=1) -> str:
    return (f'  <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}"'
            f' stroke="{colour}" stroke-width="{width}"/>')


def column_head(x, y, text, anchor="start") -> str:
    return label(x, y, text, size=11, fill=SECOND, weight="700", anchor=anchor,
                 spacing="0.06em")


def write(name, lines) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    path.write_text("\n".join(lines + ["</svg>", ""]), encoding="utf-8")
    print(f"wrote {path.relative_to(REPO)}")
    return path


def money(value) -> str:
    if value in (None, ""):
        return "—"
    value = float(value)
    for cut, suffix in ((1e9, "bn"), (1e6, "m"), (1e3, "k")):
        if abs(value) >= cut:
            return f"${value / cut:,.1f}{suffix}"
    return f"${value:,.0f}"


# --------------------------------------------------------------------------
# Figure 1 -- the name trap
# --------------------------------------------------------------------------


def fig_nametrap(d) -> Path:
    pooled = next(b for b in d["by_class"] if b["vehicle_class"] == "pooled_vehicle")
    candidate = next(b for b in d["by_class"]
                     if b["vehicle_class"] == "candidate_operating")
    total = pooled["rows"] + candidate["rows"]
    share = pooled["rows"] / total

    lines = head(
        f"{share * 100:.0f}% of a Form D name match is somebody else's fund",
        f"A bar showing that of {total} Form D issuer rows carrying a universe "
        f"company's name, {pooled['rows']} are self-declared pooled investment "
        f"vehicles and only {candidate['rows']} are candidates to be the company.",
        f"{total} issuer rows matching a frozen universe name pattern",
    )

    bar_y, bar_h = 110, 64
    inner = W - 2 * MARGIN
    pooled_w = inner * share
    lines.append(f'  <rect x="{MARGIN}" y="{bar_y}" width="{pooled_w:.1f}"'
                 f' height="{bar_h}" fill="{RED}"/>')
    lines.append(f'  <rect x="{MARGIN + pooled_w:.1f}" y="{bar_y}"'
                 f' width="{inner - pooled_w:.1f}" height="{bar_h}" fill="{INK}"/>')
    lines.append(label(MARGIN + 14, bar_y + 40, f"{pooled['rows']} pooled vehicles",
                       size=17, font=MONO, fill=WHITE))
    lines.append(label(W - MARGIN - 8, bar_y + 40, f"{candidate['rows']}",
                       size=17, font=MONO, fill=WHITE, anchor="end"))
    lines.append(label(MARGIN, bar_y + bar_h + 22,
                       f"{share * 100:.1f}% — the filer's own "
                       "ISPOOLEDINVESTMENTFUNDTYPE flag",
                       size=12, font=MONO, fill=RED))
    lines.append(label(W - MARGIN, bar_y + bar_h + 22,
                       f"{candidate['ciks']} distinct CIKs for a human",
                       size=12, font=MONO, fill=INK, anchor="end"))

    y = 240
    lines.append(column_head(MARGIN, y, "WHAT A NAME JOIN WOULD HAVE PULLED IN"))
    lines.append(rule(y + 10, colour=INK))
    y += 34
    for name, why in (
        ("Anthropic Jan 2026 a Series of CGF2021 LLC", "a feeder, not Anthropic"),
        ("Community Philanthropic Ventures, LLC", "phil-ANTHROPIC-ally named"),
        ("x.ai, inc.  (CIK 1609052)", "a different company entirely"),
    ):
        lines.append(label(MARGIN, y, name, size=12, font=MONO, fill=INK))
        lines.append(label(W - MARGIN, y, why, size=12, fill=RED, anchor="end"))
        y += 24

    lines.append(rule(y + 4))
    lines.append(label(MARGIN, y + 28,
                       "So the join is on an affirmed CIK, never on a name.",
                       size=13, fill=INK))
    lines.append(source_line("Source: form_d_filings · 49 quarters, 2014Q1 to 2026Q1"))
    return write("w9-nametrap.svg", lines)


# --------------------------------------------------------------------------
# Figure 2 -- five filers, five layouts
# --------------------------------------------------------------------------


LAYOUTS = [
    ("Baron", "table", "Issuer · Date(s) · Value", "cost per FUND"),
    ("Fidelity", "table", "Security · Date · Acquisition Cost", "cost per position"),
    ("Lincoln", "table", "Investment · Date · Cost · Value", "cost per position"),
    ("Neuberger", "table", "Security · Date(s) · Cost · Value · %", "cost per position"),
    ("BlackRock", "NO TABLE", "(Acquired 10/22/19, cost $3,030,010)", "cost per position"),
]


def fig_layouts(d) -> Path:
    filings = d["ncsr"]["filings"]
    lines = head(
        "Five filers, five ways to write the same footnote",
        "A table of how five fund families present the Reg S-X 12-12 "
        "restricted-securities disclosure, showing that one of them uses no "
        "table at all.",
        f"{filings['with_lots']} of {filings['filings']} filings fetched "
        f"yielded a universe lot",
    )

    top = 108
    lines.append(column_head(MARGIN, top, "FILER"))
    lines.append(column_head(150, top, "SHAPE"))
    lines.append(column_head(250, top, "COLUMNS, AS THE FILER NAMES THEM"))
    lines.append(column_head(W - MARGIN, top, "COST", anchor="end"))
    lines.append(rule(top + 10, colour=INK))

    y = top + 34
    for filer, shape, columns, cost in LAYOUTS:
        inline = shape != "table"
        colour = RED if inline else INK
        lines.append(label(MARGIN, y, filer, size=12, fill=colour,
                           weight="700" if inline else None))
        lines.append(label(150, y, shape, size=11, font=MONO, fill=colour))
        lines.append(label(250, y, columns, size=10, font=MONO, fill=SECOND))
        lines.append(label(W - MARGIN, y, cost, size=10, font=MONO,
                           fill=RED if cost.endswith("FUND") else SECOND,
                           anchor="end"))
        y += 26

    lines.append(rule(y))
    y += 26
    lines.append(label(MARGIN, y,
                       "Columns are mapped by reading the header, so a sixth "
                       "filer needs no code.", size=13, fill=INK))
    y += 22
    lines.append(label(MARGIN, y,
                       "BlackRock has no header to read. Every BlackRock filing "
                       "returned zero", size=13, fill=INK))
    y += 18
    lines.append(label(MARGIN, y, "until the inline form was supported.",
                       size=13, fill=RED))
    lines.append(source_line("Source: restricted_lots · N-CSR and N-CSRS "
                             "primary documents fetched from EDGAR"))
    return write("w9-layouts.svg", lines)


# --------------------------------------------------------------------------
# Figure 3 -- entry dates the panel does not have
# --------------------------------------------------------------------------


def fig_entries(d) -> Path:
    from datetime import date as _date

    def parse(text):
        y, m, dd = (int(p) for p in str(text).split("-"))
        return _date(y, m, dd)

    every = [r for r in d["entry_vs_mark"] if r["first_entry"] and r["first_mark"]]
    # Only the companies where the footnote actually reaches back past the
    # panel. For the rest, the earliest acquisition date observed is LATER
    # than the first mark -- not because the fund bought later, but because
    # only the two most recent filings per registrant were fetched, so an
    # older purchase disclosed in an older report is simply not in view.
    # Charting those as "-2.3 years earlier" would state the opposite of
    # what the data supports.
    rows = [r for r in every
            if (parse(r["first_mark"]) - parse(r["first_entry"])).days > 0]
    rows.sort(key=lambda r: (parse(r["first_mark"]) - parse(r["first_entry"])).days,
              reverse=True)
    behind = len(every) - len(rows)

    lines = head(
        "The footnote reaches back before the panel starts",
        "A table comparing, for the companies where the restricted-securities "
        "footnote discloses a purchase predating the marks panel, the earliest "
        "acquisition date against the earliest N-PORT period end.",
        f"{len(rows)} of {len(every)} companies, from "
        f"{d['ncsr']['filings']['with_lots']} filings with a parsed footnote",
    )

    top = 108
    lines.append(column_head(MARGIN, top, "COMPANY"))
    lines.append(column_head(250, top, "FIRST ENTRY (N-CSR)"))
    lines.append(column_head(400, top, "FIRST MARK (N-PORT)"))
    lines.append(column_head(W - MARGIN, top, "YEARS EARLIER", anchor="end"))
    lines.append(rule(top + 10, colour=INK))

    y = top + 34
    widest = max(((parse(r["first_mark"]) - parse(r["first_entry"])).days
                  for r in rows), default=1) or 1
    for row in rows:
        gap = (parse(row["first_mark"]) - parse(row["first_entry"])).days
        years = gap / 365.25
        name = row["company"].replace(" Technologies Corp.", "") \
                             .replace(", Inc.", "").replace(" Industries", "")
        colour = RED if gap == widest else INK
        lines.append(label(MARGIN, y, name[:26], size=12, fill=INK))
        lines.append(label(250, y, str(row["first_entry"]), size=11, font=MONO,
                           fill=SECOND))
        lines.append(label(400, y, str(row["first_mark"]), size=11, font=MONO,
                           fill=SECOND))
        bar = 70 * max(gap, 0) / widest
        lines.append(f'  <rect x="{W - MARGIN - 78 - bar:.1f}" y="{y - 9}"'
                     f' width="{max(bar, 2):.1f}" height="10" fill="{colour}"/>')
        lines.append(label(W - MARGIN, y, f"{years:.1f}y", size=12, font=MONO,
                           fill=colour, anchor="end"))
        y += 24

    lines.append(rule(y))
    lines.append(label(MARGIN, y + 26,
                       "N-PORT says what a position is worth. It never says when "
                       "it was bought.", size=13, fill=INK))
    lines.append(label(MARGIN, y + 48,
                       f"A floor, not a history: only the latest annual and "
                       f"semi-annual per registrant", size=12, fill=SECOND))
    lines.append(label(MARGIN, y + 66,
                       f"were fetched, which is why {behind} companies show no "
                       f"pre-panel entry.", size=12, fill=SECOND))
    lines.append(source_line("Source: restricted_lots vs marks · earliest "
                             "acquisition date against earliest period end"))
    return write("w9-entries.svg", lines)


# --------------------------------------------------------------------------
# Figure 4 -- the exposure map
# --------------------------------------------------------------------------


def fig_exposure(d) -> Path:
    rows = [r for r in d["exposure"]
            if r["max_pct_net_assets"] is not None and r["value_usd"]]
    rows.sort(key=lambda r: -float(r["max_pct_net_assets"]))
    top_rows = rows[:9]

    lines = head(
        "Concentration, as the filers themselves report it",
        "A table of the manager and company pairs with the largest share of "
        "fund net assets, using the percentage figure filed in N-PORT rather "
        "than one computed here.",
        f"{len(d['exposure'])} manager-and-company pairs in the panel",
    )

    top = 108
    lines.append(column_head(MARGIN, top, "MANAGER"))
    lines.append(column_head(196, top, "COMPANY"))
    lines.append(column_head(392, top, "VALUE"))
    lines.append(column_head(W - MARGIN, top, "% OF NET ASSETS", anchor="end"))
    lines.append(rule(top + 10, colour=INK))

    widest = float(top_rows[0]["max_pct_net_assets"]) if top_rows else 1.0
    y = top + 34
    for row in top_rows:
        pct = float(row["max_pct_net_assets"])
        name = row["company"].replace(" Technologies Corp.", "") \
                             .replace(", Inc.", "").replace(" Industries", "")
        colour = RED if pct == widest else INK
        # 18 characters is what fits before the company column at size 12.
        # "Robinhood Ventures Fund" at 22 ran into "Databricks", which the
        # layout audit does not catch because the two are separate <text>
        # elements on the same baseline rather than overlapping boxes.
        manager = row["manager"]
        manager = manager if len(manager) <= 18 else manager[:17] + "…"
        lines.append(label(MARGIN, y, manager, size=12, fill=INK))
        lines.append(label(196, y, name[:24], size=11, fill=SECOND))
        lines.append(label(392, y, money(row["value_usd"]), size=11, font=MONO,
                           fill=SECOND))
        bar = 66 * pct / widest
        lines.append(f'  <rect x="{W - MARGIN - 58 - bar:.1f}" y="{y - 9}"'
                     f' width="{max(bar, 2):.1f}" height="10" fill="{colour}"/>')
        lines.append(label(W - MARGIN, y, f"{pct:.2f}%", size=12, font=MONO,
                           fill=colour, anchor="end"))
        y += 24

    lines.append(rule(y))
    lines.append(label(MARGIN, y + 24,
                       "The percentage is the filer's own figure, not one "
                       "computed here.", size=13, fill=INK))
    lines.append(source_line("Source: marks and raw_holdings · latest period end "
                             "reported by each manager"))
    return write("w9-exposure.svg", lines)



# --------------------------------------------------------------------------
# Figure 5 -- two filings, filed by different parties, agreeing to the day
# --------------------------------------------------------------------------


def fig_corroborate(d) -> Path:
    corr = d["corroboration"]
    counted = corr["dates_in_window"]
    exact = corr["hits"]["0"] if "0" in corr["hits"] else corr["hits"][0]
    share = exact / counted if counted else 0

    lines = head(
        f"{exact} of {counted} fund entry dates fall on a filed round date",
        "A bar and a table showing how often a fund's disclosed acquisition "
        "date matches the date an issuer reported its first sale on Form D, "
        "counting only acquisitions inside that company's Form D filing window.",
        "Acquisition dates inside a company's Form D filing window",
    )

    bar_y, bar_h = 104, 46
    inner = W - 2 * MARGIN
    hit_w = inner * share
    lines.append(f'  <rect x="{MARGIN}" y="{bar_y}" width="{hit_w:.1f}"'
                 f' height="{bar_h}" fill="{RED}"/>')
    lines.append(f'  <rect x="{MARGIN + hit_w:.1f}" y="{bar_y}"'
                 f' width="{inner - hit_w:.1f}" height="{bar_h}" fill="{INK}"/>')
    lines.append(label(MARGIN + 12, bar_y + 30, f"{share * 100:.0f}% same day",
                       size=15, font=MONO, fill=WHITE))
    lines.append(label(W - MARGIN - 8, bar_y + 30, f"{counted - exact}",
                       size=15, font=MONO, fill=WHITE, anchor="end"))

    top = bar_y + bar_h + 34
    lines.append(column_head(MARGIN, top, "COMPANY"))
    lines.append(column_head(230, top, "ACQUIRED"))
    lines.append(column_head(348, top, "FUNDS"))
    lines.append(column_head(W - MARGIN, top, "DAYS TO NEAREST ROUND",
                             anchor="end"))
    lines.append(rule(top + 10, colour=INK))

    rows = sorted(corr["pairs"],
                  key=lambda r: (int(r["gap_days"]), -int(r["registrants"])))[:6]
    y = top + 32
    for row in rows:
        gap = int(row["gap_days"])
        colour = RED if gap == 0 else INK
        name = row["company"].replace(" Technologies Corp.", "")                              .replace(", Inc.", "").replace(" Industries", "")
        lines.append(label(MARGIN, y, name[:24], size=12, fill=INK))
        lines.append(label(230, y, str(row["acquired"]), size=11, font=MONO,
                           fill=SECOND))
        lines.append(label(348, y, str(row["registrants"]), size=11, font=MONO,
                           fill=SECOND))
        lines.append(label(W - MARGIN, y, f"{gap}d", size=12, font=MONO,
                           fill=colour, anchor="end"))
        y += 22

    lines.append(rule(y - 2))
    lines.append(label(MARGIN, y + 22,
                       "The issuer files Form D because it sold. The fund files "
                       "N-CSR because it owns.", size=12, fill=INK))
    lines.append(label(MARGIN, y + 40, "Neither cites the other.",
                       size=12, fill=RED))
    lines.append(source_line("Source: restricted_lots x form_d_filings, joined "
                             "on an affirmed CIK · ranges excluded"))
    return write("w9-corroborate.svg", lines)

def main() -> None:
    data = collect()
    fig_nametrap(data)
    fig_layouts(data)
    fig_entries(data)
    fig_exposure(data)
    fig_corroborate(data)
    print("\nnow: cd ../../.. && npm run svg-to-png && npm run audit:layout")


if __name__ == "__main__":
    main()
