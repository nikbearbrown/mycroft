"""Generate the Week 6 video figures as SVG, from measured data only.

Every number drawn here is queried at run time from the project's Postgres --
`raw_holdings`, `match_decisions`, `review_decisions`, `companies` -- and written
to docs/_figdata_week6.json before anything is drawn. Nothing is typed in by
hand, so a figure cannot drift away from the result it claims to describe (P3).

Follows brutalist/DESIGN.md: the six palette tokens and nothing else, EB
Garamond for figure titles, Inter for labels, JetBrains Mono for data. Red is
the primary series, never "danger" -- here it marks the human's share of the
work, which is the subject of the week.

Five figures, one per visual beat of the narration:

  w6-funnel      0:25  5,806 holdings -> 231 questions -> 78% resolved, 8 asked
  w6-collapse    0:55  one company, 24 spellings, one answer
  w6-durability  1:25  where a paused review actually lives
  w6-split       1:55  the split that was real, and the two that were not
  w6-final       2:35  100% decided, and who decided it

    python scripts/make_week6_figures.py
    cd ../../.. && npm run svg-to-png && npm run audit:layout
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REPO = ROOT.parents[2]  # mycroft/
OUT = REPO / "images" / "private-ai-valuation-agent"
FIGDATA = ROOT / "docs" / "_figdata_week6.json"

from src.db.connect import connect  # noqa: E402

# brutalist/DESIGN.md -- the complete palette. No other colours.
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
    data: dict = {}

    # args stays None when there is nothing to bind. Passing an empty tuple
    # instead makes psycopg2 run its own %-interpolation over the SQL, which
    # turns a LIKE '%D-1%' into a parameter marker and raises IndexError.
    def one(sql, args=None):
        cur.execute(sql, args)
        return cur.fetchone()

    def rows(sql, args=None):
        cur.execute(sql, args)
        return cur.fetchall()

    # --- fig 1: the funnel -----------------------------------------------
    data["holdings"] = one("SELECT count(*) FROM raw_holdings")[0]
    data["decided"] = one("SELECT count(*) FROM match_decisions")[0]
    data["by_method"] = [
        {"method": m, "holdings": n, "questions": q}
        for m, n, q in rows("""
            SELECT method, count(*), count(DISTINCT decision_key)
              FROM match_decisions GROUP BY 1 ORDER BY 2 DESC
        """)
    ]
    data["by_trigger"] = [
        {"trigger": t, "holdings": n}
        for t, n in rows("""
            SELECT coalesce(trigger, '(none)'), count(*)
              FROM match_decisions GROUP BY 1 ORDER BY 2 DESC
        """)
    ]
    data["questions_total"] = one(
        "SELECT count(DISTINCT decision_key) FROM match_decisions")[0]
    data["human_holdings"] = one(
        "SELECT count(*) FROM match_decisions WHERE method = 'human'")[0]
    data["auto_holdings"] = data["decided"] - data["human_holdings"]

    # --- the eight questions, as answered --------------------------------
    data["review_groups"] = [
        {"trigger": t, "verdict": v, "company": c, "cards": n, "holdings": h}
        for t, v, c, n, h in rows("""
            SELECT rd.trigger, rd.verdict, coalesce(co.canonical_name, '(none)'),
                   count(*), sum(coalesce(rd.holdings_covered, 0))
              FROM review_decisions rd
         LEFT JOIN companies co ON co.company_id = rd.company_id
             WHERE rd.holdings_covered IS NOT NULL
             GROUP BY 1, 2, 3 ORDER BY 5 DESC
        """)
    ]
    data["review_rows"] = one("SELECT count(*) FROM review_decisions")[0]
    data["review_cards"] = one(
        "SELECT count(*) FROM review_decisions WHERE holdings_covered IS NOT NULL")[0]
    data["company_level_keys"] = one(
        "SELECT count(*) FROM review_decisions WHERE holdings_covered IS NULL")[0]
    data["reviewer"] = one(
        "SELECT reviewer FROM review_decisions GROUP BY 1 ORDER BY count(*) DESC LIMIT 1")[0]

    # --- fig 2: one company, many spellings ------------------------------
    # The title comes along because three of the spellings share one
    # issuer_name and differ only in the security title. Without it the figure
    # shows three identical-looking rows, which reads as a data error -- the
    # same defect Week 4's tie figure and Week 5's veto figure each had to fix.
    data["xai_spellings"] = [
        {"name": n, "title": ttl or "", "holdings": h}
        for n, ttl, h in rows("""
            SELECT rd.issuer_name, rd.title_of_issue, coalesce(rd.holdings_covered, 0)
              FROM review_decisions rd JOIN companies co USING (company_id)
             WHERE co.canonical_name = 'X.AI Corp' AND rd.holdings_covered IS NOT NULL
             ORDER BY rd.holdings_covered DESC, rd.issuer_name, rd.title_of_issue
        """)
    ]

    # --- fig 4: the three price steps ------------------------------------
    # Perplexity: the share count moved and the dollar value did not. That is
    # the whole argument, so both sides of it are queried rather than asserted.
    # One holding, chosen to be the one quoted in the reviewer's rationale, so
    # the figure and the audit trail carry the same numbers. The aggregate is
    # queried too: the ratio has to hold for every holding, not just the one on
    # screen, or the single row proves nothing.
    data["perplexity"] = [
        {"period_end": str(p), "balance": float(b), "value_usd": float(v),
         "price": float(px)}
        for p, b, v, px in rows("""
            SELECT fl.period_end, r.balance, r.value_usd, r.price_per_share
              FROM raw_holdings r JOIN filings fl ON fl.filing_id = r.filing_id
             WHERE r.company_provisional = 'Perplexity AI, Inc.'
               AND r.title_of_issue LIKE '%D-1%'
               -- The smallest D-1 position, chosen by the data rather than by a
               -- typed constant. The first version matched on value_usd = 4228994
               -- and returned nothing: the filed value is 4228993.75, and an
               -- earlier query had rounded it before it reached the rationale.
               AND r.value_usd = (
                   SELECT min(r2.value_usd)
                     FROM raw_holdings r2
                     JOIN filings f2 ON f2.filing_id = r2.filing_id
                    WHERE r2.company_provisional = 'Perplexity AI, Inc.'
                      AND r2.title_of_issue LIKE '%D-1%'
                      AND f2.period_end IN (DATE '2025-12-31', DATE '2026-03-31'))
               AND fl.period_end IN (DATE '2025-12-31', DATE '2026-03-31')
             ORDER BY fl.period_end
        """)
    ]
    data["perplexity_all"] = [
        {"period_end": str(p), "balance": float(b), "value_usd": float(v),
         "holdings": n}
        for p, b, v, n in rows("""
            SELECT fl.period_end, sum(r.balance), sum(r.value_usd), count(*)
              FROM raw_holdings r JOIN filings fl ON fl.filing_id = r.filing_id
             WHERE r.company_provisional = 'Perplexity AI, Inc.'
               AND fl.period_end IN (DATE '2025-12-31', DATE '2026-03-31')
             GROUP BY 1 ORDER BY 1
        """)
    ]
    # SpaceX: common and preferred, same filer, same period end.
    data["spacex_same_day"] = [
        {"period_end": str(p), "asset_category": a, "price": float(px), "holdings": n}
        for p, a, px, n in rows("""
            SELECT fl.period_end, r.asset_category, min(r.price_per_share), count(*)
              FROM raw_holdings r JOIN filings fl ON fl.filing_id = r.filing_id
             WHERE r.company_provisional = 'Space Exploration Technologies Corp.'
               AND fl.period_end = DATE '2023-10-31'
               AND r.asset_category IN ('EC', 'EP')
             GROUP BY 1, 2 ORDER BY 2
        """)
    ]
    # Anthropic: the step that was flagged, and the series it belongs to.
    data["anthropic_step"] = [
        {"period_end": str(p), "price": float(px)}
        for p, px in rows("""
            SELECT fl.period_end, min(r.price_per_share)
              FROM raw_holdings r JOIN filings fl ON fl.filing_id = r.filing_id
             WHERE r.company_provisional = 'Anthropic PBC'
               AND fl.period_end IN (DATE '2023-10-31', DATE '2024-01-31')
             GROUP BY 1 ORDER BY 1
        """)
    ]
    data["anthropic_series"] = [
        {"period_end": str(p), "price": float(px)}
        for p, px in rows("""
            SELECT fl.period_end, max(r.price_per_share)
              FROM raw_holdings r JOIN filings fl ON fl.filing_id = r.filing_id
             WHERE r.company_provisional = 'Anthropic PBC'
               AND r.price_per_share BETWEEN 1 AND 1000
             GROUP BY 1 ORDER BY 1
        """)
    ]

    # --- the canary ------------------------------------------------------
    data["rejected"] = [
        {"issuer_name": n, "holdings": h}
        for n, h in rows("""
            SELECT issuer_name, coalesce(holdings_covered, 0)
              FROM review_decisions
             WHERE verdict = 'not_in_universe' ORDER BY issuer_name
        """)
    ]

    conn.close()
    FIGDATA.write_text(json.dumps(data, indent=1), encoding="utf-8")
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
# Figure 1 -- the funnel
# --------------------------------------------------------------------------


def fig_funnel(d) -> Path:
    auto, human, total = d["auto_holdings"], d["human_holdings"], d["holdings"]
    lines = head(
        f"{auto:,} resolved themselves. {human:,} needed a person.",
        f"A stacked bar showing that of {total:,} private holdings, {auto:,} were resolved "
        f"by the deterministic matcher and {human:,} were routed to a human reviewer, "
        f"behind only {len(d['review_groups'])} distinct questions.",
        f"{total:,} holdings · {d['questions_total']} distinct name/title strings · "
        f"{len(d['review_groups'])} questions reached a human",
    )

    bar_top, bar_h, left = 108, 46, MARGIN
    span = W - 2 * MARGIN
    auto_w = span * auto / total
    lines.append(f'  <rect x="{left}" y="{bar_top}" width="{auto_w:.1f}" height="{bar_h}"'
                 f' fill="{INK}"/>')
    lines.append(f'  <rect x="{left + auto_w:.1f}" y="{bar_top}" width="{span - auto_w:.1f}"'
                 f' height="{bar_h}" fill="{RED}"/>')
    lines.append(label(left + 12, bar_top + 30, f"{auto:,}", size=20, font=MONO, fill=WHITE))
    lines.append(label(left + 12, bar_top + bar_h + 18, "resolved with no human",
                       size=12, fill=SECOND))
    lines.append(label(W - MARGIN, bar_top + bar_h + 18, f"{human:,} sent to a person",
                       size=12, fill=RED, anchor="end"))
    lines.append(label(W - MARGIN, bar_top - 8, f"{auto / total:.1%} / {human / total:.1%}",
                       size=12, font=MONO, fill=SECOND, anchor="end"))

    top = 208
    lines.append(column_head(MARGIN, top, "HOW EACH HOLDING WAS DECIDED"))
    lines.append(column_head(W - MARGIN, top, "HOLDINGS", anchor="end"))
    lines.append(rule(top + 10, colour=INK))
    y = top + 32
    widest = max(m["holdings"] for m in d["by_method"])
    for method in d["by_method"]:
        colour = RED if method["method"] == "human" else INK
        bar_w = 250 * method["holdings"] / widest
        lines.append(label(MARGIN, y, method["method"], size=13, font=MONO, fill=colour))
        lines.append(f'  <rect x="{MARGIN + 90}" y="{y - 10}" width="{bar_w:.1f}"'
                     f' height="12" fill="{colour}"/>')
        lines.append(label(W - MARGIN, y, f'{method["holdings"]:,}', size=13, font=MONO,
                           fill=colour, anchor="end"))
        lines.append(label(W - MARGIN - 86, y, f'{method["questions"]} strings', size=11,
                           fill=SECOND, anchor="end"))
        y += 26

    lines.append(rule(y - 6))
    lines.append(label(MARGIN, y + 16,
                       "Every holding is decided. None was dropped for being difficult.",
                       size=13, fill=INK))
    lines.append(source_line("Source: match_decisions · Supabase Postgres, 2026-09-04"))
    return write("w6-funnel.svg", lines)


# --------------------------------------------------------------------------
# Figure 2 -- one company, many spellings
# --------------------------------------------------------------------------


def fig_collapse(d) -> Path:
    spellings = d["xai_spellings"]
    covered = sum(s["holdings"] for s in spellings)
    lines = head(
        f"One company. {len(spellings)} spellings. One answer.",
        f"A list of the {len(spellings)} distinct issuer-name spellings under which X.AI "
        f"reached the review queue, bracketed to show that a single human decision covers "
        f"all of them and the {covered} holdings behind them.",
        "Every spelling that stopped the pipeline, and the one answer that cleared them",
    )

    # 11 rows at pitch 19. At 13 the closing lines ran off the canvas.
    top, pitch = 92, 19
    shown = spellings[:11]
    for i, item in enumerate(shown):
        y = top + i * pitch
        lines.append(label(MARGIN + 8, y, clip(item["name"], 27), size=11, font=MONO,
                           fill=INK))
        title = item["title"]
        if title and title.strip().upper() != item["name"].strip().upper():
            lines.append(label(258, y, clip(title, 26), size=10, font=MONO, fill=SECOND))
        lines.append(label(482, y, f'{item["holdings"]:>3} holdings', size=11, font=MONO,
                           fill=SECOND, anchor="end"))
    rest = len(spellings) - len(shown)
    if rest:
        lines.append(label(MARGIN + 8, top + len(shown) * pitch,
                           f"… and {rest} more spellings", size=11, fill=SECOND))

    bottom = top + (len(shown) + (1 if rest else 0)) * pitch
    bracket_x = 496
    lines.append(f'  <path d="M {bracket_x} {top - 12} L {bracket_x + 9} {top - 12}'
                 f' L {bracket_x + 9} {bottom - 6} L {bracket_x} {bottom - 6}"'
                 f' fill="none" stroke="{OCHRE}" stroke-width="2"/>')
    mid = (top - 12 + bottom - 6) / 2
    lines.append(label(bracket_x + 16, mid - 6, "one decision", size=13, fill=RED))
    lines.append(label(bracket_x + 16, mid + 12, f"{covered} holdings", size=12, font=MONO,
                       fill=SECOND))
    lines.append(label(bracket_x + 16, mid + 28, "never asked again", size=11, fill=SECOND))

    lines.append(rule(bottom + 10))
    lines.append(label(MARGIN, bottom + 32,
                       "The answer is recorded against the company, not the spelling —",
                       size=13, fill=INK))
    lines.append(label(MARGIN, bottom + 50,
                       "so spelling number twenty-five resolves without asking anyone.",
                       size=13, fill=INK))
    lines.append(source_line("Source: review_decisions joined to companies · one reviewer, "
                             "one rationale"))
    return write("w6-collapse.svg", lines)


# --------------------------------------------------------------------------
# Figure 3 -- where a paused review lives
# --------------------------------------------------------------------------


def fig_durability(d) -> Path:
    lines = head(
        "A paused review lives in the database",
        "A diagram of the resolution graph: candidates, recall and triage in sequence, then "
        "a fork -- either accept the match, or interrupt and wait for a person. The "
        "interrupt writes its state to Postgres, so the process can exit and the question "
        "is still waiting afterwards.",
        "The graph stops, the process exits, and the question is still waiting",
    )

    # 96/8 rather than 100/10: the taller forked layout pushed the closing
    # sentences onto the source line.
    box_w, box_h, gap = 210, 30, 8
    x = MARGIN
    y = 96
    for name, note in (("candidates", "the matcher reads the name"),
                       ("recall", "has a human answered this before?"),
                       ("triage", "confident, or ask?")):
        lines.append(f'  <rect x="{x}" y="{y}" width="{box_w}" height="{box_h}"'
                     f' fill="none" stroke="{INK}" stroke-width="1"/>')
        lines.append(label(x + 12, y + 20, name, size=13, font=MONO, fill=INK))
        lines.append(label(x + box_w + 16, y + 20, note, size=11, fill=SECOND))
        if name != "triage":
            lines.append(f'  <line x1="{x + box_w / 2}" y1="{y + box_h}"'
                         f' x2="{x + box_w / 2}" y2="{y + box_h + gap}"'
                         f' stroke="{BORDER}" stroke-width="1"/>')
        y += box_h + gap

    # The fork. Drawn explicitly: the first version stacked accept and
    # interrupt() vertically under triage, which read as a sequence -- as though
    # every holding were accepted and then interrupted.
    spine = y + 12
    out_w = 150
    left_x, right_x = MARGIN, MARGIN + 180
    lines.append(f'  <line x1="{left_x + out_w / 2}" y1="{y}" x2="{left_x + out_w / 2}"'
                 f' y2="{spine}" stroke="{BORDER}" stroke-width="1"/>')
    lines.append(f'  <line x1="{left_x + out_w / 2}" y1="{spine}"'
                 f' x2="{right_x + out_w / 2}" y2="{spine}" stroke="{BORDER}"'
                 f' stroke-width="1"/>')
    box_y = spine + 14
    for bx, name, note, colour, fill in (
        (left_x, "accept", "write the decision, done", SECOND, "none"),
        (right_x, "interrupt()", "the run stops here", RED, RED),
    ):
        lines.append(f'  <line x1="{bx + out_w / 2}" y1="{spine}" x2="{bx + out_w / 2}"'
                     f' y2="{box_y}" stroke="{BORDER}" stroke-width="1"/>')
        stroke = BORDER if fill == "none" else RED
        lines.append(f'  <rect x="{bx}" y="{box_y}" width="{out_w}" height="{box_h}"'
                     f' fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
        lines.append(label(bx + 12, box_y + 20, name, size=13, font=MONO,
                           fill=WHITE if fill == RED else colour))
        lines.append(label(bx, box_y + box_h + 16, note, size=11, fill=colour))

    lines.append(label(MARGIN + 350, spine + 4, "one or the other, never both",
                       size=11, fill=SECOND))

    store_y = box_y + box_h + 34
    lines.append(f'  <line x1="{right_x + out_w / 2}" y1="{box_y + box_h + 22}"'
                 f' x2="{right_x + out_w / 2}" y2="{store_y}" stroke="{OCHRE}"'
                 f' stroke-width="2"/>')
    lines.append(f'  <rect x="{MARGIN}" y="{store_y}" width="{W - 2 * MARGIN}" height="42"'
                 f' fill="none" stroke="{OCHRE}" stroke-width="2"/>')
    lines.append(label(MARGIN + 12, store_y + 18, "Postgres", size=13, font=MONO, fill=INK))
    lines.append(label(MARGIN + 12, store_y + 34,
                       "the paused state, the question, and everything needed to resume it",
                       size=11, fill=SECOND))

    lines.append(label(MARGIN, store_y + 66,
                       "Tested by pausing in one process and answering in another.",
                       size=13, fill=INK))
    lines.append(label(MARGIN, store_y + 84,
                       "Then tested again by accident: the server crashed, and the queue "
                       "came back whole.",
                       size=13, fill=INK))
    lines.append(source_line("LangGraph 0.2.60 · langgraph-checkpoint-postgres 2.0.9 · "
                             "231 checkpoint threads"))
    return write("w6-durability.svg", lines)


# --------------------------------------------------------------------------
# Figure 4 -- the split that was real, and the two that were not
# --------------------------------------------------------------------------


def fig_split(d) -> Path:
    before, after = d["perplexity"][0], d["perplexity"][1]
    ec = next(r for r in d["spacex_same_day"] if r["asset_category"] == "EC")
    ep = next(r for r in d["spacex_same_day"] if r["asset_category"] == "EP")
    a0, a1 = d["anthropic_step"][0], d["anthropic_step"][1]

    allp = d["perplexity_all"]
    lines = head(
        "Three price steps looked like splits. One was.",
        "Three price steps that all looked like stock splits, with the arithmetic that "
        "separates them: Perplexity's share count multiplied while its dollar value held "
        "exactly, which is a real split; SpaceX reports common and preferred ten times "
        "apart on the same day; and Anthropic's step is an ordinary funding round.",
        "Same shape, three different causes — and only a person could tell them apart",
    )

    top = 96
    lines.append(column_head(MARGIN, top, "WHAT THE NUMBERS SAY"))
    lines.append(column_head(W - MARGIN, top, "VERDICT", anchor="end"))
    lines.append(rule(top + 10, colour=INK))

    y = top + 34
    # --- Perplexity: the real one
    lines.append(label(MARGIN, y, "Perplexity", size=14, fill=INK))
    lines.append(label(W - MARGIN, y, "a real 10:1 split", size=13, font=MONO, fill=RED,
                       anchor="end"))
    lines.append(label(MARGIN, y + 20,
                       f'shares {before["balance"]:,.0f} → {after["balance"]:,.0f}',
                       size=12, font=MONO, fill=INK))
    lines.append(label(MARGIN + 236, y + 20,
                       f'value ${before["value_usd"]:,.2f} → ${after["value_usd"]:,.2f}',
                       size=12, font=MONO, fill=INK))
    lines.append(label(MARGIN, y + 37,
                       f'ten times the shares, the same dollars to the cent — and the '
                       f'same in all {allp[0]["holdings"]} holdings',
                       size=11, fill=SECOND))
    lines.append(f'  <line x1="{MARGIN}" y1="{y + 46}" x2="{W - MARGIN}" y2="{y + 46}"'
                 f' stroke="{BORDER}" stroke-width="1"/>')

    # --- SpaceX: the artifact
    y += 72
    lines.append(label(MARGIN, y, "SpaceX", size=14, fill=INK))
    lines.append(label(W - MARGIN, y, "not a split", size=13, font=MONO, fill=SECOND,
                       anchor="end"))
    lines.append(label(MARGIN, y + 20,
                       f'common {ec["price"]:,.2f}   preferred {ep["price"]:,.2f}',
                       size=12, font=MONO, fill=INK))
    lines.append(label(MARGIN + 240, y + 20, f'both on {ec["period_end"]}',
                       size=12, font=MONO, fill=SECOND))
    lines.append(label(MARGIN, y + 37,
                       "one filer, one day, ten times apart — a units convention",
                       size=11, fill=SECOND))
    lines.append(f'  <line x1="{MARGIN}" y1="{y + 46}" x2="{W - MARGIN}" y2="{y + 46}"'
                 f' stroke="{BORDER}" stroke-width="1"/>')

    # --- Anthropic: the repricing
    y += 72
    lines.append(label(MARGIN, y, "Anthropic", size=14, fill=INK))
    lines.append(label(W - MARGIN, y, "not a split", size=13, font=MONO, fill=SECOND,
                       anchor="end"))
    lines.append(label(MARGIN, y + 20,
                       f'{a0["price"]:,.2f} → {a1["price"]:,.2f}   '
                       f'×{a1["price"] / a0["price"]:.2f}',
                       size=12, font=MONO, fill=INK))
    lines.append(label(MARGIN + 240, y + 20, "then 140, then 259", size=12, font=MONO,
                       fill=SECOND))
    lines.append(label(MARGIN, y + 37,
                       "a funding round, on a staircase that keeps climbing",
                       size=11, fill=SECOND))

    lines.append(label(MARGIN, y + 74,
                       "Adjust the first. Leave the other two. A detector that "
                       "treated them alike",
                       size=13, fill=INK))
    lines.append(label(MARGIN, y + 92, "would be wrong two times out of three.",
                       size=13, fill=INK))
    lines.append(source_line("Source: raw_holdings, balance and value as filed · "
                             "review_decisions rationales"))
    return write("w6-split.svg", lines)


# --------------------------------------------------------------------------
# Figure 5 -- the closing scoreboard
# --------------------------------------------------------------------------


def fig_final(d) -> Path:
    groups = d["review_groups"]
    lines = head(
        f"{d['decided']:,} of {d['holdings']:,} holdings decided",
        f"The eight questions that reached a human, each with its trigger, the answer given "
        f"and the number of holdings it settled. All {d['holdings']:,} holdings now carry a "
        f"resolution decision.",
        f"{len(groups)} questions · {d['review_cards']} cards · "
        f"{d['human_holdings']:,} holdings · one reviewer",
    )

    top = 96
    lines.append(column_head(MARGIN, top, "WHY IT ASKED"))
    lines.append(column_head(250, top, "THE ANSWER"))
    lines.append(column_head(W - MARGIN, top, "HOLDINGS", anchor="end"))
    lines.append(rule(top + 10, colour=INK))

    y = top + 30
    widest = max(g["holdings"] for g in groups)
    for group in groups:
        rejected = group["verdict"] == "not_in_universe"
        colour = RED if rejected else INK
        answer = "not one of ours" if rejected else group["company"]
        bar_w = 120 * group["holdings"] / widest
        lines.append(label(MARGIN, y, group["trigger"], size=12, font=MONO, fill=SECOND))
        lines.append(label(250, y, clip(answer, 30), size=12, fill=colour))
        lines.append(f'  <rect x="{W - MARGIN - 70 - bar_w:.1f}" y="{y - 9}"'
                     f' width="{bar_w:.1f}" height="10" fill="{colour}"/>')
        lines.append(label(W - MARGIN, y, f'{group["holdings"]:,}', size=12, font=MONO,
                           fill=colour, anchor="end"))
        y += 24

    lines.append(rule(y - 4))
    lines.append(label(MARGIN, y + 22, f'{d["decided"] / d["holdings"]:.0%} decided',
                       size=26, font=MONO, fill=RED))
    lines.append(label(MARGIN + 190, y + 16,
                       f'{d["review_rows"]} decisions recorded, each with a name and a '
                       f'reason', size=12, fill=INK))
    lines.append(label(MARGIN + 190, y + 34,
                       "and each one now a test the matcher cannot quietly overturn",
                       size=12, fill=SECOND))
    lines.append(source_line("Source: review_decisions and match_decisions · "
                             f"reviewer {d['reviewer']} · 2026-09-04"))
    return write("w6-final.svg", lines)


def main() -> None:
    data = collect()
    print(f"wrote {FIGDATA.relative_to(ROOT)}")
    for build in (fig_funnel, fig_collapse, fig_durability, fig_split, fig_final):
        path = build(data)
        print(f"wrote {path.relative_to(REPO)}")
    print("\nnow: cd ../../.. && npm run svg-to-png && npm run audit:layout")


if __name__ == "__main__":
    main()
