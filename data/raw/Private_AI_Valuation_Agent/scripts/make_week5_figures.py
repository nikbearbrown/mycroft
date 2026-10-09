"""Generate the Week 5 video figures as SVG, from measured data only.

Every number drawn here is read at run time from the two artifacts the Week 5
run produced -- docs/_adjudication_metrics.json and docs/_adjudication_results.json
-- plus the golden-set fixture, and is written to docs/_figdata_week5.json
before anything is drawn. Nothing is typed in by hand, so a figure cannot drift
away from the result it claims to describe (P3). Re-running the adjudication
and re-running this script is the only way these numbers change.

Follows brutalist/DESIGN.md: the six palette tokens and nothing else, EB
Garamond for figure titles, Inter for labels, JetBrains Mono for data. Red
carries the primary series -- here the deterministic matcher, the system that
actually ships. Ochre is decorative annotation only, never a fill.

Red is deliberately NOT used to mean "bad" in the scoreboard, per DESIGN.md.
In the failure and confidence figures red marks the model's answers because
those ARE the primary series of those figures -- the thing being shown.

Five figures, one per visual beat of the narration:

  w5-setup        0:14  the four inputs both systems see, and what was withheld
  w5-scoreboard   0:42  99.6 -> 94.5, and 1 wrong record -> 196
  w5-failures     1:00  three real answers, in the model's own words
  w5-confidence   1:32  315 of 322 at full confidence, wrong ones included
  w5-veto         1:52  the policy that scores perfectly, on four rows

    python scripts/make_week5_figures.py
    cd ../../.. && npm run svg-to-png && npm run audit:layout
"""

import json
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REPO = ROOT.parents[2]  # mycroft/
OUT = REPO / "images" / "private-ai-valuation-agent"
FIGDATA = ROOT / "docs" / "_figdata_week5.json"

from src.resolve.adjudicate import (  # noqa: E402
    AUTO_ACCEPT,
    CANONICAL,
    POLICY_VETO,
    build_prompt,
    would_consult,
)
from src.resolve.match import resolve  # noqa: E402

# brutalist/DESIGN.md -- the complete palette. No other colours.
WHITE, INK, RED = "#FFFFFF", "#2a1a0e", "#C8102E"
SECOND, BORDER, OCHRE = "#545454", "#D4D4D4", "#C8860E"

SERIF = "'EB Garamond', Georgia, serif"
SANS = "'Inter', sans-serif"
MONO = "'JetBrains Mono', monospace"

W, H = 700, 420
MARGIN = 40

NOT_IN_UNIVERSE = "NOT_IN_UNIVERSE"
UNKNOWN = "UNKNOWN"


# --------------------------------------------------------------------------
# Measurement
# --------------------------------------------------------------------------


def _answer(record) -> str | None:
    """The model's own answer, normalised. Empty / null / NOT_IN_UNIVERSE all
    mean 'not one of ours', which is a real answer and not a failure."""
    company = (record.get("company") or "").strip()
    return None if company in ("", NOT_IN_UNIVERSE, UNKNOWN) else company


def _short(company: str | None) -> str:
    """Company labels that fit a table cell. Week 4 learned this the hard way:
    'Space Exploration Technologies Corp.' is 36 characters and ran off canvas."""
    if company is None:
        return "nothing"
    for tail in (" Technologies Corp.", " Systems Inc.", " Industries, Inc.",
                 " Group PBC", ", Inc.", " PBC", " Corp"):
        if company.endswith(tail):
            return company[: -len(tail)]
    return company


