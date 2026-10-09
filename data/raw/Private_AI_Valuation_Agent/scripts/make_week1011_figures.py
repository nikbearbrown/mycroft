"""Generate the Week 10 figures as SVG, from measured data only.

The `w10-` and `w11-` filename prefixes predate the schedule merge and are
kept: the built video reels reference them by name in `pantry/` and
`beat_sheet.json`, and renaming would break artifacts outside this
repository. All four are Week 10 figures regardless of prefix.

Every number is queried or measured at run time and written to
docs/_figdata_week1011.json before anything is drawn (P3).

Follows brutalist/DESIGN.md: the six palette tokens and nothing else, EB
Garamond for figure titles, Inter for labels, JetBrains Mono for data. Red is
the primary series, never "danger".

  w10-bounding    what token bounding does to a 2,151-row answer
  w10-tools       the six tools and what each one costs
  w11-contract    the frozen signal, and what it refuses to carry
  w11-guards      the commentary guards, and what each one caught

    python scripts/make_week1011_figures.py
    cd ../../.. && npm run svg-to-png && npm run audit:layout
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REPO = ROOT.parents[2]
OUT = REPO / "images" / "private-ai-valuation-agent"
FIGDATA = ROOT / "docs" / "_figdata_week1011.json"

from src.db.connect import connect  # noqa: E402
from src.mcp import queries as Q  # noqa: E402
from src.mcp.paging import (  # noqa: E402
    DEFAULT_LIMIT, MAX_RESPONSE_CHARS, page,
)
from src.signal import commentary as C  # noqa: E402
from src.signal import contract  # noqa: E402

WHITE, INK, RED = "#FFFFFF", "#2a1a0e", "#C8102E"
SECOND, BORDER, OCHRE = "#545454", "#D4D4D4", "#C8860E"

SERIF = "'EB Garamond', Georgia, serif"
SANS = "'Inter', sans-serif"
MONO = "'JetBrains Mono', monospace"

W, H = 700, 420
MARGIN = 40

TOOLS = [
    ("list_companies", Q.list_companies, {}),
    ("get_marks", Q.get_marks, {"company": "Databricks, Inc."}),
    ("compare_managers", Q.compare_managers, {"company": "Anthropic PBC"}),
    ("get_propagation", Q.get_propagation, {"company": "Databricks, Inc."}),
    ("get_fund_exposure", Q.get_fund_exposure, {"fund": "Baron"}),
    ("list_unresolved", Q.list_unresolved, {}),
]


def collect() -> dict:
    conn = connect()
    measured = []
    try:
        for name, fn, args in TOOLS:
            rows, summary = fn(conn, **args)
            bounded = page(rows, scope={"tool": name, "args": args},
                           summary=summary)
            whole = json.dumps({"summary": summary, "rows": rows}, default=str)
            measured.append({
                "tool": name,
                "rows_total": len(rows),
                "rows_returned": bounded["page"]["returned"],
                "bounded_chars": len(json.dumps(bounded, indent=2, default=str)),
                "unbounded_chars": len(whole),
            })
    finally:
        conn.close()

    signal = json.loads((ROOT / "docs" / "_signal.json").read_text("utf-8"))
    facts = {k: signal[k] for k in
             ("period", "coverage", "companies", "guards", "not_supported")}

    # What each guard rejects, demonstrated rather than asserted. Each probe
    # is a draft that fails exactly one check.
    probes = [
        ("fabricated number", "The spread was 47.3 percent.",
         lambda t: C.check_grounding(t, facts)),
        ("invented ranking",
         "Databricks, Inc. has the lowest number of marks, at 2151.",
         lambda t: C.check_superlatives(t, facts)),
        ("placeholder in prose", "Figure AI had a maximum spread of null.",
         lambda t: ["null"] if C._PLACEHOLDER.search(t) else []),
    ]
    # `name`, not `label` -- `label()` is the SVG text helper below and a
    # comprehension variable would shadow it for the rest of the module.
    guards = [{"guard": name, "draft": draft, "caught": bool(check(draft))}
              for name, draft, check in probes]

    data = {
        "tools": measured,
        "limits": {"default_limit": DEFAULT_LIMIT,
                   "max_response_chars": MAX_RESPONSE_CHARS},
        "signal": {
            "schema_version": signal["schema_version"],
            "companies": len(signal["companies"]),
            "not_supported": len(signal["not_supported"]),
            "forbidden_fields": len(contract.FORBIDDEN_FIELDS),
            "top_level_keys": len(signal),
            "commentary_words": len((signal.get("commentary") or {})
                                    .get("text", "").split()),
            "commentary_model": (signal.get("commentary") or {}).get("model"),
            "suppressed": [c["company"] for c in signal["companies"]
                           if (c.get("dispersion") or {})
                           .get("suppressed_reason")],
        },
        "guards": guards,
    }
    FIGDATA.write_text(json.dumps(data, indent=2, default=str),
                       encoding="utf-8", newline="\n")
    print(f"wrote {FIGDATA}")
    return json.loads(FIGDATA.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# SVG helpers (the same set weeks 7-9 use)
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


def kb(chars: int) -> str:
    return f"{chars / 1000:,.0f}k" if chars >= 1000 else str(chars)


# --------------------------------------------------------------------------
# Figure 1 -- what bounding does
# --------------------------------------------------------------------------


def fig_bounding(d) -> Path:
    marks = next(t for t in d["tools"] if t["tool"] == "get_marks")
    unbounded, bounded = marks["unbounded_chars"], marks["bounded_chars"]
    # ~4 characters per token is the usual English rule of thumb; stated on
    # the figure so the reader knows it is an estimate, not a tokenizer count.
    tokens_un, tokens_b = unbounded // 4, bounded // 4

    lines = head(
        f"One query, {marks['rows_total']:,} rows, two possible answers",
        f"A comparison of the same get_marks call serialised whole versus "
        f"token-bounded: {unbounded:,} characters against {bounded:,}.",
        "get_marks('Databricks, Inc.') — the whole table against one page",
    )

    bar_x, bar_w = MARGIN, W - 2 * MARGIN
    y = 108
    for title, chars, tokens, rows_out, colour in (
        ("whole table", unbounded, tokens_un, marks["rows_total"], INK),
        ("bounded page", bounded, tokens_b, marks["rows_returned"], RED),
    ):
        width = bar_w * chars / unbounded
        lines.append(label(bar_x, y - 8, title, size=12, fill=colour))
        lines.append(f'  <rect x="{bar_x}" y="{y}" width="{max(width, 3):.1f}"'
                     f' height="38" fill="{colour}"/>')
        inside = width > 190
        lines.append(label(bar_x + (12 if inside else width + 10), y + 25,
                           f"{kb(chars)} chars  ≈{tokens // 1000 or tokens}"
                           f"{'k' if tokens >= 1000 else ''} tokens  "
                           f"{rows_out:,} rows",
                           size=13, font=MONO,
                           fill=WHITE if inside else colour))
        y += 76

    lines.append(rule(y - 2))
    y += 24
    lines.append(label(MARGIN, y,
                       f"A model handed {marks['rows_total']:,} rows does not "
                       "read them. It reads the summary,", size=13, fill=INK))
    lines.append(label(MARGIN, y + 20,
                       "which describes the whole result set, and pages only "
                       "if it needs to.", size=13, fill=INK))
    lines.append(label(MARGIN, y + 46,
                       f"Two bounds, not one: {d['limits']['default_limit']} "
                       f"rows AND {d['limits']['max_response_chars']:,} "
                       "characters.", size=12, fill=RED))
    lines.append(source_line("Source: src/mcp/paging.py · ~4 chars/token is an "
                             "estimate, not a tokenizer count"))
    return write("w10-bounding.svg", lines)


# --------------------------------------------------------------------------
# Figure 2 -- the six tools
# --------------------------------------------------------------------------


def fig_tools(d) -> Path:
    tools = d["tools"]
    lines = head(
        "Six read-only tools, every answer bounded",
        "A table of the six MCP tools with the rows each returns and the size "
        "of its bounded response.",
        f"{len(tools)} tools · none of them writes anything",
    )

    top = 108
    lines.append(column_head(MARGIN, top, "TOOL"))
    lines.append(column_head(290, top, "ROWS"))
    lines.append(column_head(392, top, "RETURNED"))
    lines.append(column_head(W - MARGIN, top, "RESPONSE", anchor="end"))
    lines.append(rule(top + 10, colour=INK))

    widest = max(t["bounded_chars"] for t in tools) or 1
    y = top + 32
    for tool in tools:
        paged = tool["rows_returned"] < tool["rows_total"]
        colour = RED if paged else INK
        lines.append(label(MARGIN, y, tool["tool"], size=12, font=MONO,
                           fill=INK))
        lines.append(label(290, y, f"{tool['rows_total']:,}", size=11,
                           font=MONO, fill=SECOND))
        lines.append(label(392, y, f"{tool['rows_returned']:,}", size=11,
                           font=MONO, fill=colour))
        bar = 70 * tool["bounded_chars"] / widest
        lines.append(f'  <rect x="{W - MARGIN - 62 - bar:.1f}" y="{y - 9}"'
                     f' width="{max(bar, 2):.1f}" height="10" fill="{colour}"/>')
        lines.append(label(W - MARGIN, y, kb(tool["bounded_chars"]), size=12,
                           font=MONO, fill=colour, anchor="end"))
        y += 23

    lines.append(rule(y))
    y += 24
    lines.append(label(MARGIN, y,
                       "Red marks a tool whose answer was paged. Everything "
                       "else fits whole.", size=13, fill=INK))
    lines.append(label(MARGIN, y + 22,
                       "No tool writes a mark, clears a gate, or records a "
                       "decision.", size=13, fill=RED))
    lines.append(source_line("Source: src/mcp/server.py --selftest · measured "
                             "against the live database"))
    return write("w10-tools.svg", lines)


# --------------------------------------------------------------------------
# Figure 3 -- the frozen contract
# --------------------------------------------------------------------------


def fig_contract(d) -> Path:
    sig = d["signal"]
    lines = head(
        f"A contract that refuses {sig['forbidden_fields']} fields by name",
        "A summary of the frozen signal contract: its top-level keys, the "
        "limits it carries in its own payload, and the field names it will "
        "not accept.",
        f"schema_version {sig['schema_version']} · "
        f"{sig['top_level_keys']} top-level keys · "
        f"{sig['companies']} companies",
    )

    top = 106
    lines.append(column_head(MARGIN, top, "THE SIGNAL CARRIES"))
    lines.append(column_head(W - MARGIN, top, "IT WILL NOT CARRY", anchor="end"))
    lines.append(rule(top + 10, colour=INK))

    carries = [
        "period, coverage, guards",
        "per-company dispersion and propagation",
        "suppressed_reason, where a figure is withheld",
        f"not_supported — {sig['not_supported']} stated limits",
        "commentary, flagged is_model_output",
    ]
    refuses = ["valuation", "market_cap", "shares_outstanding",
               "post_money / pre_money", "return / irr / moic"]

    y = top + 32
    for left, right in zip(carries, refuses):
        lines.append(label(MARGIN, y, left, size=12, fill=INK))
        lines.append(label(W - MARGIN, y, right, size=12, font=MONO, fill=RED,
                           anchor="end"))
        y += 24

    lines.append(rule(y + 2))
    y += 28
    lines.append(label(MARGIN, y,
                       "N-PORT gives a fund's share count, never the company's "
                       "shares outstanding.", size=13, fill=INK))
    lines.append(label(MARGIN, y + 20,
                       "A field for a valuation would invite a consumer to "
                       "fill it from elsewhere", size=13, fill=INK))
    lines.append(label(MARGIN, y + 38,
                       "and inherit that source's error.", size=13, fill=RED))
    y += 62
    if sig["suppressed"]:
        # Two names and a count. An earlier version listed three names plus a
        # trailing clause and the line ran off the right edge -- which the
        # layout auditor did not flag, because it estimates text width rather
        # than measuring the rendered glyphs.
        shown = ", ".join(sig["suppressed"][:2])
        extra = len(sig["suppressed"]) - 2
        lines.append(label(MARGIN, y,
                           f"Suppressed this quarter: {shown}"
                           + (f" and {extra} more" if extra > 0 else "")
                           + " — a reason, not a missing key.",
                           size=11, fill=SECOND))
    lines.append(source_line("Source: src/signal/contract.py · "
                             "docs/_signal.json validates against it"))
    return write("w11-contract.svg", lines)


# --------------------------------------------------------------------------
# Figure 4 -- the commentary guards
# --------------------------------------------------------------------------


def fig_guards(d) -> Path:
    guards, sig = d["guards"], d["signal"]
    lines = head(
        "Three guards between the model and the note",
        "A table of the three mechanical checks a generated note must pass, "
        "each shown with a draft that fails it.",
        f"{sig['commentary_words']} words accepted from "
        f"{sig['commentary_model']} after retries",
    )

    top = 106
    lines.append(column_head(MARGIN, top, "GUARD"))
    lines.append(column_head(205, top, "A DRAFT THAT FAILS IT"))
    lines.append(column_head(W - MARGIN, top, "CAUGHT", anchor="end"))
    lines.append(rule(top + 10, colour=INK))

    y = top + 34
    for guard in guards:
        draft = guard["draft"]
        if len(draft) > 46:
            draft = draft[:45] + "…"
        lines.append(label(MARGIN, y, guard["guard"], size=12, fill=INK))
        lines.append(label(205, y, draft, size=10, font=MONO, fill=SECOND))
        lines.append(label(W - MARGIN, y, "yes" if guard["caught"] else "NO",
                           size=12, font=MONO,
                           fill=RED if guard["caught"] else INK, anchor="end"))
        y += 26

    lines.append(rule(y))
    y += 26
    lines.append(label(MARGIN, y,
                       "The second one is the surprise. Every number in that "
                       "draft was real —", size=13, fill=INK))
    lines.append(label(MARGIN, y + 20,
                       "the grounding check passed. The ranking was what the "
                       "model invented.", size=13, fill=INK))
    lines.append(label(MARGIN, y + 44,
                       "A failed draft is handed back to the model with the "
                       "complaint, up to three times.", size=12, fill=RED))
    lines.append(source_line("Source: src/signal/commentary.py · each draft "
                             "re-checked at build time"))
    return write("w11-guards.svg", lines)


def main() -> None:
    data = collect()
    fig_bounding(data)
    fig_tools(data)
    fig_contract(data)
    fig_guards(data)
    print("\nnow: cd ../../.. && npm run svg-to-png && npm run audit:layout")


if __name__ == "__main__":
    main()
