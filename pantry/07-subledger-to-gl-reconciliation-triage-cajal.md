# CAJAL Figure Report — Chapter 7: Subledger-to-GL Reconciliation Triage

_Density: recommend 5 figures, [Mechanistic]._

## Figure 1 — Subledger, GL, and the Reconciliation Split
Priority: Critical · Type: systems diagram

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a converging-then-splitting systems diagram at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette. On the left place two source nodes: an AR subledger node holding several small detail tokens (invoices, payments, credits, adjustments) in primary sky blue, and below it a GL control-account node shown as a single balance token in dominant blue. Both feed by single arrows into a central reconciliation-process node. From the reconciliation node, draw two diverging single arrows to two output nodes on the right: matched items (cleared) in bluish green, and an exception queue (requires accountant judgment) in secondary orange. Annotate visually that the GL control account should equal the sum of all open subledger items by drawing a thin equivalence bracket linking the subledger detail cluster to the GL balance token. Keep the central reconciliation node the structural hub. Uniform 1pt strokes, no baked-in text, no shadows, no gradients.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
`[C - CONTENT]` From "What a Subledger Reconciliation Is Actually Doing" diagram callout: AR subledger (individual invoices, payments, credits, adjustments) and GL control account (single balance) feed a reconciliation process; outputs are matched items (clear) and an exception queue (requires accountant judgment); GL control account should equal the sum of open subledger items.
`[O - ORGANIZATION]` Two sources → central reconciliation hub → two diverging outputs; equivalence bracket linking subledger sum to GL balance; single → arrows.
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; subledger #56B4E9, GL #0072B2, matched output #009E73, exception queue #E69F00.
`[E - EXCLUSIONS]` Omit the four source-verification checks (Figure 2), the deterministic/fuzzy funnel (Figure 3), the five exception classes (Figure 4), the aging schedule (Figure 5), the $47,000 example specifics, the gate-as-review-surface prose.

BLOCK 3 — NEGATIVE PROMPT:
spreadsheet rows, numbers, charts, code, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 2 — Four Source-Verification Gates
Priority: Important · Type: structural schematic

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a four-row verification schematic at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette. Stack four equal-width rows, one per pre-matching check: source-file identity (system, version, timestamp), period-coverage match, control totals, duplicate transaction IDs — all in primary sky blue. To the right of each row place a distinct vermillion stop-marker token representing the halt-and-act consequence when the check fails (re-pull, confirm period convention, reconcile export, require human review). Down the left edge run a single vertical arrow indicating these are the first gate in the recipe and must all clear before matching begins. Keep rows uniform with reserved interior whitespace for captioning; bake in no text. Uniform 1pt strokes, no shadows, no gradients; one shared frame so the four read as a single mandatory verification block.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
`[C - CONTENT]` From "The Source Verification Problem" table: four pre-matching checks — source-file identity (system/version/timestamp), period-coverage match, control totals (export ties to source system), duplicate transaction IDs — each with a halt/stop consequence if failed. Source verification is the first gate.
`[O - ORGANIZATION]` Four stacked rows under one frame; per-row stop-marker; left-edge ↓ arrow marking precedence (these run before matching).
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; checks #56B4E9, stop markers #D55E00.
`[E - EXCLUSIONS]` Omit the source/GL split diagram (Figure 1), the matching funnel (Figure 3), the five exception classes (Figure 4), the aging schedule (Figure 5), the $47,000 example, the review-surface gate prose.

BLOCK 3 — NEGATIVE PROMPT:
spreadsheet gridlines, numbers, charts, code, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 3 — Deterministic Before Fuzzy: The Matching Funnel
Priority: Critical · Type: process flowchart

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a two-stage funnel flow at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette. At the top, all items enter stage one, deterministic matching (exact transaction ID, exact amount, exact period), drawn as a wide funnel mouth in primary sky blue. Matched items exit sideways to a "cleared — no judgment needed" node in bluish green. The remaining unmatched items fall through to stage two, fuzzy matching (relaxed criteria), drawn in secondary orange, which produces a suggested classification labeled explicitly as a hypothesis. These flow into an exception-queue node where every item carries an unreviewed status, in reddish purple as the transitional state. From the exception queue draw one arrow to an accountant-review node marked as where confirmation is required before status changes. Use single forward arrows, keep the funnel narrowing downward, uniform 1pt strokes, no baked-in text, no shadows, no gradients.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
`[C - CONTENT]` From "Matching: Deterministic Before Fuzzy" diagram callout: stage 1 deterministic matching (exact ID/amount/period) → matched items exit as "cleared, no judgment"; remaining items → stage 2 fuzzy matching → "suggested classification" labeled hypothesis → exception queue with status "unreviewed" → accountant review (confirmation required before status changes). Deterministic = certainty; fuzzy = hypotheses; accountant converts hypotheses to conclusions.
`[O - ORGANIZATION]` Top-to-bottom narrowing funnel, two stages; matched items branch out at stage 1; single → arrows; exception queue → accountant review.
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; deterministic #56B4E9, cleared #009E73, fuzzy #E69F00, exception/unreviewed #CC79A7.
`[E - EXCLUSIONS]` Omit the source-verification checks (Figure 2), the source/GL split (Figure 1), the five exception classes (Figure 4), the aging schedule (Figure 5), the two-customer cross-reference, the $47,000 example.