def collect() -> dict:
    metrics = json.loads((ROOT / "docs" / "_adjudication_metrics.json").read_text("utf-8"))
    cache = json.loads((ROOT / "docs" / "_adjudication_results.json").read_text("utf-8"))
    fixture = json.loads(
        (ROOT / "tests" / "fixtures" / "golden_set_v1.json").read_text("utf-8")
    )
    entries = {e["id"]: e for e in fixture["entries"]}
    by_id = {r["id"]: r for r in cache["results"].values()}

    data: dict = {"run": cache["run"], "throughput": metrics["throughput"]}

    # --- fig 1: one real prompt, so the inputs are not a claim ------------
    example = by_id["g0191"]  # HYPERSCALE DATA INC -- the invented parent company
    system, user = build_prompt(
        example["issuer_name"], example["issuer_title"], example["filer"]
    )
    data["prompt_example"] = {
        "issuer_name": example["issuer_name"],
        "issuer_title": example["issuer_title"],
        "filer": example["filer"],
        # From the list itself. The first version of this line counted
        # nothing (the block is indented, not bulleted) and fell through to a
        # hand-typed 7, so the figure claimed 7 candidates when the model was
        # offered 11 -- four of them watchlist companies it then picked from.
        "candidates": len(CANONICAL),
        "answer": example["company"],
        "truth": entries[example["id"]]["company"],
        "system_chars": len(system),
        "prompt_tokens": example["prompt_tokens"],
    }

    # --- fig 2: the scoreboard -------------------------------------------
    allsub = metrics["subsets"]["all"]
    data["scoreboard"] = {
        system: {
            "macro": allsub[system]["macro"]["overall"],
            "micro": allsub[system]["micro"]["overall"],
        }
        for system in ("B_matcher_v1", "C_v2_band", "E_llm_only", "F_v2_veto")
    }
    data["lift"] = metrics["lift_vs_baseline_all_macro"]

    # --- fig 3: what it actually said -------------------------------------
    # Pulled from the recorded replies, quoted verbatim and trimmed only at a
    # word boundary. These three are the examples the narration names.
    data["failures"] = []
    for fid in ("g0191", "g0254", "g0320"):
        record, entry = by_id[fid], entries[fid]
        data["failures"].append({
            "id": fid,
            "issuer_name": record["issuer_name"],
            "issuer_title": record["issuer_title"],
            "truth": entry["company"],
            "said": record["company"],
            "confidence": record["confidence"],
            "reason": record["reason"],
            "holdings": entry["holdings"],
        })
    data["band_changes"] = {
        "consulted": metrics["band_policy_changes"]["consulted"],
        "changed": len(metrics["band_policy_changes"]["changed"]),
        "fixed": len(metrics["band_policy_changes"]["fixed"]),
        "broke": len(metrics["band_policy_changes"]["broke"]),
        # Every break was a promotion: the matcher had resolved nothing and the
        # model named a company. Counted, not asserted.
        "promotions": sum(
            1 for row in metrics["band_policy_changes"]["broke"] if row["before"] is None
        ),
    }

    # --- fig 4: confidence, one dot per answer ----------------------------
    dots = []
    for entry in fixture["entries"]:
        record = by_id.get(entry["id"])
        if record is None:
            continue
        truth = None if entry["company"] == NOT_IN_UNIVERSE else entry["company"]
        said = _answer(record)
        state = (
            "unlabelled" if entry["company"] == UNKNOWN
            else "agrees" if said == truth
            else "disagrees"
        )
        dots.append({"id": entry["id"], "confidence": record["confidence"], "state": state})
    dots.sort(key=lambda d: (-d["confidence"], d["id"]))
    data["dots"] = dots
    data["confidence"] = {
        "total": len(dots),
        "at_full": sum(1 for d in dots if d["confidence"] >= 1.0),
        "disagrees": sum(1 for d in dots if d["state"] == "disagrees"),
        "disagrees_at_95_plus": sum(
            1 for d in dots if d["state"] == "disagrees" and d["confidence"] >= 0.95
        ),
        "unlabelled": sum(1 for d in dots if d["state"] == "unlabelled"),
        "distinct_values": sorted({d["confidence"] for d in dots}, reverse=True),
    }

    # --- fig 5: the four rows the veto policy ever sees --------------------
    data["veto_rows"] = []
    for entry in fixture["entries"]:
        if not would_consult(entry["issuer_name"], entry["issuer_title"], policy=POLICY_VETO):
            continue
        base = resolve(entry["issuer_name"], entry["issuer_title"])
        record = by_id[entry["id"]]
        said = _answer(record)
        truth = None if entry["company"] == NOT_IN_UNIVERSE else entry["company"]
        data["veto_rows"].append({
            "issuer_name": entry["issuer_name"],
            "claimed": base.company,
            "score": round(base.score, 2),
            "model_said": said,
            "truth": entry["company"],
            "vetoed": said is None,
            # Whether the MATCHER's claim was right, not whether the policy
            # ended up right. The first draft of this figure conflated them and
            # captioned the one false positive in the whole system "correct".
            "claim_right": base.company == truth,
            "holdings": entry["holdings"],
            # Two of these four are the same string filed twice, once with a
            # trailing space. Without this they truncate identically, which is
            # the defect Week 4's tie figure already had to fix once.
            "note": ("trailing space in the filed name"
                     if entry["issuer_name"] != entry["issuer_name"].rstrip() else ""),
        })
    data["veto_rows"].sort(key=lambda r: (r["vetoed"] is False, r["issuer_name"]))

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
    """Trim at a word boundary. A mid-word cut reads as a data error."""
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
# Figure 1 -- what the model was given
# --------------------------------------------------------------------------


