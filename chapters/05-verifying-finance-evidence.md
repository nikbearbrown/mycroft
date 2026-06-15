# Chapter 5 — Verifying Finance Evidence
*What it means to know something, versus knowing that something parsed.*

A reconciliation ties. A spreadsheet parses. A chart renders cleanly with no broken references and no error flags. These are satisfying facts. They feel like evidence of correctness. But here is the thing none of them prove: that the explanation is true, or that the decision built on top of them is safe.

This is the verification problem in finance work, and it is subtler than it first appears. The issue is not that the numbers are wrong — they might be perfectly right. The issue is that "the numbers are right" is a much narrower claim than "the conclusion is warranted." When you move from one to the other without examining the gap, you have done something that looks like analysis but is actually an assumption.

I want to work through what it actually means to verify finance evidence — not just confirm that an artifact is structurally intact, but interrogate whether it is adequate for the judgment it is supposed to support.

---

## The Difference Between Parsing and Proving

Imagine a variance report for Q3. The file opens. The formulas return numbers. The period labels match. The comparison to Q2 and prior-year Q3 is formatted correctly. Nothing is broken.

Now: is the variance explained?

The structural integrity of the file tells you nothing about this. The report could be comparing the right periods or the wrong ones — and if the extract ran with a filter that excluded a category, the comparison is wrong in a way that will not announce itself. The source system could have restated Q2 after the extract ran, making the prior-period column stale. The account mapping could have changed mid-year, meaning Q3 and Q3-prior are not comparable on the same basis. None of these problems cause the file to fail to parse.

This is the core distinction I want to establish before anything else: structural integrity is a necessary condition for evidence, not a sufficient one. The artifact has to parse *and* be complete, fresh, correctly mapped, and logically coherent before the conclusions it supports are warranted.

<!-- → [DIAGRAM: Two-level stack — bottom level labeled "Structural integrity" (file parses, formulas return, no broken references) with a checkmark that does NOT propagate upward; top level labeled "Evidentiary adequacy" (complete, fresh, correctly mapped, logically coherent, conclusions warranted) — an arrow from bottom to top labeled "necessary but not sufficient"; the gap between levels is the focus of the chapter] -->

Finance work has a habit of conflating these two levels. The reason is partly practical — if something parses, it usually means someone did the work, and the work usually produces something approximately right. But "approximately right" is not a standard that holds up when the artifact influences a cash decision, a reporting number, or an external disclosure.

---

## Six Questions Worth Asking

There are six dimensions along which finance evidence can be adequate or inadequate. None of them are exotic. What makes them worth naming explicitly is that each one fails silently — the artifact looks fine even when the dimension is broken.

**Completeness.** Does the data cover the full population it claims to cover? A receivables aging that excludes one subsidiary because the extract was scoped narrowly will show a cleaner picture than the business actually has. A budget comparison that only pulls loaded cost centers will understate the variance. Completeness gaps do not produce error messages; they produce plausible-looking outputs with a hole in them.

The completeness question is: what should be here, and is it? Not "does the file have rows" but "does the file have the right rows."

**Freshness.** When was the source data extracted, and does that timing create a mismatch with the period being analyzed? An accounts payable report pulled at 9 a.m. on close day will differ from one pulled at 5 p.m. after the final batch runs. A prior-period column extracted before a restatement will differ from one extracted after. Stale data is not wrong data — it is data from a different moment, which may or may not reflect the moment that matters.

The freshness question is: does the extract timestamp match the period you are analyzing, and is there any known event between then and now that would change the numbers?

**Control totals.** Does the extracted data agree to an authoritative source? Pulling a transaction list and summing it should produce a number that ties to the general ledger. If it does not, either the extract is incomplete or the source systems are out of sync, and you need to know which. Control totals are the mechanism that connects the working file to the authoritative record.

The control total question is: what is the number this should tie to, and does it?

