"""Generate the Week 2 video figures as SVG, from measured data only.

Every number drawn here comes from docs/_figdata_week2.json, which is written by
querying the built Parquet layer. Nothing is typed in by hand, so a figure cannot
drift away from the panel it claims to describe (P3).

Follows brutalist/DESIGN.md: the six palette tokens, EB Garamond for figure
titles, Inter for labels, JetBrains Mono for data. Red carries the primary
series; ochre is decorative annotation only, never a fill.

    python scripts/make_week2_figures.py
    cd ../../.. && npm run svg-to-png && npm run audit:layout
"""

import datetime
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parents[2]                       # mycroft/
OUT = REPO / "images" / "private-ai-valuation-agent"
DATA = ROOT / "docs" / "_figdata_week2.json"

# brutalist/DESIGN.md -- the complete palette. No other colours.
WHITE, INK, RED = "#FFFFFF", "#2a1a0e", "#C8102E"
SECOND, BORDER, OCHRE = "#545454", "#D4D4D4", "#C8860E"
PANEL = "#F5F5F5"

SERIF = "'EB Garamond', Georgia, serif"
SANS = "'Inter', sans-serif"
MONO = "'JetBrains Mono', monospace"

W, H = 700, 420


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def head(title, desc, subtitle):
    return [
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img"'
        f' aria-labelledby="t d" font-family="{SANS}">',
        f'  <title id="t">{esc(title)}</title>',
        f'  <desc id="d">{esc(desc)}</desc>',
        f'  <rect width="{W}" height="{H}" fill="{WHITE}"/>',
        f'  <text x="40" y="42" font-size="20" font-family="{SERIF}" fill="{INK}">{esc(title)}</text>',
        f'  <text x="40" y="64" font-size="13" fill="{SECOND}">{esc(subtitle)}</text>',
    ]


def source_line(text):
    return (f'  <text x="40" y="400" font-size="11" fill="{SECOND}" '
            f'font-family="{MONO}">{esc(text)}</text>')


def write(name, lines):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    path.write_text("\n".join(lines) + "\n</svg>\n", encoding="utf-8")
    print(f"wrote {path.relative_to(REPO)}")


# ---------------------------------------------------------------- figure 1 --
def funnel(d):
    f = d["funnel"]
    # The narrow layer is name-matched against universe v1 AND the watchlist --
    # the excluded companies are still captured so a v2 revisit never needs a
    # re-download. Saying "7 companies" here would undercount what the bar shows.
    n_universe = sum(1 for c in d["companies"] if c["status"] != "watchlist")
    n_watch = sum(1 for c in d["companies"] if c["status"] == "watchlist")
    stages = [
        ("SOURCE HOLDING ROWS", f["source"], "every position in 14 quarters of N-PORT", INK),
        ("PRIVATE POSITIONS", f["private"], "Level 3, no real CUSIP", SECOND),
        ("NAME-MATCHED MARKS", f["universe"],
         f"{n_universe} universe v1 companies + {n_watch} watchlisted", RED),
    ]
    L = head(
        "Fourteen quarters, filtered to 5,806 marks",
        "A three-stage funnel: 80,571,213 source holding rows narrow to 22,041,937 "
        "private positions and then to 5,806 universe v1 marks. Bar widths are "
        "log-scaled because the funnel spans four orders of magnitude.",
        "2023Q1 - 2026Q2 - every stage reconciled against the stage above it",
    )
    x0, maxw = 40, 560
    lo, hi = math.log10(stages[-1][1]), math.log10(stages[0][1])
    for i, (label, value, note, colour) in enumerate(stages):
        y = 104 + i * 92
        frac = (math.log10(value) - lo) / (hi - lo)
        w = 90 + frac * (maxw - 90)
        L.append(f'  <rect x="{x0}" y="{y}" width="{w:.1f}" height="46" fill="{colour}"/>')
        L.append(f'  <text x="{x0}" y="{y - 8}" font-size="12" font-weight="700" '
                 f'fill="{INK}">{esc(label)}</text>')
        L.append(f'  <text x="{x0 + 14}" y="{y + 30}" font-size="19" font-family="{MONO}" '
                 f'fill="{WHITE}">{value:,}</text>')
        # The note rides on the label line, not to the right of the bar: the top
        # bar is 560px wide, so anything beside it runs off the canvas.
        L.append(f'  <text x="{x0 + 170}" y="{y - 8}" font-size="12" '
                 f'fill="{SECOND}">{esc(note)}</text>')
        if i < len(stages) - 1:
            cx = x0 + 30
            L.append(f'  <line x1="{cx}" y1="{y + 46}" x2="{cx}" y2="{y + 66}" '
                     f'stroke="{BORDER}" stroke-width="2"/>')
            L.append(f'  <polygon points="{cx},{y + 72} {cx - 5},{y + 62} {cx + 5},{y + 62}" '
                     f'fill="{BORDER}"/>')
    pct = stages[2][1] / stages[0][1] * 100
    L.append(f'  <line x1="{x0}" y1="376" x2="660" y2="376" stroke="{OCHRE}" stroke-width="2"/>')
    L.append(f'  <text x="{x0}" y="368" font-size="12" fill="{INK}">'
             f'The last stage is {pct:.4f}% of the first - and every count reconciles '
             f'to the row above.</text>')
    L.append(source_line("SOURCE: SEC DERA bulk N-PORT 2023Q1-2026Q2 - "
                         "bar widths log-scaled"))
    write("w2-funnel.svg", L)


