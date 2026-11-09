# n8n code node: Code in Python1  (Week 10 — richer HTML email digest)
# Human-readable digest ONLY. The machine JSON signal is the separate "Code in
# Python" node; the two are deliberately distinct outputs (plan.md).
# Reads the run row after narratives + community opinions + sector narrative are
# attached: each leaderboard entity carries e["narrative"], e["communityOpinion"];
# the row carries row["sectorNarrative"].
import html as _html

OCHRE = "#C8860E"   # negative / mixed sentiment (brand-safe; no green, no danger-red)
RED   = "#C8102E"   # breakout emphasis only
INK   = "#2a1a0e"
SEC   = "#545454"


def esc(s):
    return _html.escape(str(s if s is not None else ""))


def arrow(v):
    if v > 0: return "&#9650;"   # ▲
    if v < 0: return "&#9660;"   # ▼
    return "&mdash;"


def sentiment_color(s):
    return OCHRE if s in ("negative", "mixed") else SEC


def func(_items):
    row = _items[0]["json"]
    lb = row.get("leaderboard", [])
    run_date = row.get("run_date", "")
    sector = row.get("sectorNarrative") or {}

    # --- Sector narrative (only if present and not degraded) ---
    sector_html = ""
    if sector.get("narrative") and not sector.get("degraded"):
        themes = " &middot; ".join(esc(t) for t in (sector.get("crossEntityThemes") or [])[:6])
        sector_html = (
            f'<p style="font-family:sans-serif;font-size:14px;color:{INK};margin:8px 0 16px">'
            f'<b>Sector this week:</b> {esc(sector["narrative"])}'
            + (f'<br><span style="color:{SEC};font-size:12px">Themes: {themes}</span>' if themes else "")
            + '</p>'
        )

    # --- Leaderboard table ---
    rows = []
    for i, e in enumerate(lb, 1):
        top = e.get("topStory") or {}
        narr = e.get("narrative") or {}
        badges = ""
        if e.get("breakout"):
            badges += f' <span style="color:{RED};font-weight:bold">BREAKOUT</span>'
        if e.get("lowConfidence"):
            badges += f' <span style="color:{SEC}">&#9888;</span>'  # ⚠
        ticker = f' <span style="color:{SEC};font-size:12px">{esc(e.get("ticker"))}</span>' if e.get("ticker") else ""
        theme_tone = ""
        if narr.get("theme") or narr.get("tone"):
            theme_tone = f'{esc(narr.get("theme") or "—")} / {esc(narr.get("tone") or "—")}'
        top_cell = "&mdash;"
        if top:
            top_cell = (f'<a href="{esc(top.get("permalink") or top.get("url"))}">'
                        f'{esc(top.get("title") or "—")}</a> '
                        f'<span style="color:{SEC}">({esc(top.get("points", 0))} pts)</span>')
        rows.append(
            f'<tr>'
            f'<td>{i}</td>'
            f'<td><b>{esc(e.get("entity"))}</b>{ticker}{badges}</td>'
            f'<td align="right">{esc(e.get("buzzScore"))}</td>'
            f'<td align="right">{arrow(e.get("velocity", 0))} {esc(e.get("velocity", 0))}</td>'
            f'<td>{theme_tone}</td>'
            f'<td>{top_cell}</td>'
            f'</tr>'
        )

    # --- Community Opinion section (per entity, in leaderboard order) ---
    op_blocks = []
    for e in lb:
        op = e.get("communityOpinion") or {}
        if op.get("degraded") or not op.get("summary"):
            continue
        sent = op.get("sentiment") or "neutral"
        low = ' <span style="color:%s;font-size:12px">(low confidence)</span>' % OCHRE if op.get("lowConfidence") else ""
        themes = " &middot; ".join(esc(t) for t in (op.get("themes") or [])[:5])
        op_blocks.append(
            f'<div style="margin:10px 0;padding:8px 12px;border-left:3px solid {SEC}">'
            f'<b>{esc(e.get("entity"))}</b> '
            f'<span style="color:{sentiment_color(sent)};text-transform:capitalize">{esc(sent)}</span>{low}<br>'
            f'<span style="font-size:13px;color:{INK}">{esc(op.get("summary"))}</span>'
            + (f'<br><span style="color:{SEC};font-size:12px">Themes: {themes}</span>' if themes else "")
            + '</div>'
        )
    opinions_html = ""
    if op_blocks:
        opinions_html = (f'<h3 style="font-family:sans-serif;color:{INK};margin-top:20px">'
                         f'Community Opinion</h3>' + "".join(op_blocks))

    html = f"""
    <div style="font-family:sans-serif;color:{INK};max-width:760px">
    <h2 style="margin-bottom:4px">Hacker News AI Buzz &mdash; {esc(run_date)}</h2>
    {sector_html}
    <table cellpadding="6" cellspacing="0"
           style="border-collapse:collapse;font-size:14px;width:100%;border:1px solid #D4D4D4">
      <tr style="background:#F0EBE3;text-align:left">
        <th>#</th><th>Entity</th><th>Buzz</th><th>Velocity</th><th>Theme / Tone</th><th>Top story</th>
      </tr>
      {''.join(rows)}
    </table>
    {opinions_html}
    <p style="color:{SEC};font-size:12px;margin-top:16px">
      &#9888; = low-confidence (sparse). Ochre = negative/mixed sentiment.
      Top stories are relevance-filtered (title must mention the entity). Automated digest.
    </p>
    </div>
    """
    return [{"json": {"subject": f"HN AI Buzz — {run_date}", "html": html}}]


return func(_items)
