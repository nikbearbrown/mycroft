# CAJAL Figure Report — Chapter 3: The Verified Finance Data Contract

_Density: recommend 4 figures, [Mechanistic]._

## Figure 1 — Assertion vs. Evidence
Priority: Critical · Type: comparison panels

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a single-column two-panel comparison at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette. The left panel, Assertion, holds a short stack of plain tokens suggesting a fluent summary, model output, and three empty placeholder slots (no source path, no version, no owner) rendered in secondary orange to read as ungrounded. The right panel, Evidence, holds a taller stack of seven filled tokens — source file, period, entity, version, owner, control total, logged transformation — rendered in bluish green to read as verifiable. Between the panels draw a single left-to-right arrow indicating the conversion that the data contract performs, turning the left column into the right. Keep panel frames equal in width but let the right stack be visibly fuller to show that evidence carries more verification handles. Uniform 1pt strokes, no baked-in text, no shadows, no gradients; only the two panel colors plus a neutral arrow.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
`[C - CONTENT]` From "What Evidence Actually Means in Finance" diagram callout: Assertion (fluent summary, model output, no source path, no version, no owner) vs. Evidence (source file, period, entity, version, owner, control total, logged transformation); the contract converts the left into the right.
`[O - ORGANIZATION]` Two panels left/right; left = sparse/empty slots, right = filled stack; single → arrow (conversion).
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; Assertion #E69F00, Evidence #009E73.
`[E - EXCLUSIONS]` Omit the full eleven/twelve-field contract inventory (Figure 2), the recipe-boundary diagram (Figure 3), the phase-gate flow (Figure 4), the three-layer evidence taxonomy, AS1105 text, the board-packet numbers (61%, 14 months, -$340k).

BLOCK 3 — NEGATIVE PROMPT:
checkmarks/crosses, code, numbers, charts, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 2 — The Data Contract Field Inventory
Priority: Critical · Type: structural schematic

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a structured field schematic at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette. The chapter defines twelve contract fields; to respect the six-to-eight component limit, split into two stacked clusters of six within one figure, each cluster a labeled group-frame. Cluster one (Identity & integrity) holds six equal cells: source, period, entity, version, owner, freshness — in primary sky blue. Cluster two (Processing & accountability) holds six equal cells: schema, control total, transformation, log, report, approval record — in secondary orange, except the approval-record cell which is drawn in bluish green to mark it as the human-accountability field. Draw a single thin downward arrow from cluster one to cluster two indicating that identity fields precede processing fields. Keep cells uniform in size with reserved interior whitespace for later captioning; bake in no text. Uniform 1pt strokes, no shadows, no gradients, clean group-frame outlines.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito. Split applied: 12 fields → two clusters of six within one schematic (split point named: identity/integrity fields vs. processing/accountability fields).
`[C - CONTENT]` The twelve data-contract fields from "What a Data Contract Contains": source, period, entity, version, owner, freshness, schema, control total, transformation, log, report, approval record; approval record is the human-accountability gate field.
`[O - ORGANIZATION]` Two six-cell clusters stacked, each a group-frame; one ↓ arrow (precedence); uniform cells.
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; identity cluster #56B4E9, processing cluster #E69F00, approval-record cell #009E73.
`[E - EXCLUSIONS]` Omit the assertion/evidence panels (Figure 1), the recipe-boundary diagram (Figure 3), the phase-gate flow (Figure 4), the three-layer taxonomy, the board-packet figures, AS1105 quotation.

