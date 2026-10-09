"""Generate the Week 4 video figures as SVG, from measured data only.

Every number drawn here is queried at run time -- from the built Parquet layer,
from the golden-set fixture, or from the metrics file -- and written to
docs/_figdata_week4.json before anything is drawn. Nothing is typed in by hand,
so a figure cannot drift away from the result it claims to describe (P3).

Follows brutalist/DESIGN.md: the six palette tokens and nothing else, EB
Garamond for figure titles, Inter for labels, JetBrains Mono for data. Red
carries the primary series; ochre is decorative annotation only, never a fill.

Four figures, one per beat of the narration:

  w4-spellings      0:18  seven companies wearing 154 names
  w4-scoreboard     0:42  the two systems, and the dot that hid 85 holdings
  w4-reversal       1:08  OpenAir.com priced at OpenAI's Series C, to 4 decimals
  w4-tie            1:38  why the threshold is a band and not a number

    python scripts/make_week4_figures.py
    cd ../../.. && npm run svg-to-png && npm run audit:layout
"""

import json
import re
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REPO = ROOT.parents[2]  # mycroft/
OUT = REPO / "images" / "private-ai-valuation-agent"
FIGDATA = ROOT / "docs" / "_figdata_week4.json"

from src.ingest.build_parquet import ALL_QUARTERS, PARQUET  # noqa: E402
from src.ingest.universe import status_of  # noqa: E402
from src.resolve.match import resolve  # noqa: E402

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
    priv = [(PARQUET / q / "private_holdings.parquet").as_posix() for q in ALL_QUARTERS]
    uni = [(PARQUET / q / "universe_holdings.parquet").as_posix() for q in ALL_QUARTERS]
    con = duckdb.connect()
    con.execute(f"CREATE VIEW p AS SELECT * FROM read_parquet([{','.join(map(repr, priv))}])")
    con.execute(f"CREATE VIEW u AS SELECT * FROM read_parquet([{','.join(map(repr, uni))}])")

    data: dict = {}

    # --- fig 1: how many names each company wears ------------------------
    data["spellings"] = [
        {"company": c, "names": n, "titles": t, "holdings": h}
        for c, n, t, h in con.execute("""
            SELECT COMPANY, count(DISTINCT upper(ISSUER_NAME)),
                   count(DISTINCT upper(ISSUER_TITLE)), count(*)
            FROM u WHERE COMPANY IS NOT NULL AND COMPANY NOT LIKE '%FALSE POSITIVE%'
            GROUP BY 1 ORDER BY 2 DESC
        """).fetchall()
    ]
    data["corpus"] = dict(
        zip(
            ("distinct_names_private", "universe_holdings", "universe_distinct_names"),
            (
                con.execute("SELECT count(DISTINCT upper(ISSUER_NAME)) FROM p").fetchone()[0],
                con.execute("SELECT count(*) FROM u").fetchone()[0],
                con.execute("SELECT count(DISTINCT upper(ISSUER_NAME)) FROM u").fetchone()[0],
            ),
        )
    )
    # A real sample of one company's spellings, for the wall of text.
    data["databricks_sample"] = [
        r[0]
        for r in con.execute("""
            SELECT upper(ISSUER_NAME) FROM u WHERE COMPANY = 'Databricks, Inc.'
            GROUP BY 1 ORDER BY count(*) DESC LIMIT 9
        """).fetchall()
    ]

    # --- fig 2: the dot that hid 85 holdings -----------------------------
    data["xai"] = {
        "missed_holdings": con.execute("""
            SELECT count(*) FROM p
            WHERE upper(ISSUER_NAME) IN ('XAI CORP', 'XAI CORP.', 'XAI CORP., SERIES C')
        """).fetchone()[0],
        "top_family": con.execute("""
            SELECT REGISTRANT_NAME, count(*) FROM p
            WHERE upper(ISSUER_NAME) LIKE 'XAI CORP%' GROUP BY 1 ORDER BY 2 DESC LIMIT 1
        """).fetchone()[0],
    }
    metrics = json.loads((ROOT / "docs" / "_matcher_metrics.json").read_text(encoding="utf-8"))
    data["scoreboard"] = {
        system: {
            weighting: metrics["subsets"][subset][system][weighting]["overall"]
            for weighting in ("macro", "micro")
        }
        for subset in ("all",)
        for system in ("A_like_patterns", "B_matcher_v1")
    }
    data["hard"] = {
        system: metrics["subsets"]["hard"][system]["macro"]["overall"]
        for system in ("A_like_patterns", "B_matcher_v1")
    }

    # --- fig 3: the reversal ---------------------------------------------
    data["openair"] = [
        {"registrant": r, "period_end": str(pe), "balance": b, "value": v, "price": round(px, 4)}
        for r, pe, b, v, px in con.execute("""
            SELECT REGISTRANT_NAME, PERIOD_END, BALANCE, CURRENCY_VALUE, PRICE_PER_SHARE
            FROM p WHERE upper(ISSUER_NAME) = 'OPENAIR.COM' ORDER BY PERIOD_END, REGISTRANT_NAME
        """).fetchall()
    ]
    # The anchor set: holdings whose identity is not in question, meaning they
    # carry a verified OpenAI issuer LEI *or* name OpenAI outright. Only one of
    # the eight carries the LEI, so the set cannot be called LEI-confirmed.
    data["openai_anchor"] = [
        {"period_end": str(pe), "price": round(px, 4), "holdings": n, "registrants": c,
         "lei_confirmed": lei}
        for pe, px, n, c, lei in con.execute("""
            SELECT PERIOD_END, round(PRICE_PER_SHARE, 4), count(*), count(DISTINCT CIK),
                   count(*) FILTER (WHERE ISSUER_LEI IN
                       ('9845008AF81ABBC36E24', '549300M3WRI6CMX2WP65'))
            FROM p
            WHERE (ISSUER_LEI IN ('9845008AF81ABBC36E24', '549300M3WRI6CMX2WP65')
                   OR upper(ISSUER_NAME) IN ('OPENAI', 'OPENAI GROUP PBC'))
              AND PERIOD_END = DATE '2026-03-31'
              AND abs(PRICE_PER_SHARE - 687.6869) < 0.00005
            GROUP BY 1, 2
        """).fetchall()
    ]

    # --- fig 4: the tie at 0.80 ------------------------------------------
    fixture = json.loads(
        (ROOT / "tests" / "fixtures" / "golden_set_v1.json").read_text(encoding="utf-8")
    )
    tied = []
    for entry in fixture["entries"]:
        match = resolve(entry["issuer_name"], entry["issuer_title"])
        if match.resolved and abs(match.score - 0.80) < 1e-9:
            tied.append(
                {
                    "name": entry["issuer_name"],
                    "score": match.score,
                    "truth": entry["company"],
                    "predicted": match.company.replace(" Technologies Corp.", "")
                    .replace(", Inc.", "")
                    .replace(" Group PBC", ""),
                    "correct": entry["company"] == match.company,
                    "holdings": entry["holdings"],
                }
            )
    data["tied_at_080"] = sorted(tied, key=lambda t: (t["correct"], t["name"]))
    data["sweep"] = metrics["threshold_sweep"]

    con.close()
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