<!-- → [TABLE: Six-row table — column headers: "Dimension", "The silent failure mode", "The question to ask" — rows: Completeness (missing population, excluded entities) "What should be here?"; Freshness (stale extract, pre-restatement data) "Does the timestamp match the moment?"; Control totals (extract doesn't tie to GL) "What does this reconcile to?"; Mapping (account reclassification, changed categories) "Are the categories consistent across periods?"; Threshold logic (wrong cutoff, inappropriate materiality level) "Is this threshold right for this decision?"; Contradiction (two sources tell different stories) "What would explain the discrepancy?"] -->

**Mapping.** Are the categories consistent across the periods being compared? Account reclassifications, cost center restructurings, and product line redefinitions all change the basis of comparison without changing the format of the output. A trend that shows Q3 up 12% over Q3-prior might be a real increase, or it might be a reclassification that moved revenue from one line to another. Mapping problems are particularly hard to catch because they require knowledge that lives outside the file — organizational history, chart-of-accounts change logs, system migration records.

The mapping question is: have the categories changed between periods, and if so, is the comparison adjusted for that?

**Threshold logic.** When the recipe flags items for review, is the threshold appropriate for this period, this entity, and this type of decision? A fixed dollar threshold that was calibrated for a large division will underperform in a smaller one. A percentage threshold that works for operating expenses will produce different results for capital items. Threshold logic is a design decision that can go stale even when the numbers it produces look reasonable.

The threshold question is: is this cutoff the right one for the judgment this output is supposed to support?

**Contradiction.** Do different sources that should agree actually agree? If the CRM shows closed deals that are not in the revenue recognition system, something is wrong. If the payroll system and the general ledger disagree on compensation expense, one of them is wrong, and the difference needs an explanation. Contradictions between sources are diagnostically valuable — they point toward either a process gap or a data quality problem — but only if you look for them.

The contradiction question is: is there another source that should agree with this one, and does it?

---

## What Warranted Verbs Actually Do

Here is a practice that I find genuinely useful, and that the assessment artifact for this chapter is built around: warranted verbs.

The idea is simple. The language you use to describe a finding should be calibrated to the evidence you have. There are things the evidence can establish — facts that follow directly from verified source data. There are things the evidence can suggest — patterns that are consistent with a hypothesis but do not rule out alternatives. There are things the evidence cannot claim — conclusions that would require information you do not have. And there are things that need review — items where the evidence is ambiguous and a professional judgment is required before the artifact can go forward.

These four categories correspond to four families of verbs.

"Can say" verbs: *confirms, shows, establishes, documents, records.* Use these when the evidence is complete, fresh, reconciled, and directly supports the statement. "The Q3 extract confirms total revenue of $4.2 million, reconciled to the general ledger as of close."

"Can suggest" verbs: *indicates, is consistent with, appears to, may reflect.* Use these when the pattern supports the conclusion but the evidence does not rule out alternatives. "The month-over-month trend indicates a possible shift in customer mix, though the analysis does not isolate the cause."

"Cannot claim" language: when the evidence does not support the conclusion, say so explicitly rather than using hedged language that implies support. "The available data does not cover subsidiary B; no conclusion about consolidated performance can be drawn from this extract."

"Needs review" flags: when a finding is ambiguous — when the threshold logic may be wrong, when a mapping change is suspected, when two sources disagree without explanation — the artifact should flag the item explicitly and hold it at the gate rather than carrying it forward.

<!-- → [TABLE: Four-row table — column headers: "Category", "Warranted verbs / language", "Use when" — rows: Can say (confirms, shows, establishes, documents, records) "Evidence is complete, fresh, reconciled, directly supports the statement"; Can suggest (indicates, is consistent with, appears to, may reflect) "Pattern supports the conclusion but alternatives are not ruled out"; Cannot claim (explicit statement of what the evidence does not support) "Evidence is incomplete or does not cover the conclusion"; Needs review (explicit flag held at gate) "Finding is ambiguous — threshold, mapping, or source conflict present"] -->

The warranted-verb discipline does something important beyond accurate language: it makes the gap between evidence and conclusion visible. A summary that uses "confirms" throughout signals that someone checked the evidence and it held up. A summary that uses "indicates" and "may reflect" signals that the pattern is real but the causal story needs a professional judgment. A summary with explicit "cannot claim" statements signals where the analysis has limits. These signals are useful to the reviewer — they tell you where to spend your attention.

When AI drafts the summary, the warranted-verb discipline becomes a specification. A prompt that instructs the model to use only language calibrated to the evidence level — and to flag explicitly where the evidence is insufficient — produces a more useful output than one that allows the model to write in confident analytical language regardless of what the data actually supports.

---

## The Model's Role in Verification

There is a version of this that sounds like AI is the problem — that the verification failures happen because models write confidently about evidence they have not checked. That is a real failure mode, but it is not the whole picture.

A well-designed recipe can do significant verification work. It can check completeness against a defined population. It can compare extract timestamps to a period definition and flag staleness. It can run control-total checks and surface discrepancies. It can look for contradictions between sources. What it surfaces in these checks is genuinely useful — it is preparation work that would otherwise fall to the analyst.

The limit is not that the model cannot find gaps. The limit is that the model cannot judge whether a gap matters. A completeness gap in subsidiary B might be immaterial in a given period — subsidiary B contributed 0.3% of revenue and the analysis is for a high-level management review. Or it might be critical — subsidiary B is the one that had the acquisition close in Q3 and excluding it understates the story by $4 million. The recipe can flag the gap. It cannot decide which situation you are in, because that requires knowing what the analysis is for and who will use it.

This is where the PCAOB's evidence standard becomes useful as a frame. AS 1105 defines evidence as sufficient and appropriate — sufficient in quantity, appropriate in relevance and reliability. Sufficiency and appropriateness are not properties that a recipe can assess in context. They depend on the purpose of the artifact, the stakes of the decision, and the standards that apply in this particular situation. Those are professional judgments, and they belong on the human side of the gate.

<!-- → [DIAGRAM: Verification pipeline — sequence of boxes: "Recipe checks completeness, freshness, control totals, mapping, threshold logic, contradictions" → "Recipe flags gaps and surfaces findings" → [GATE: human adequacy check] → "Human judges sufficiency and appropriateness in context" → "Artifact released with warranted language" — below the pipeline, a label: "The recipe finds the gaps. The human decides whether they matter."] -->

---

## What Gets Written Near the Conclusion

One habit I want to name explicitly, because it is easy to skip under time pressure: writing the evidence limits near the conclusion, not at the end of the document.

The standard approach to caveats in professional work is to put them at the bottom — a limitations section, a footnote, a final paragraph that walks back the confidence of the main finding. The problem with this structure is that the person who reads the executive summary and stops there never sees the limits. The conclusion travels without its caveats.

Writing evidence limits near the conclusion — immediately adjacent to the claim — keeps the gap between evidence and conclusion visible at the point where the claim is made. "Revenue appears to have increased 8% quarter-over-quarter; this comparison excludes subsidiary B, which was not available in the extract at time of analysis" is a different artifact than "Revenue increased 8% quarter-over-quarter" followed by a footnote three pages later.

The warranted-verb list you build as this chapter's assessment artifact is an exercise in this discipline. For each conclusion in your analysis, write the verb, write the evidence category it belongs to, and write the limit in one sentence. Not a long caveats section — a one-sentence characterization of what the evidence does and does not support, placed next to the finding it qualifies.

If the analysis is worth doing, the limits are worth stating. If the limits are too significant to state without undermining the finding, the finding is not yet ready to go through the gate.

---

## What AI Cannot Decide

The verification discipline in this chapter has a clear ceiling: AI cannot decide materiality or sufficiency in context.

Materiality is a judgment about whether a gap, a discrepancy, or an uncertainty is large enough — in this situation, for this decision, for this audience — to affect the conclusion or require disclosure. It is not a calculation; it is a professional assessment. A 3% completeness gap is immaterial in one context and fatal to the analysis in another. The threshold is set by the purpose of the work and the standards that govern it, and those depend on information that lives outside the data.

Sufficiency is similar. The PCAOB standard requires that audit evidence be sufficient — that there is enough of it to support the conclusion. But "enough" is not a number; it is a judgment about the relationship between the evidence, the risk of the conclusion being wrong, and the consequences of being wrong. A recipe can count the rows. It cannot assess whether the count is sufficient.

This is the phase gate in its verification form. The recipe prepares the evidence surface — complete, fresh, reconciled, mapped, threshold-checked, contradiction-checked — and flags what it could not resolve. The human adequacy check is the professional judgment about whether that surface is good enough for this decision. The recipe tells you what you have. The professional tells you whether it is enough.

---

## Building the Warranted-Verb List

The assessment artifact for this chapter is a warranted-verb list for one analysis you own or have worked in. For each conclusion in that analysis, write four things: the conclusion, the verb you would use to characterize it, the evidence category it belongs to (can say, can suggest, cannot claim, needs review), and a one-sentence statement of the evidence limit.

If the analysis is hypothetical or based on a sanitized sample, that is fine — label it as such. The exercise is in the discipline of the list, not in the specific numbers.

What the list will show you, almost inevitably, is that some conclusions you have been characterizing as established findings are actually suggestions, and some suggestions are close to "cannot claim." That is not a failure of the analysis; it is the analysis becoming honest about what it knows. A conclusion that survives the warranted-verb test is a stronger conclusion, because it has been checked against the evidence that actually supports it.

The verification checklist for this chapter: evidence limits are written near the conclusion, not at the end. Model judgments are labeled as model judgments. Causal language is blocked unless the evidence supports a causal claim, not just a correlation. Machine conformance checks whether the required fields exist. Human adequacy checks whether the work is sufficient for the finance decision it supports.

---

## What Would Change My Mind

The warranted-verb framework assumes that the categories — can say, can suggest, cannot claim, needs review — are stable across contexts. I think that is largely true, but I am not certain it holds in every situation.

There are contexts where "can suggest" is the highest standard available, and where acting on suggestions is the professional norm — early-stage forecasting, scenario analysis, exploratory work before a formal close. In those contexts, labeling a finding as "can suggest" and moving it forward through the gate may be appropriate. The framework needs to account for what "adequate" means for the specific decision, not just in the abstract.

If someone showed me a class of finance decisions where the warranted-verb discipline systematically blocked useful analysis — where the requirement to qualify language kept professionals from acting on real patterns — I would want to understand whether the problem is the framework or the evidence standards being applied. The goal is calibrated language, not universal hedging.

---

## Still Puzzling

The threshold question is the one I find hardest to operationalize. I know that thresholds should be calibrated to the decision, the entity, and the period. I know that a fixed-dollar threshold calibrated for a large division will underperform in a smaller one. But I do not have a clean rule for how to set the threshold in the first place, or how to know when it has gone stale. That question connects to the data contract in Chapter 3, which is about the discipline that makes the evidence layer reliable — but I have not worked out how the contract should specify threshold logic in a way that updates as the business changes.

---

## LLM Exercises

**Exercise 1.** Take a summary or conclusion from a finance artifact you have worked with — a variance explanation, a budget commentary, a period-end note. Paste it into a prompt and ask the model to identify every verb that characterizes a finding, then classify each verb as "can say," "can suggest," "cannot claim," or "needs review" based on the evidence described in the surrounding text. Review the classifications: where does the model draw the line, and where do you disagree?

**Exercise 2.** Design a completeness check for one data extract you use regularly. What is the defined population the extract should cover? What is the mechanism you would use to verify that coverage — a row count against a control table, a sum against a GL total, a cross-reference to an authoritative list? Write the check as a recipe step, then ask the model to identify any cases where the check would pass but the extract could still be incomplete.

**Exercise 3.** Write a prompt that instructs an AI to draft a variance commentary using only warranted verbs — specifying that the model must distinguish between what the data confirms, what it suggests, and what it cannot support, and that it must flag any item where the evidence is insufficient for a claim. Compare the output to a commentary drafted without that instruction. What changed in the language, and what did the model flag that a standard prompt would have asserted?
