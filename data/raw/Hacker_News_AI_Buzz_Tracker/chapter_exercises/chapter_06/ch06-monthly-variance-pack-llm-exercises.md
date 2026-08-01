# Chapter 6: Monthly Variance Pack

## Warm-up

### Exercise 1

The six ingredients and their contracts:

1. **Actuals** — source: the approved GL/ERP export or close file, not a preliminary pull. Contract: must carry a version identifier and timestamp.
2. **Budget** — source: the current-version budget file for the same period and entity. Contract: version identifier for that period/entity.
3. **Forecast** (optional) — source: same version requirements as budget. Contract: same identifier discipline, when present.
4. **Mapping tables** — source: the current-period crosswalk from account codes to report lines. Contract: reconciled to the full account list, with unmapped accounts flagged.
5. **Thresholds** — source: human-set materiality parameters. Contract: set before the run, never inferred by the model during it.
6. **Prior comments** — source: the prior-period commentary file. Contract: dated to the prior period, attached as labeled context, not as current explanation.

The ingredient most likely to produce a variance that *looks* correct but is computed against stale inputs is **budget**. The arithmetic on a stale budget version is still internally consistent — the subtraction is correct — so nothing about the output looks broken. But if the budget was revised after that version was pulled, every delta in the pack is measuring against a plan that no longer exists, and there's no visual signal in a clean table that would tip a reader off. Mapping tables are a close second for the same reason: a stale mapping still produces a number for every line, it just quietly misattributes some of them.

### Exercise 2

The five operations: compute, rank, flag, attach, stop.

"Stop" belongs on the list as an operation because the recipe has to actively decide, at a defined point, that it will not go further — it is not simply the recipe running out of things to do. A recipe that "just runs out" after flagging would, by default, be free to keep going: to write a sentence about why the flagged line moved, to characterize a variance as favorable or concerning, to fill the blank commentary cell with something plausible. Naming "stop" as a designed step is what prevents that default drift. It is the same distinction the chapter draws between a blank commentary cell (a designed absence, carrying information) and a missing commentary cell (an oversight). Stop is the gate being built into the recipe's own scope, not a property that emerges from the recipe simply having nothing left to compute.

### Exercise 3

Merging "Prior commentary (sourced)" and "Current explanation (owner required)" into one column would erase the one piece of information the two-column structure exists to preserve: *who said this, and when*. The chapter's argument is that the commentary column is the exact place where a model-generated sentence becomes indistinguishable from a human-authored one if both share a column and formatting — that indistinguishability is "the commentary problem" the chapter spends a full section on. A single merged column reintroduces exactly that ambiguity: a reader can no longer tell whether a given cell is last month's sourced, dated explanation being carried forward for context, or this month's reviewed judgment written by a named professional. The two-column split is not a formatting preference — it is the mechanism that makes provenance visible, per the chapter's own claim that "the fix is structural, not instructional." Collapsing it back into one column undoes the fix and reopens the exact failure mode (a plausible-sounding explanation traveling with the authority of a reviewed one) that the structure was built to close.

## Application

### Exercise 4

The sentence — *"Revenue missed budget by $420K (−8.3%). This appears to reflect timing differences in customer billings, consistent with prior-quarter patterns."* — mixes two layers.

- "Revenue missed budget by $420K (−8.3%)" is **verified evidence**: a computed, reproducible delta that traces to an actuals row and a budget row.
- "This appears to reflect timing differences in customer billings, consistent with prior-quarter patterns" is **model judgment** dressed as a finding. It is a causal claim (why the miss happened) and a pattern claim (consistency with prior quarters) that the recipe has no license to make — nothing in the ingredient list (actuals, budget, mapping, thresholds, prior comments) supports a statement about *why* billings shifted. It reads exactly like the chapter's "commentary problem": fluent, plausible, and unattributed to any named reviewer.

It cannot appear in the distribution pack as written because a reader cannot tell that the second sentence is a machine-generated guess rather than a finance professional's reviewed explanation — the two sentences share the same voice and the same cell.

Rewritten so the recipe stops at the right place:

```
Revenue: $420K unfavorable to budget (−8.3%). FLAGGED — exceeds threshold.
Prior commentary (sourced, [prior period]): [prior period's dated comment, or blank if none].
Current explanation (owner required): _____________________ (blank — pending review)
```

The recipe computes and flags the delta and reports the sourced prior comment if one exists; it leaves the current-explanation cell blank rather than supplying its own causal read, and routes the flagged line to the named reviewer for that quarter.

### Exercise 5