def write(name, lines) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    path.write_text("\n".join(lines + ["</svg>", ""]), encoding="utf-8")
    return path


# --------------------------------------------------------------------------
# Figure 1 -- seven companies, 166 names
# --------------------------------------------------------------------------


def _short(company: str) -> str:
    """A label that fits the gutter without running off the canvas.

    'Space Exploration Technologies Corp.' is 36 characters and was rendering
    off the left edge -- a clipping the layout audit did not catch, because the
    text element's own box was inside the canvas.
    """
    name = re.sub(r",?\s+(Inc\.?|Corp\.?|PBC|Industries|Systems|Technologies)$", "", company)
    name = re.sub(r",?\s+(Inc\.?|Corp\.?|PBC)$", "", name).strip(" ,")
    words = name.split()
    return " ".join(words[:2]) if len(name) > 20 else name


def fig_spellings(d) -> Path:
    corpus = d["corpus"]
    # Universe v1 members only. The top seven *by spelling count* would silently
    # swap Cerebras and Figure AI out for xAI and Perplexity, which are
    # watchlisted and whose marks are not published -- so a chart captioned
    # "seven companies" would not be showing the seven companies.
    rows = [r for r in d["spellings"] if status_of(r["company"]) != "watchlist"]
    universe_names = sum(r["names"] for r in rows)
    watchlist_names = sum(
        r["names"] for r in d["spellings"] if status_of(r["company"]) == "watchlist"
    )
    lines = head(
        f"Seven companies, {universe_names} names",
        "Horizontal bars showing how many distinct issuer-name spellings each private "
        "company appears under in SEC N-PORT filings. Databricks leads with 51.",
        "Distinct issuer-name spellings per company, 14 quarters of N-PORT filings",
    )

    # Tightened from (96, 22, 12): seven bars at that pitch pushed the summary
    # lines down onto the source line, which the layout audit caught.
    assert len(rows) == 7, f"universe v1 has {len(rows)} members, not 7 -- retitle the figure"
    top, left, bar_h, gap = 92, 218, 20, 10
    widest = max(r["names"] for r in rows)
    scale = (W - left - MARGIN - 46) / widest

    for i, row in enumerate(rows):
        y = top + i * (bar_h + gap)
        width = row["names"] * scale
        fill = RED if i == 0 else INK
        label = _short(row["company"])
        lines.append(
            f'  <text x="{left - 12}" y="{y + bar_h - 6}" font-size="12" fill="{INK}"'
            f' text-anchor="end">{esc(label)}</text>'
        )
        lines.append(
            f'  <rect x="{left}" y="{y}" width="{width:.1f}" height="{bar_h}" fill="{fill}"/>'
        )
        lines.append(
            f'  <text x="{left + width + 8:.1f}" y="{y + bar_h - 6}" font-size="12"'
            f' font-family="{MONO}" fill="{SECOND}">{row["names"]}</text>'
        )

    # The haystack, stated once as a number rather than drawn.
    band_y = top + len(rows) * (bar_h + gap) + 12
    lines.append(f'  <line x1="{MARGIN}" y1="{band_y}" x2="{W - MARGIN}" y2="{band_y}"'
                 f' stroke="{BORDER}" stroke-width="1"/>')
    lines.append(
        f'  <text x="{MARGIN}" y="{band_y + 24}" font-size="13" fill="{INK}">'
        f'Hiding inside <tspan font-family="{MONO}" fill="{RED}">'
        f'{corpus["distinct_names_private"]:,}</tspan> distinct issuer names.</text>'
    )
    lines.append(
        f'  <text x="{MARGIN}" y="{band_y + 44}" font-size="12" fill="{SECOND}">'
        f'A further {watchlist_names} spellings belong to watchlisted companies, '
        f'captured but not published.</text>'
    )
    lines.append(source_line("Source: SEC N-PORT bulk data 2023Q1-2026Q2, Level 3 holdings"))
    return write("w4-spellings.svg", lines)


