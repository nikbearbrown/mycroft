# CAJAL Figure Report — Cash Forecast Variance Explainer
_Density: recommend 4 figures, Mechanistic._

## Figure 1 — Variance Bridge Waterfall
Priority: Critical · Type: statistical/quantitative

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a waterfall (bridge) chart moving from an opening forecast balance to an actual ending balance. Start with a full bar for the opening forecast balance on the left. Add a sequence of floating step bars, one per cash-flow category (collections, payroll, vendor payments, tax, financing, other), each rising or falling to represent that category's variance, leading to a final full bar for the actual ending balance on the right. Distinguish two visual classes of step bars: explained variances (solid fill, known driver attached) and unexplained variances (hatched or patterned fill, no source found). Mark the cumulative gap between total explained and total variance as an open-variance region requiring treasury or FP&A review. Anchor the axis at zero; no 3D. Keep six categories maximum. Use single-headed connectors between steps. Color separates explained from unexplained, not categories. Single 89mm column. Flat vector, colorblind-safe palette, no baked numeric labels, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito; zero-anchored, no 3D.
[C - CONTENT] opening forecast balance bar; per-category step bars (collections, payroll, vendor payments, tax, financing, other); actual ending balance bar; explained vs unexplained visual classes; open-variance region requiring treasury/FP&A review.
[O - ORGANIZATION] left-to-right waterfall, zero baseline; opening → category steps → actual ending; explained solid vs unexplained hatched; open-gap region marked.
[P - PRESENTATION] flat vector; opening/closing anchor bars dominant #0072B2; explained steps active #009E73; unexplained steps blocking #D55E00 with hatch; open-variance region neutral hatch over #D55E00; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit version/period checks (Figure 2); omit four-state classification (Figure 3); omit escalation-record content; omit specific dollar values; omit sign-convention table.

BLOCK 3 — NEGATIVE PROMPT:
3D bars, dollar amounts, axis numbers, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 2 — Version and Period Confirmation Gates
Priority: Important · Type: process flowchart

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a two-gate stop-condition flowchart that runs before any variance computation. Show an entry node, then a first gate checking forecast version (a locked version exists that predates the period start). If unresolved, route to a halt node requiring human confirmation of the baseline version. If resolved, proceed to a second gate checking period alignment (all source data covers the same period boundaries). If unresolved, route to a halt node identifying misaligned sources and requiring correction. Only when both gates pass does an arrow proceed to a "variance analysis begins" node. Draw the two halt nodes with a blocking treatment to emphasize these are stop conditions, not warnings. Use single-headed arrows. Keep the two gates and two halts tidy and clearly sequential at 89mm. Flat vector, colorblind-safe palette, no baked text, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] entry; gate 1 forecast version (locked version predating period start; halt → require human confirmation of baseline); gate 2 period alignment (all sources cover same period; halt → identify misaligned sources, require correction); both pass → variance analysis begins.
[O - ORGANIZATION] sequential: entry → version gate → period gate → analysis-begins; each gate has a blocking halt branch; → progression, ⊣ at halts.
[P - PRESENTATION] flat vector; gate nodes dominant #0072B2; pass path active #009E73; halt nodes blocking #D55E00; entry node primary #56B4E9; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit the waterfall (Figure 1); omit driver four-state logic; omit escalation record; omit dollar figures; omit category comparison table.

BLOCK 3 — NEGATIVE PROMPT:
calendar widgets with dates, version numbers, dollar amounts, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 3 — Four-State Driver Classification
Priority: Critical · Type: process flowchart

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a classification diagram for a single category variance flowing into four mutually exclusive states. From one input node (a category variance) branch into four outcome nodes: fully explained (driver source matches full amount, reference attached), partially explained (driver matches part, residual flagged), timing-verify (dated transaction near period boundary, requires treasury confirmation), and unexplained (no driver found, escalation if material). Mark states three and four (timing-verify and unexplained) with an emphasis that they require human review before resolution, while fully explained reads as cleanly closed. Use single-headed arrows from the input to each state. Keep the four states parallel, balanced, and clearly differentiated by fill. Single 89mm column, no more than six labeled regions. Flat vector, colorblind-safe palette, no baked text, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] input: category variance; state 1 fully explained (driver matches full amount, reference attached); state 2 partially explained (driver matches part, residual flagged); state 3 timing-verify (dated transaction near boundary, treasury confirmation required); state 4 unexplained (no driver, escalation if material); states 3 and 4 require human review.
[O - ORGANIZATION] one input → four parallel state nodes; states 3 and 4 emphasized as requiring human review; → branching.
[P - PRESENTATION] flat vector; fully explained active #009E73; partially explained secondary #E69F00; timing-verify transitional #CC79A7; unexplained blocking #D55E00; input node primary #56B4E9; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit the waterfall; omit version/period gates; omit escalation-record table detail; omit dollar values; omit sign-convention content.

BLOCK 3 — NEGATIVE PROMPT:
dollar amounts, transaction-record screenshots, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 4 — Unexplained Variance Escalation Record
Priority: Supplementary · Type: structural schematic

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a schematic of the unexplained-variance escalation record as a single structured row template with labeled field zones. Show aligned field cells for: variance ID, category, amount, period, sources checked, residual after driver attachment, and escalation status. Emphasize the "sources checked" zone as a search log — represent it as a small ordered list of distinct source slots (disbursement log, AP aging, period-boundary search) to convey that the record documents what was searched, not just the gap. Mark the escalation-status zone as the terminal handoff to a controller or CFO. Keep the single template row clean and aligned, with the search-log zone visually distinct from the identifying zones. Single 89mm column. Use color to mark the search-log zone and the escalation terminal. Flat vector, colorblind-safe palette, no baked text, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] field zones: variance ID, category, amount, period, sources checked (search log: disbursement log, AP aging, period-boundary search), residual after driver attachment, escalation status (terminal handoff to controller/CFO).
[O - ORGANIZATION] single structured row template, aligned field zones; sources-checked zone shown as ordered search-log slots; escalation-status zone marked as terminal handoff.
[P - PRESENTATION] flat vector; identifying zones primary #56B4E9; search-log zone secondary #E69F00; escalation terminal dominant #0072B2; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit the waterfall; omit version/period gates; omit four-state diagram; omit specific dollar values and dates; omit forecast-revision narrative.

BLOCK 3 — NEGATIVE PROMPT:
readable field text, dollar amounts, dates, IDs as text, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Video Candidate Pass
Figure 1 — CANDIDATE — a waterfall building step by step is a natural animation — accumulating category steps and revealing the unexplained gap as a hatched region dramatizes "the gap is a finding, not a story."
Figure 2 — WEAK CANDIDATE — sequential gates could animate halts — but reads cleanly static.
Figure 3 — NOT A CANDIDATE — static four-way branch — classification reads at a glance.
Figure 4 — NOT A CANDIDATE — static record schematic — reference template.

Video candidates: 1. Recommended for production: Figure 1 — the variance bridge is the chapter's central artifact; animating the waterfall accumulating to the actual balance and exposing the unexplained hatched gap shows disaggregation defeating the plausible-narrative shortcut.
