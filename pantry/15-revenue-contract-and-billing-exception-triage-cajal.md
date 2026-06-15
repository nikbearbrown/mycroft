# CAJAL Figure Report — Revenue Contract and Billing Exception Triage
_Density: recommend 4 figures, Mechanistic._

## Figure 1 — Contract Source Chain with Stop Signal
Priority: Critical · Type: process flowchart

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a linear source-chain diagram of a contract's authoritative documents leading to the billing configuration. Draw an ordered sequence: master agreement, then amendment 1 (references master), amendment 2 (references amendment 1), amendment 3 (references amendment 2), then the current billing configuration as the final node. Below the chain, draw a parallel verification track with check points aligned under each link: executed?, references prior document?, no gap?, and billing reflects this version?. Insert a prominent stop signal at a broken or missing link in the chain, labeled conceptually as an amendment gap where the run halts. Use single-headed arrows along the chain. Make the stop signal the dominant blocking element to convey that a missing amendment halts the comparison. Keep the chain to four documents plus the billing node for legibility at 89mm. Flat vector, colorblind-safe palette, no baked text, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] ordered chain: master agreement → amendment 1 (references master) → amendment 2 (references amendment 1) → amendment 3 (references amendment 2) → current billing configuration; parallel verification track: executed?, references prior document?, no gap?, billing reflects this version?; stop signal at a missing link = amendment gap, run halts.
[O - ORGANIZATION] linear chain on top, parallel check track below; → progression; blocking stop signal at missing link; ⊣ at gap.
[P - PRESENTATION] flat vector; chain document nodes primary #56B4E9; billing-config node dominant #0072B2; verification-track checks secondary #E69F00; stop signal blocking #D55E00; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit the normalization table (Figure 2); omit two-bucket triage (Figure 3); omit exception-pack structure (Figure 4); omit dollar values and dates; omit ASC 606 step detail.

BLOCK 3 — NEGATIVE PROMPT:
contract document photos, readable clause text, dollar amounts, dates as text, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 2 — Normalized Contract Data: Five Field Categories
Priority: Important · Type: comparison panels

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a five-row comparison panel mapping contract terms to billing-system fields for comparison. Each row is one field category with three aligned cells: the contract source, the billing-system field, and the comparison logic. The five categories are dates, products/services, prices, milestones, and modifications. Arrange as a clean stacked grid with consistent column zones; the comparison-logic zone should carry an accent to signal it is where a flag may be raised. Mark the milestones row distinctly to indicate it is where factual mismatches and accounting questions collide. Keep five rows aligned and uniform at 89mm. Use color to separate the contract-source zone from the billing-field zone and to mark the comparison-logic zone. Flat vector, colorblind-safe palette, no baked text, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] dates (effective/term/billing cycle/milestones vs config dates; match within one billing cycle or flag); products/services (description/tier/unit vs SKU/product code; match via mapping table or flag unmapped); prices (contracted rate/discount/escalation vs configured rate; match to current-period rate or flag variance); milestones (delivery event/completion trigger vs billing event config; match event definition or flag for accounting review); modifications (amendment date/superseded provision vs last billing update; amendment post-dates last billing update → flag); milestones row marked as collision point.
[O - ORGANIZATION] five rows (categories) by three zones (contract source, billing field, comparison logic); comparison-logic zone accented; milestones row emphasized.
[P - PRESENTATION] flat vector; contract-source zone primary #56B4E9; billing-field zone secondary #E69F00; comparison-logic zone dominant #0072B2; milestones-collision marker transitional #CC79A7; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit the source chain (Figure 1); omit two-bucket triage (Figure 3); omit exception-pack structure (Figure 4); omit dollar values; omit ASC 606 five-step narrative.