BLOCK 3 — NEGATIVE PROMPT:
spreadsheet gridlines mimicking a real table, code, numbers, charts, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 3 — The Recipe Boundary
Priority: Important · Type: systems diagram

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a two-side boundary diagram at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette. The left side, Preparation Layer, holds five small linked nodes for file tracing, schema comparison, control-total check, version logging, and report generation, drawn in sky blue. The right side, Accountable Layer, holds four nodes for materiality judgment, adequacy assessment, accounting treatment, and release decision, drawn in bluish green. Down the center draw a single tall vertical gate line marking that human approval is required before crossing. Draw one horizontal arrow that begins among the preparation nodes, reaches the gate line, and stops there — the recipe stops at the gate; a second short arrow resumes on the right side under the accountable nodes to show the human crossing. Keep the central gate line the dominant vertical stroke. Uniform 1pt strokes, no baked-in text, no shadows, no gradients.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
`[C - CONTENT]` From "The Recipe That Stops at the Right Place" diagram callout: preparation-layer tasks (file tracing, schema comparison, control-total check, version logging, report generation) left; accountable-layer tasks (materiality, adequacy, accounting treatment, release) right; vertical gate where human approval is required; the recipe stops at the gate, the professional crosses it.
`[O - ORGANIZATION]` Left → gate → right, horizontal; recipe arrow stops at gate; human arrow resumes past it; central gate line dominant.
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; preparation #56B4E9, accountable #009E73, gate #000000.
`[E - EXCLUSIONS]` Omit the field inventory (Figure 2), the assertion/evidence panels (Figure 1), the phase-gate linear flow (Figure 4), the three-layer taxonomy, the three supervision questions, board-packet numbers.

BLOCK 3 — NEGATIVE PROMPT:
realistic padlock, keys, code, numbers, charts, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 4 — The Phase Gate Flow
Priority: Important · Type: process flowchart

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a left-to-right process flow at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette. Start with a source-files node, then an AI-preparation node containing four small sub-marks for tracing, schema check, control total, and log, drawn in sky blue. Next place a distinct vertical gate element representing the human review with three internal check-marks for scope confirmed, approval identified, verification possible. From the gate draw two outgoing paths: a "stop conditions" path looping leftward back to preparation in reddish purple as the transitional return, and an "adequate" path continuing rightward in bluish green into a final accountable node holding materiality, treatment, and release. Make the gate the focal element. Use single-headed arrows throughout, uniform 1pt strokes, no baked-in text, no shadows, no gradients.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
`[C - CONTENT]` From "What the Gate Actually Does" diagram callout: source files → AI preparation (tracing, schema check, control total, log) → gate (reviews: scope confirmed? approval identified? verification possible?) → accountable layer (materiality, treatment, release); a stop-conditions branch loops left back to preparation; an adequate branch continues right.
`[O - ORGANIZATION]` Linear with a decision gate that branches: → forward (adequate) and ← loop-back (stop conditions); gate as focal node.
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; preparation #56B4E9, accountable forward path #009E73, stop-condition loop #CC79A7, gate #000000.
`[E - EXCLUSIONS]` Omit the recipe-boundary zones (Figure 3), the field inventory (Figure 2), the assertion/evidence panels (Figure 1), the three-layer taxonomy, the provenance-note artifact, board-packet figures.

BLOCK 3 — NEGATIVE PROMPT:
realistic padlock, keys, code, numbers, charts, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Video Candidate Pass

Figure 1 — STATIC SUFFICIENT — none — a two-state contrast; the conversion arrow conveys the single transformation in a still.
Figure 2 — STATIC SUFFICIENT — none — a reference inventory of fields; inherently static.
Figure 3 — STATIC SUFFICIENT — none — a structural boundary; stop-at-gate reads via truncated arrow.
Figure 4 — VIDEO CANDIDATE — ≥3 sequential causal stages — source → preparation sub-steps → gate decision with a branch back on stop conditions; an animated run through the gate (including the loop-back when a stop condition fires) shows the gate's two outcomes dynamically.

Video candidates: 1. Recommended for production: Figure 4 — animating a record flowing through preparation to the gate, then branching either forward (adequate) or looping back (stop condition fires), demonstrates that the gate is an active decision point, not a rubber stamp — the chapter's central claim about what the gate actually does.