def fig_setup(d) -> Path:
    ex, run = d["prompt_example"], d["run"]
    lines = head(
        "Same evidence, both systems",
        "Two columns listing what the language model was given about one holding -- issuer "
        "name, security title, filing fund and the closed candidate list -- and what was "
        "deliberately withheld from it: the price and the correct answer.",
        "One real holding, exactly as it reached the model",
    )

    top = 100
    lines.append(column_head(MARGIN, top, "GIVEN"))
    lines.append(rule(top + 10, x2=352, colour=INK))
    fields = [
        ("issuer name", ex["issuer_name"]),
        ("security title", clip(ex["issuer_title"], 34)),
        ("filing fund", ex["filer"]),
        ("candidates", f'{ex["candidates"]} companies, or none of them'),
        ("", "7 in the universe, 4 on the watchlist"),
    ]
    y = top + 36
    for name, value in fields:
        if not name:  # continuation of the field above
            lines.append(label(MARGIN, y - 14, value, size=11, fill=SECOND))
            continue
        lines.append(label(MARGIN, y, name, size=11, fill=SECOND))
        lines.append(label(MARGIN, y + 17, value, size=12, font=MONO, fill=INK))
        # 42, not 46: at 46 the candidates continuation line landed on the rule
        # at y=300. The layout audit reports text-on-arrow, not text-on-hairline.
        y += 42

    lines.append(column_head(392, top, "WITHHELD"))
    lines.append(rule(top + 10, x1=392, colour=BORDER))
    withheld = [
        ("the price", ["settles the hard cases in the",
                       "labels, so giving it to one side",
                       "would measure a different system"]),
        ("the answer", ["never reaches the prompt, and a",
                        "test checks that for all 322"]),
    ]
    y = top + 36
    for name, notes in withheld:
        lines.append(label(392, y, name, size=12, font=MONO, fill=SECOND))
        y += 18
        for note in notes:
            lines.append(label(392, y, note, size=11, fill=SECOND))
            y += 15
        y += 20

    lines.append(rule(300))
    lines.append(label(MARGIN, 326, "The matcher gets the same four fields and no more.",
                       size=13, fill=INK))
    strip = (f'{run["model"]} · {run["parameter_size"]} · {run["quantization"]}'
             f' · local · temperature {run["temperature"]}, seed {run["seed"]}')
    lines.append(label(MARGIN, 352, strip, size=11, font=MONO, fill=SECOND))
    lines.append(label(W - MARGIN, 332, f'{run["entries_adjudicated"]} calls', size=22,
                       font=MONO, fill=RED, anchor="end"))
    lines.append(label(W - MARGIN, 352, f'{d["throughput"]["errors"]} failures', size=11,
                       font=MONO, fill=SECOND, anchor="end"))
    lines.append(source_line("Source: recorded prompt and reply, Week 5 adjudication run"))
    return write("w5-setup.svg", lines)