BLOCK 3 — NEGATIVE PROMPT:
numbers, charts, code, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 4 — The Five Exception Classes
Priority: Important · Type: hierarchy/taxonomy

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a five-class taxonomy at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette, ordered by ascending urgency. Stack five equal-width class rows: timing difference (lowest urgency, clears next period, no entry), mapping error (medium, correcting journal entry), duplicate (medium, void or reverse), missing support (medium-high, control finding), unexplained (high, escalate to controller). Encode urgency by color progression that avoids red-green pairing: timing in bluish green, mapping and duplicate in secondary orange, missing support in reddish purple, unexplained in vermillion. Beside each row place a small distinct resolution-action glyph (self-clearing mark, journal-entry mark, void mark, document-search mark, escalation-up-arrow). Down the left edge run a single vertical arrow indicating rising urgency. Keep rows uniform with reserved interior whitespace for captioning; bake in no text. Uniform 1pt strokes, no shadows, no gradients.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
`[C - CONTENT]` From "The Exception Classifications" table: five mutually exclusive classes — timing difference (clears next period, low), mapping error (correcting entry, medium), duplicate (void/reverse, medium), missing support (control finding, medium-high), unexplained (escalate, high); each maps to a distinct resolution and urgency. Classification is a hypothesis the accountant confirms.
`[O - ORGANIZATION]` Five stacked rows ordered by urgency; left-edge ↓/↑ arrow (rising urgency); per-row resolution glyph.
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; timing #009E73, mapping #E69F00, duplicate #E69F00, missing support #CC79A7, unexplained #D55E00.
`[E - EXCLUSIONS]` Omit the matching funnel (Figure 3), the source-verification checks (Figure 2), the source/GL split (Figure 1), the aging schedule (Figure 5), the multi-entity exercise, the $47,000 example.

BLOCK 3 — NEGATIVE PROMPT:
traffic-light red-green coding, numbers, charts, code, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 5 — Aging the Exception Queue
Priority: Supplementary · Type: timeline/progression

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a horizontal aging-progression strip at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette. Along a left-to-right time axis marked in period intervals, show a single exception item as a token that persists across periods, changing state as it ages: at period 1 a new timing difference in bluish green (unreviewed), at period 2 still open and shifting toward secondary orange (no longer plausibly a timing difference), at period 3-plus an escalated item in vermillion requiring controller sign-off before close. Above the axis draw a faint carry-forward bracket showing that open items are always carried into the next period's queue and cannot silently age out. Keep the single item's progression the clear focus; use one token tracked across the strip rather than many tokens. Uniform 1pt strokes, no baked-in text, no shadows, no gradients, axis baseline neutral.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
`[C - CONTENT]` From "Aging the Queue and Carrying Forward" table: an open item's age changes its meaning — a timing difference open three periods is no longer a timing difference; aged items escalate; the carry-forward of prior-period open items prevents the "cleared by aging out" failure (items disappearing without a resolution record). Aging is a fact; the why is judgment.
`[O - ORGANIZATION]` Left-to-right time axis with period intervals; one item tracked across states (→ progression); carry-forward bracket above.
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; period-1 #009E73, period-2 #E69F00, period-3+ #D55E00.
`[E - EXCLUSIONS]` Omit the five-class taxonomy detail (Figure 4), the matching funnel (Figure 3), the source-verification checks (Figure 2), the source/GL split (Figure 1), the gate-as-review-surface prose, the $47,000 example.

BLOCK 3 — NEGATIVE PROMPT:
calendar illustrations, numbers, charts, code, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Video Candidate Pass

Figure 1 — STATIC SUFFICIENT — none — a stable source-to-output structure; the split reads in a still.
Figure 2 — STATIC SUFFICIENT — none — four parallel pre-checks; a reference block, not a sequence.
Figure 3 — VIDEO CANDIDATE — ≥3 sequential causal stages — items entering deterministic matching, clearing or falling through to fuzzy, becoming hypotheses, then awaiting confirmation; an animated funnel shows certainty separating from hypothesis.
Figure 4 — STATIC SUFFICIENT — none — a five-class ranking; inherently static.
Figure 5 — VIDEO CANDIDATE — transformation below direct observation — an item changing class/urgency as it ages across periods is a transition a still can only freeze at points.

Video candidates: 2. Recommended for production: Figure 3 — animating the funnel (deterministic matches clearing out, the residue dropping into fuzzy matching and emerging as labeled hypotheses) makes the chapter's central discipline — certainty before guessing, suggestions are not conclusions — kinetic and memorable.
