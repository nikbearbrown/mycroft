# Chapter 4: Two Customers

## Exercise 1

Missing from the agent contract: the inputs are described as "Q3 receivables" and "prior quarter" with no file path, no version, no timestamp, so two people running this description could pull different exports and get different results. There is no output schema, so nothing defines what a valid flagged-items table looks like or which fields it must contain. There are no stop conditions, so the recipe has no way to halt if the receivables file is missing or the prior quarter file does not match on period. There is no log, so nothing records what was actually compared or what threshold was applied.

Missing from the human report card: there is no purpose sentence explaining what decision this comparison is meant to support. There are no caveats, so nobody knows whether the recipe checked anything beyond the raw comparison, for instance whether it reconciled to a control total. There are no named decisions, so a reviewer does not know what action, if any, is required before the flagged items move forward. There is no gate, so nobody is named as the approver and nothing says what approval means.

## Exercise 2

a) This run checks whether accounts payable items in this month's aging file are still open from the prior month in a way that suggests a payment delay or a data error.
b) This run checks whether this month's actual spending against budget, by account, falls within the range expected for this point in the fiscal year.
c) This run checks whether any payment in this month's disbursement file matches another payment already made to the same vendor for the same amount and invoice reference.

## Exercise 3

First, halt if the AP aging file or the payment ledger is missing or fails to open. Without this, the recipe would either crash uninformatively or, worse, silently run against a stale cached file and produce a comparison that looks current but isn't.

Second, halt if the period labels on the two files do not match, for instance one file is tagged Q3 and the other is tagged Q2. Without this, the recipe would compare two periods that are not actually comparable and produce a variance that reflects a period mismatch rather than a real change.

Third, halt if the row count in either file falls far outside its expected range, for instance a file that normally has thousands of rows arrives with fifty. Without this, the recipe would run its comparison against a truncated or corrupted extract and produce a flagged-items list that looks complete but is missing most of the real data.

## Exercise 4

Workflow: a monthly variance report comparing actual departmental spend to budget.

Inputs: `budget_2026_v1.csv` and `actuals_2026-06_v2.csv`, both pulled from the accounting system export on the first business day of the following month, tagged to fiscal period 2026-06.

Steps: normalize both files to the same account structure, join on account code and department, compute variance in dollars and percent for each line, and flag any line where the variance exceeds ten percent or five thousand dollars, whichever is larger.

Output schema: a flags table with required fields `account_code`, `department`, `budget_amount`, `actual_amount`, `variance_dollars`, `variance_percent`, `period`.

Stop conditions: halt if either source file is missing, if the account structures do not match after normalization, if the period tags on the two files disagree, or if more than half the accounts are flagged, since that suggests a structural problem rather than a set of real variances.

Log pointer: `/logs/budget-variance-2026-06-run-001.json`.

## Exercise 5

Purpose: this run checks whether June's actual departmental spend is within the range budgeted for June, and flags any account that is meaningfully over or under.

Evidence summary: the run flagged nine accounts. Six are timing differences, spend that will land in July instead of June, and fall back within range once adjusted for timing. Three are real overages totaling forty-one thousand dollars, concentrated in the marketing department, that were not anticipated in the June budget.

Caveats: the recipe compared spend to budget but did not check whether the budget itself was revised after it was set, and did not check whether the marketing overage ties to a specific approved initiative. It also did not check any account below the ten percent or five thousand dollar threshold, so smaller drift would not appear here.

Decisions: the marketing department head needs to confirm whether the forty-one thousand dollar overage was approved and, if not, explain the driver before the report goes to the finance committee.

Gate: the department finance manager signs off that the flagged items have been explained and that the report is ready to move forward, or sends it back if the explanation is missing.

## Exercise 6