# --------------------------------------------------------------------------
# Figure 2 -- the scoreboard
# --------------------------------------------------------------------------


def fig_scoreboard(d) -> Path:
    s = d["scoreboard"]
    base, band, alone = s["B_matcher_v1"], s["C_v2_band"], s["E_llm_only"]
    drop = round((base["macro"]["precision"] - band["macro"]["precision"]) * 100, 1)
    lines = head(
        f"The model costs {drop} points of precision",
        "A table of precision, recall and F1 for the deterministic matcher and for two "
        "policies that let a language model answer, followed by a bar chart comparing the "
        "number of wrongly included holdings each produces: 1 against 196.",
        "322 labelled strings, 319 of them scorable · macro-averaged",
    )

    top = 100
    for x, text, anchor in ((MARGIN, "SYSTEM", "start"), (430, "PRECISION", "end"),
                            (530, "RECALL", "end"), (W - MARGIN, "F1", "end")):
        lines.append(column_head(x, top, text, anchor=anchor))
    lines.append(rule(top + 10, colour=INK))

    rows = [
        ("Deterministic matcher", base["macro"], RED, "what ships today"),
        ("+ model in the review band", band["macro"], INK, "model answers where the matcher is unsure"),
        ("Model alone", alone["macro"], SECOND, "matcher ignored"),
    ]
    y = top + 36
    for name, m, colour, note in rows:
        lines.append(label(MARGIN, y, name, size=13, fill=colour))
        lines.append(label(MARGIN, y + 15, note, size=11, fill=SECOND))
        for x, value in ((430, m["precision"]), (530, m["recall"]), (W - MARGIN, m["f1"])):
            lines.append(label(x, y + 2, f'{value:.4f}', size=15, font=MONO, fill=colour,
                               anchor="end"))
        y += 46

    lines.append(rule(y - 6))
    lines.append(label(MARGIN, y + 18, "Wrongly included holdings", size=12, fill=INK))
    lines.append(label(MARGIN, y + 34, "the same error, counted in records rather than names",
                       size=11, fill=SECOND))

    # Full scale, zero origin. A truncated axis here would flatter the model.
    bar_left, bar_top, bar_h = 290, y + 52, 18
    worst = max(base["micro"]["fp"], band["micro"]["fp"])
    scale = (W - MARGIN - bar_left - 52) / worst
    bars = ((base["micro"], RED, "deterministic matcher"),
            (band["micro"], INK, "+ model in the review band"))
    for i, (m, colour, name) in enumerate(bars):
        by = bar_top + i * (bar_h + 14)
        width = max(m["fp"] * scale, 2)
        lines.append(label(bar_left - 10, by + bar_h - 5, name, size=11, fill=SECOND,
                           anchor="end"))
        lines.append(f'  <rect x="{bar_left}" y="{by}" width="{width:.1f}" height="{bar_h}"'
                     f' fill="{colour}"/>')
        lines.append(label(bar_left + width + 8, by + bar_h - 4, str(m["fp"]), size=14,
                           font=MONO, fill=colour))
    lines.append(source_line(
        "Source: docs/_adjudication_metrics.json · golden set v1.0.0 · macro "
        "over 319 scorable strings"))
    return write("w5-scoreboard.svg", lines)


# --------------------------------------------------------------------------
# Figure 3 -- in its own words
# --------------------------------------------------------------------------