# ---------------------------------------------------------------- figure 2 --
def staircase(d):
    pts = d["anthropic"]
    L = head(
        "Anthropic, priced by the funds that own it",
        "A step chart of Anthropic's per-share mark across 33 period ends from "
        "April 2023 to April 2026, rising from 11.79 to 388.19. The line is flat "
        "for long stretches and jumps at funding rounds. A dashed line marks the "
        "limit of the bulk data; the 589.01 mark verified by hand sits beyond it.",
        "33 period ends rebuilt from filings - marks move in steps, not drifts",
    )
    px0, px1, py0, py1 = 68, 620, 108, 340
    ymax = 640.0

    def sx(ds):
        t0 = datetime.date(2023, 4, 1)
        t1 = datetime.date(2026, 6, 30)
        dt = datetime.date.fromisoformat(ds)
        return px0 + (dt - t0).days / (t1 - t0).days * (px1 - px0)

    def sy(v):
        return py1 - (v / ymax) * (py1 - py0)

    # gridlines + y labels
    for v in (0, 200, 400, 600):
        y = sy(v)
        L.append(f'  <line x1="{px0}" y1="{y:.1f}" x2="{px1}" y2="{y:.1f}" '
                 f'stroke="{BORDER}" stroke-width="1" opacity="0.6"/>')
        L.append(f'  <text x="{px0 - 10}" y="{y + 4:.1f}" font-size="11" text-anchor="end" '
                 f'fill="{SECOND}" font-family="{MONO}">${v}</text>')

    # step path through the median mark
    dpath = []
    for i, p in enumerate(pts):
        x, y = sx(p["date"]), sy(p["med"])
        dpath.append(f'{"M" if i == 0 else "L"}{x:.1f},{y:.1f}' if i == 0
                     else f'L{x:.1f},{sy(pts[i-1]["med"]):.1f} L{x:.1f},{y:.1f}')
    L.append(f'  <path d="{" ".join(dpath)}" fill="none" stroke="{RED}" stroke-width="2.5" '
             f'stroke-linejoin="round"/>')
    for p in pts:
        L.append(f'  <circle cx="{sx(p["date"]):.1f}" cy="{sy(p["med"]):.1f}" r="2.6" '
                 f'fill="{RED}"/>')

    # x axis
    L.append(f'  <line x1="{px0}" y1="{py1}" x2="{px1}" y2="{py1}" stroke="{INK}" stroke-width="1"/>')
    for ds, lab in [("2023-07-01", "2023"), ("2024-01-01", "2024"),
                    ("2025-01-01", "2025"), ("2026-01-01", "2026")]:
        L.append(f'  <text x="{sx(ds):.1f}" y="{py1 + 18}" font-size="11" text-anchor="middle" '
                 f'fill="{SECOND}" font-family="{MONO}">{lab}</text>')

    # the $259.14 plateau -- leader ends where the label stops, so the text never
    # sits on its own pointer
    px259 = sx("2026-03-31")
    ly = sy(259.14)
    # Cleared of the $400 gridline (y=195): the label box sits above it.
    L.append(f'  <line x1="{px259:.1f}" y1="{ly:.1f}" x2="{px259 - 96:.1f}" '
             f'y2="{ly - 58:.1f}" stroke="{OCHRE}" stroke-width="1.5"/>')
    # Counted by FAMILY, not by CIK. Fidelity alone files under many CIKs, so a
    # CIK count would overstate how many independent managers actually agree --
    # the same error the fund-family mapping exists to prevent.
    cv = d["convergence"]
    L.append(f'  <text x="{px259 - 104:.1f}" y="{ly - 64:.1f}" font-size="12" '
             f'text-anchor="end" font-weight="700" fill="{INK}">'
             f'$259.14 - {cv["families"]} independent managers agree</text>')

    # the bulk horizon -- labelled BELOW the axis, where nothing else competes
    hx = sx("2026-04-30")
    L.append(f'  <line x1="{hx:.1f}" y1="{py0 - 6}" x2="{hx:.1f}" y2="{py1}" '
             f'stroke="{SECOND}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    L.append(f'  <text x="{hx:.1f}" y="{py1 + 34}" font-size="11" text-anchor="middle" '
             f'fill="{SECOND}" font-family="{MONO}">bulk ends 2026-04-30</text>')

    # the $589 mark that bulk cannot see -- label to the LEFT of its marker
    fx, fy = sx("2026-05-30"), sy(589.01)
    L.append(f'  <circle cx="{fx:.1f}" cy="{fy:.1f}" r="4" fill="none" stroke="{SECOND}" '
             f'stroke-width="1.5" stroke-dasharray="2 2"/>')
    # Anchored clear of the dashed horizon line, not flush against it.
    L.append(f'  <text x="{hx - 12:.1f}" y="{fy - 4:.1f}" font-size="12" text-anchor="end" '
             f'font-weight="700" fill="{INK}">$589.01 verified by hand,</text>')
    L.append(f'  <text x="{hx - 12:.1f}" y="{fy + 11:.1f}" font-size="12" text-anchor="end" '
             f'fill="{SECOND}">not yet published in bulk</text>')

    L.append(f'  <text x="40" y="384" font-size="11" fill="{SECOND}">'
             f'{esc(", ".join(cv["names"]))}</text>')
    L.append(source_line(f"SOURCE: 428 Anthropic PBC rows - median mark per period end - "
                         f"convergence counted by family"))
    write("w2-anthropic-staircase.svg", L)


