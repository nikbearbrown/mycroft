# CAJAL Figure Report — Budget-Request Normalizer and Challenge Pack
_Density: recommend 4 figures, Mechanistic._

## Figure 1 — The Normalization Pipeline
Priority: Critical · Type: systems diagram

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a left-to-right systems diagram of the budget-normalization pipeline. On the left, place six distinct input blocks representing six department submissions, each drawn with a visibly different shape or icon to convey heterogeneous templates. Converge all six into a central pipeline drawn as three sequential stages: period alignment, then account alignment, then currency alignment. On the right, the pipeline emits a single unified comparison surface block, visually regular and uniform to contrast with the irregular inputs. Use single-headed arrows from each input into the pipeline and one arrow from the pipeline to the unified surface. Keep the six inputs varied but not cluttered; the three pipeline stages should read as an ordered sequence. The contrast between irregular inputs and the single regular output carries the meaning. Flat vector, colorblind-safe palette, single 89mm column, no baked text, white background, 1pt strokes, no more than eight labeled regions.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] six department submissions in different shapes (heterogeneous templates); three-stage pipeline: period alignment, account alignment, currency alignment; single normalized comparison surface output.
[O - ORGANIZATION] six inputs on left → converge into three-stage pipeline → single unified output on right; → progression; visual irregular-to-regular contrast.
[P - PRESENTATION] flat vector; six inputs in varied secondary/transitional hues (#E69F00, #CC79A7, #F0E442); pipeline stages primary #56B4E9; unified output active #009E73; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit template-verification gate (Figure 2); omit dollar figures; omit department names; omit headcount/rate detail; omit challenge-question content; do not depict whether numbers are right.

BLOCK 3 — NEGATIVE PROMPT:
spreadsheet cells with numbers, company logos, dollar amounts, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 2 — Template Verification Gate
Priority: Important · Type: comparison panels

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a four-row comparison panel for the pre-normalization verification gate. Each row is one verification check, with three aligned cells: the check, what it catches, and the recipe action if the check fails. The four rows are template version, required fields present, period coverage match, and currency declaration. Lay the rows out as a clean stacked grid with consistent column zones. Above or alongside the rows, place a single gate symbol indicating that any failed submission does not enter the normalization pipeline — draw this as a blocking junction. Use a blocking visual treatment on the action cells to signal rejection or pause. Keep the layout calm: four rows by three zones, even spacing, single 89mm column. Use color to separate the catch zone from the action zone, not to decorate. Flat vector, colorblind-safe palette, no baked text, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] template version (old template → reject, log version received vs required, notify submitter); required fields present (missing headcount/rate/mapping → flag, pause, request resubmission); period coverage match (incomplete fiscal year → flag gap, request resubmission); currency declaration (currency not declared → flag, request declaration before normalization); gate concept: failed submission does not enter pipeline [inferred junction].
[O - ORGANIZATION] four rows (checks) by three zones (check, what it catches, action if failed); blocking gate junction marking entry refusal; ⊣ blocking on action zone.
[P - PRESENTATION] flat vector; check rows primary #56B4E9; catch zone secondary #E69F00; action/reject zone blocking #D55E00; gate junction dominant #0072B2; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit the pipeline (Figure 1); omit headcount rate-card detail; omit prior-period comparison; omit challenge-question content; omit dollar figures.

BLOCK 3 — NEGATIVE PROMPT:
checkmark/X emoji, dollar amounts, real account codes, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 3 — Prior-Period Change Table
Priority: Important · Type: statistical/quantitative

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a quantitative change-table figure for one department's budget lines. Structure it as a small grouped horizontal bar chart with a zero-anchored baseline, one cluster per account category (headcount, software renewals, a new-initiative line). For each cluster, show paired bars representing prior-year actual and submitted request so the year-over-year change is visually obvious. Mark the headcount cluster with a flag accent to indicate it exceeds the attention threshold, and mark the new-initiative line distinctly to indicate it has no prior-year counterpart (new spend). Keep the y-axis at zero with no 3D. Place a horizontal threshold reference line to indicate the attention filter. Limit to three to four categories so the chart stays legible at 89mm. Use color to distinguish prior-year from submitted bars and to mark flagged clusters. Flat vector, colorblind-safe palette, no baked numeric labels, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito; zero-anchored y-axis, no 3D.
[C - CONTENT] three account clusters (headcount, software renewals, new-initiative line); paired bars per cluster (prior-year actual, submitted request); headcount flagged above threshold; new-initiative line flagged as new spend (no prior-year counterpart); a threshold reference line.
[O - ORGANIZATION] grouped horizontal bars, zero baseline; paired prior-vs-submitted bars per cluster; threshold reference line; flag markers on headcount and new-spend clusters.
[P - PRESENTATION] flat vector; prior-year bars secondary #E69F00; submitted-request bars primary #56B4E9; flagged/over-threshold markers blocking #D55E00; threshold line black #000000; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit pipeline and gate figures; omit specific dollar values; omit challenge-question text; omit percentage callouts baked as text; omit the rate-card/assumption detail.

BLOCK 3 — NEGATIVE PROMPT:
3D bars, dollar amounts, percentage text, axis number labels, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 4 — Flag-to-Challenge-Question Flow with Distribution Gate
Priority: Supplementary · Type: process flowchart

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a left-to-right flow showing how flags become challenge questions and how the distribution gate works. On the left, three flag-type nodes: unsupported assumption, threshold-exceeding change, and new spend without rationale. Each flows by single-headed arrow into a central "generate sourced challenge question" node. From there, an arrow leads to a "planning-lead review" gate drawn as a distinct decision node, where questions may be removed, combined, or added. Only after the gate does an arrow exit to "pack distributed to departments." Mark the gate prominently to signal that nothing reaches departments before review. Keep the three flag types parallel and tidy, the generation node central, and the gate as the clear control point. Flat vector, colorblind-safe palette, single 89mm column, no baked text, white background, 1pt strokes, no more than seven labeled regions.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] three flag types (unsupported assumption, threshold-exceeding change, new spend without rationale); generate sourced challenge question node; planning-lead review gate (remove/combine/add); pack distributed to departments terminal.
[O - ORGANIZATION] three flags → generation node → planning-lead gate → distribution; → progression; gate as control point before distribution.
[P - PRESENTATION] flat vector; flag nodes secondary #E69F00; generation node primary #56B4E9; planning-lead gate dominant #0072B2; distribution terminal active #009E73; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit verbatim challenge-question wording; omit dollar figures; omit pipeline/normalization stages; omit the change-table chart; omit department names.

BLOCK 3 — NEGATIVE PROMPT:
question-mark icons, dollar amounts, speech bubbles with text, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Video Candidate Pass
Figure 1 — CANDIDATE — irregular inputs transforming into a uniform surface through sequential stages — animating six varied inputs collapsing through period, account, then currency alignment into one regular surface dramatizes normalization.
Figure 2 — NOT A CANDIDATE — static check matrix — no temporal sequence.
Figure 3 — NOT A CANDIDATE — static bar chart — comparison reads at a glance.
Figure 4 — WEAK CANDIDATE — flow could animate the gate hold — but the static figure already communicates the gate clearly.

Video candidates: 1. Recommended for production: Figure 1 — the normalization concept (heterogeneous to homogeneous) is inherently a transformation, and staged motion through the three alignment stages shows the pipeline doing structural work without judging the numbers.