Of the three supervision questions, **Scope** is the one that would have caught this. The question "which entity or entities is the agent operating in?" requires the scope parameter to name the consolidated parent's *current* structural boundary, not simply "consolidated parent" as an unexamined label — and it requires the agent to check the actuals file's entity population against that boundary rather than assume the file is already correctly scoped.

Scope parameter that would have prevented the error:

```
entity_scope: consolidated_parent
entity_list: [as of period-end, from the corporate structure/divestiture log — NOT inferred from the actuals file's own contents]
exclude_if_divested_before: period_end_date
action: if any entity present in the actuals file is not in entity_list, exclude it from the variance
        computation and flag it explicitly as "present in source, excluded from scope — divested [date]"
```

The key discipline is that the entity list has to come from an authoritative structural source (a divestiture log, a corporate-entity register) rather than being derived from whatever entities happen to show up in the actuals extract — otherwise a stale extract and a stale scope parameter can agree with each other and both be wrong.

### Exercise 6

Before release, the finance professional must review the flagged $310K unfavorable COGS line against its actual source data — not accept the prior month's "timing of supplier invoices; expected to reverse" comment as still applicable, since a prior-period explanation is context, not a current answer. Adequate review means: confirming whether the invoice timing did in fact reverse this period (checking the actual invoice dates against the prior comment's claim), and if it did not reverse, writing a fresh current explanation rather than re-using the stale one. Two hours is enough time to do this for one flagged line — the chapter's own example (45 minutes for a full flag list) sets the pace.

The approver is the named finance professional accountable for that cost center or the FP&A lead reviewing the full pack — not whoever is closest to the deadline. The approval record should show: the reviewer's name, the date/time of review, a note on whether the prior period's "expected to reverse" explanation held (yes/no, with the checked evidence), the current-period explanation in the owner-required column (or an explicit "unresolved, releasing with open flag" note if the deadline truly cannot accommodate full resolution), and the reviewer's sign-off. If the line genuinely cannot be resolved in two hours, the honest move is to release the pack with that line marked open and flagged for follow-up — not to silently copy the prior comment forward as if it were reviewed.

## Synthesis

### Exercise 7

The team lead's proposal — auto-copy prior commentary to current explanation when the current variance is within 10% of last month's, no human review required — fails against the three-layer taxonomy on the point that matters most, though it has a defensible core.

**Where it holds up:** Verified evidence is unaffected — the 10%-proximity test itself is a legitimate, reproducible computation (comparing two verified deltas), and using it to *triage* which lines get priority human attention is a reasonable preparation-layer step. Flagging "this line's variance is close to last month's" as a signal for the reviewer to look at first is fine; that's ranking, not explaining.

**Where it fails:** The proposal treats "the variance is numerically similar" as license to skip judgment about "the variance has the same *cause*" — and those are not the same claim. A COGS variance can land within 10% of last month's dollar figure for a completely different reason (a new vendor issue this month, coincidentally similar in size to last month's invoice-timing issue). Numerical similarity is not causal continuity. Auto-copying the prior explanation into the *current* explanation column is exactly the boundary violation the chapter names: it moves language from "prior commentary (sourced)" into "current explanation (owner required)" without a human ever looking at the current period's facts. It converts human judgment into a rule triggered by a threshold — precisely the "gate clears itself... on vibes" failure the chapter's principles warn against, except here it's on a numeric proxy for vibes instead of vibes themselves. The tell: after twelve months of auto-copying, an auditor asking "who confirmed the COGS line and when" would get the answer "no one, a threshold copied last quarter's guess forward," which is the same accountability gap the chapter describes for AI-generated commentary — just with the prior human's words filling the role a model's sentence would otherwise fill.

A structural fix that preserves the labor-saving intent: keep the 10%-proximity flag as a *sorting* signal (route close-to-prior lines to a fast-review queue), but require the reviewer to still explicitly re-affirm or rewrite the explanation and attach their name — even if that affirmation takes ten seconds because the explanation genuinely still holds. The record then shows a human decision was made, not that a threshold made it for them.

### Exercise 8

**Four-entity structure:** three subsidiaries (A, B, C) plus the consolidated parent.

