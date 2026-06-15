# CAJAL Figure Report — AP/AR Exception and Aging Workbench
_Density: recommend 4 figures, Mixed._

## Figure 1 — AR vs. AP Aging Distribution
Priority: Important · Type: statistical/quantitative

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a side-by-side horizontal bar chart showing outstanding-balance distribution across five aging buckets for AR and AP. The five buckets are current, 1-30 days past due, 31-60, 61-90, and 90-plus, arranged top to bottom from current to most overdue. Draw two bar series, one for AR and one for AP, in two distinct colors, grouped per bucket so the reader compares receivables and payables aging at each stage. Anchor the value axis at zero; no 3D. Keep the buckets evenly spaced and clearly ordered so the time dimension reads from least to most overdue. Add a subtle reference cue marking that the snapshot is valid only as of its date. Use color only to distinguish AR from AP. Keep to five buckets and two series for legibility at 89mm. Flat vector, colorblind-safe palette, no baked numeric labels, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito; zero-anchored axis, no 3D.
[C - CONTENT] five aging buckets (current, 1-30, 31-60, 61-90, 90+); two grouped series (AR balance, AP balance); ordered current-to-overdue; as-of-date validity cue [inferred].
[O - ORGANIZATION] grouped horizontal bars, zero baseline, five ordered buckets, AR vs AP series; time ordering top-to-bottom.
[P - PRESENTATION] flat vector; AR series primary #56B4E9; AP series secondary #E69F00; as-of cue neutral black #000000; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit duplicate-candidate logic (Figure 2); omit AR routing (Figure 3); omit specific dollar values; omit invoice counts as text; omit supervision content.

BLOCK 3 — NEGATIVE PROMPT:
3D bars, dollar amounts, invoice-count numbers, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 2 — Duplicate Candidate Match Criteria
Priority: Important · Type: comparison panels

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a four-row comparison panel for AP duplicate-candidate matching. Each row is one match criterion with three aligned cells: the criterion, what the recipe checks, and a relative match-strength weight shown as a small zero-anchored weight bar. The four criteria are vendor (master-data match), amount (exact or within tolerance), date window (within N days), and invoice number (distinct numbers required). Represent match-strength weight as a short horizontal bar per row so the reader sees relative contribution. Include a clear visual reminder that the recipe only flags candidates — it never confirms, holds, or contacts the vendor — drawn as a blocking terminal that stops short of any action. Keep four rows tidy and aligned at 89mm, with color separating the check zone from the weight zone. Flat vector, colorblind-safe palette, no baked text, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito; zero-anchored weight bars.
[C - CONTENT] vendor (master-data match, not name string); amount (exact or within tolerance); date window (invoice dates within N days, human-set); invoice number (distinct required; same number = processing error, different problem); match-strength weight per criterion; recipe flags candidates only — no confirm, no hold, no vendor contact [inferred blocking terminal].
[O - ORGANIZATION] four rows (criteria) by three zones (criterion, check, weight bar); blocking terminal marking "candidate only, no action"; ⊣ at action boundary.
[P - PRESENTATION] flat vector; criterion rows primary #56B4E9; weight bars dominant #0072B2; action-boundary terminal blocking #D55E00; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit aging chart (Figure 1); omit AR routing (Figure 3); omit dollar tolerances as numbers; omit fraud-statistic figures; omit supervision-question content.

