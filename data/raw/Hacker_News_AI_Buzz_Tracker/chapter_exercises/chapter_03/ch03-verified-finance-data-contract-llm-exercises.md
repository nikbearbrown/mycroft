# Chapter 3: The Verified Finance Data Contract

## Exercise 1

The eleven fields, each with one reason it matters:

Source, the specific file or system a number came from, because without a named source nobody can reproduce the number.
Period, the exact date range covered, because a quarter can mean calendar or fiscal, actuals or accruals.
Entity, the legal or operating entity represented, because a parent and its subsidiaries each produce a different version of the same metric.
Version, which instance of the export was used, because files get regenerated and the wrong pull looks identical to the right one.
Owner, the human responsible for the source's accuracy, because accountability has to sit with a person, not a tool.
Freshness, when the source was last updated, because a number can be accurate and still be too old for the decision at hand.
Schema, the structure and meaning of the fields, because a silent reclassification between two exports can masquerade as a real variance.
Control total, the checksum confirming the data arrived intact, because a row count mismatch is direct evidence something happened in transit.
Transformation, the log of operations applied between source and report, because each step is a place an error can enter and needs to be reproducible.
Log, the machine readable record of what the agent did, because a summary paragraph cannot be replayed and checked.
Report, the human readable output for review, because it is the surface for judgment, not a replacement for the evidence behind it.
Approval record, who reviewed the work and confirmed it, because this is the moment the accountable layer takes ownership.

If I suspected a number had changed between Tuesday and Thursday, I would check version first. Version is the field built specifically to separate one day's export from another, and everything else, the period, the entity, even the control total, can look identical across two versions while the underlying pull is different.

## Exercise 2

What is missing is everything the two layer distinction requires before a number counts as evidence: the source file the model pulled from, the period and entity it covers, which version of the export it used, who owns that source, and whether the figure has been reconciled against a control total. "The model" names a preparation step, not an accountable one, and a preparation step with no visible inputs is not verifiable by anyone other than the person who ran it. Before I could treat the figure as evidence, my colleague would need to supply the export path, the period and entity it represents, the version and timestamp of the pull, and the name of the person accountable for that source's accuracy. Only once those fields exist does the number move from an assertion produced by a model into a record someone else could reproduce.

## Exercise 3

Scope: what period, entity, source system, and action space is the agent operating in. If this is never asked, the agent may quietly read from an out of scope entity or period, and nobody would notice until the numbers stopped reconciling.

Approval: who clears the gate before the output moves forward. If this is never asked, there is no identified moment where responsibility passes from the model to a person, so the output can drift into use without anyone having actually taken ownership of it.

Verification: what source, control total, or owner confirmation would make this finding defensible. If this is never asked, a fluent looking output gets treated as settled simply because it reads like an answer, with nobody having checked whether a defensible trail exists behind it.

## Exercise 4

The recipe crosses the boundary at the point where it stops computing the variance and starts generating a paragraph explaining why the variance occurred. Pulling the export, computing the period over period difference, and formatting the result are all preparation, mechanical, checkable, source bound. Explaining the cause requires knowing what actually happened in the business that quarter, a hiring freeze, a pricing change, a one time write off, and that knowledge does not live in the export. The rewritten scope: the recipe pulls the named export, ties it to the prior period's export by matching schema and control total, computes the variance in dollars and percent for each line, and flags any line above a stated materiality threshold. It stops there and hands the flagged table to a named finance reviewer, who supplies the explanation from their own knowledge of the business and confirms it before the note goes anywhere else.

## Exercise 5

Two sentences to add: "This note is missing the version of the export used, so it is not currently possible to confirm which day's pull produced this figure or to reproduce it if challenged. It is also missing the named owner of the source and a transformation log, so there is no record of who is accountable for the underlying data or what operations, if any, were applied to it before this figure was calculated." Naming the gap directly, rather than presenting the note as complete, is what keeps a thin provenance note honest instead of just quiet about what it lacks.

