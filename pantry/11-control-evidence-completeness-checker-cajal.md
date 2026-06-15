# CAJAL Figure Report — Control-Evidence Completeness Checker
_Density: recommend 4 figures, Mechanistic._

## Figure 1 — Control Claim Decomposition
Priority: Critical · Type: hierarchy/taxonomy

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a radial decomposition diagram for a single control claim. Place a central node representing the claim that a risk was mitigated. Extend four branches outward to four element nodes: period (evidence timestamps fall within the review window), population (the sample represents the full transaction set), people (preparer and reviewer identified and authorized), and process (required steps documented and traceable). Each of the four element nodes terminates in a small uniform node conveying that the evidence must establish this element or the claim is unsupported. Keep the four branches balanced around the center, evenly spaced, with single-headed connectors from the center outward. The figure should read as one claim resting on exactly four supporting elements, each conditional. Flat vector, colorblind-safe palette, single 89mm column, no baked text, white background, 1pt strokes, five primary nodes plus four small terminal nodes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] center: control claim (risk was mitigated); four element branches — period (timestamps within review window), population (sample represents full set), people (preparer and reviewer identified and authorized), process (required steps documented and traceable); each branch ends in a node meaning "evidence must establish this or the claim is unsupported."
[O - ORGANIZATION] central hub with four balanced branches; each branch → conditional terminal node; radial hierarchy.
[P - PRESENTATION] flat vector; central claim dominant #0072B2; four element nodes in distinct hues (primary #56B4E9, secondary #E69F00, transitional #CC79A7, bluish green #009E73); conditional terminals neutral black #000000 outline; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit the eight-check matrix (Figure 2); omit ledger structure; omit readiness-vs-reliability content; omit dollar figures; omit SOX/PCAOB citation text.

BLOCK 3 — NEGATIVE PROMPT:
binder/folder photos, dollar amounts, regulatory citation text, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 2 — The Eight Completeness Checks
Priority: Critical · Type: comparison panels

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render an eight-row comparison panel, one row per completeness check, with three aligned cells per row: the check, what the recipe examines, and the flag condition. The eight checks are period coverage, evidence existence, preparer proof, reviewer proof, timestamp integrity, sample coverage, stale artifacts, and prior exceptions. Lay the rows out as a tidy stacked grid with consistent column zones; the flag-condition zone should carry a blocking accent to signal the failure trigger. Because eight rows is the design ceiling, keep each row compact and uniform with strong horizontal rhythm so the matrix stays scannable at 89mm. Use color to mark the flag-condition zone and to band alternating rows subtly for legibility, not for decoration. Flat vector, colorblind-safe palette, no baked text, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] period coverage (timestamp vs review window; flag: outside period); evidence existence (required items per map; flag: required item missing); preparer proof (identified individual in authorized role; flag: missing/unauthorized preparer); reviewer proof (identified individual with oversight; flag: missing/unauthorized/same as preparer); timestamp integrity (logical sequence; flag: approval before preparation or report after close date); sample coverage (transactions reviewed vs population; flag: below threshold or population undefined); stale artifacts (reuse from prior period; flag: predates current period by more than one cycle); prior exceptions (unresolved prior findings; flag: prior exception without documented remediation).
[O - ORGANIZATION] eight rows (checks) by three zones (check, examines, flag condition); flag-condition zone marked as trigger; subtle row banding.
[P - PRESENTATION] flat vector; check column primary #56B4E9; examines column neutral; flag-condition zone blocking #D55E00; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit ledger figure (Figure 3); omit claim-decomposition (Figure 1); omit readiness-vs-reliability split (Figure 4); omit dollar/sample-count specifics; omit remediation-support narrative.