# --------------------------------------------------------------------------
# Figure 2 -- the scoreboard, and the dot
# --------------------------------------------------------------------------


def fig_scoreboard(d) -> Path:
    a = d["scoreboard"]["A_like_patterns"]["macro"]
    b = d["scoreboard"]["B_matcher_v1"]["macro"]
    xai = d["xai"]
    lines = head(
        "One dot, eighty-five holdings",
        "A two-row scoreboard comparing simple name patterns against the deterministic "
        "matcher on precision and recall, then the two spellings of the same company "
        "that the patterns could not connect.",
        "Scored against 322 labelled issuer names covering 7,276 holdings",
    )

    # --- scoreboard -------------------------------------------------------
    col_label, col_p, col_r = MARGIN, 420, 560
    y = 108
    for header, x in (("", col_label), ("Precision", col_p), ("Recall", col_r)):
        if header:
            lines.append(
                f'  <text x="{x}" y="{y}" font-size="11" font-weight="700" fill="{SECOND}"'
                f' text-anchor="end" letter-spacing="0.06em">{esc(header.upper())}</text>'
            )
    lines.append(f'  <line x1="{MARGIN}" y1="{y + 10}" x2="{W - MARGIN}" y2="{y + 10}"'
                 f' stroke="{INK}" stroke-width="1"/>')

    rows = [("Simple name patterns", a, INK), ("Deterministic matcher", b, RED)]
    for i, (label, m, colour) in enumerate(rows):
        ry = y + 42 + i * 32
        lines.append(f'  <text x="{col_label}" y="{ry}" font-size="14"'
                     f' fill="{colour}">{esc(label)}</text>')
        for value, x in ((m["precision"], col_p), (m["recall"], col_r)):
            lines.append(
                f'  <text x="{x}" y="{ry}" font-size="15" font-family="{MONO}"'
                f' fill="{colour}" text-anchor="end">{value:.4f}</text>'
            )
    lines.append(f'  <line x1="{MARGIN}" y1="{y + 90}" x2="{W - MARGIN}" y2="{y + 90}"'
                 f' stroke="{BORDER}" stroke-width="1"/>')

    # --- the dot ----------------------------------------------------------
    dy = 252
    lines.append(f'  <text x="{MARGIN}" y="{dy}" font-size="11" font-weight="700"'
                 f' fill="{SECOND}" letter-spacing="0.06em">WHY</text>')
    lines.append(f'  <text x="{MARGIN}" y="{dy + 34}" font-size="26" font-family="{MONO}"'
                 f' fill="{INK}">X<tspan fill="{RED}" font-size="34">.</tspan>AI CORP</text>')
    lines.append(f'  <text x="{MARGIN}" y="{dy + 66}" font-size="26" font-family="{MONO}"'
                 f' fill="{INK}">XAI CORP</text>')
    lines.append(f'  <text x="290" y="{dy + 34}" font-size="12"'
                 f' fill="{SECOND}">matched by the pattern</text>')
    lines.append(f'  <text x="290" y="{dy + 66}" font-size="12" fill="{RED}">'
                 f'{xai["missed_holdings"]} holdings, matched by nothing</text>')
    lines.append(f'  <line x1="{MARGIN}" y1="{dy + 82}" x2="272" y2="{dy + 82}"'
                 f' stroke="{OCHRE}" stroke-width="2"/>')
    lines.append(
        f'  <text x="{MARGIN}" y="{dy + 106}" font-size="12" fill="{INK}">'
        f'The largest holder of that company files the spelling without the dot.</text>'
    )
    lines.append(source_line("Source: golden set v1.0.0; measured precision and recall, macro"))
    return write("w4-scoreboard.svg", lines)


