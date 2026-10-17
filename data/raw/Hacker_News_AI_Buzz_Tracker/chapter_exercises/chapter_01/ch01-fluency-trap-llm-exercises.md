# Chapter 1: The Fluency Trap

## Exercise 1

Explanation analyzed (the chapter's opening note):
"Revenue is down this quarter because enterprise renewals slipped. The renewal pipeline showed softness in the mid-market segment, which accounts for approximately 23% of total recurring revenue."

(a) The claims being made:
1. Revenue is down this quarter.
2. The reason revenue is down is that enterprise renewals slipped.
3. The mid-market segment is about 23 percent of total recurring revenue.

(b) The causal language:
The clear causal phrase is "because enterprise renewals slipped." The word "because" is what turns a description of a number into a claim about its cause. The sentence structure (revenue down, then "because," then the mid-market segment) also frames a correlation as if it were the proven driver.

The phrase "showed softness" is not actually causal language. It sounds like it is explaining something, but it states no number and names no driver. It is worth flagging precisely because it reads as analysis while saying nothing verifiable, which is the fluency problem in miniature.

(c) The source that would need to exist for each claim to be verifiable:
1. For the revenue drop: the revenue export for this quarter and the prior quarter, tied to the General Ledger.
2. For the cause: the renewal and churn export from the Customer Relationship Management system. Churn here means the customers who did not renew or who cancelled. The export would need to show the renewal dollars lost and a ranking that rules out pricing changes, timing, or a data pull error as the larger cause.
3. For the 23 percent figure: a schedule of Annual Recurring Revenue broken down by segment, taken from the system of record.

## Exercise 2

The first distinct claim in the opening paragraph is "Revenue is down this quarter."

| Claim | Source | Period | Owner | Status | Gate required |
|---|---|---|---|---|---|
| Revenue is down this quarter versus the prior quarter | Not identified. The prompt supplied no export. | "This quarter" is undefined. No period boundary was given. | Not identified | Unsupported. The size and direction are unverified and the period floats. | Tie to the period revenue export with explicit dated period labels and a named owner before use. |

Every cell other than the claim itself is empty, and each empty cell is a finding rather than a missing answer. The blank source and blank owner are the point of the artifact: they make the gaps visible that the polished sentence hid.

## Exercise 3

Scope, a bad answer: "Explain why revenue moved." There is no period, no entity, no source file, and no defined action space. The model has nothing real to ground in, so whatever it writes is produced from the surface shape of the request rather than from records.

Approval, a bad answer: "Whoever reviews it will catch any problems." There is no named approver and no defined gate, so the output moves forward by default the moment someone copies it into a deck. A role is not a person, and "whoever reviews it" is the same as no one.

Verification, a bad answer: "It reads as consistent with what we expected." Sounding plausible is not the same as being traceable. No source row, no control total, and no owner confirmation is named, so nothing can be defended if the number is questioned.

## Exercise 4

The four paragraph commentary I am auditing:

"Net revenue for the month was 4.2 million dollars, up 6 percent versus the prior month, driven primarily by stronger performance in the North America region. Operating expenses came in at 2.8 million dollars, slightly above plan, largely because of higher than expected marketing spend tied to the new product launch, which we expect to normalize next month. Days sales outstanding improved to 41 days, reflecting tighter collections discipline. Overall the month reflects healthy momentum and the team recommends no corrective action at this time."

The assessment artifact, one row per distinct claim or number:

| Claim | Source | Period | Owner | Status | Gate required |
|---|---|---|---|---|---|
| Net revenue was 4.2 million dollars, up 6 percent versus the prior month | Not identified | Current month, undated | Controller | Unsupported | Tie both figures to the General Ledger revenue export and confirm the percentage calculation |
| The growth was driven by the North America region | Not identified | Current month | Regional finance lead | Owner needed | Confirm North America was the largest driver rather than price, mix, or timing |
| Operating expenses were 2.8 million dollars, slightly above plan | Not identified | Current month versus plan | Financial planning lead | Unsupported | Tie to the General Ledger and the budget file, and quantify the variance |
| The expense overage was caused by marketing spend on the launch and will normalize next month | Not identified, and the second half is a forecast | Current month, plus a forward looking claim about next month | Marketing finance lead | Owner needed | Confirm the launch was the driver, and either remove the prediction or label it a forecast with an owner |
| Days sales outstanding improved to 41 days because of tighter collections | Not identified | Current month | Accounts receivable lead | Owner needed | Tie to the accounts receivable aging report and confirm the cause was collections rather than invoice timing or one large receipt |
| The month is healthy and no corrective action is needed | None. This is a conclusion. | Current month | Controller or Chief Financial Officer | Owner needed | This is a judgment, not a finding. It cannot be carried by prepared text and needs an accountable sign off. |

Not one of these claims carries a source on its own. The most dangerous rows are the forecast smuggled into the expense sentence ("will normalize next month") and the final row, where a judgment ("no corrective action") has been written in the same confident voice as the numbers. Those are the two places where preparation has quietly crossed into judgment.

## Exercise 5

Before I would touch the note I would need answers to these questions:
1. Which export does each number tie to, and at what version and timestamp.
2. What exact dates the period covers, and whether every figure shares that same boundary.
3. Who confirmed each stated cause, or whether the causes are guesses made by the model.
4. Who is the accountable owner for each segment or driver claim, and whether they have signed off.
5. Whether I am authorized only to improve clarity, or also to cut or flag claims that have no support.
6. Who the named approver is and what standard they hold a note going to the Chief Financial Officer to.

Cleaning the language without answering these reproduces the fluency trap because editing only improves the surface, which is the exact quality that already makes fluent output dangerous. A smoother paragraph is more likely to be approved and harder to push back on, since a clean draft invites approval while a rough one invites questions. If the cause of the variance is something the model guessed and I make that sentence crisper, I have raised the confidence of an unverified claim without adding any evidence, and I have put my own polish on someone else's ungrounded statement. The correct order is to build the assessment artifact first and tie out the claims, and only then to improve the wording.

## Exercise 6

The rule that artificial intelligence output needs human review before it goes anywhere is necessary because without any human in the loop, fluent output enters the record with no one accountable for it, which is the worst case.

It is not sufficient because the rule says that review happens but not what review checks. The natural failure is that a reviewer reads for fluency, asking whether the text sounds right and reads cleanly, instead of reading for grounding, asking what each claim is tied to. Since polished output always sounds right, a fluency review reliably passes claims that have no support. The rule ends up being satisfied by the very behavior it was meant to prevent.

To make the rule sufficient, it would need to add:
1. A definition of what review means, namely tying each claim to a source rather than approving prose.
2. A requirement that the reviewer signs off on the assessment artifact, the table of claim, source, period, owner, status, and gate, rather than on the paragraph.
3. A named approver, a specific person, with a logged record of who approved what and when.
4. A rule that any claim still marked unsupported or owner needed blocks release until it is resolved.
5. A separation of the two reviews, so that improving the wording and confirming the evidence are different steps and passing one does not count as passing the other.

## Exercise 7

Scope, set before the model runs: one entity, the month that just closed compared to the prior month and to plan. The source is the locked General Ledger export with a version number and timestamp, plus the budget file. The action space is drafting commentary only, with no authority to release or send anything.

What the model receives: the locked two period General Ledger export and the budget file with their versions and timestamps, a variance threshold set by the human (for example, flag any line over a set dollar or percentage amount), and a fixed format in which every flagged line carries the account, the current and prior or plan figures, the dollar and percentage variance, and empty fields for driver, source, owner, and status.

What the model produces: a variance table where every line over the threshold has its numbers tied to source rows, a draft narrative in which every stated cause is marked as an inference to be confirmed, and a pre filled assessment artifact in which the source field is completed only where a number actually ties to the export, and every stated cause defaults to owner needed.

The assessment artifact: the columns are claim, source, period, owner, status, and gate required. The status values are verified, inferred, unsupported, and owner needed. The model is allowed to mark a row verified only when the arithmetic ties to a named source row. Every cause defaults to owner needed.

The named approver: the Controller, a specific named individual, with the approval logged with date and time.

The criteria the approver uses to decide the output is ready:
1. Every number ties to a source row in the locked export and the control total reconciles.
2. Every stated cause has a confirming owner who has been contacted, with no inferred or unsupported rows left, or those rows are cut from the note.
3. Period labels are exact dates rather than floating phrases.
4. Any forward looking statement is removed or relabeled as a forecast with an owner.
5. The approver can say in one sentence how they would defend each remaining claim to the Chief Financial Officer.

The stop condition is that the recipe halts at the assessment artifact. It does not send, file, or insert anything into the deck. Only after the Controller clears the gate, with that decision logged, does the note move forward, and any final polishing of the language happens after sign off rather than before.

## Exercise 8

The Public Company Accounting Oversight Board standard AS1105 requires that audit evidence be sufficient, meaning enough in quantity, and appropriate, meaning relevant and reliable, and that it support the conclusion through a traceable basis.

Evaluating a generated variance note as it usually arrives:

Sufficient: it fails. The note is the entire output. No underlying records are attached or cited, so there is no body of evidence that could be enough.

Appropriate, relevance: partial. The claims are topically about the variance, but relevance to a conclusion requires that the evidence actually bear on that conclusion, and a guessed cause does not.

Appropriate, reliability: it fails. A model paraphrase is among the least reliable forms of evidence. It does not come from the source system, it is not independently corroborated, and it carries no version or provenance.

Traceable to source: it fails by default, because nothing in the document points to a specific row in a specific export.

The conditions under which artificial intelligence prepared output could meet the standard are not that the text itself becomes evidence, since it never does, but that the preparation step is restructured so that:
1. Every number is generated from a named, versioned, timestamped export, with the citation embedded in the output so the figure can be traced to a row.
2. Every transformation is logged, so the chain from report back to log, script, recipe, and source is unbroken.
3. The model does not assert causes. It leaves them as flagged gaps for an accountable person to confirm, and the confirmation is recorded.
4. A control total ties the prepared figures back to the General Ledger.
5. A named professional reviews, confirms, and signs, supplying the evidentiary standing and the accountability that the text alone cannot have.

In other words, the model can assemble a traceable, corroborated, logged surface, while the judgment about sufficiency and appropriateness and the accountable sign off stay with a person. The standard is met by the structure built around the model, never by the fluent text on its own.

## Exercise 9

The difficulty is that defensible means different things for a department variance note, a board presentation, an audit workpaper, and a disclosure schedule, and the standard usually lives in individual reviewers' heads, so it changes depending on who happens to review.

A process for making the standard explicit:

First, define artifact tiers by consequence rather than by department.

| Tier | Examples | Consequence if wrong |
|---|---|---|
| Internal orientation | Team review surface, working variance draft | Rework, low impact |
| Internal decision | Department budget note, headcount input | Misallocated resources |
| Leadership | Board deck, Chief Financial Officer package | Strategic misdirection, reputational damage |
| External or attested | Audit workpaper, disclosure schedule, investor communication | Restatement, audit finding, legal exposure |

Second, ask the same calibration questions once per tier, to set the standard rather than per artifact:
1. Who is the audience and what decision do they make from it.
2. What is the worst realistic consequence of a wrong number or claim.
3. What level of traceability is required, from claim level citation up to a control total, independent corroboration, or a formal workpaper.
4. Who is the named accountable owner, and what is the minimum sign off, from peer up to controller or partner.
5. What must be retained, and for how long, to reconstruct the basis later.

Third, build the standard into the gate rather than into the reviewer. Each artifact is tagged with its tier when it is created. The assessment artifact template changes by tier, so a low tier may let an inferred row ship with a flag while the highest tier forbids any row that is not verified and requires a full evidence binder. The gate's release criteria are pulled from the tier definition, so two different reviewers of the same tier apply the same bar. The required seniority of the approver is set by the tier and is logged. The machine checks the mechanical tier requirements, such as whether citations are present and whether any unsupported rows remain at a high tier, while the human checks whether the work is actually adequate. This turns adequacy from a private judgment into a written standard that the gate enforces.