## Exercise 6

Stop condition: if the control total does not match, meaning the count of records the recipe processed differs from the count the source system reports, the recipe halts before producing any output and flags the discrepancy with both counts stated explicitly. It does not attempt to reconcile the difference itself and does not proceed on the 10,000 it did process as if that were the full picture. A human reviewer would need to confirm where the missing fourteen records went, whether they were filtered out by a known and documented rule, dropped due to a schema mismatch, or lost in transit, and whether their absence is material to the output before allowing the recipe to rerun or the partial result to be used.

## Exercise 7

Verified evidence: tracing source files, checking control totals, flagging schema mismatches. These are mechanical, checkable operations that produce a reproducible trail. Model judgment: the formatted report itself, since producing a clean layout from verified inputs still involves the model making presentational choices that are useful but not themselves evidence. Human judgment: the senior accountant's review and approval for distribution, since that is the point where someone accountable decides the package is adequate to release.

The ambiguous activity is the formatted report. Formatting sounds like preparation, mechanical output, but a report that selects which variances to highlight or how to group accounts is already making a judgment about what matters, which edges toward the accountable layer. Whether it stays preparation or crosses into judgment depends on whether the selection criteria were set in advance by a human or decided by the model on the fly, and the description as given does not say which.

## Exercise 8

Task: accounts receivable aging. A recipe pulls the aging schedule, buckets balances by days outstanding, and drafts a paragraph explaining which customers are at risk of default and recommending a bad debt reserve adjustment. The paragraph reads cleanly, cites specific account names and days outstanding, and gets attached to the month end close package. Nobody stops to ask whether the recipe actually knows anything about those customers' circumstances beyond the aging bucket, and the reserve adjustment moves into the close package on the strength of how confident the paragraph sounds.

Redesigned workflow: the recipe's scope is the aging export for one entity and one period, read only, no write access to the general ledger. It computes the bucketed aging, ties the total to the accounts receivable control total in the trial balance, and flags any account past a stated days outstanding threshold. It stops there. The approval owner is the credit and collections manager, a named person, who reviews the flagged accounts against their own knowledge of each customer's payment history and correspondence before deciding on any reserve change. The verification standard: no reserve adjustment moves forward unless the flagged account ties to the trial balance control total and the collections manager has documented, in their own words, the basis for treating that account as at risk.

## Exercise 9

The strongest counterargument: Auditing Standard 1105 does not actually require a document to have been produced by a human, it requires that the information help the auditor reach conclusions and that it be reliable, and reliability is explicitly a function of the source and circumstances of its creation. A logged, reproducible AI output could in principle satisfy that if three things were true. First, the log would need to record every input, source file, version, timestamp, and every transformation applied, with enough detail that a different reviewer could rerun the same steps against the same sources and get the same output. Second, the transformation record would need to show that no step in the process involved the model asserting a fact not present in its inputs, meaning the output is a computation over verified data rather than a generation drawing on the model's own priors. Third, the approval chain would need a named human who reviewed the log itself, not just the output, and attested that the inputs and transformations were adequate for the conclusion drawn.

Evaluating my own argument: it mostly holds for the preparation layer, a control total check or a schema comparison, logged and reproducible, is genuinely closer to audit evidence than an unlogged one. But it dissolves as soon as the AI output includes any interpretive step, a causal explanation, a materiality call, a recommended treatment, because at that point the "circumstances of its creation" include a model generating language from patterns rather than reasoning from the specific facts of the case, and no amount of logging turns a plausible sounding inference into a traceable one. The log can prove what data went in and what operations ran. It cannot prove that a judgment rendered in fluent prose was actually derived from those operations rather than from the model's general sense of what a plausible variance explanation sounds like. That gap is exactly why the chapter treats AI output as non-evidence by default, and my counterargument only narrows that default, it does not remove it.