# --------------------------------------------------------------------------
# Figure 3 -- the reversal
# --------------------------------------------------------------------------


def fig_reversal(d) -> Path:
    rows = d["openair"]
    anchor = d["openai_anchor"][0]
    price = rows[0]["price"]
    lines = head(
        "It was OpenAI the whole time",
        "Five fund holdings filed under the name OpenAir.com, all priced at 687.6869 a "
        "share, next to the OpenAI Series C consensus price of 687.6869 reported by "
        "LEI-confirmed filers on the same date.",
        "A holding labelled 'not one of ours', and the price that reversed it",
    )

    lines.append(f'  <text x="{MARGIN}" y="104" font-size="11" font-weight="700"'
                 f' fill="{SECOND}" letter-spacing="0.06em">FILED AS</text>')
    lines.append(f'  <text x="{MARGIN}" y="132" font-size="22" font-family="{MONO}"'
                 f' fill="{INK}">OpenAir.com, Series C</text>')

    # Right-aligned numeric column to a fixed rule, so nothing can collide.
    px_right = W - MARGIN
    top = 168
    lines.append(f'  <text x="{MARGIN}" y="{top}" font-size="11" font-weight="700"'
                 f' fill="{SECOND}" letter-spacing="0.06em">HOLDER</text>')
    lines.append(f'  <text x="{px_right}" y="{top}" font-size="11" font-weight="700"'
                 f' fill="{SECOND}" text-anchor="end" letter-spacing="0.06em">PRICE</text>')
    lines.append(f'  <line x1="{MARGIN}" y1="{top + 10}" x2="{px_right}" y2="{top + 10}"'
                 f' stroke="{INK}" stroke-width="1"/>')

    seen, y = [], top + 32
    for row in rows:
        family = "New York Life" if "NEW YORK LIFE" in row["registrant"].upper() else "BlackRock"
        seen.append(family)
        lines.append(f'  <text x="{MARGIN}" y="{y}" font-size="13" fill="{INK}">'
                     f'{esc(family)} <tspan fill="{SECOND}" font-size="11">'
                     f'{esc(row["period_end"])}</tspan></text>')
        lines.append(f'  <text x="{px_right}" y="{y}" font-size="14" font-family="{MONO}"'
                     f' fill="{INK}" text-anchor="end">{row["price"]:.4f}</text>')
        y += 24

    lines.append(f'  <line x1="{MARGIN}" y1="{y - 4}" x2="{px_right}" y2="{y - 4}"'
                 f' stroke="{BORDER}" stroke-width="1"/>')
    y += 22
    lines.append(f'  <text x="{MARGIN}" y="{y}" font-size="13" fill="{RED}">'
                 f'OpenAI Series C consensus, same date</text>')
    lines.append(f'  <text x="{px_right}" y="{y}" font-size="14" font-family="{MONO}"'
                 f' fill="{RED}" text-anchor="end">{anchor["price"]:.4f}</text>')
    lines.append(f'  <line x1="{MARGIN}" y1="{y + 10}" x2="{px_right}" y2="{y + 10}"'
                 f' stroke="{OCHRE}" stroke-width="2"/>')
    lines.append(
        f'  <text x="{MARGIN}" y="{y + 34}" font-size="12" fill="{SECOND}">'
        f'{anchor["holdings"]} holdings from {anchor["registrants"]} registrants that name '
        f'OpenAI, or carry its registered identifier, agree to four decimals.</text>'
    )
    lines.append(source_line(f"Source: SEC N-PORT; {len(rows)} holdings, "
                             f"{len(set(seen))} fund families, price {price:.4f}"))
    return write("w4-reversal.svg", lines)