BLOCK 3 — NEGATIVE PROMPT:
invoice screenshots, dollar amounts, day-count numbers, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 3 — AR Exception Routing to Human-Action Queues
Priority: Critical · Type: process flowchart

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a routing flowchart from a single AR aging export into four exception queues. From the aging-export source node, branch by condition into four destination queues: past-due with owner assigned and no dispute routes to a collections follow-up queue; dispute status attached routes to a dispute resolution queue; no owner assigned routes to a supervisor assignment queue; counterparty anomaly detected routes to a data-quality queue. All four queues converge into a single shared "human action" zone. Draw a prominent blocking boundary showing that none of the four queues flows directly to customer communication, holds, payment release, write-off, or record merge — the boundary is the workbench limit. Use single-headed arrows for routing. Keep four parallel queues tidy and the action boundary unmistakable at 89mm. Flat vector, colorblind-safe palette, no baked text, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] aging export source; four routed queues — past-due/owner-assigned/no-dispute → collections follow-up; dispute status → dispute resolution; no owner → supervisor assignment; counterparty anomaly → data quality; convergence into human-action zone; blocking boundary: no direct customer communication, holds, payment release, write-off, or record merge.
[O - ORGANIZATION] one source → four conditional queues → human-action convergence; ⊣ blocking boundary before any world-acting step; → routing.
[P - PRESENTATION] flat vector; source node primary #56B4E9; four queues in distinct hues (secondary #E69F00, transitional #CC79A7, dominant #0072B2, bluish green #009E73); human-action zone neutral; action boundary blocking #D55E00; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit aging chart; omit duplicate-criteria panel; omit dollar values; omit invoice text; omit supervision table.

BLOCK 3 — NEGATIVE PROMPT:
email/envelope icons with text, dollar amounts, customer names, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Figure 4 — The Action Boundary: Queue Prep vs. World Actions
Priority: Critical · Type: comparison panels

BLOCK 1 — ILLUSTRAE PASTE BLOCK:
Render a two-zone comparison split by a strong vertical boundary line representing the queue as the action boundary. The left zone is preparation, attributed to the recipe, listing what it does: sort, age, flag, queue, confirm as-of date, route exceptions. The right zone is judgment, attributed to humans, listing the world-acting steps: send communications, place payment holds, release payments, write off balances, merge customer records. Make the central boundary line the most prominent element, labeled conceptually as the queue where preparation ends and judgment begins. Keep both zones balanced with five to six compact items each. Use a blocking accent on the right-zone items to mark them as consequential world actions. Single 89mm column. Flat vector, colorblind-safe palette, no baked text, white background, 1pt strokes.

BLOCK 2 — FULL SCOPE:
[S - SPECIFICATION] default textbook: single-column 89mm, ≥300 DPI, vector, Okabe-Ito.
[C - CONTENT] left (recipe / preparation): sort, age, flag, queue, confirm as-of date, route exceptions; right (human / judgment): send communications, place payment holds, release payments, write off balances, merge customer records; central boundary: the queue (preparation ends, judgment begins).
[O - ORGANIZATION] two zones separated by a prominent vertical boundary; recipe-side left, human-side right; boundary as primary emphasis; ⊣ on right-zone items.
[P - PRESENTATION] flat vector; preparation zone primary #56B4E9; judgment/world-action zone blocking #D55E00; central boundary dominant #0072B2; 1pt strokes; white background; NO baked text.
[E - EXCLUSIONS] omit aging chart; omit duplicate-criteria; omit the four-queue routing; omit dollar figures; omit Monday-report narrative.

BLOCK 3 — NEGATIVE PROMPT:
money/cash icons, envelope icons with text, dollar amounts, text labels, words, gibberish letters, titles, captions, decorative borders, realistic textures, drop shadows, gradient backgrounds, photographic elements, dual-headed arrows, hand-drawn styles, human figures, visual clutter, watermarks, red-green color combinations, rainbow color scales, 3D perspective distortion.

## Video Candidate Pass
Figure 1 — NOT A CANDIDATE — static distribution chart — reads at a glance.
Figure 2 — NOT A CANDIDATE — static criteria panel — reference matrix.
Figure 3 — CANDIDATE — conditional routing of items into queues then stopping at a boundary animates well — exceptions flowing into four queues and halting at the action boundary dramatizes "it stopped."
Figure 4 — WEAK CANDIDATE — boundary reveal could animate — but the static split already lands the point.

Video candidates: 1. Recommended for production: Figure 3 — the chapter's climax is "then it stopped"; animating items routing into the four queues and visibly halting at the action boundary before any world action is the most teachable moment of the chapter.
