# CAJAL Figure Report — Chapter 4: Two Customers

_Density: recommend 4 figures, [Mechanistic]._

## Figure 1 — The Two Customers
Priority: Critical · Type: comparison panels

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a single-column two-panel comparison at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette. The left panel, the Agent Contract, holds five stacked tokens — file-path inputs, deterministic steps, output schema, stop conditions, run log — drawn in primary sky blue to read as machine-facing precision. The right panel, the Human Report Card, holds five stacked tokens — purpose statement, evidence summary, explicit caveats, decisions named, gate visible — drawn in secondary orange to read as reviewer-facing legibility. Between the two panels leave a clearly marked gap with a single neutral connector spanning it, representing what most recipes skip by serving only one customer. Keep the two panels equal in size and token count to express that both customers have genuinely different but equally complete needs. Uniform 1pt strokes, no baked-in text, no shadows, no gradients; two panel colors plus a neutral gap marker only.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
`[C - CONTENT]` From "The Two Customers" diagram callout: Agent Contract (file-path inputs, deterministic steps, output schema, stop conditions, run log) vs. Human Report Card (purpose statement, evidence summary, explicit caveats, decisions named, gate visible); the gap between them is what most recipes skip.
`[O - ORGANIZATION]` Two equal panels left/right, five tokens each; neutral connector across a marked gap (the skipped middle).
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; Agent Contract #56B4E9, Human Report Card #E69F00.
`[E - EXCLUSIONS]` Omit the five-component agent-contract detail table (Figure 2), the five-component report-card detail (Figure 3), the three-failure-mode panel (Figure 4), the two-customer recipe-note sample, the JSON example string, any dollar figures.

BLOCK 3 — NEGATIVE PROMPT:
JSON braces, code, numbers, charts, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 2 — Anatomy of the Agent Contract
Priority: Important · Type: structural schematic

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a vertical five-component schematic at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette. Stack five equal-width component bands in order: inputs, steps, output schema, stop conditions, run log — all in primary sky blue to mark the agent/machine-facing contract. Beside each band, on the right margin, place a small distinct risk-marker token in vermillion representing what goes wrong without that component (ambiguous pulls, unmaintainable runs, undetected bad output, proceeding on bad data, conclusion without basis). Connect the five bands top-to-bottom with a single thin spine arrow showing they form one ordered specification that makes a run auditable. Keep bands uniform with interior whitespace reserved for captioning; bake in no text. Uniform 1pt strokes, no shadows, no gradients, clean rectangular bands.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
`[C - CONTENT]` From "What the Agent Contract Requires" table: five components — inputs (source/version/period), steps (deterministic sequence), output schema (valid-output definition), stop conditions (halt criteria), run log (what ran and was found); each paired with its failure-if-missing. The contract is what makes a run auditable.
`[O - ORGANIZATION]` Vertical five-band stack with a top-to-bottom spine arrow (ordered); right-margin risk-marker per band.
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; components #56B4E9, risk markers #D55E00.
`[E - EXCLUSIONS]` Omit the human report-card components (Figure 3), the two-customer comparison panels (Figure 1), the three-failure-mode panel (Figure 4), the recipe-note sample, the JSON string, dollar figures.

BLOCK 3 — NEGATIVE PROMPT:
JSON braces, code, numbers, charts, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 3 — Anatomy of the Human Report Card
Priority: Important · Type: structural schematic

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a vertical five-component schematic at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette, mirroring the agent-contract figure so the pair reads as parallel. Stack five equal-width component bands in order: purpose, evidence summary, caveats, decisions, gate — in secondary orange to mark the reviewer-facing report card, except the final gate band rendered in bluish green to mark it as the accountable approval moment. Connect the bands top-to-bottom with a single thin spine arrow showing the report card builds toward the gate. Beside each band place a small neutral marker indicating the question it answers (what was this trying to find; what did it find; what it did not check; what the human must do; who approves). Keep bands uniform with interior whitespace reserved for captioning; bake in no text. Uniform 1pt strokes, no shadows, no gradients.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
`[C - CONTENT]` From "What the Human Report Card Requires" table: five components — purpose (what was this trying to find), evidence summary (what did it find), caveats (what it did not check), decisions (what the human must do), gate (who approves and what approval means); the gate is the accountable sign-off.
`[O - ORGANIZATION]` Vertical five-band stack mirroring Figure 2; top-to-bottom spine arrow building toward the gate; per-band question marker.
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; components #E69F00, gate band #009E73.
`[E - EXCLUSIONS]` Omit the agent-contract components (Figure 2), the comparison panels (Figure 1), the three-failure-mode panel (Figure 4), the recipe-note sample, the $28,400 / 14-flag specifics, the JSON string.

BLOCK 3 — NEGATIVE PROMPT:
JSON braces, code, numbers, charts, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 4 — Three Ways a Recipe Serves Neither Customer
Priority: Important · Type: comparison panels

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a three-panel failure-mode comparison at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette. Three equal columns sit side by side. Column one, Written for machines: a full agent-contract token cluster present but the human-report side empty, rendered in sky blue with a hollow gap on the human side. Column two, Written for humans: a polished output token present but the agent-contract side empty/irreproducible, rendered in orange with a hollow gap on the machine side. Column three, Written for the builder: a central implicit-knowledge token with both customer sides hollow, rendered in reddish purple as the transitional/fragile case. Below all three columns draw a single convergence arrow pointing down to one shared outcome node — both customers unserved — rendered in vermillion. Keep columns equal width; let the hollow gaps be the visual signal in each. Uniform 1pt strokes, no baked-in text, no shadows, no gradients.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
`[C - CONTENT]` From "Why Most Recipes Serve Neither" diagram callout: three failure modes — written for machines (agent contract present, no human report), written for humans (polished output, no agent contract, irreproducible), written for the builder (implicit knowledge, neither served when builder leaves); all three converge to "both customers unserved."
`[O - ORGANIZATION]` Three equal columns, each showing one side filled and the other hollow (builder column both hollow); single ↓ convergence arrow to a shared failure node.
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; machines #56B4E9, humans #E69F00, builder #CC79A7, shared failure node #D55E00.
`[E - EXCLUSIONS]` Omit the agent-contract anatomy (Figure 2), the report-card anatomy (Figure 3), the two-customer panels (Figure 1), the recipe-note sample, the accountability-thread prose, dollar/flag specifics.

BLOCK 3 — NEGATIVE PROMPT:
JSON braces, code, numbers, charts, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Video Candidate Pass

Figure 1 — STATIC SUFFICIENT — none — a two-state comparison of parallel needs; a still holds the symmetry.
Figure 2 — STATIC SUFFICIENT — none — a reference anatomy of components; inherently static.
Figure 3 — STATIC SUFFICIENT — none — a mirror reference anatomy; inherently static.
Figure 4 — STATIC SUFFICIENT — none — a three-case taxonomy converging on one outcome; the convergence reads in a still and has no temporal mechanism.

Video candidates: 0. Recommended for production: none — this chapter's content is specification and taxonomy, not sequential mechanism; every figure is a structural comparison best served by a static rendering.