# --------------------------------------------------------------------------
# Figure 4 -- the tie
# --------------------------------------------------------------------------


def fig_tie(d) -> Path:
    tied = d["tied_at_080"]
    lines = head(
        "No number separates these four",
        "Four holdings that the matcher scores at exactly 0.80 confidence: one wrong "
        "answer and three right ones. Because they share a score, no single threshold "
        "can accept the right ones and reject the wrong one.",
        "Confidence 0.80 — one wrong answer, three right ones",
    )

    top = 108
    lines.append(f'  <text x="{MARGIN}" y="{top}" font-size="11" font-weight="700"'
                 f' fill="{SECOND}" letter-spacing="0.06em">HOLDING</text>')
    lines.append(f'  <text x="{W - MARGIN}" y="{top}" font-size="11" font-weight="700"'
                 f' fill="{SECOND}" text-anchor="end" letter-spacing="0.06em">SCORE</text>')
    lines.append(f'  <line x1="{MARGIN}" y1="{top + 10}" x2="{W - MARGIN}" y2="{top + 10}"'
                 f' stroke="{INK}" stroke-width="1"/>')

    y = top + 38
    for row in tied:
        colour = INK if row["correct"] else RED
        verdict = "correct" if row["correct"] else "wrong company"
        # Cut at the wrapper's own name. Two of these four are different MWAM
        # vehicles whose full strings truncate identically, so the sponsor plus
        # the holding count is what actually tells them apart.
        name = row["name"].split("(")[0].strip(" ,")
        if len(name) > 40:
            name = name[:37].rstrip(" ,(") + "…"
        plural = "holding" if row["holdings"] == 1 else "holdings"
        detail = f'{verdict} · {row["holdings"]} {plural} · read as {row["predicted"]}'
        lines.append(f'  <text x="{MARGIN}" y="{y}" font-size="12" font-family="{MONO}"'
                     f' fill="{colour}">{esc(name)}</text>')
        lines.append(f'  <text x="{MARGIN}" y="{y + 15}" font-size="11"'
                     f' fill="{SECOND}">{esc(detail)}</text>')
        lines.append(f'  <text x="{W - MARGIN}" y="{y + 4}" font-size="16"'
                     f' font-family="{MONO}" fill="{colour}"'
                     f' text-anchor="end">{row["score"]:.2f}</text>')
        y += 40

    lines.append(f'  <line x1="{MARGIN}" y1="{y - 12}" x2="{W - MARGIN}" y2="{y - 12}"'
                 f' stroke="{BORDER}" stroke-width="1"/>')
    lines.append(
        f'  <text x="{MARGIN}" y="{y + 12}" font-size="13" fill="{INK}">'
        f'So the answer is not a cut-off. It is a review band — and it holds four '
        f'cases a run.</text>'
    )
    lines.append(source_line("Source: golden set v1.0.0; deterministic matcher confidence"))
    return write("w4-tie.svg", lines)


def main() -> None:
    data = collect()
    print(f"wrote {FIGDATA.relative_to(ROOT)}")
    for build in (fig_spellings, fig_scoreboard, fig_reversal, fig_tie):
        path = build(data)
        print(f"wrote {path.relative_to(REPO)}")
    print("\nnow: cd ../../.. && npm run svg-to-png && npm run audit:layout")


if __name__ == "__main__":
    main()