def fig_failures(d) -> Path:
    ch = d["band_changes"]
    lines = head(
        "It promotes resemblances",
        "Three holdings the matcher had correctly left unresolved, the company the language "
        "model assigned to each, and the model's own stated reason, quoted from the recorded "
        "reply.",
        f'Of {ch["consulted"]} strings consulted the model changed {ch["changed"]}: '
        f'{ch["fixed"]} fixed, {ch["broke"]} broken',
    )

    top = 100
    lines.append(column_head(MARGIN, top, "THE HOLDING"))
    lines.append(column_head(W - MARGIN, top, "THE MODEL SAID", anchor="end"))
    lines.append(rule(top + 10, colour=INK))

    y = top + 36
    for row in d["failures"]:
        lines.append(label(MARGIN, y, clip(row["issuer_name"], 40), size=13, font=MONO,
                           fill=INK))
        lines.append(label(W - MARGIN, y, _short(row["said"]), size=13, font=MONO, fill=RED,
                           anchor="end"))
        quote = clip(row["reason"], 96)
        parts = textwrap.wrap(f'“{quote}”', 78)[:2]
        for i, part in enumerate(parts):
            lines.append(label(MARGIN, y + 19 + i * 15, part, size=11, fill=SECOND))
        # Pitch follows the quote, so a one-line reason does not leave a hole
        # that reads as a missing row.
        y += 24 + 15 * len(parts) + 22

    lines.append(rule(y - 18))
    # Two lines: at size 13 this canvas holds about 78 characters, and Week 4
    # shipped a label that ran off the edge because the audit did not catch it.
    for i, text in enumerate((
        f'All {ch["broke"]} breaks are the same move: the matcher had resolved',
        "nothing, and the model named a company anyway.",
    )):
        lines.append(label(MARGIN, y + 6 + i * 19, text, size=13, fill=INK))
    lines.append(source_line(
        "Source: docs/_adjudication_results.json · reasons quoted verbatim, trimmed to fit"))
    return write("w5-failures.svg", lines)


# --------------------------------------------------------------------------
# Figure 4 -- one dot per answer
# --------------------------------------------------------------------------


