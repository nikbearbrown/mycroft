# CAJAL Figure Report — Close Flux Analysis and Balance-Sheet Review
_Density: recommend 4 figures, Mechanistic._

## Figure 1 — Close Workflow: Status Line vs. Adequacy Gate
Priority: Critical · Type: process flowchart

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a single-column left-to-right process flowchart of a financial close workflow leading to release. Begin at a "period end" node, then a cluster of three parallel completed close tasks: journals posted, reconciliations submitted, intercompany eliminations done. Converge these into a "status: green" milestone marker. Continue with an arrow to "trial balance extracted," then to "flux analysis computed" (material movements ranked, support checked). Place a decision gate node labeled as the controller review (support adequate? unexplained items resolved?), then a terminal "sign-off and release" node. Visually separate the "status: green" milestone from the controller-review gate with a clear horizontal gap, and mark that gap as the adequacy gap. Use directional single-headed arrows for progression. Keep the status milestone and the gate node visually distinct in fill weight so the reader sees they answer different questions. Flat vector, colorblind-safe palette, generous whitespace, six labeled stages maximum on the main spine.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] period end; three completed close tasks (journals posted, reconciliations submitted, intercompany eliminations done); status: green milestone; trial balance extracted; flux analysis computed (movements ranked, support checked); controller review gate (support adequate? unexplained resolved?); sign-off and release; the adequacy gap [inferred] between status milestone and gate.
[O - ORGANIZATION] horizontal spine; three completed tasks merge → status milestone → trial balance → flux compute → gate → release; → for progression; explicit horizontal gap labeled as adequacy gap between status milestone and gate.
[P - PRESENTATION] flat vector; status milestone secondary #E69F00; gate dominant #0072B2; completed-task nodes primary #56B4E9; release node active #009E73; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit dollar figures; omit dashboard UI chrome; omit specific account names; omit the prepaid-asset example; omit timeline dates; omit the support decision-tree detail (separate figure).

BLOCK 3 — NEGATIVE PROMPT:
dashboard screenshots, account ledgers, dollar amounts, calendar dates, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 2 — Source Contracts for Flux Analysis
Priority: Important · Type: comparison panels

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a three-row comparison panel layout, one row per flux-analysis input. Row one is the current trial balance, row two the prior trial balance, row three the threshold parameters. Give each row four aligned cells representing: the input, its source, the version requirement, and the failure mode if the version is wrong. Lay the cells out as a clean aligned grid with consistent column zones so the eye reads top-to-bottom by input and left-to-right by attribute. Use a subtle directional cue on the failure-mode cell to signal it is the consequence column. Keep the prior-trial-balance row visually emphasized to mark it as the highest-risk input (restatement risk). Flat vector, colorblind-safe palette, three rows by four zones, no more than seven labeled regions. Maintain even spacing and a single column width of 89mm. Use color only to distinguish the three input rows and to mark the consequence zone; do not bake any text into the cells.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] current trial balance (close-complete GL extract, version+timestamp after journals post, mid-close extract overstates movement); prior trial balance (prior-period approved close, same version as prior flux review, restated prior balance inflates flux); threshold parameters (human-set materiality by category, set before run, model-inferred thresholds may misfit entity).
[O - ORGANIZATION] three rows (inputs) by four attribute zones (input, source, version requirement, failure mode); failure-mode zone marked as consequence; prior-trial-balance row emphasized.
[P - PRESENTATION] flat vector; current-TB row primary #56B4E9; prior-TB row dominant #0072B2; threshold row secondary #E69F00; consequence zone blocking accent #D55E00; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit the workflow spine (Figure 1); omit dollar values; omit support-coverage logic; omit supervision questions; omit the carryforward/residual content.