BLOCK 3 — NEGATIVE PROMPT:
spreadsheet cells with values, SKU codes as text, dollar amounts, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 3 — Two-Bucket Exception Triage Funnel
Priority: Critical · Type: process flowchart

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a funnel-shaped triage diagram. At the top, a single input node represents all flagged exceptions from the comparison. The funnel narrows to a central triage decision, then splits into two distinct exit paths. The left path is factual mismatches (examples: wrong price, wrong date, renamed SKU, missing amendment reflected in billing) routing to billing operations for correction. The right path is accounting-policy questions (examples: contract-modification type, milestone timing, variable consideration, principal-versus-agent) routing to the accounting team for a policy memo. Between the paths, place the triage rule: can billing ops resolve this without an accounting interpretation? Yes routes left, no routes right. Use single-headed arrows. Keep the two paths visually distinct and balanced, with the triage decision as the pivot. Single 89mm column. Flat vector, colorblind-safe palette, no baked text, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] input: all flagged exceptions; triage decision (can billing ops resolve without accounting interpretation?); left path factual mismatches (wrong price, wrong date, renamed SKU, missing amendment in billing) → billing ops correction; right path accounting-policy questions (modification type, milestone timing, variable consideration, principal-vs-agent) → accounting policy memo.
[O - ORGANIZATION] funnel input → triage pivot → two exit paths (factual left, policy right); → progression; pivot as decision point.
[P - PRESENTATION] flat vector; input/funnel primary #56B4E9; triage pivot dominant #0072B2; factual-mismatch path active #009E73; accounting-policy path secondary #E69F00; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit the source chain; omit normalization table; omit exception-pack layout (Figure 4); omit dollar values; omit ASC 606 step text.

BLOCK 3 — NEGATIVE PROMPT:
dollar amounts, SKU codes as text, document icons with text, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 4 — Exception Review Pack: Two-Section Structure
Priority: Supplementary · Type: structural schematic

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a schematic of the exception review pack as a stacked two-section layout with a header band. The header band is a source-chain summary showing per-contract zones: amendments verified, gaps found, run status (complete or stopped). Below it, section one is factual mismatches with aligned field zones: contract ID, field, contract value, billing value, amendment source, effective date, correction needed, status. Below that, section two is accounting-policy questions with aligned field zones: contract ID, exception description, ASC 606 topic, facts for analysis, assigned to, status. Keep the two sections visually separated by a clear divider so the reader sees they are never interleaved. Use distinct color bands for the header, the factual section, and the policy section. Keep field zones as labeled regions, not readable text, aligned at 89mm. Flat vector, colorblind-safe palette, no baked text, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] header: source-chain summary (contract ID, amendments verified, gaps found, run status complete/stopped); section 1 factual mismatches (contract ID, field, contract value, billing value, amendment source, effective date, correction needed, status); section 2 accounting-policy questions (contract ID, exception description, ASC 606 topic, facts for analysis, assigned to, status); two sections never interleaved.
[O - ORGANIZATION] header band on top, then two stacked sections separated by a clear divider; section field zones as aligned regions.
[P - PRESENTATION] flat vector; header band dominant #0072B2; factual-mismatch section active #009E73; accounting-policy section secondary #E69F00; divider black #000000; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit the source chain diagram; omit normalization table; omit triage funnel; omit readable field text and dollar values; omit ASC 606 step narrative.

BLOCK 3 — NEGATIVE PROMPT:
readable field text, dollar amounts, SKU/contract IDs as text, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Video Candidate Pass
Figure 1 — CANDIDATE — a chain building link by link then halting at a missing amendment animates the stop condition — staging the chain and the abrupt halt at the gap teaches why a broken source chain stops the run.
Figure 2 — NOT A CANDIDATE — static mapping panel — reference matrix.
Figure 3 — CANDIDATE — exceptions funneling and splitting into two buckets animates the triage — but Figure 1's stop condition is more distinctive.
Figure 4 — NOT A CANDIDATE — static pack schematic — structural reference.

Video candidates: 2. Recommended for production: Figure 1 — the source-chain halt is the chapter's most counterintuitive discipline (stop, do not reconstruct); animating the chain building and then halting at the missing amendment makes "the run stops here" unmistakable, and it is more visually distinctive than the triage funnel.