- **Source contracts:** each subsidiary needs its own actuals file (approved local-entity GL export, versioned/timestamped) and its own current-version budget file for the same period. The consolidated parent's actuals should be the group's consolidation output, not a fourth independently-sourced file, so that parent-level variances are traceable to the sum of the three subsidiaries plus any consolidation adjustments (intercompany eliminations, FX translation). The consolidation-adjustment figure itself needs its own version identifier, since it is a real, separately-produced number, not a residual.
- **Mapping table strategy:** one master mapping table maintained at the group level, with entity-specific extensions where a subsidiary has accounts the others don't (e.g., a local statutory account). A single master table (rather than four independent ones) prevents the same economic line item from landing on different report rows across entities, which would make the consolidated flag list incomparable across subsidiaries.
- **Threshold structure:** entity-specific, not uniform in absolute dollar terms, but with a shared percentage threshold as the primary trigger and an absolute-dollar floor scaled to each entity's size (e.g., 5% of budgeted line value, or $50K, whichever is larger, with the $50K floor set per-entity relative to that entity's typical line size). A uniform absolute-dollar threshold would either bury a genuinely material miss at a small subsidiary or flood the pack with immaterial noise from the largest one.
- **Gate design:** one gate per subsidiary (the local controller or FP&A owner reviews and approves their entity's flagged lines and commentary) plus one consolidation-level gate (the group FP&A lead or CFO reviews the combined ranked list, the consolidation adjustments, and signs off on release to the CFO/board). Four local approvals feeding one final approval — not four independent releases and not a single approver reviewing all four entities' raw detail alone, which would make the local owners' domain knowledge invisible in the record.
- **Commentary structure:** the same two-sub-column pattern (prior commentary sourced / current explanation owner-required) at the subsidiary level, carried up into the consolidated pack with the originating entity tagged on each row, so the CFO reviewing the combined list can see which local owner is accountable for which explanation.

**Two highest-risk failure points:**
1. **Consolidation adjustments as an unreviewed residual.** If the group-level actuals are built as "sum of subsidiaries plus a plug to match the reported consolidated total," that plug can silently absorb real errors from any subsidiary's extract, and the pack would show a clean set of entity-level deltas while the consolidation line itself carries an unexplained, unflagged number.
2. **Threshold gaming through entity choice.** Because thresholds are entity-specific, there's a risk that a line item hovering near materiality gets classified under whichever entity's threshold is more forgiving (e.g., a shared-services cost allocated to the entity with the higher dollar floor). This needs an explicit rule for which entity "owns" a shared or allocated line before the threshold is applied, or the flag list becomes gameable by allocation choice rather than driven by materiality.

## Challenge

### Exercise 9

**The strongest version of the CFO's argument:** A distribution pack with a row of visible blanks in the current-explanation column reads, to an audience that doesn't know the chapter's design intent, as incomplete work — as if the finance team ran out of time rather than deliberately withheld judgment. In a pack that goes to a board or external readers, that appearance carries real cost: it can look like the finance function isn't keeping pace with the close, and it can prompt exactly the kind of unstructured, undocumented verbal explanation (a hallway comment, an off-the-record aside in the board meeting) that the chapter's P7 ("the margin is part of the record") says should never happen — because at least a labeled preliminary placeholder would be a written, attributable artifact instead of an unrecorded verbal gloss filling the same gap. If the placeholder is clearly marked "preliminary — not reviewed," the CFO's argument goes, it protects the professional appearance of the pack while still, in theory, preserving the distinction between reviewed and unreviewed language.

**Evaluating it:** The argument does not survive scrutiny, but it correctly identifies a real presentation problem rather than an imaginary one. The chapter's own account of why the model-generated sentence is dangerous is that it is "indistinguishable from a human-authored explanation if both are sitting in the same column with the same formatting" — and a "preliminary, AI-generated" placeholder sitting in the *same physical cell* as a human explanation reintroduces exactly that risk in practice, however clearly it's labeled in principle. Labels degrade: a "preliminary" tag gets trimmed in a copy-paste into a board deck, a PDF export loses a footnote, a reader skims past a small-font caveat next to a full, fluent sentence. The chapter's blank-cell design isn't solving an aesthetic problem badly — it's refusing a shortcut that reintroduces the exact failure mode (fluent language mistaken for reviewed judgment) that motivates the whole two-column structure. So the tension is genuine — the appearance problem is real — but the CFO's proposed fix (fill the blank) reopens the vulnerability the design exists to close.

**A structural resolution that keeps the gate:** Separate the *appearance* problem from the *content* problem. Rather than filling the current-explanation cell with generated text, make the blank itself a labeled, designed state rather than an apparent gap: a standard visual convention across the whole pack (e.g., "Pending review — assigned to [named owner], due [date/time]") that appears in every unresolved cell, styled distinctly from filled cells, so a blank reads as "review in progress, on a specific person's desk" rather than "nobody got to this." This gives the reader the same reassurance the CFO wants — the gap isn't invisible neglect, it's tracked, owned, and dated — without ever putting model-generated causal language into the cell that's supposed to carry human accountability. It converts "blank equals unfinished" into "blank equals scheduled," which is a presentation fix that adds information rather than one that fabricates it.
