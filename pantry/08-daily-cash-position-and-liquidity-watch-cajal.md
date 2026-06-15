# CAJAL Figure Report — Chapter 8: Daily Cash Position and Liquidity Watch

_Density: recommend 4 figures, [Mechanistic]._

## Figure 1 — Recipe Scope vs. Treasury Action Boundary
Priority: Critical · Type: systems diagram

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a two-zone boundary diagram at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette. The left zone, recipe scope, holds six small linked nodes: bank-feed ingestion, balance normalization, availability bucketing, threshold comparison, breach flagging, escalation alert — all in primary sky blue to read as permitted read-only preparation. The right zone, treasury action boundary, holds five nodes: payment initiation, account sweeps, credit-facility draws, investment placement or liquidation, wire transfers — all in vermillion to read as forbidden actions for the recipe. Between the two zones draw a single hard vertical line, the heaviest stroke in the figure, labeled by position as the hard boundary where the recipe stops. Critically, draw no arrow crossing the boundary — nothing from the left passes to the right. Keep both zones equal in visual weight so the contrast is observation versus action. Uniform 1pt strokes, no baked-in text, no shadows, no gradients.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
`[C - CONTENT]` From "Why Cash Is Different" diagram callout: recipe scope (bank-feed ingestion, balance normalization, availability bucketing, threshold comparison, breach flagging, escalation alert) vs. treasury action boundary (payment initiation, account sweeps, credit-facility draws, investment placement/liquidation, wire transfers); a hard boundary where the recipe stops; the recipe never crosses into action.
`[O - ORGANIZATION]` Two zones left/right; one dominant hard vertical boundary line; deliberately no crossing arrow (alert, do not act).
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; recipe scope #56B4E9, action boundary #D55E00, boundary line #000000.
`[E - EXCLUSIONS]` Omit the five-step pipeline (Figure 2), the normalization field schematic (Figure 3), the liquidity-watch structure (Figure 4), the supervision questions, the late-feed opening scenario specifics, the pre-approved-sweep exception prose.

BLOCK 3 — NEGATIVE PROMPT:
arrows crossing the boundary, dollar signs, numbers, charts, code, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 2 — The Five-Step Cash Position Pipeline
Priority: Critical · Type: process flowchart

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a left-to-right five-step pipeline at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette. Place five sequential step-nodes connected by single forward arrows: validate feed freshness (flag if late or stale), normalize by account/entity/currency (flag unknown accounts), bucket by availability (operating/restricted/investment/facility), compare to thresholds (flag breaches, never suppress), escalate to treasury team (information only, no recommended action) — all in primary sky blue. Beside steps one, two, and four place small vermillion flag-markers representing the stop-or-flag failure modes (stale feed accepted, account silently dropped, breach suppressed). After the fifth node, draw a single short arrow to a terminal marker that reads as a full stop, with a small note-zone indicating "treasury decides what happens next" and explicitly no continuation into action. Keep step nodes uniform; the terminal stop should read as deliberate. Uniform 1pt strokes, no baked-in text, no shadows, no gradients.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
`[C - CONTENT]` From "The Five Steps of the Cash Position Recipe" diagram callout: 1 validate feed freshness (flag if late/stale) → 2 normalize by account/entity/currency (flag unknown accounts) → 3 bucket by availability (operating/restricted/investment/facility) → 4 compare to thresholds (flag breaches, never suppress) → 5 escalate to treasury (information only); recipe stops here, treasury decides next. Failure modes: accepting a feed without timestamp check, dropping accounts silently, suppression logic.
`[O - ORGANIZATION]` Linear left-to-right; single → arrows; per-step flag-markers on failure-prone steps; deliberate terminal stop after step 5.
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; steps #56B4E9, failure-mode flags #D55E00.
`[E - EXCLUSIONS]` Omit the scope/action boundary zones (Figure 1), the normalization field schematic (Figure 3), the liquidity-watch structure (Figure 4), the read-only sweep-argument prose, the supervision questions, specific clock times.

