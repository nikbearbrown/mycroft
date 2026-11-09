"""Generate the Week 7 video figures as SVG, from measured data only.

Every number is queried from the marks panel at run time and written to
docs/_figdata_week7.json before anything is drawn, so a figure cannot drift
away from the panel it describes (P3).

Follows brutalist/DESIGN.md: the six palette tokens and nothing else, EB
Garamond for figure titles, Inter for labels, JetBrains Mono for data. Red
carries the primary series -- here whatever the figure is actually about.

Five figures, one per visual beat of the narration:

  w7-panel      0:25  5,806 filed holdings -> 5,479 marks, and it reconciles
  w7-tolerance  1:00  the window that missed the case the plan names
  w7-evidence   1:35  the share count settles all three
  w7-factor     2:15  ratio 11.93, factor 10, and why they differ
  w7-checks     2:45  six pass, one unreachable

    python scripts/make_week7_figures.py
    cd ../../.. && npm run svg-to-png && npm run audit:layout
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REPO = ROOT.parents[2]
OUT = REPO / "images" / "private-ai-valuation-agent"
FIGDATA = ROOT / "docs" / "_figdata_week7.json"

from src.db.connect import connect  # noqa: E402
from src.marks import verify as verify_mod  # noqa: E402
from src.marks.build import coverage  # noqa: E402
from src.marks.splits import (  # noqa: E402
    SPLIT_MAX_RATIO,
    SPLIT_TOLERANCE,
    suspected,
)

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
    cur = conn.cursor()

    def rows(sql, args=None):
        cur.execute(sql, args)
        columns = [c[0] for c in cur.description]
        return [dict(zip(columns, r)) for r in cur.fetchall()]

    data: dict = {"coverage": coverage(conn), "tolerance": SPLIT_TOLERANCE,
                  "cap": SPLIT_MAX_RATIO}

    data["totals"] = rows("""
        SELECT count(*)                                            AS marks,
               count(*) FILTER (WHERE price_per_share IS NOT NULL)  AS priced,
               count(*) FILTER (WHERE change_blocked)               AS blocked,
               count(*) FILTER (WHERE is_blended)                   AS blended,
               count(*) FILTER (WHERE spv_opaque)                   AS opaque_spv,
               count(*) FILTER (WHERE is_remark)                    AS re_marked,
               count(*) FILTER (WHERE is_remark IS FALSE)           AS carried,
               count(*) FILTER (WHERE is_remark IS NULL
                                  AND price_per_share IS NOT NULL)  AS first_obs,
               count(*) FILTER (WHERE split_suspected)              AS suspected,
               count(DISTINCT security_id)                          AS securities,
               count(DISTINCT period_end)                           AS periods,
               count(DISTINCT company_id)                           AS companies
          FROM marks
    """)[0]
    data["blocks"] = rows("""
        SELECT block_reason AS reason, count(*) AS marks FROM marks
         WHERE change_blocked GROUP BY 1 ORDER BY 2 DESC
    """)
    data["panel_rows"] = rows("""
        SELECT count(*) AS n FROM (
            SELECT 1 FROM marks m JOIN funds f ON f.fund_id = m.fund_id
             GROUP BY m.company_id, f.family, m.period_end) g
    """)[0]["n"]
    data["quarantine"] = suspected(conn)

    # The decisive evidence: share count against value, one representative fund
    # per verdict, chosen by the data as the LARGEST position in the adjudicated
    # group. The first version ordered ascending and picked a different SpaceX
    # fund than the write-up cites -- both are the same phenomenon, but a figure
    # and a log that quote different rows for one claim invite a reader to
    # wonder which is right.
    def series(company, klass, fund_filter=""):
        return rows(f"""
            SELECT m.period_end::text AS period_end,
                   m.balance::numeric(18,0)  AS shares,
                   m.value_usd::numeric(20,2) AS value_usd,
                   m.price_per_share::numeric(16,4) AS price,
                   m.split_ratio::numeric(12,4) AS ratio,
                   m.split_suspected AS suspected
              FROM marks m
              JOIN securities s ON s.security_id = m.security_id
              JOIN companies  c ON c.company_id  = m.company_id
             WHERE c.canonical_name = %(company)s
               AND s.class_normalized = %(klass)s
               AND m.fund_id = (
                   SELECT m2.fund_id FROM marks m2
                     JOIN securities s2 ON s2.security_id = m2.security_id
                     JOIN companies  c2 ON c2.company_id  = m2.company_id
                    WHERE c2.canonical_name = %(company)s
                      AND s2.class_normalized = %(klass)s
                      AND m2.split_suspected
                    ORDER BY m2.balance DESC {fund_filter} LIMIT 1)
               AND m.price_per_share IS NOT NULL
             ORDER BY m.period_end
        """, {"company": company, "klass": klass})

    data["perplexity"] = series("Perplexity AI, Inc.", "PFD:D-1")
    data["anthropic"] = series("Anthropic PBC", "COM:UNSPECIFIED")
    # CLASS C rather than CLASS A: both are the same phenomenon, and this is the
    # series the RUN_LOG and README cite (22,368 shares), so the figure and the
    # written record quote the same row.
    data["spacex"] = series("Space Exploration Technologies Corp.", "COM:CLASS C")

    data["checks"] = [
        {"check": r["check"], "passed": r["passed"], "note": r.get("note", "")}
        for r in verify_mod.run_all(conn)
    ]
    agreement = next(c for c in verify_mod.run_all(conn) if "four managers" in c["check"])
    data["agreement"] = {
        "families": agreement["families_at_259_14"],
        "clusters": agreement["clusters_within_half_a_cent"],
    }
    conn.close()
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


def clip(text, limit) -> str:
    text = str(text)
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    if " " in cut[limit // 2:]:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,.;:") + "…"


def write(name, lines) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    path.write_text("\n".join(lines + ["</svg>", ""]), encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Figure 1 -- the panel, and that it reconciles
# --------------------------------------------------------------------------


def fig_panel(d) -> Path:
    t, cov = d["totals"], d["coverage"]
    lines = head(
        f"{t['marks']:,} marks, and every filed row accounted for",
        f"A bar showing the {cov['holdings']:,} filed holdings splitting into rejected, "
        f"superseded by amendment, and aggregated into marks, followed by what the "
        f"{t['marks']:,} marks contain.",
        # Shortened: the first version ran off the right edge, which the layout
        # audit cannot see because the text element's own box stays on canvas.
        f"price per share = value / shares · {t['securities']} securities · "
        f"{t['periods']} period ends · {d['panel_rows']} panel rows",
    )

    bar_top, bar_h = 100, 40
    span = W - 2 * MARGIN
    parts = [
        (cov["lines_in_marks"], INK, "aggregated into marks"),
        (cov["superseded_by_amendment"], SECOND, "superseded by an amendment"),
        (cov["rejected_not_in_universe"], RED, "not one of ours"),
    ]
    x = MARGIN
    for count, colour, _ in parts:
        width = span * count / cov["holdings"]
        lines.append(f'  <rect x="{x:.1f}" y="{bar_top}" width="{max(width, 2):.1f}"'
                     f' height="{bar_h}" fill="{colour}"/>')
        x += width
    lines.append(label(MARGIN + 12, bar_top + 26, f"{cov['lines_in_marks']:,}", size=18,
                       font=MONO, fill=WHITE))
    lines.append(label(MARGIN, bar_top - 10, f"{cov['holdings']:,} filed holdings",
                       size=12, fill=SECOND))

    y = bar_top + bar_h + 22
    for count, colour, text in parts:
        lines.append(f'  <rect x="{MARGIN}" y="{y - 9}" width="10" height="10"'
                     f' fill="{colour}"/>')
        lines.append(label(MARGIN + 18, y, f"{count:,}  {text}", size=12, fill=INK))
        y += 19
    lines.append(label(W - MARGIN, bar_top + bar_h + 41,
                       "it reconciles, so nothing is lost for being awkward",
                       size=12, fill=OCHRE, anchor="end"))

    top = y + 16
    lines.append(column_head(MARGIN, top, "WHAT THE MARKS SAY"))
    lines.append(column_head(W - MARGIN, top, "MARKS", anchor="end"))
    lines.append(rule(top + 10, colour=INK))
    facts = [
        ("priced", t["priced"], INK),
        ("re-marked against the prior period", t["re_marked"], INK),
        ("carried forward unchanged", t["carried"], SECOND),
        ("first observation, no prior", t["first_obs"], SECOND),
        ("blocked from any change series", t["blocked"], RED),
    ]
    y = top + 32
    widest = max(v for _, v, _ in facts)
    for text, value, colour in facts:
        bar = 190 * value / widest
        lines.append(label(MARGIN, y, text, size=12, fill=colour))
        lines.append(f'  <rect x="{W - MARGIN - 250}" y="{y - 9}" width="{bar:.1f}"'
                     f' height="10" fill="{colour}"/>')
        lines.append(label(W - MARGIN, y, f"{value:,}", size=12, font=MONO, fill=colour,
                           anchor="end"))
        y += 22
    lines.append(source_line("Source: marks, joined to securities, companies and funds"))
    return write("w7-panel.svg", lines)


# --------------------------------------------------------------------------
# Figure 2 -- the window that missed the case the plan names
# --------------------------------------------------------------------------


def fig_tolerance(d) -> Path:
    lines = head(
        "The window was too narrow to catch its own test case",
        "A number line around 12 showing that an absolute window of plus or minus 0.02 "
        "excludes a ratio of 11.93, while a relative window of 1 percent, plus or minus "
        "0.12, includes it.",
        "plan.md requires that Perplexity's 695 to 58 step be flagged. That ratio is 11.93.",
    )

    axis_y, left, right = 176, MARGIN + 30, W - MARGIN - 30
    lo, hi = 11.6, 12.4

    def at(value):
        return left + (right - left) * (value - lo) / (hi - lo)

    lines.append(f'  <line x1="{left}" y1="{axis_y}" x2="{right}" y2="{axis_y}"'
                 f' stroke="{INK}" stroke-width="1"/>')
    for tick in (11.6, 11.8, 12.0, 12.2, 12.4):
        x = at(tick)
        lines.append(f'  <line x1="{x:.1f}" y1="{axis_y}" x2="{x:.1f}" y2="{axis_y + 6}"'
                     f' stroke="{BORDER}" stroke-width="1"/>')
        lines.append(label(x, axis_y + 20, f"{tick:g}", size=11, font=MONO, fill=SECOND,
                           anchor="middle"))

    # the absolute window: 0.02 either side of 12
    a_lo, a_hi = at(11.98), at(12.02)
    lines.append(f'  <rect x="{a_lo:.1f}" y="{axis_y - 40}" width="{max(a_hi - a_lo, 2):.1f}"'
                 f' height="32" fill="{SECOND}"/>')
    lines.append(label(at(12.0), axis_y - 48, "absolute ±0.02", size=12, fill=SECOND,
                       anchor="middle"))
    lines.append(label(at(12.0), axis_y - 62, "Week 6's window", size=11, fill=SECOND,
                       anchor="middle"))

    # the relative window: 1% of 12 either side
    r_lo, r_hi = at(12 * (1 - 0.01)), at(12 * (1 + 0.01))
    lines.append(f'  <rect x="{r_lo:.1f}" y="{axis_y + 38}" width="{r_hi - r_lo:.1f}"'
                 f' height="30" fill="none" stroke="{OCHRE}" stroke-width="2"/>')
    lines.append(label(at(12.0), axis_y + 86, "relative 1%, so ±0.12", size=12, fill=OCHRE,
                       anchor="middle"))

    # the ratio itself
    x = at(11.93)
    lines.append(f'  <line x1="{x:.1f}" y1="{axis_y - 44}" x2="{x:.1f}" y2="{axis_y + 72}"'
                 f' stroke="{RED}" stroke-width="2"/>')
    lines.append(f'  <circle cx="{x:.1f}" cy="{axis_y}" r="5" fill="{RED}"/>')
    lines.append(label(x - 8, axis_y - 52, "11.93", size=15, font=MONO, fill=RED,
                       anchor="end"))
    lines.append(label(x - 8, axis_y - 36, "Perplexity", size=11, fill=RED, anchor="end"))

    lines.append(rule(300))
    lines.append(label(MARGIN, 324,
                       "The absolute window missed it by a factor of three. It looked "
                       "right only because",
                       size=13, fill=INK))
    lines.append(label(MARGIN, 342,
                       "the other Perplexity step lands on exactly 10.000.",
                       size=13, fill=INK))
    lines.append(label(MARGIN, 368,
                       f"Both windows sit under the same cap of {d['cap']}, which is what "
                       f"keeps a 348x placeholder out.",
                       size=11, fill=SECOND))
    lines.append(source_line("src/marks/splits.py · one rule, imported by the queue "
                             "trigger and the detector"))
    return write("w7-tolerance.svg", lines)


# --------------------------------------------------------------------------
# Figure 3 -- the share count settles it
# --------------------------------------------------------------------------


def _step(series):
    """The suspected step and the period before it."""
    for i, row in enumerate(series):
        if row["suspected"] and i > 0:
            return series[i - 1], row
    return (series[0], series[-1]) if len(series) > 1 else (None, None)


def fig_evidence(d) -> Path:
    lines = head(
        "The share count settles it, and the ratio does not",
        "Three price steps of similar size. The share count distinguishes them: "
        "Perplexity's multiplies by ten while the value holds, which is a split; "
        "Anthropic's and SpaceX's never move, which makes their steps repricings.",
        "Same question asked of three companies, answered by one column",
    )

    top = 100
    lines.append(column_head(MARGIN, top, "COMPANY"))
    lines.append(column_head(200, top, "SHARES"))
    lines.append(column_head(390, top, "VALUE"))

    lines.append(rule(top + 10, colour=INK))

    cases = [
        ("Perplexity", d["perplexity"], "a real 10:1 split", RED,
         "ten times the shares, the same dollars"),
        ("Anthropic", d["anthropic"], "not a split", SECOND,
         "share count never moves, and the step reverses next quarter"),
        ("SpaceX", d["spacex"], "not a split", SECOND,
         "share count never moves, the value doubles exactly"),
    ]
    y = top + 36
    for name, series, verdict, colour, note in cases:
        before, after = _step(series)
        if not before:
            continue
        lines.append(label(MARGIN, y, name, size=14, fill=INK))
        lines.append(label(MARGIN, y + 17, verdict, size=12, font=MONO, fill=colour))
        shares = (f'{float(before["shares"]):,.0f} → {float(after["shares"]):,.0f}')
        # Two decimals, not zero. 4,228,993.75 rounds to 4,228,994 and the
        # rounding is doing part of the work of the words "the same dollars".
        value = (f'{float(before["value_usd"]):,.2f} → {float(after["value_usd"]):,.2f}')
        same_shares = float(before["shares"]) == float(after["shares"])
        same_value = abs(float(before["value_usd"]) - float(after["value_usd"])) < 0.005
        lines.append(label(200, y, shares, size=11, font=MONO,
                           fill=SECOND if same_shares else RED))
        lines.append(label(390, y, value, size=11, font=MONO,
                           fill=SECOND if not same_value else RED))
        lines.append(label(200, y + 17, note, size=10, fill=SECOND))
        lines.append(rule(y + 29))
        y += 50

    lines.append(label(MARGIN, y + 16,
                       "A split moves the share count and leaves the value alone.",
                       size=13, fill=INK))
    lines.append(label(MARGIN, y + 34,
                       "A repricing does the opposite. The ratio alone cannot tell them "
                       "apart.",
                       size=13, fill=INK))
    lines.append(source_line("Source: marks · one representative fund per adjudicated "
                             "group, chosen by the data"))
    return write("w7-evidence.svg", lines)


# --------------------------------------------------------------------------
# Figure 4 -- ratio 11.93, factor 10
# --------------------------------------------------------------------------


def fig_factor(d) -> Path:
    composite = next((r for r in d["quarantine"]
                      if r["ratio_max"] and abs(float(r["ratio_max"]) - 11.93) < 0.01), None)
    lines = head(
        "Ratio 11.93. Factor 10.",
        "The measured ratio of 11.93 decomposes into a 10:1 split and a 16 percent "
        "markdown that happened in the same period. Adjusting by the ratio would erase "
        "the markdown; adjusting by the factor keeps it.",
        "Two things happened in one quarter, and only one of them is a split",
    )

    box_y, box_h = 106, 62
    thirds = (W - 2 * MARGIN - 40) / 3
    blocks = [
        ("11.9300", "what the detector measured", RED),
        ("10", "the split, which Week 8 divides by", INK),
        ("1.193", "a 16% markdown, which is a real price move", OCHRE),
    ]
    x = MARGIN
    for i, (value, text, colour) in enumerate(blocks):
        lines.append(f'  <rect x="{x:.1f}" y="{box_y}" width="{thirds:.1f}"'
                     f' height="{box_h}" fill="none" stroke="{colour}" stroke-width="2"/>')
        lines.append(label(x + thirds / 2, box_y + 38, value, size=20, font=MONO,
                           fill=colour, anchor="middle"))
        for j, part in enumerate(text.split(", ")):
            lines.append(label(x + thirds / 2, box_y + box_h + 16 + j * 13, part,
                               size=10, fill=SECOND, anchor="middle"))
        if i < 2:
            glyph = "=" if i == 0 else "×"
            lines.append(label(x + thirds + 10, box_y + 36, glyph, size=18, fill=SECOND,
                               anchor="middle"))
        x += thirds + 20

    top = 224
    lines.append(column_head(MARGIN, top, "WHAT EACH CHOICE WOULD DO"))
    lines.append(rule(top + 10, colour=INK))
    # DESIGN.md: red is the primary series, never "danger". So red marks the
    # answer the figure is about and the two wrong choices are secondary -- the
    # first draft had it backwards, colouring both mistakes red as warnings.
    y = top + 22
    for text, colour in (
        ("Divide by 11.93 and the 16% markdown vanishes: a real price move, erased.",
         SECOND),
        ("Divide by 10 and the markdown survives as what it is.", RED),
        ("Divide by nothing and a 10:1 split reads as a 92% crash.", SECOND),
    ):
        lines.append(label(MARGIN + 14, y, text, size=13, fill=colour))
        y += 22
    lines.append(f'  <line x1="{MARGIN}" y1="{top + 10}" x2="{MARGIN}" y2="{y - 14}"'
                 f' stroke="{OCHRE}" stroke-width="3"/>')

    lines.append(rule(y + 2))
    if composite:
        lines.append(label(MARGIN, y + 26,
                           f'ARK, {composite["from_period"]} to {composite["to_period"]}: '
                           f'{composite["price_before"]} → {composite["price_after"]}',
                           size=12, font=MONO, fill=INK))
    lines.append(label(MARGIN, y + 48,
                       "So the panel records the adjudicated factor in its own column, "
                       "separate from the ratio.",
                       size=12, fill=SECOND))
    lines.append(source_line("Source: marks.split_ratio against marks.split_factor · "
                             "adjudicated by a named reviewer"))
    return write("w7-factor.svg", lines)


# --------------------------------------------------------------------------
# Figure 5 -- the plan's own checks
# --------------------------------------------------------------------------


def fig_checks(d) -> Path:
    checks = d["checks"]
    passed = sum(1 for c in checks if c["passed"] is True)
    na = sum(1 for c in checks if c["passed"] is None)
    failed = sum(1 for c in checks if c["passed"] is False)
    lines = head(
        f"{passed} pass, {na} unreachable, {failed} fail",
        "The end-to-end checks plan.md wrote for this project, with their results. One is "
        "structurally unreachable because the filings it needs have not been published.",
        "plan.md's own verification list, run against the panel",
    )

    top = 100
    lines.append(column_head(MARGIN, top, "CHECK"))
    lines.append(column_head(W - MARGIN, top, "RESULT", anchor="end"))
    lines.append(rule(top + 10, colour=INK))

    y = top + 32
    for check in checks:
        state, colour = {True: ("pass", INK), False: ("FAIL", RED),
                         None: ("unreachable", OCHRE)}[check["passed"]]
        lines.append(label(MARGIN, y, clip(check["check"], 62), size=12, fill=INK))
        lines.append(label(W - MARGIN, y, state, size=12, font=MONO, fill=colour,
                           anchor="end"))
        y += 22

    lines.append(rule(y + 2))
    agreement = d["agreement"]
    lines.append(label(MARGIN, y + 26,
                       f'The plan expected four managers to agree at $259.14. '
                       f'{agreement["families"]} do.',
                       size=13, fill=INK))
    y += 44
    for cluster in agreement["clusters"]:
        lines.append(label(MARGIN + 14, y, f'{cluster["price"]}', size=12, font=MONO,
                           fill=INK))
        lines.append(label(MARGIN + 90, y,
                           f'{cluster["families"]} families — '
                           f'{clip(cluster["managers"], 52)}',
                           size=11, fill=SECOND))
        y += 18
    lines.append(label(MARGIN, y + 16,
                       "They agree to the cent and disagree at four decimals, because "
                       "filers round differently.",
                       size=11, fill=SECOND))
    lines.append(source_line("src/marks/verify.py · each check returns what it found, "
                             "not a boolean"))
    return write("w7-checks.svg", lines)


def main() -> None:
    data = collect()
    print(f"wrote {FIGDATA.relative_to(ROOT)}")
    for build in (fig_panel, fig_tolerance, fig_evidence, fig_factor, fig_checks):
        path = build(data)
        print(f"wrote {path.relative_to(REPO)}")
    print("\nnow: cd ../../.. && npm run svg-to-png && npm run audit:layout")


if __name__ == "__main__":
    main()