BLOCK 3 — NEGATIVE PROMPT:
checkmark/X icons, dollar amounts, sample counts as numbers, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 3 — Evidence Readiness Ledger Structure
Priority: Important · Type: structural schematic

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a schematic of the evidence readiness ledger as a grid: rows are controls and columns are the check dimensions plus identifying fields. Show a control-ID column, a description column, a period column, then eight check-dimension columns, a coverage-notes column, and a status column. Within the body cells, represent the four possible cell states (pass, flag, missing, not applicable) as four distinct fill swatches so the reader sees the ledger is a state matrix, not a pass/fail report. Include a small legend strip mapping the four swatch styles to the four states, using fills only with no baked words. Emphasize, with a contrasting band, that there is no control-level ready column and no effectiveness conclusion column. Keep the grid clean and aligned at 89mm with restrained columns. Flat vector, colorblind-safe palette, no baked text, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] ledger grid: control ID, control description, period, eight check columns (evidence existence, period coverage, preparer proof, reviewer proof, timestamp integrity, sample coverage, stale artifact, prior exception/remediation support), coverage notes, status; four cell states (pass, flag, missing, N/A) shown as distinct fills; explicit absence of a ready/effectiveness column [inferred emphasis band].
[O - ORGANIZATION] rows = controls, columns = checks + fields; body cells as four-state swatches; legend strip for the four states; emphasis band marking the omitted effectiveness column.
[P - PRESENTATION] flat vector; pass active #009E73; flag secondary #E69F00; missing blocking #D55E00; N/A neutral grey/black outline #000000; header band dominant #0072B2; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit verbatim status words inside cells; omit dollar figures; omit the eight-check definitions (Figure 2); omit reliability content (Figure 4); omit the claim decomposition.

BLOCK 3 — NEGATIVE PROMPT:
readable cell text, status words, dollar amounts, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 4 — Readiness vs. Reliability: The Recipe Boundary
Priority: Critical · Type: comparison panels

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a two-column comparison with a strong vertical dividing line down the center marking the boundary where the recipe stops. The left column is evidence readiness, attributed to the recipe, listing its structural checks as compact uniform items: present, within period, authorized signatures, sufficient sample, no stale artifacts, prior exceptions documented. The right column is evidence reliability, attributed to the human, listing its judgment items: source is independent, evidence is direct not inferred, underlying systems are controlled, evidence is credible given the risk, design is adequate for the assertion. Treat the central divider as the most prominent element — a clear gate line separating machine checks from human judgment. Keep both columns balanced, five to six items each, single 89mm column overall. Use color to distinguish the recipe side from the human side. Flat vector, colorblind-safe palette, no baked text, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] left (recipe / readiness): present, within period, authorized signatures, sufficient sample, no stale artifacts, prior exceptions documented; right (human / reliability): source independent, evidence direct not inferred, underlying systems controlled, evidence credible given risk, design adequate for assertion; central divider: the gate where the recipe stops.
[O - ORGANIZATION] two balanced columns separated by a prominent vertical gate line; recipe-side left, human-side right; divider as primary emphasis.
[P - PRESENTATION] flat vector; recipe/readiness column primary #56B4E9; human/reliability column dominant #0072B2; central gate line blocking #D55E00; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit the eight-check matrix; omit ledger grid; omit claim decomposition; omit dollar figures; omit AS 1105/PCAOB citation text.

BLOCK 3 — NEGATIVE PROMPT:
regulatory citation text, dollar amounts, scales-of-justice icons, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Video Candidate Pass
Figure 1 — WEAK CANDIDATE — radial decomposition could animate branch-by-branch — but it reads cleanly as a static hierarchy.
Figure 2 — NOT A CANDIDATE — static eight-row matrix — reference table, no sequence.
Figure 3 — NOT A CANDIDATE — static ledger schematic — structural reference.
Figure 4 — CANDIDATE — the recipe-stops boundary is a hand-off that animates well — building the left (recipe) column, then drawing the gate line, then revealing the right (human) column stages the central thesis of the chapter.

Video candidates: 1. Recommended for production: Figure 4 — the readiness/reliability boundary is the chapter's human-only claim; animating the gate line dropping between machine checks and human judgment makes "the recipe stops here" viscerally clear.
