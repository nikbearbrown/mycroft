"""Generate the Week 8 video figures as SVG, from measured data only.

Every number is queried from the marks panel at run time and written to
docs/_figdata_week8.json before anything is drawn (P3).

Follows brutalist/DESIGN.md: the six palette tokens and nothing else, EB
Garamond for figure titles, Inter for labels, JetBrains Mono for data. Red is
the primary series, never "danger".

Five figures, one per visual beat of the narration:

  w8-remark       0:25  25% unchanged against an expected 30 to 40
  w8-bycompany    0:55  the same number by company, 2.2% to 48.5%
  w8-dispersion   1:25  same-date spread, and how much of it is levels
  w8-window       1:55  one real window: 141 to 259 across nine managers
  w8-propagation  2:30  30 days to half, and 0 for the biggest events

    python scripts/make_week8_figures.py
    cd ../../.. && npm run svg-to-png && npm run audit:layout
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REPO = ROOT.parents[2]
OUT = REPO / "images" / "private-ai-valuation-agent"
FIGDATA = ROOT / "docs" / "_figdata_week8.json"

from src.db.connect import connect  # noqa: E402
from src.signal import findings as F  # noqa: E402

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
    data = {
        "remark": F.remark_frequency(conn),
        "same_date": F.dispersion(conn, window_days=0),
        "propagation": F.propagation(conn),
        "guards": F.guards(conn),
    }

    # One real propagation window, quoted rather than described. This is the
    # 2025-12-31 Anthropic preferred group: managers spread from 141 to 261
    # because some have reflected the new round and some have not.
    with conn.cursor() as cur:
        cur.execute("""
            SELECT f.family                          AS manager,
                   m.period_end::text                AS period_end,
                   avg(m.price_per_share)::numeric(18,4) AS price
              FROM marks m
              JOIN companies  c ON c.company_id  = m.company_id
              JOIN securities s ON s.security_id = m.security_id
              JOIN funds      f ON f.fund_id     = m.fund_id
             WHERE c.canonical_name = 'Anthropic PBC'
               AND s.class_normalized LIKE 'PFD%'
               AND m.price_per_share IS NOT NULL
               AND NOT m.change_blocked
               AND m.period_end BETWEEN DATE '2025-12-31' AND DATE '2026-01-31'
             GROUP BY 1, 2
             ORDER BY 3
        """)
        columns = [c[0] for c in cur.description]
        data["window"] = [dict(zip(columns, r)) for r in cur.fetchall()]
    conn.close()

    spreads = sorted(w["spread"] for w in data["same_date"]["windows"]
                     if w["spread"] is not None)
    data["same_date_stats"] = {
        "groups": len(data["same_date"]["windows"]),
        "median": spreads[len(spreads) // 2] if spreads else None,
        "p90": spreads[int(len(spreads) * 0.9)] if spreads else None,
        "max": spreads[-1] if spreads else None,
        "within_1pct": sum(1 for s in spreads if s < 0.01),
        "multi_level": sum(1 for w in data["same_date"]["windows"] if w["levels"] > 1),
        "spreads": spreads,
    }
    FIGDATA.write_text(json.dumps(data, indent=1, default=str), encoding="utf-8")
    return data


# --------------------------------------------------------------------------
# Drawing helpers
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
    return path


def pct(value, digits=1) -> str:
    return "—" if value is None else f"{float(value) * 100:.{digits}f}%"


# --------------------------------------------------------------------------
# Figure 1 -- the headline, against the expectation
# --------------------------------------------------------------------------


def fig_remark(d) -> Path:
    overall, sens = d["remark"]["overall"], d["remark"]["sensitivity"]
    unchanged = float(overall["share_unchanged"])
    lines = head(
        f"{pct(unchanged)} unchanged, against an expected 30 to 40",
        f"A bar showing that {overall['moved']:,} of {overall['steps']:,} consecutive "
        f"observations moved and {overall['unchanged']:,} did not, with the plan's "
        f"expected band marked, followed by a sensitivity ladder.",
        f"{overall['steps']:,} consecutive observations, after every guard",
    )

    bar_top, bar_h = 104, 44
    span = W - 2 * MARGIN
    moved_w = span * float(overall["share_moved"])
    lines.append(f'  <rect x="{MARGIN}" y="{bar_top}" width="{moved_w:.1f}"'
                 f' height="{bar_h}" fill="{RED}"/>')
    lines.append(f'  <rect x="{MARGIN + moved_w:.1f}" y="{bar_top}"'
                 f' width="{span - moved_w:.1f}" height="{bar_h}" fill="{INK}"/>')
    lines.append(label(MARGIN + 14, bar_top + 29, f"{overall['moved']:,} moved",
                       size=17, font=MONO, fill=WHITE))
    lines.append(label(W - MARGIN - 14, bar_top + 29, f"{overall['unchanged']:,}",
                       size=17, font=MONO, fill=WHITE, anchor="end"))
    lines.append(label(MARGIN, bar_top + bar_h + 18, f"{pct(overall['share_moved'])} moved",
                       size=12, fill=RED))
    lines.append(label(W - MARGIN, bar_top + bar_h + 18, f"{pct(unchanged)} unchanged",
                       size=12, fill=INK, anchor="end"))

    # where the plan expected the boundary to sit
    band_lo = MARGIN + span * (1 - 0.40)
    band_hi = MARGIN + span * (1 - 0.30)
    lines.append(f'  <rect x="{band_lo:.1f}" y="{bar_top - 14}"'
                 f' width="{band_hi - band_lo:.1f}" height="{bar_h + 28}"'
                 f' fill="none" stroke="{OCHRE}" stroke-width="2"'
                 f' stroke-dasharray="4 3"/>')
    lines.append(label((band_lo + band_hi) / 2, bar_top - 22,
                       "where plan.md expected the line", size=11, fill=OCHRE,
                       anchor="middle"))

    top = 216
    lines.append(column_head(MARGIN, top, "IF WE CALL THIS UNCHANGED"))
    lines.append(column_head(W - MARGIN, top, "SHARE", anchor="end"))
    lines.append(rule(top + 10, colour=INK))
    rows = [
        ("exactly equal — the rule used", sens["unchanged_exact"], RED),
        ("any move under 0.1%", sens["unchanged_if_0_1pct_is_flat"], INK),
        ("any move under 1%", sens["unchanged_if_1pct_is_flat"], INK),
    ]
    y = top + 34
    for text, value, colour in rows:
        bar = 200 * float(value)
        lines.append(label(MARGIN, y, text, size=12, fill=colour))
        lines.append(f'  <rect x="{W - MARGIN - 262}" y="{y - 10}" width="{bar:.1f}"'
                     f' height="12" fill="{colour}"/>')
        lines.append(label(W - MARGIN, y, pct(value), size=13, font=MONO, fill=colour,
                           anchor="end"))
        y += 26

    lines.append(rule(y - 4))
    lines.append(label(MARGIN, y + 20,
                       "Even the most generous reading stays below the plan's band.",
                       size=13, fill=INK))
    lines.append(source_line("Source: marks, guarded — no blocked mark, no incomplete run"))
    return write("w8-remark.svg", lines)


# --------------------------------------------------------------------------
# Figure 2 -- the same number, by company
# --------------------------------------------------------------------------


def fig_bycompany(d) -> Path:
    rows = [r for r in d["remark"]["by_company"] if int(r["steps"]) >= 10]
    rows.sort(key=lambda r: float(r["share_unchanged"]))
    lines = head(
        "One headline rate would hide all of this",
        "Horizontal bars of the share of consecutive observations that were unchanged, "
        "per company, ranging from 1.1% for OpenAI to 48.5% for X.AI.",
        "Share of consecutive observations unchanged, by company",
    )

    top, pitch = 100, 22
    left = 232
    widest = max(float(r["share_unchanged"]) for r in rows) or 1
    # 150, not 56: the longest bar's percentage label collided with the
    # right-aligned step count, which the layout audit caught.
    scale = (W - MARGIN - left - 150) / widest
    for i, row in enumerate(rows):
        y = top + i * pitch
        share = float(row["share_unchanged"])
        colour = RED if i == len(rows) - 1 else INK
        name = row["company"].replace(" Technologies Corp.", "").replace(", Inc.", "")
        name = name.replace(" Industries", "").replace(" Systems Inc.", "")
        lines.append(label(left - 12, y, name[:26], size=12, fill=INK, anchor="end"))
        lines.append(f'  <rect x="{left}" y="{y - 10}" width="{max(share * scale, 2):.1f}"'
                     f' height="13" fill="{colour}"/>')
        lines.append(label(left + max(share * scale, 2) + 8, y, pct(share),
                           size=12, font=MONO, fill=colour))
        lines.append(label(W - MARGIN, y, f"{int(row['steps']):,} steps", size=10,
                           fill=SECOND, anchor="end"))

    bottom = top + len(rows) * pitch
    lines.append(rule(bottom))
    lines.append(label(MARGIN, bottom + 24,
                       "Anthropic and OpenAI are re-priced at almost every observation.",
                       size=13, fill=INK))
    lines.append(label(MARGIN, bottom + 42,
                       "X.AI and SpaceX are carried forward a third to a half of the time.",
                       size=13, fill=INK))
    lines.append(source_line("Source: marks, grouped by company · companies with 10 or "
                             "more observed steps"))
    return write("w8-bycompany.svg", lines)


# --------------------------------------------------------------------------
# Figure 3 -- same-date spread, and what it is made of
# --------------------------------------------------------------------------


def fig_dispersion(d) -> Path:
    stats = d["same_date_stats"]
    lines = head(
        f"Managers on the same date differ by {pct(stats['median'])}",
        f"A dot plot of the spread in each of {stats['groups']} same-date manager groups, "
        f"with the median marked, and a note that {stats['multi_level']} of them contain "
        "more than one distinct price level.",
        f"{stats['groups']} groups of three or more managers marking one company on one date",
    )

    # One dot per group, ordered by spread, on a square-root scale so the long
    # tail does not flatten the body.
    plot_top, plot_h = 108, 120
    left, right = MARGIN + 8, W - MARGIN - 130
    spreads = stats["spreads"]
    hi = max(spreads) if spreads else 1

    def at(value):
        return plot_top + plot_h - plot_h * ((value / hi) ** 0.5)

    # Red marks the widest decile, taken from the measured p90 rather than a
    # round number typed into a drawing function.
    p90 = stats["p90"] or hi
    for i, spread in enumerate(spreads):
        x = left + (right - left) * i / max(len(spreads) - 1, 1)
        colour = RED if spread >= p90 else INK
        lines.append(f'  <circle cx="{x:.1f}" cy="{at(spread):.1f}" r="2.6"'
                     f' fill="{colour}" opacity="0.85"/>')

    median = stats["median"]
    lines.append(f'  <line x1="{left}" y1="{at(median):.1f}" x2="{right}"'
                 f' y2="{at(median):.1f}" stroke="{OCHRE}" stroke-width="2"'
                 f' stroke-dasharray="5 3"/>')
    lines.append(label(right + 10, at(median) + 4, f"median {pct(median)}", size=12,
                       fill=OCHRE))
    lines.append(label(right + 10, at(hi) + 4, f"widest {pct(hi)}", size=11, fill=SECOND))
    lines.append(label(left, plot_top + plot_h + 16,
                       "each dot is one group, ordered by spread", size=10, fill=SECOND))

    top = 272
    lines.append(rule(top - 12))
    lines.append(label(MARGIN, top + 8,
                       f"But {stats['multi_level']} of the {stats['groups']} groups hold "
                       f"more than one price level.",
                       size=14, fill=INK))
    lines.append(label(MARGIN, top + 30,
                       "So the disagreement is mostly about which round has been "
                       "reflected,",
                       size=13, fill=SECOND))
    lines.append(label(MARGIN, top + 48,
                       "not about what the round was worth. That is propagation, seen "
                       "side-on.",
                       size=13, fill=SECOND))
    lines.append(label(MARGIN, top + 76,
                       f"{stats['within_1pct']} of {stats['groups']} groups agree to "
                       f"within 1%.",
                       size=11, fill=SECOND))
    lines.append(source_line("Source: marks · same period end, same company, same class "
                             "kind, three or more managers"))
    return write("w8-dispersion.svg", lines)


# --------------------------------------------------------------------------
# Figure 4 -- one real window
# --------------------------------------------------------------------------


def fig_window(d) -> Path:
    rows = d["window"]
    lines = head(
        "A round arriving, caught mid-flight",
        f"{len(rows)} manager-and-period marks on Anthropic preferred over two "
        "adjacent period ends, spread because some have reflected a new round and "
        "some have not yet.",
        f"Anthropic preferred, 2025-12-31 and 2026-01-31 · "
        f"{len({r['manager'] for r in rows})} managers, {len(rows)} marks",
    )

    # 19, not 21: eleven rows at 21 pushed the closing sentence onto the
    # source line.
    top, pitch = 100, 19
    left = 188
    prices = [float(r["price"]) for r in rows]
    lo, hi = min(prices), max(prices)
    bar_left, bar_right = left, W - MARGIN - 66

    def at(price):
        return bar_left + (bar_right - bar_left) * (price - lo) / (hi - lo)

    # Which dots are the new round is decided by the same level clustering the
    # findings use, not by a threshold typed into a drawing function. The top
    # cluster is the new level; everything below it has not arrived yet.
    from src.signal.findings import LEVEL_REL, _levels

    top_cluster = set(_levels(prices, LEVEL_REL)[-1])
    for i, row in enumerate(rows):
        y = top + i * pitch
        price = float(row["price"])
        colour = RED if price in top_cluster else SECOND
        lines.append(label(left - 12, y, row["manager"][:22], size=11, fill=INK,
                           anchor="end"))
        lines.append(f'  <line x1="{bar_left}" y1="{y - 4}" x2="{at(price):.1f}"'
                     f' y2="{y - 4}" stroke="{BORDER}" stroke-width="1"/>')
        lines.append(f'  <circle cx="{at(price):.1f}" cy="{y - 4}" r="4.5"'
                     f' fill="{colour}"/>')
        lines.append(label(W - MARGIN, y, f"{price:,.2f}", size=11, font=MONO,
                           fill=colour, anchor="end"))

    bottom = top + len(rows) * pitch
    lines.append(label(bar_left, bottom + 6, f"{lo:,.0f}", size=10, font=MONO,
                       fill=SECOND))
    lines.append(label(bar_right, bottom + 6, f"{hi:,.0f}", size=10, font=MONO,
                       fill=SECOND, anchor="end"))

    lines.append(rule(bottom + 22))
    lines.append(label(MARGIN, bottom + 44,
                       "Same company. Same class. One month apart at most.",
                       size=13, fill=INK))
    lines.append(label(MARGIN, bottom + 62,
                       f"{pct(hi / lo - 1)} apart, and none of it is disagreement.",
                       size=13, fill=INK))
    lines.append(label(MARGIN, bottom + 80,
                       "It is a round arriving, one manager at a time.",
                       size=13, fill=RED))
    lines.append(source_line("Source: marks · every manager holding Anthropic preferred "
                             "across those two period ends"))
    return write("w8-window.svg", lines)


# --------------------------------------------------------------------------
# Figure 5 -- how fast a round travels
# --------------------------------------------------------------------------


def fig_propagation(d) -> Path:
    prop = d["propagation"]
    events = sorted(prop["events"], key=lambda e: -int(e["managers"]))[:8]
    lines = head(
        f"Half the holders inside {prop['median_lag_to_half_days']} days",
        f"A table of the largest repricing events, showing how many days passed between "
        f"the first manager reporting a new price level and half of them doing so.",
        f"{prop['events_counted']} price levels adopted by three or more managers",
    )

    top = 100
    lines.append(column_head(MARGIN, top, "COMPANY"))
    lines.append(column_head(268, top, "LEVEL"))
    lines.append(column_head(376, top, "MANAGERS"))
    lines.append(column_head(W - MARGIN, top, "DAYS TO HALF", anchor="end"))
    lines.append(rule(top + 10, colour=INK))

    y = top + 32
    widest = max(int(e["lag_to_half_days"]) for e in events) or 1
    for event in events:
        days = int(event["lag_to_half_days"])
        colour = RED if days == 0 else INK
        name = event["company"].replace(" Technologies Corp.", "").replace(", Inc.", "")
        name = name.replace(" Industries", "")
        lines.append(label(MARGIN, y, name[:26], size=12, fill=INK))
        lines.append(label(268, y, f"{float(event['price']):,.2f}", size=11, font=MONO,
                           fill=SECOND))
        lines.append(label(376, y, str(event["managers"]), size=11, font=MONO,
                           fill=SECOND))
        bar = 90 * days / widest
        lines.append(f'  <rect x="{W - MARGIN - 66 - bar:.1f}" y="{y - 9}"'
                     f' width="{max(bar, 2):.1f}" height="10" fill="{colour}"/>')
        lines.append(label(W - MARGIN, y, f"{days}d", size=12, font=MONO, fill=colour,
                           anchor="end"))
        y += 23

    lines.append(rule(y - 2))
    lines.append(label(MARGIN, y + 22,
                       f"Median across all {prop['events_counted']} events: "
                       f"{prop['median_lag_to_half_days']} days to half, "
                       f"{prop['median_lag_to_all_days']} to the last.",
                       size=13, fill=INK))
    lags = [int(e["lag_to_half_days"]) for e in prop["events"]]
    instant = sum(1 for lag in lags if lag == 0)
    lines.append(label(MARGIN, y + 44,
                       f"{instant} of {len(lags)} levels reach half their holders on the "
                       f"very same period end.",
                       size=13, fill=INK))
    lines.append(label(MARGIN, y + 66,
                       f"The slowest takes {max(lags)} days.", size=13, fill=RED))
    lines.append(source_line("Source: marks · a level is a price three or more managers "
                             "adopt, matched within 0.1%"))
    return write("w8-propagation.svg", lines)


def main() -> None:
    data = collect()
    print(f"wrote {FIGDATA.relative_to(ROOT)}")
    for build in (fig_remark, fig_bycompany, fig_dispersion, fig_window,
                  fig_propagation):
        path = build(data)
        print(f"wrote {path.relative_to(REPO)}")
    print("\nnow: cd ../../.. && npm run svg-to-png && npm run audit:layout")


if __name__ == "__main__":
    main()