The log is not the evidence summary because the log is built for a different reader with a different need. The log records every operation the recipe performed, in a structure meant to be replayed by another process, and its field names assume the reader already knows what a flag_id or a source_line means. A reviewer opening the log is not asking "did this run correctly," which is what the log answers. The reviewer is asking "what does this mean for the decision I have to make," which the log does not answer at all. The log has no purpose statement, so the reviewer does not know what question the run was even trying to settle. It has no caveats, so the reviewer cannot tell what the recipe did not check. It has no named decision or gate, so the reviewer has no way of knowing what action, if any, is required. Handing someone a log instead of a report card does not save a step, it just moves the translation work from the recipe's author onto every future reviewer, and each of them will translate it differently.

## Exercise 7

Recovering the agent contract starts with the artifacts that actually exist rather than the memory of the person who left: the source files the workflow reads each month, any scheduling configuration that shows when it runs, and any output files it has produced historically. From the historical outputs, you can reverse-engineer the output schema, since the fields that actually appear in two years of monthly files are the fields the recipe reliably produces. From the source file naming conventions and folder structure, you can often recover the input specification, which paths, which naming pattern for versions. The steps are the hardest part to recover honestly, since the code may do more than anyone remembers; the safest approach is to read the code itself rather than guess from outputs, and to note any behavior that doesn't match anyone's current expectation as a discrepancy to be resolved, not silently fixed. Stop conditions, if the code has any, can be found the same way; if the code has none, that absence itself is a finding to log, not something to backfill from imagination.

Constructing the human report card starts from the current reviewers rather than the recipe's history: interview whoever currently receives the output and ask what they actually do with it, what they wish it told them, and what they've learned to ignore. That tells you the real purpose and the real decision points, which may have drifted from whatever the recipe was originally built for. The caveats section should be built from a fresh read of what the recipe's steps do and do not check, not from institutional memory of what it used to check, since two years of unwritten changes may have altered the actual scope. The gate should be assigned to whoever currently has the accountability, which may not be who had it when the recipe was built.

## Exercise 8

A single-customer recipe is acceptable only when both of two conditions hold: the output truly never leaves an automated pipeline that another process consumes, and no human decision or approval depends on that output at any point, now or foreseeably. A routine internal check that feeds directly into another script, with no report ever generated for a human, can reasonably skip the human report card, since there is no reviewer to serve. A one-time, throwaway comparison a single analyst runs and reads themselves, never again, and never shares, can reasonably skip the full agent contract, since there is no future maintainer or auditor who needs it reproduced.

But most workflows described as low-stakes and routine do not actually meet either condition; they simply have not yet had a bad month. A routine reconciliation looks low-stakes until the one month its flagged item turns out to be a real six-figure error, and at that point the missing agent contract means nobody can show how the flag was computed, and the missing report card means nobody documented what was checked before it was cleared. The risk a single-customer recipe introduces even in low-stakes contexts is the same risk this chapter names for any recipe: when it eventually matters, and eventually most recurring workflows do, the thread back to evidence will not exist, and by then the person who could reconstruct it from memory may be gone.

## Exercise 9

The three factors interact rather than each independently setting the depth. Reviewer domain knowledge sets the floor of translation needed; a controller who reads AP agings daily needs less spelled out than a first-time reviewer. Consequence sets how much the summary must anticipate challenge; a routine finding can be summarized in a sentence, while a disclosure-supporting finding must survive someone reading it a year later during an audit. Reversibility sets the urgency and the completeness bar; an irreversible action, like a payment that clears, demands a summary detailed enough to support the decision before it happens, not after.

Tiered evidence summary:

Routine: a single sentence stating what was flagged and its size, with the raw log referenced but not restated, since the decision it supports is low-stakes and reversible, for instance an internal reconciliation feeding a same-day correction.

Material: a short paragraph naming what was found, which specific items drove it, the size in dollars, what was and was not checked, and what remains open, because a material finding may inform a decision that is harder to unwind and may face scrutiny from someone other than the immediate reviewer.

Disclosure-supporting: a full evidence summary including every caveat, every control total check performed and its result, an explicit statement of what the recipe cannot conclude, and named confirmation from the line owner for any inferred detail, because this tier feeds an external-facing or irreversible action and must independently survive being read by someone with no context on the run, possibly during a later audit or dispute.