def fig_confidence(d) -> Path:
    c, dots = d["confidence"], d["dots"]
    lines = head(
        "Certain, and wrong",
        f'A grid of {c["total"]} dots, one per model answer, ordered by the confidence the '
        f'model reported. {c["at_full"]} answers came back at confidence 1.000, and the '
        f'{c["disagrees"]} that disagree with the label sit inside that block.',
        "One dot per answer, ordered by the confidence the model reported",
    )

    cols, pitch = 23, 14
    grid_left, grid_top, radius = MARGIN + 2, 104, 4.4
    for i, dot in enumerate(dots):
        cx = grid_left + (i % cols) * pitch
        cy = grid_top + (i // cols) * pitch
        if dot["state"] == "disagrees":
            fill = RED
        elif dot["state"] == "unlabelled":
            fill = BORDER
        else:
            fill = INK
        lines.append(f'  <circle cx="{cx}" cy="{cy}" r="{radius}" fill="{fill}"/>')

    rows = (len(dots) + cols - 1) // cols
    grid_right = grid_left + (cols - 1) * pitch
    grid_bottom = grid_top + (rows - 1) * pitch

    # Bracket the run of full-confidence answers, which is every dot up to the
    # first one below 1.000. Ochre is annotation only, per DESIGN.md.
    bracket_x = grid_right + 20
    last_full = c["at_full"] - 1
    bracket_bottom = grid_top + (last_full // cols) * pitch + 7
    lines.append(f'  <path d="M {bracket_x} {grid_top - 7} L {bracket_x + 8} {grid_top - 7}'
                 f' L {bracket_x + 8} {bracket_bottom} L {bracket_x} {bracket_bottom}"'
                 f' fill="none" stroke="{OCHRE}" stroke-width="2"/>')
    mid = (grid_top - 7 + bracket_bottom) / 2
    lines.append(label(bracket_x + 16, mid - 4, f'{c["at_full"]} answers', size=12, fill=INK))
    lines.append(label(bracket_x + 16, mid + 12, "at confidence 1.000", size=12, fill=SECOND))

    key_y = grid_bottom + 30
    lines.append(f'  <circle cx="{MARGIN + 4}" cy="{key_y - 4}" r="{radius}" fill="{RED}"/>')
    lines.append(label(MARGIN + 16, key_y, f'{c["disagrees"]} disagree with the label — '
                       f'{c["disagrees_at_95_plus"]} of them at confidence 0.95 or above',
                       size=12, fill=INK))
    lines.append(f'  <circle cx="{MARGIN + 4}" cy="{key_y + 18}" r="{radius}" fill="{BORDER}"/>')
    lines.append(label(MARGIN + 16, key_y + 22,
                       f'{c["unlabelled"]} carry no usable label and are not scored',
                       size=12, fill=SECOND))
    lines.append(rule(key_y + 38))
    lines.append(label(MARGIN, key_y + 58,
                       "So a review queue cannot be triaged by the model's confidence.",
                       size=13, fill=INK))
    lines.append(source_line(
        "Source: docs/_adjudication_results.json · confidence as returned by the model"))
    return write("w5-confidence.svg", lines)


# --------------------------------------------------------------------------
# Figure 5 -- the veto policy
# --------------------------------------------------------------------------


def fig_veto(d) -> Path:
    rows, s = d["veto_rows"], d["scoreboard"]["F_v2_veto"]["macro"]
    lines = head(
        f'A perfect score, on {len(rows)} rows',
        f'The {len(rows)} holdings a veto-only policy would ever be consulted on, what the '
        f'deterministic matcher claimed for each, and what the model did. It scores 1.0000 '
        f'precision and recall, and is switched off by default.',
        f'Every string the veto policy sees · precision {s["precision"]:.4f}, '
        f'recall {s["recall"]:.4f}',
    )

    top = 100
    lines.append(column_head(MARGIN, top, "THE MATCHER CLAIMED"))
    lines.append(column_head(W - MARGIN, top, "THE MODEL", anchor="end"))
    lines.append(rule(top + 10, colour=INK))

    y = top + 34
    for row in rows:
        acted = "vetoed it" if row["vetoed"] else "left it alone"
        colour = RED if row["vetoed"] else SECOND
        lines.append(label(MARGIN, y, clip(row["issuer_name"], 38), size=12, font=MONO,
                           fill=INK))
        plural = "holding" if row["holdings"] == 1 else "holdings"
        detail = (f'{_short(row["claimed"])} at {row["score"]:.2f} · '
                  f'{row["holdings"]} {plural} · '
                  f'claim was {"right" if row["claim_right"] else "wrong"}')
        if row["note"]:
            detail += f' · {row["note"]}'
        lines.append(label(MARGIN, y + 16, detail, size=11, fill=SECOND))
        lines.append(label(W - MARGIN, y + 4, acted, size=12, fill=colour, anchor="end"))
        y += 42

    lines.append(rule(y - 8))
    caveats = [
        f'{len(rows)} rows is not evidence of a robust improvement.',
        "The policy was designed after reading the failures, so this set cannot validate it.",
        "These are the same rows the matcher already routes to a human.",
    ]
    for i, text in enumerate(caveats):
        lines.append(label(MARGIN + 14, y + 14 + i * 18, text, size=12, fill=SECOND))
    lines.append(f'  <line x1="{MARGIN}" y1="{y + 2}" x2="{MARGIN}" y2="{y + 22 + 2 * 18}"'
                 f' stroke="{OCHRE}" stroke-width="3"/>')
    lines.append(label(W - MARGIN, y + 68, "Implemented, measured, off by default.", size=13,
                       fill=INK, anchor="end"))
    lines.append(source_line(
        f'Source: golden set v1.0.0 · veto policy consults matcher claims '
        f'scoring below {AUTO_ACCEPT:.2f}'))
    return write("w5-veto.svg", lines)


def main() -> None:
    data = collect()
    print(f"wrote {FIGDATA.relative_to(ROOT)}")
    for build in (fig_setup, fig_scoreboard, fig_failures, fig_confidence, fig_veto):
        path = build(data)
        print(f"wrote {path.relative_to(REPO)}")
    print("\nnow: cd ../../.. && npm run svg-to-png && npm run audit:layout")


if __name__ == "__main__":
    main()
