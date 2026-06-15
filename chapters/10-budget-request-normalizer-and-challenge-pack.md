# Chapter 10 — Budget-Request Normalizer and Challenge Pack
*What happens when six departments send six different answers to the same question.*

Every year, sometime in Q3, finance asks the same question of every department: what do you need next year, and why?

The answers come back in six different shapes.

The engineering department submits a spreadsheet with headcount by role, fully loaded cost assumptions, and a tab that explains the methodology. The marketing department submits a narrative deck with a budget number on slide fourteen and no supporting detail. The operations department uses last year's template, which had a different account structure. The sales department's submission has headcount in one currency and software costs in another, because the team is split across two regions. The product department includes a new initiative in the base budget without flagging it as new spend. The legal department submits on time with everything required, but their headcount rate assumptions are eighteen months old.

The budget analyst's job, before any planning discussion happens, is to turn those six submissions into a surface where the numbers can actually be compared. Not to decide which requests are reasonable — that is the planning discussion. To make the comparison possible in the first place.

This is the normalization problem. And it is exactly the kind of work where AI-assisted preparation earns its value — not by making funding decisions, but by doing the structural work that makes funding decisions well-informed.

---

## Why Comparison Requires a Common Structure

The reason budget submissions arrive in different shapes is not that departments are disorganized. It is that each department optimized their submission for their own clarity, not for cross-departmental comparison. Engineering knows its headcount; it built a headcount-first template. Marketing knows its program spend; it built a program-first template. Both are internally coherent. Neither is comparable to the other without transformation.

The transformation has three dimensions. First, period alignment: all submissions need to cover the same fiscal year, with the same period boundaries, broken into the same intervals. A submission that covers a calendar year when the company uses a fiscal year ending in September needs to be re-periodized. A submission that provides annual totals when the planning model needs monthly phasing needs to be expanded.

Second, account alignment: every line item needs to map to the same chart of accounts so that headcount costs in engineering and headcount costs in marketing land in the same GL account in the plan. A submission that calls a line "team salaries" needs to be mapped to the same account code as one that calls it "compensation expense." The mapping is not always obvious — travel and entertainment might be one account in one department's template and two accounts in another's.

Third, currency alignment: any submission denominated in a non-base currency needs to be converted using a documented rate — not the analyst's judgment about the current rate, but the planning rate approved by treasury for the budget cycle.

None of these transformations involves judgment about whether the numbers are right. They are mechanical steps that convert heterogeneous inputs into a homogeneous comparison surface. The recipe can do them reliably and document every transformation in a log. The analyst cannot do them reliably at scale while also thinking about the substance of the submissions.

<!-- → [DIAGRAM: Six department submission boxes on the left, each with a different shape (different color/icon representing different templates). Center: Normalization pipeline with three stages labeled Period alignment, Account alignment, Currency alignment. Right: Single normalized comparison surface. Caption: Normalization converts heterogeneous inputs into a surface where numbers can be compared. It does not evaluate whether the numbers are right.] -->

---

## Template Verification Before Normalization

Before the normalization pipeline touches any submission, there is a gate that is easy to overlook and costly to skip: verifying that each submission used the current template.

Budget templates change from cycle to cycle. New accounts are added, old ones are retired, headcount rate assumptions are updated, the period structure changes when the fiscal calendar shifts. A submission built on last year's template may use account codes that no longer exist in the current chart of accounts, headcount rates that don't match the current compensation planning assumptions, or a period structure that doesn't align with the current fiscal year.

Normalizing a submission built on the wrong template produces a normalized artifact that looks correct and isn't. The account mapping will be wrong in ways the normalization log cannot detect, because the log doesn't know which accounts were retired — it just maps what it receives to the closest current match, which may be the wrong one.

The recipe should reject old-template submissions before normalization begins. Not flag them for review — reject them, with a specific error message that names the template version received and the template version required. The submission owner needs to resubmit on the current template. This is not a documentation formality. It is the condition under which the normalization output is trustworthy.

The rejection log is also useful information for the planning lead: which departments submitted on the wrong template, and how many days before the deadline? A pattern of old-template submissions is a signal about the template distribution process, not just about individual departments.