BLOCK 3 — NEGATIVE PROMPT:
spreadsheet gridlines with numbers, real account codes, dollar amounts, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 3 — Support Coverage Decision Tree
Priority: Critical · Type: process flowchart

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a top-down decision tree for a single flagged account movement. Start with one root node representing a detected material flux. Branch into three mutually exclusive outcomes based on support-file state: support file exists and is current-dated (supported, needs review); support file exists but is prior-period dated (stale support, needs update); no support file (unsupported, blocks gate). Route all three outcome nodes downward into a single shared human-review gate node. From the gate, show that only the supported-needs-review path can exit forward to a sign-off terminal, while the stale and unsupported paths loop to a "requires additional human action" node before they may re-enter the gate. Use single-headed arrows throughout; use a blocking visual treatment on the unsupported path and a transitional treatment on the stale path. Flat vector, colorblind-safe palette, one root, three branches, one gate, limited terminal nodes, generous vertical spacing, single 89mm column.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] root: material flux detected; branch 1: support exists, current-dated → supported, needs review; branch 2: support exists, prior-period dated → stale support, needs update; branch 3: no support → unsupported, blocks gate; shared human-review gate; sign-off terminal (reachable only from supported path); requires-additional-human-action node for stale and unsupported paths.
[O - ORGANIZATION] root → three branches → converge at gate; only supported branch → sign-off; stale and unsupported → additional-action node → re-enter gate; → progression, ⊣ blocking on unsupported path.
[P - PRESENTATION] flat vector; supported path active #009E73; stale path transitional #CC79A7; unsupported path blocking #D55E00; gate dominant #0072B2; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit the source-contract table (Figure 2); omit ranking/carryforward content; omit dollar amounts; omit account-type examples; omit supervision questions.

BLOCK 3 — NEGATIVE PROMPT:
dollar amounts, account names, file icons with readable text, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 4 — Supervision Questions in the Close Context
Priority: Important · Type: comparison panels

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a three-row comparison panel mapping the three supervision questions to the close workflow. Row one is scope, row two is approval, row three is verification. Give each row two aligned cells: the close-specific application and the failure if the question is left unasked. Arrange as a clean two-zone grid, rows stacked vertically, with a consistent divider between the application zone and the failure zone. Mark the failure zone with a blocking accent to signal consequence. Keep each row visually distinct by question using three different hues. Maintain even spacing, single 89mm column, no more than six labeled regions total. Use a subtle directional cue from application to failure to show that skipping the question produces the failure. Flat vector, colorblind-safe palette, no baked text, white background, 1pt strokes throughout.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] scope (period confirmed, entity-specific, action space limited to read-and-report; failure: wrong period or silent entity expansion); approval (named controller, sign-off authority, dated approval record; failure: release before gate, unresolved items travel forward); verification (support exists, current-period, treatment confirmed by reviewer with standing; failure: "supported" label without evaluation).
[O - ORGANIZATION] three rows (questions) by two zones (application, failure); failure zone marked as consequence; application → failure directional cue.
[P - PRESENTATION] flat vector; scope row primary #56B4E9; approval row dominant #0072B2; verification row secondary #E69F00; failure zone blocking #D55E00; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit the workflow spine; omit support decision tree; omit dollar figures; omit residual/zero-flux content; omit the prepaid-asset narrative.

BLOCK 3 — NEGATIVE PROMPT:
checkmark icons, dollar amounts, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Video Candidate Pass
Figure 1 — CANDIDATE — sequential workflow with a visible adequacy gap and a gate that re-routes — staged build of the close spine, dropping the status milestone and then revealing the adequacy gap before the gate, animates the chapter's core distinction.
Figure 2 — NOT A CANDIDATE — static comparison table — no temporal sequence to animate.
Figure 3 — WEAK CANDIDATE — branching decision logic could animate per-branch — but the three-branch tree reads clearly as a static figure; motion adds little.
Figure 4 — NOT A CANDIDATE — static mapping panel — no progression.

Video candidates: 1. Recommended for production: Figure 1 — the status-vs-adequacy distinction is the chapter's thesis, and a staged reveal of the adequacy gap between the green milestone and the controller gate makes the abstract point concrete in a way a static figure only implies.
