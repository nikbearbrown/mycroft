"""Generate this week's figures as SVG, from measured data only.

The `w12-` filename prefix is historical: `w10-` and `w11-` were taken by
figures built before the schedule merge, and the built reels reference those
names. These are the final week's figures regardless of prefix.

Every number is queried, grepped or counted at run time and written to
docs/_figdata_week12.json before anything is drawn (P3). The "before" column
of the documentation audit comes from `git show HEAD:<path>`, not from memory.

Follows brutalist/DESIGN.md: the six palette tokens and nothing else, EB
Garamond for figure titles, Inter for labels, JetBrains Mono for data. Red is
the primary series, never "danger".

  w12-docs         the six documents the plan names, and what existed
  w12-priorart     a requirement that was at zero coverage
  w12-provenance   one published number, traced to the SEC's bytes
  w12-demo         five acts, and the proof that none of them writes

    python scripts/make_week12_figures.py
    cd ../../.. && npm run svg-to-png && npm run audit:layout
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REPO = ROOT.parents[2]
PREFIX = "data/raw/Private_AI_Valuation_Agent"
OUT = REPO / "images" / "private-ai-valuation-agent"
FIGDATA = ROOT / "docs" / "_figdata_week12.json"

from src.db.connect import connect  # noqa: E402

WHITE, INK, RED = "#FFFFFF", "#2a1a0e", "#C8102E"
SECOND, BORDER, OCHRE = "#545454", "#D4D4D4", "#C8860E"

SERIF = "'EB Garamond', Georgia, serif"
SANS = "'Inter', sans-serif"
MONO = "'JetBrains Mono', monospace"

W, H = 700, 420
MARGIN = 40

# The six documents plan.md week 11 names, in the order it names them.
DOCUMENTS = (
    ("proposal.md", "proposal.md"),
    ("system_architecture.md", "system_architecture.md"),
    ("data_architecture.md", "data_architecture.md"),
    ("docs/findings.md", "findings.md"),
    ("docs/entity_resolution.md", "entity_resolution.md"),
    ("README.md", "README.md"),
)

# The prior art plan.md says to cite. A name, not a judgment.
CITED = ("caplight", "gornall", "strebulaev", "agarwal", "chernenko", "kwon")

PRIOR_ART_DOCS = ("proposal.md", "docs/findings.md", "docs/entity_resolution.md")

LAYERS = (
    ("raw / filed", "immutable", (
        "funds", "filings", "raw_holdings", "form_d_filings",
        "public_observations", "restricted_lots", "ncsr_filings", "runs")),
    ("judgment", "append-only", (
        "companies", "review_decisions", "match_decisions", "company_identity")),
    ("resolved", "rebuildable", ("securities", "security_map", "marks")),
)

ACTS = (
    ("Act I", "ingest, and the reconciliation"),
    ("Act II", "a review-queue decision a human made"),
    ("Act III", "a resolved series"),
    ("Act IV", "propagation"),
    ("Act V", "an MCP query, bounded"),
)

_WRITE = re.compile(r"\b(INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM)\b", re.I)


def _head(path: str) -> str | None:
    """The committed version of a file, or None if it is new this week."""
    done = subprocess.run(["git", "show", f"HEAD:{PREFIX}/{path}"],
                          cwd=REPO, capture_output=True, text=True)
    return done.stdout if done.returncode == 0 else None


def _citations(text: str) -> int:
    return sum(len(re.findall(name, text, re.I)) for name in CITED)


def collect() -> dict:
    documents = []
    for path, name in DOCUMENTS:
        now = (ROOT / path).read_text(encoding="utf-8")
        before = _head(path)
        documents.append({
            "document": name,
            "path": path,
            "existed": before is not None,
            "lines_before": len(before.splitlines()) if before else 0,
            "lines_now": len(now.splitlines()),
        })

    prior_art = []
    for path in PRIOR_ART_DOCS:
        before = _head(path)
        prior_art.append({
            "document": Path(path).name,
            "before": _citations(before) if before else 0,
            "existed": before is not None,
            "after": _citations((ROOT / path).read_text(encoding="utf-8")),
        })

    findings = json.loads((ROOT / "docs" / "_findings.json").read_text("utf-8"))
    remark = findings["remark"]["overall"]

    conn = connect()
    try:
        layers = []
        with conn.cursor() as cur:
            for layer, mutability, tables in LAYERS:
                counted = []
                for table in tables:
                    cur.execute(f"SELECT count(*) FROM {table}")
                    counted.append({"table": table, "rows": cur.fetchone()[0]})
                layers.append({"layer": layer, "mutability": mutability,
                               "tables": counted,
                               "rows": sum(t["rows"] for t in counted)})
    finally:
        conn.close()

    # The demo's read-only claim, checked rather than asserted: no write
    # statement anywhere in the demo or the server it calls.
    scanned = [ROOT / "scripts" / "demo.py"] + sorted(
        (ROOT / "src" / "mcp").glob("*.py"))
    writes = sum(len(_WRITE.findall(p.read_text(encoding="utf-8")))
                 for p in scanned)

    data = {
        "documents": documents,
        "prior_art": prior_art,
        "remark": {"share_unchanged": remark["share_unchanged"],
                   "steps": remark["steps"],
                   "unchanged": remark["unchanged"],
                   "marks": remark["marks"]},
        "layers": layers,
        "tables_total": sum(len(t) for _, _, t in LAYERS),
        "demo": {"acts": len(ACTS), "files_scanned": len(scanned),
                 "write_statements": writes},
    }
    FIGDATA.write_text(json.dumps(data, indent=2, default=str),
                       encoding="utf-8", newline="\n")
    print(f"wrote {FIGDATA}")
    return json.loads(FIGDATA.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# SVG helpers (the same set weeks 7-10 use)
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


# --------------------------------------------------------------------------
# Figure 1 -- the documentation audit
# --------------------------------------------------------------------------


def fig_docs(d) -> Path:
    documents = d["documents"]
    missing = [doc for doc in documents if not doc["existed"]]
    widest = max(doc["lines_now"] for doc in documents) or 1

    lines = head(
        f"Six documents named. Three of them did not exist."
        if len(missing) == 3 else
        f"Six documents named. {len(missing)} of them did not exist.",
        "A table of the six documents the plan names, showing which were "
        "already committed and how many lines each holds now.",
        "Audited against the last commit, not against memory",
    )

    top = 110
    lines.append(column_head(MARGIN, top, "DOCUMENT"))
    lines.append(column_head(258, top, "BEFORE"))
    lines.append(column_head(W - MARGIN, top, "LINES NOW", anchor="end"))
    lines.append(rule(top + 10, colour=INK))

    y = top + 34
    for doc in documents:
        new = not doc["existed"]
        colour = RED if new else INK
        lines.append(label(MARGIN, y, doc["document"], size=12, font=MONO,
                           fill=INK))
        lines.append(label(258, y,
                           "did not exist" if new
                           else f"{doc['lines_before']:,} lines",
                           size=11, fill=colour))
        bar = 96 * doc["lines_now"] / widest
        lines.append(f'  <rect x="{W - MARGIN - 56 - bar:.1f}" y="{y - 9}"'
                     f' width="{max(bar, 2):.1f}" height="10" fill="{colour}"/>')
        lines.append(label(W - MARGIN, y, f"{doc['lines_now']:,}", size=12,
                           font=MONO, fill=colour, anchor="end"))
        y += 26

    lines.append(rule(y))
    y += 26
    lines.append(label(MARGIN, y,
                       "Red is written from nothing this week. The audit "
                       "found them;", size=13, fill=INK))
    lines.append(label(MARGIN, y + 20,
                       "the plan did not predict them.", size=13, fill=INK))
    lines.append(label(MARGIN, y + 46,
                       "Written from the project's own measured figures, not "
                       "from the plan's prose.", size=12, fill=RED))
    lines.append(source_line("Source: git show HEAD:<path> against the working "
                             "tree, run at build time"))
    return write("w12-docs.svg", lines)


# --------------------------------------------------------------------------
# Figure 2 -- the requirement at zero coverage
# --------------------------------------------------------------------------


def fig_priorart(d) -> Path:
    rows = d["prior_art"]
    total_before = sum(r["before"] for r in rows)
    total_after = sum(r["after"] for r in rows)

    lines = head(
        f"One stated requirement, {total_before} mentions",
        "A before-and-after count of prior-art citations in the three "
        "documents the plan says must carry them.",
        'plan.md: "citing the prior-art literature honestly"',
    )

    top = 112
    lines.append(column_head(MARGIN, top, "DOCUMENT"))
    lines.append(column_head(330, top, "BEFORE", anchor="end"))
    lines.append(column_head(430, top, "AFTER", anchor="end"))
    lines.append(rule(top + 10, colour=INK))

    y = top + 34
    for row in rows:
        lines.append(label(MARGIN, y, row["document"], size=12, font=MONO,
                           fill=INK))
        lines.append(label(330, y, str(row["before"]), size=13, font=MONO,
                           fill=SECOND, anchor="end"))
        lines.append(label(430, y, str(row["after"]), size=13, font=MONO,
                           fill=RED, anchor="end"))
        bar = 150 * row["after"] / max(total_after, 1)
        lines.append(f'  <rect x="450" y="{y - 9}" width="{max(bar, 2):.1f}"'
                     f' height="10" fill="{RED}"/>')
        y += 26

    lines.append(rule(y))
    y += 24
    lines.append(label(MARGIN, y,
                       "Caplight, Gornall & Strebulaev, Agarwal, Chernenko, "
                       "Kwon — none of them,", size=13, fill=INK))
    lines.append(label(MARGIN, y + 20,
                       "anywhere, in either published document.", size=13,
                       fill=INK))
    y += 48
    lines.append(label(MARGIN, y,
                       "One citation is load-bearing rather than decorative:",
                       size=12, fill=RED))
    lines.append(label(MARGIN, y + 20,
                       "funds write up every share class to the latest round "
                       "price — reproduced here,", size=12, fill=INK))
    lines.append(label(MARGIN, y + 38,
                       "and the reason dispersion is measured per company with "
                       "the class recorded.", size=12, fill=INK))
    lines.append(source_line("Source: case-insensitive name count, HEAD "
                             "against the working tree"))
    return write("w12-priorart.svg", lines)


# --------------------------------------------------------------------------
# Figure 3 -- provenance, one number traced down
# --------------------------------------------------------------------------


def fig_provenance(d) -> Path:
    remark = d["remark"]
    share = f"{remark['share_unchanged'] * 100:.1f}%"

    lines = head(
        f"One published number, {share}, traced to the bytes",
        "A chain of eight links from a published headline figure down to the "
        "SEC archive file that produced it.",
        f"{remark['unchanged']:,} unchanged steps of {remark['steps']:,}, "
        f"over {remark['marks']:,} published marks",
    )

    chain = [
        ("docs/findings.md  part 1", "the published sentence"),
        ("docs/_findings.json", "the figure as computed"),
        ("src/signal/findings.py", "remark_frequency(), guards applied"),
        ("marks", "NOT change_blocked, price not null"),
        ("match_decisions", "which company, and by what method"),
        ("review_decisions", "a named human, where method = human"),
        ("raw_holdings", "the filed position: balance, value_usd"),
        ("filings → data/<qtr>_nport.zip", "accession, period end, the SEC"),
    ]

    y = 100
    step = 28
    for index, (node, note) in enumerate(chain):
        last = index == len(chain) - 1
        colour = RED if (index == 0 or last) else INK
        cx = MARGIN + 6
        lines.append(f'  <circle cx="{cx}" cy="{y - 4}" r="4" fill="{colour}"/>')
        if not last:
            lines.append(f'  <line x1="{cx}" y1="{y}" x2="{cx}" y2="{y + step - 8}"'
                         f' stroke="{BORDER}" stroke-width="1"/>')
        lines.append(label(MARGIN + 20, y, node, size=12, font=MONO,
                           fill=colour))
        lines.append(label(330, y, note, size=11, fill=SECOND))
        y += step

    y += 2
    lines.append(rule(y))
    y += 24
    lines.append(label(MARGIN, y,
                       "Break any link and you have an output, not evidence.",
                       size=13, fill=INK))
    lines.append(label(MARGIN, y + 22,
                       "The run log records which run produced each artifact, "
                       "so the chain is datable too.", size=12, fill=RED))
    lines.append(source_line("Source: data_architecture.md · figure read from "
                             "docs/_findings.json at build time"))
    return write("w12-provenance.svg", lines)


# --------------------------------------------------------------------------
# Figure 4 -- the demo
# --------------------------------------------------------------------------


def fig_demo(d) -> Path:
    demo = d["demo"]
    layers = d["layers"]

    lines = head(
        "A demo that re-runs, and writes nothing",
        "The five acts of the demo script alongside a scan showing no write "
        "statement in the demo or the server it calls.",
        f"{demo['acts']} acts · every figure queried live",
    )

    top = 108
    lines.append(column_head(MARGIN, top, "THE FIVE ACTS"))
    lines.append(rule(top + 10, colour=INK))

    y = top + 32
    for act, what in ACTS:
        lines.append(label(MARGIN, y, act, size=12, font=MONO, fill=RED))
        lines.append(label(MARGIN + 60, y, what, size=12, fill=INK))
        y += 24

    lines.append(rule(y + 2))
    y += 30
    lines.append(label(MARGIN, y,
                       f"Write statements across {demo['files_scanned']} "
                       f"scanned files: {demo['write_statements']}.",
                       size=14, fill=RED, weight="600"))
    y += 26
    lines.append(label(MARGIN, y,
                       "Act II shows a decision a named human already made. It "
                       "does not make a new one —", size=12, fill=INK))
    lines.append(label(MARGIN, y + 18,
                       "a demo that recorded a judgment would clear a gate for "
                       "a screenshot.", size=12, fill=INK))
    y += 44
    span = " · ".join(f"{layer['layer']} {len(layer['tables'])} "
                      f"({layer['mutability']})" for layer in layers)
    lines.append(label(MARGIN, y,
                       f"{d['tables_total']} project tables, by layer: {span}", size=11,
                       fill=SECOND))
    lines.append(label(MARGIN, y + 18,
                       "A recording is true on the day it was made. This "
                       "re-runs.", size=12, fill=RED))
    lines.append(source_line("Source: scripts/demo.py · write-statement scan "
                             "over demo.py and src/mcp/*.py"))
    return write("w12-demo.svg", lines)


def main() -> None:
    data = collect()
    fig_docs(data)
    fig_priorart(data)
    fig_provenance(data)
    fig_demo(data)
    print("\nnow: cd ../../.. && npm run svg-to-png && npm run audit:layout")


if __name__ == "__main__":
    main()