BLOCK 3 — NEGATIVE PROMPT:
arrows continuing into action steps, dollar signs, numbers, charts, code, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 3 — Normalization Structure and Validation Rules
Priority: Important · Type: structural schematic

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a field-and-rule schematic at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette. Show one normalized cash-position row decomposed into seven fields stacked or arranged in a single labeled group-frame: entity, account, account type, currency, local balance, functional equivalent, as-of timestamp — drawn in primary sky blue. Beside each field place a small distinct validation marker (matches master list, matches account registry or flags unknown, classified or flagged, designated rate or flags, reconciles to statement, uses dated rate, matches expected window or flags late). Render the validation markers that trigger a flag-on-failure in secondary orange to distinguish must-validate fields. Keep the seven fields uniform with reserved interior whitespace for captioning; bake in no text. Use one shared frame so the seven read as a single normalized record. Uniform 1pt strokes, no shadows, no gradients.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
`[C - CONTENT]` From "The Cash Position Normalization Structure" table: seven fields — entity, account, account type, currency, local balance, functional equivalent, as-of timestamp — each with a validation rule (match master entity list; match account registry or flag unknown; classify or flag; designated rate or flag; reconcile to statement; use dated rate; match expected window or flag late). A cash position that omits an account is incorrect, not partial.
`[O - ORGANIZATION]` Seven fields under one group-frame; per-field validation marker; flag-on-failure markers distinguished; no sequence arrows (parallel fields of one record).
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; fields #56B4E9, flag-on-failure markers #E69F00.
`[E - EXCLUSIONS]` Omit the five-step pipeline (Figure 2), the scope/action boundary (Figure 1), the liquidity-watch output structure (Figure 4), the read-only-discipline prose, the supervision questions, specific balances.

BLOCK 3 — NEGATIVE PROMPT:
spreadsheet gridlines, dollar signs, numbers, charts, code, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 4 — The Liquidity Watch Output
Priority: Important · Type: structural schematic

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a four-section output schematic at 89mm width, 300 DPI, flat vector, white background, Okabe-Ito palette, representing the read-only liquidity watch. Stack four labeled section-frames top to bottom: feed status (account, expected time, actual time, status current/late/missing) at the top in primary sky blue; cash position (entity, account, type, currency, balances, as-of, vs. threshold, status) in dominant blue as the main body; threshold alerts (entity, account, threshold, balance, shortfall, escalation sent) in vermillion to mark breaches that are never suppressed; coverage notes (accounts excluded, unknown accounts flagged, feeds missing) in secondary orange. Within the cash-position section, attach a small clock-style as-of marker to each balance row to express that every number carries a timestamp. Keep the feed-status freshness summary at the top as the first thing read. Uniform 1pt strokes, no baked-in text, no shadows, no gradients; reserve interior whitespace for captioning.

BLOCK 2 — FULL SCOPE:
`[S - SPECIFICATION]` Single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
`[C - CONTENT]` From "What the Liquidity Watch Actually Shows" table: four sections — feed status (current/late/missing), cash position (entity/account/type/currency/balances/as-of/vs.-threshold), threshold alerts (never suppressed), coverage notes (excluded/unknown accounts, missing feeds); every balance carries an as-of timestamp; unknown accounts flagged not omitted; freshness summary at top.
`[O - ORGANIZATION]` Four stacked section-frames top-to-bottom (freshness first); per-balance timestamp marker; no flow arrows (a structured output, not a process).
`[P - PRESENTATION]` Flat vector, Okabe-Ito hex, uniform 1pt strokes, white background, no baked text, no style suggestions; feed status #56B4E9, cash position #0072B2, threshold alerts #D55E00, coverage notes #E69F00.
`[E - EXCLUSIONS]` Omit the five-step pipeline (Figure 2), the normalization field rules (Figure 3), the scope/action boundary (Figure 1), the supervision-questions prose, the pre-approved-sweep exception, specific balances and times.

BLOCK 3 — NEGATIVE PROMPT:
dashboard gauges, spreadsheet gridlines, dollar signs, numbers, charts, code, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Video Candidate Pass

Figure 1 — STATIC SUFFICIENT — none — the point is a fixed, uncrossed boundary; motion would risk implying a crossing the chapter forbids.
Figure 2 — VIDEO CANDIDATE — ≥3 sequential causal stages — five ordered steps ending in a deliberate stop; an animated run that flags a stale feed, flags an unknown account, surfaces an unsuppressed breach, then halts at escalation dramatizes "alert, do not act."
Figure 3 — STATIC SUFFICIENT — none — a parallel field-and-rule record; reference, not sequence.
Figure 4 — STATIC SUFFICIENT — none — a structured output layout; inherently static.

Video candidates: 1. Recommended for production: Figure 2 — animating the five steps so the flow visibly stops dead at escalation (with no arrow continuing into any action) is the most direct way to convey the chapter's organizing principle that the recipe alerts but never moves money.