<!-- → [TABLE: Four-row table. Columns: Verification Check, What It Catches, Recipe Action if Failed. Rows: Template version (old template — rejects submission, logs version received vs. required, notifies submitter), Required fields present (missing headcount, rate assumptions, account mapping — flags missing fields, pauses submission, requests resubmission), Period coverage match (doesn't cover full fiscal year — flags gap, requests resubmission), Currency declaration (submission currency not declared — flags, requests declaration before normalization). Caption: Template verification is the first gate. A submission that fails it does not enter the normalization pipeline.] -->

---

## Normalizing Headcount and Rate Assumptions

Headcount is where budget submissions diverge most consequentially. A ten-person engineering team and a ten-person marketing team cost different amounts, and the difference is not just base salary — it is benefits loading, payroll taxes, equity, and any location-based adjustments. A submission that enters headcount as a count without specifying role, level, or location cannot be normalized to a cost with any reliability.

The recipe checks headcount submissions against a planning rate card: the approved set of fully-loaded cost assumptions for each role, level, and location that treasury or HR publishes at the start of the budget cycle. A headcount line that specifies "senior software engineer, San Francisco, full-time" can be priced reliably from the rate card. A headcount line that specifies "engineer" cannot — the range between a junior engineer and a principal engineer in the same location can be a factor of three.

When a headcount line cannot be matched to the rate card, the recipe flags it as unsupported. Not wrong — unsupported. The department may have a perfectly reasonable explanation: a new role that isn't on the rate card yet, a contractor arrangement that uses a different rate structure, a position that's currently open and being scoped. But until the explanation is provided and the rate is confirmed by the appropriate owner, the cost estimate for that line is a gap in the submission.

The same logic applies to non-headcount assumptions. A software renewal with no documented contract rate, a travel budget with no stated per-head assumption, a facilities cost with no stated square footage and rate — each of these is an unsupported assumption that the challenge pack needs to surface. The recipe flags them; the business partner conversation confirms or resolves them.

<!-- → [TABLE: Three-row table. Columns: Assumption Type, What the Recipe Checks, Flag if. Rows: Headcount (role, level, location against rate card — role or level unspecified, rate card match fails), Software/SaaS (contract or renewal rate against vendor contract log — no documented contract rate, renewal date not current period), Travel/Entertainment (per-head rate against policy — no per-head assumption stated, rate exceeds policy maximum). Caption: Unsupported assumptions are not wrong assumptions. They are assumptions without a documented basis. The flag requests the basis; the business partner provides it.] -->

---

## Prior-Period Comparison

Once the submission is normalized, the recipe compares it to the prior-year actuals and the current-year plan for the same department and account structure.

This comparison does not evaluate whether the request is reasonable. It describes what changed and by how much. A department requesting 40% more headcount than last year's approved plan is not necessarily requesting too much — the company may be growing, the department may have a new charter, the prior plan may have been underfunded. But the 40% is a fact, and the fact needs to be visible in the planning discussion.

The prior-period comparison generates a change table: for each account and headcount line, the prior-year actual, the current-year plan, the current-year estimate-to-complete, the submitted request for next year, and the year-over-year change in both absolute and percentage terms. Lines with changes above a threshold — which the planning lead sets before the cycle begins — are flagged for the challenge pack.

The threshold is not a judgment about what is acceptable. It is a filter that directs attention. The planning discussion has limited time; the challenge pack should direct that time toward the submissions where the numbers changed most significantly and the explanations are most needed.

New spend — budget for initiatives, projects, or capabilities that did not exist in the prior plan — requires special handling. New spend that is buried in the base budget rather than identified as new spend is a common error and occasionally a deliberate one. The recipe compares the current submission to the prior-year account structure and flags any account or headcount line that has no prior-year counterpart. The flag does not assume the new spend is unjustified. It asks the submitting department to explicitly acknowledge that it is new and to provide the supporting rationale.

<!-- → [TABLE: Example change table for one department. Columns: Account, Prior Year Actual, Current Year Plan, Current Year EAC, Submitted Request, YoY Change ($), YoY Change (%), Flag. Sample rows showing headcount (flagged at +35%), software renewals (within threshold), new initiative line (flagged as new spend, no prior year). Caption: The change table describes what changed. It does not evaluate whether the change is justified. That is the planning discussion.] -->

---

## Generating the Challenge Questions

The challenge pack is the output the planning lead takes into the budget review conversation. It has two sections: the normalized comparison surface and the challenge questions.

The challenge questions are generated from the flags: every unsupported assumption, every threshold-exceeding change, every piece of new spend without an explicit rationale label. For each flag, the recipe generates a specific, sourced question — not a generic prompt but a question that names the line item, states the flagged condition, and asks for the specific information needed to resolve it.

"Headcount line 'senior engineer, unspecified location' cannot be priced from the rate card. What is the intended location and level for this position?"

"Travel and entertainment is budgeted at $1,200 per head against a policy maximum of $800. What is the basis for the above-policy rate?"

"Account 6430 (new initiative spend) has no prior-year counterpart. Please confirm this is new spend and provide the initiative brief and approval status."

These questions are not challenges to the department's judgment. They are requests for the information needed to confirm or price the assumptions the submission is built on. The planning discussion is more productive when the finance team arrives having already identified the specific gaps rather than discovering them mid-conversation.

The challenge pack is reviewed by the planning lead before it goes to the departments. The planning lead may remove questions that have already been answered informally, combine questions that relate to the same issue, or add questions based on context the recipe doesn't have. The pack is a preparation layer; the planning lead's review is the gate.

<!-- → [TABLE: Example challenge pack section. Columns: Flag Type, Department, Line Item, Flag Description, Challenge Question. Three example rows covering: unsupported headcount (engineering, senior engineer line — location/level unspecified — "What is the intended location and level?"), above-policy rate (sales, T&E — $1,200 vs. $800 policy maximum — "What is the basis for the above-policy assumption?"), new spend (product, initiative account — no prior-year counterpart — "Please confirm new spend and provide initiative brief."). Caption: Challenge questions are sourced, specific, and resolvable. They ask for information, not justification.] -->

---

## The Gate Before Distribution

The challenge pack does not go to departments until the planning lead has reviewed it. This is not a delay — it is the step that converts a preparation artifact into an accountable communication.

The recipe produces the pack. The planning lead confirms three things. First, completeness: are all required submissions present? A missing submission is a planning gap that needs to be flagged before the review cycle begins, not discovered during it. Second, accuracy: do the challenge questions reflect actual flags, and do the flags reflect actual conditions in the submissions? A false flag — a question generated from a normalization artifact rather than a real assumption gap — wastes the department's time and the planning lead's credibility. Third, tone and scope: are the questions appropriate for the relationship and the planning stage? The planning lead may rephrase questions that are technically accurate but likely to put a department on the defensive in ways that are counterproductive.

After the planning lead's review, the pack goes out. Before it, it does not. The gate is the point where the preparation layer ends and the accountable planning conversation begins.

The recipe cannot approve or deny funding. It cannot decide whether a 40% headcount increase is justified or whether an above-policy travel rate reflects a legitimate business need. Those are judgments that require context, relationships, and accountability — all of which belong to the business partners having the planning conversation.

What the recipe can do is ensure they arrive at that conversation with a clean surface, documented assumptions, specific questions, and a clear record of what was submitted, what was flagged, and why. A budget planning process built on that foundation is faster, more consistent, and more defensible than one built on six different spreadsheets that no one managed to compare before the meeting started.

---

## What Would Change My Mind

If departments submitted budget requests through a shared planning system with enforced templates — where old templates were technically unavailable, headcount lines required role and location fields before the form would accept them, and new spend was a separate workflow from base budget — much of the normalization and verification work would move upstream. The recipe would still be needed for the comparison and challenge question generation, but the rejection and flag rates for template and assumption problems would drop significantly. The preparation work would shrink; the review conversation would still require the same human judgment.

## Still Puzzling

The challenge question generation is the step in this recipe where the preparation/judgment line is hardest to hold. A well-generated challenge question looks a lot like a challenge — it names a specific condition in the submission and asks for a response. In practice, some departments will read the questions as conclusions rather than requests for information, and the conversation can start defensively rather than collaboratively. The right calibration between specificity (which makes questions actionable) and tone (which determines whether they land as inquiry or accusation) is currently left to the planning lead's review. That is probably the right answer, but it means the quality of the challenge pack's reception depends on a human judgment step that the recipe cannot assist with.

---

## Exercises

**Warm-up**

1. *(Low difficulty)* A department submits a budget using last year's template, which has three account codes that were retired in the current chart of accounts. Explain why the recipe should reject this submission rather than attempt to map the old account codes to current ones, and what information the rejection message should contain. *What this tests: understanding of why template verification is a gate, not a best-effort mapping problem.*

2. *(Low difficulty)* A headcount line reads "two analysts, TBD location." Identify what is missing, why the recipe flags it as unsupported rather than wrong, and what specific information is needed to resolve the flag. *What this tests: distinction between unsupported assumptions and incorrect assumptions.*

3. *(Low difficulty)* The prior-period comparison flags a line item showing 0% change from last year's actuals. Explain why a 0% change line might still warrant a challenge question. *What this tests: understanding that the threshold filter directs attention but does not define what requires scrutiny.*

**Application**

4. *(Medium difficulty)* A sales department submission includes travel and entertainment budgeted at $950 per head. Company policy caps T&E at $800 per head for the sales team. The department's submission note says "above policy, approved by CRO." Write the challenge question the pack should include for this line, and explain what the planning lead would need to verify before accepting the "approved by CRO" claim. *What this tests: application of the flag-and-question logic to a submission that includes a justification that cannot be verified by the recipe.*

5. *(Medium difficulty)* Design the normalization log structure for a three-currency submission (USD base, GBP and EUR inputs). Specify: what rate is used, where the rate comes from, how the conversion is documented, and what the stop condition is if no approved planning rate exists for a currency in the submission. *What this tests: application of the documentation and stop-condition principles to the currency normalization step.*

6. *(Medium difficulty)* A product department embeds $400,000 of new initiative spend in account 6200 (base operating expense) with no new-spend flag. The recipe flags it as new spend because account 6200 had no prior-year counterpart in the product department's history. Write the challenge question for this flag. Then explain: what is the planning risk if this flag is not surfaced before the planning discussion? *What this tests: understanding of why new-spend identification is a control step, not just a documentation preference.*

**Synthesis**

7. *(High difficulty)* You are building the normalization recipe for a company with fourteen departments, three currencies, two fiscal calendar conventions (one acquired subsidiary uses a different year-end), and a rate card that HR updates mid-cycle when compensation bands change. Design the recipe's handling of the mid-cycle rate card update: what happens to submissions that were normalized before the update, how are they flagged, and what does the planning lead need to do? *What this tests: integration of the normalization principles with a realistic operational complication — the recipe as a living process, not a one-time run.*

8. *(High difficulty)* The planning lead reviews the challenge pack and removes eight questions before distribution, saying "I already know the answers to these from conversations last week." Evaluate this decision: under what conditions is it appropriate for the planning lead to remove challenge questions from the pack, and what documentation practice should accompany the removal to preserve the audit trail? *What this tests: understanding of the gate review as an accountable step, not just an editorial one — and what "reviewed and removed" means for the planning record.*

**Challenge**

9. *(Advanced)* The "Still Puzzling" section identifies a real tension: challenge questions that are specific enough to be actionable can land as accusations rather than inquiries, and the calibration is left to the planning lead's review — a human judgment step the recipe cannot assist with. Design a tiered question format that preserves specificity while signaling collaborative intent: what would a three-tier structure look like (information request, assumption flag, policy exception), how would the language differ across tiers, and how would the planning lead's review criteria differ for each tier? Address whether this tiering should be visible to the departments receiving the pack or only to the planning team. *What this tests: ability to operationalize the tone calibration problem the chapter leaves open — designing a structure that makes the human judgment step more consistent without removing it.*