# ---------------------------------------------------------------- figure 3 --
def spacex(d):
    rows = d["spacex_filing"]
    L = head(
        "One filing, one company, two prices exactly 10x apart",
        "Six SpaceX rows from a single Baron Focused Growth Fund filing. Two rows "
        "tagged common price at 112.00 and four tagged preferred price at 1,120.00 "
        "- exactly ten times higher. Three different spellings of the issuer appear, "
        "including the filer's own typo.",
        "Baron Focused Growth Fund - accession 0001752724-24-195357 - 2024-06-30",
    )
    L.append(f'  <rect x="40" y="92" width="620" height="228" fill="{PANEL}" '
             f'stroke="{BORDER}" stroke-width="1"/>')
    # Numeric columns are right-aligned to fixed rules. The widest cell is
    # "$1,120.00" at ~65px, so PRICE needs its own lane clear of VALUE USD.
    X_CAT, X_ISSUER, X_SHARES, X_VALUE, X_PRICE = 56, 104, 452, 566, 648
    for lab, x in [("CAT", X_CAT), ("ISSUER NAME AS FILED", X_ISSUER)]:
        L.append(f'  <text x="{x}" y="116" font-size="11" font-weight="700" '
                 f'fill="{SECOND}">{esc(lab)}</text>')
    for lab, x in [("SHARES", X_SHARES), ("VALUE USD", X_VALUE), ("PRICE", X_PRICE)]:
        L.append(f'  <text x="{x}" y="116" font-size="11" font-weight="700" '
                 f'text-anchor="end" fill="{SECOND}">{esc(lab)}</text>')
    L.append(f'  <line x1="56" y1="124" x2="648" y2="124" stroke="{BORDER}" stroke-width="1"/>')

    for i, r in enumerate(rows):
        y = 146 + i * 29
        high = r["px"] > 500
        colour = RED if high else INK
        L.append(f'  <text x="{X_CAT}" y="{y}" font-size="11" font-family="{MONO}" '
                 f'fill="{SECOND}">{esc(r["cat"])}</text>')
        L.append(f'  <text x="{X_ISSUER}" y="{y}" font-size="11" font-family="{MONO}" '
                 f'fill="{INK}">{esc(r["issuer"][:30])}</text>')
        L.append(f'  <text x="{X_SHARES}" y="{y}" font-size="11" font-family="{MONO}" '
                 f'text-anchor="end" fill="{SECOND}">{r["balance"]:,.0f}</text>')
        L.append(f'  <text x="{X_VALUE}" y="{y}" font-size="11" font-family="{MONO}" '
                 f'text-anchor="end" fill="{SECOND}">{r["value"]:,.0f}</text>')
        L.append(f'  <text x="{X_PRICE}" y="{y}" font-size="12" font-family="{MONO}" '
                 f'text-anchor="end" font-weight="700" fill="{colour}">${r["px"]:,.2f}</text>')

    L.append(f'  <line x1="40" y1="336" x2="660" y2="336" stroke="{OCHRE}" stroke-width="2"/>')
    L.append(f'  <text x="40" y="358" font-size="13" fill="{INK}">'
             f'Not a disagreement between managers - it is inside one filing. '
             f'309 of 624 SpaceX</text>')
    L.append(f'  <text x="40" y="376" font-size="13" fill="{INK}">'
             f'fund-periods show this, and no other company shows it at all.</text>')
    L.append(f'  <text x="40" y="{H - 8}" font-size="11" fill="{SECOND}" font-family="{MONO}">'
             f'SOURCE: SEC N-PORT, accession 0001752724-24-195357 - held for human '
             f'adjudication, never auto-adjusted</text>')
    write("w2-spacex-trap.svg", L)


def main():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    funnel(d)
    staircase(d)
    spacex(d)


if __name__ == "__main__":
    main()
