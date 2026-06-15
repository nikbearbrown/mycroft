# Chapter 13 — Cash Forecast Variance Explainer
*How to build the bridge between what you expected and what happened — without filling the gaps with stories.*

The forecast said the company would end the week with $4.2 million in the operating account. The actual ending balance is $3.1 million. The difference is $1.1 million.

Someone is going to ask what happened.

There are two ways to answer that question. The first is to look at the data — the forecast file, the bank statement, the payroll register, the collections report — and build a systematic account of how much of the difference you can explain with sources and how much you cannot. The second is to look at the $1.1 million, recall that payroll ran this week and collections have been slow, and write a paragraph that sounds like an explanation.

The second answer is faster. It is also the more dangerous one. "Payroll timing and slower collections" is plausible for almost any week when cash came in below forecast. It requires no sources. It cannot be verified. And if the real reason the balance is $1.1 million low is that a large payment went out twice — a duplicate disbursement that nobody caught — the plausible story will paper over the control failure until someone digs deeper.

The recipe's job is to build the first kind of answer, even when it is incomplete. Especially when it is incomplete.

---

## What a Variance Bridge Actually Is

A cash forecast variance bridge is a structured account of the movement from forecast to actual. It has a beginning and an ending: opening cash balance, expected and actual. It has a middle: every category of cash inflow and outflow, with the forecast amount, the actual amount, and the difference. And it has an accounting that adds up: the sum of all the category differences should equal the total forecast-versus-actual variance.

The bridge is not an explanation. It is a disaggregation. Instead of one $1.1 million mystery, you have ten or fifteen line items — collections, payroll, vendor payments, tax disbursements, financing activity — each with its own forecast, actual, and difference. Some of those differences will be small and expected. Some will be large and explainable from known sources: payroll runs on a cycle, the payroll register shows the amount, the difference matches the timing. Some will be large and not immediately explainable. Those are the gaps the recipe marks and leaves open.

The bridge's value is in what it separates. A $1.1 million variance that is mostly timing — payroll landed two days early, a large customer payment came in two days after period end — is a very different situation from a $1.1 million variance where $800,000 is unexplained after all known drivers are attached. The bridge makes that difference visible. A narrative paragraph buries it.

<!-- → [DIAGRAM: Waterfall chart structure showing: Opening forecast balance → plus/minus each category variance (collections, payroll, vendor payments, tax, financing, other) → Actual ending balance. Categories split into two groups: "Explained — known driver attached" (solid fill) and "Unexplained — no source found" (hatched fill). Gap between total explained and total variance labeled "Open variance requiring treasury/FP&A review." Caption: The bridge disaggregates the total variance into explained and unexplained components. The unexplained portion is a finding, not a narrative opportunity.] -->

---

## Version Control and Period Confirmation

Before the recipe computes anything, two confirmations have to happen.

The first is forecast version. Cash forecasts are living documents — they get updated as new information arrives. A thirteen-week rolling forecast might have been updated three times in the week being reviewed. Which version is the right baseline for the variance analysis? The answer is not "the most recent version before the period ended" — that answer allows the forecast to be implicitly revised toward actuals, which defeats the purpose of the comparison. The right version is the one that was locked at the start of the period, before any actuals were known.

The version confirmation needs to be explicit in the recipe: the forecast file used, its timestamp, its version identifier, and the confirmation that it predates the period start. If multiple versions exist and none is clearly locked at the right time, that is a process gap — the recipe flags it and requires human confirmation of which version to use before proceeding.

The second confirmation is period alignment. The forecast may cover a week that ends on Friday; the bank statements may settle on different dates; the payroll register may reflect pay dates rather than process dates. The recipe checks that every source covers exactly the same period and flags any mismatch. A one-day period mismatch between the forecast and the collections data can produce a timing difference that looks like a collections variance but is actually an alignment artifact.

These are stop conditions. A version-ambiguous comparison and a period-misaligned comparison produce outputs that look like variance analysis and aren't. The recipe does not proceed past these checks until they resolve.

<!-- → [TABLE: Two-row table. Columns: Confirmation, What It Checks, Stop Condition if Unresolved. Rows: Forecast version (locked version exists predating period start — halt, require human confirmation of baseline version), Period alignment (all source data covers same period boundaries — halt, identify misaligned sources, require correction before proceeding). Caption: Version and period confirmation are not setup steps. They are the conditions under which the variance analysis is meaningful.] -->

---

## Building the Category Comparison

Once the forecast version and period are confirmed, the recipe computes the forecast-versus-actual difference for each cash flow category in the forecast structure.

The categories vary by organization, but the logic is the same: for every line in the forecast, find the corresponding actuals and compute the difference. Inflows (collections, financing proceeds, other receipts) are positive when actual exceeds forecast and negative when actual falls short. Outflows (payroll, vendor payments, tax, debt service) are positive when actual was less than forecast — meaning you spent less than expected — and negative when actual exceeded forecast.

The sign convention matters and needs to be stated explicitly in the recipe documentation. A cash flow analysis where positive and negative mean different things for inflows versus outflows is a source of persistent errors, especially when someone other than the original recipe author is reading the output.

The sum check is the first verification after the category comparison is built: the sum of all category variances should equal the total opening-to-closing variance. If it does not, something is wrong — a category was missed, a sign was flipped, a source file covered a different period than the others. The recipe flags a sum failure as a critical error and halts. There is no useful output from a bridge that doesn't add up.

<!-- → [TABLE: Example category comparison structure. Columns: Category, Forecast ($), Actual ($), Variance ($), Sign Meaning. Rows showing: Collections (inflow — positive variance = more cash than expected), Payroll (outflow — negative variance = more cash out than expected), Vendor payments (outflow), Tax disbursements (outflow), Financing activity (inflow/outflow), Other receipts (inflow). Bottom row: Total variance — sum check must equal opening forecast minus actual ending balance. Caption: The sign convention must be stated, consistent, and checked. A bridge that doesn't sum correctly is not a bridge.] -->

---

## Attaching Known Drivers

A category variance is a fact. A driver is the explanation for that fact. The recipe attaches drivers where they exist from known sources and leaves variances undriven where they don't.

Known drivers come from a narrow set of sources: the payroll register (which explains payroll variances to the dollar), the collections aging report (which explains collections variances by customer and invoice), the disbursement log (which explains vendor payment variances by transaction), the tax payment schedule (which explains tax disbursements), and any documented financing activity. These are structured sources — the recipe can match category variances to driver records mechanically, with amounts and references.

The matching works like reconciliation: a variance that can be fully explained by a single driver record closes cleanly. A variance that can be partially explained leaves a residual. A variance with no matching driver record stays entirely unexplained.

The driver attachment produces four states for each category variance. Fully explained: the driver source accounts for the full amount. Partially explained: the driver source accounts for some of the variance, and a residual remains. Timing: the variance appears to be a period-boundary effect — cash that was forecast in this period arrived in the next period or vice versa — based on dated transaction records. Unexplained: no driver source was found.

The timing category requires care. A timing classification is not a conclusion the recipe reaches on its own — it is a hypothesis based on dated records showing transactions near the period boundary. The recipe flags timing variances as "timing — verify" rather than "timing — confirmed." The treasury analyst confirms whether the transaction did in fact land in the adjacent period and whether it was a one-time occurrence or a systematic forecasting error.

<!-- → [DIAGRAM: Four-state classification for each category variance. State 1: "Fully explained" — driver source matches full amount, source reference attached. State 2: "Partially explained" — driver source matches partial amount, residual flagged. State 3: "Timing — verify" — dated transaction near period boundary, requires treasury confirmation. State 4: "Unexplained" — no driver source found, escalation required if material. Caption: Driver attachment produces four states. States 3 and 4 require human review before the variance is resolved.] -->

---

## The Unexplained Material Variance

The unexplained variance is the most important output of the bridge. It is what the recipe does not know — and the honest record of what it does not know is more valuable than a generated story to fill the gap.

The recipe applies a materiality threshold — set by the planning lead or treasury before the cycle begins — and flags any unexplained variance above the threshold as requiring escalation. The flag includes the amount, the category, the period, and the specific information that was checked and not found: "No driver record found in payroll register, disbursement log, or collections aging report. No period-boundary transaction identified."

That documentation is important. It is not just a flag — it is a record of the search. When the treasury analyst or FP&A lead investigates, they know exactly what the recipe already checked and can focus on what it didn't. If the investigation finds the explanation — a payment that was logged under the wrong category, a bank feed delay that caused a true timing difference — the finding is added to the bridge with source documentation and the unexplained variance closes. If the investigation doesn't find an explanation, the variance stays open.

An unexplained material variance that stays open is an escalation. It goes to the controller or CFO with full documentation: the bridge, the driver attachment results, the search log, and the conclusion that the variance cannot be explained from available sources. That is not a failure of the recipe. It is the recipe doing its job — surfacing what is real rather than papering over it.

The alternative — generating a plausible narrative for the unexplained variance — is not just intellectually dishonest. It is a control risk. The point of the variance bridge is to catch the things the forecast missed: timing errors, systematic forecasting biases, and, occasionally, duplicate payments or other transactional errors that would not surface without systematic comparison. A recipe that fills unexplained variances with stories is a recipe that reliably misses control failures.

<!-- → [TABLE: Unexplained variance escalation record structure. Columns: Variance ID, Category, Amount, Period, Sources Checked, Residual After Driver Attachment, Escalation Status. Example row: "CV-2024-Q4-07, Vendor payments, $183,400, Week of 2024-10-14, Disbursement log (v3), AP aging (2024-10-14), — No match found, — Escalated to Controller 2024-10-18." Caption: The escalation record documents the search, not just the gap. The investigator knows exactly what was checked.] -->

---

## The Forecast Revision Question

After the bridge is built and the drivers are attached, there is one question the recipe deliberately does not answer: should the forecast be revised?

The variance analysis tells you what happened and how much of it you can explain. It does not tell you whether the explanations are one-time or recurring, whether the forecast model has a systematic bias, or whether the business conditions that drove the variance are likely to persist. Those are judgments that require context the recipe does not have — knowledge of the business cycle, the customer relationship behind a large collections miss, the vendor negotiation that delayed a payment, the financing decision that shifted a draw date.

Treasury and FP&A make the forecast revision decision. The bridge gives them a clean surface to make it from: here is what changed, here is how much we can explain, here is what remains open. The decision about what to do with that information — revise the forecast, adjust the model, investigate further, accept the variance as one-time — belongs to the people who carry accountability for the forecast's accuracy and the organization's liquidity position.

The recipe prepares the surface. The treasury analyst or FP&A lead crosses the gate.

---

## What Would Change My Mind

If treasury systems maintained real-time cash flow actuals with transaction-level categorization that matched the forecast structure — and if that categorization were done at the point of transaction rather than after the fact — the driver attachment step would be much simpler. The variance would still need human review for materiality and forecast revision implications, but the unexplained population would be smaller because the categorization would be richer. The control value of the bridge — catching duplicate payments, surfacing systematic biases — would remain exactly the same.

## Still Puzzling

The timing category is the hardest to operationalize cleanly. A timing variance is a hypothesis: cash that was forecast in this period arrived in the adjacent period, or vice versa. Confirming it requires checking the adjacent period's actuals — which the recipe can do mechanically — but deciding whether the timing difference reflects a one-time event or a systematic forecasting error requires judgment about the business cycle. The line between "timing" and "the forecast is systematically wrong about when this cash moves" is consequential for forecast revision decisions, and the recipe cannot draw it. How do you build a bridge that makes the timing/systematic distinction visible to the human reviewer without overclaiming what the categorization means?

---

## Exercises

**Warm-up**

1. *(Low difficulty)* The weekly cash forecast was updated on Thursday afternoon, and the period being reviewed ends on Friday. Explain why the Thursday update cannot serve as the forecast baseline for the variance analysis, and what the recipe should do if no locked prior version exists. *What this tests: understanding of why version control is a prerequisite for meaningful variance analysis.*

2. *(Low difficulty)* A collections variance of negative $240,000 means actual collections were $240,000 less than forecast. A payroll variance of negative $240,000 means actual payroll was $240,000 more than forecast. Explain why the same sign can mean different things for inflow and outflow categories, and why the sign convention must be stated explicitly in the recipe documentation. *What this tests: understanding of the sign convention problem and its failure mode.*

3. *(Low difficulty)* After driver attachment, a vendor payment variance of $183,000 shows no matching record in the disbursement log, the AP aging report, or the period-boundary transaction search. What is the correct recipe output for this variance, and why is "likely a timing difference" not an acceptable classification? *What this tests: understanding of why unexplained variances must remain open rather than receiving plausible-but-unsourced classifications.*

**Application**

4. *(Medium difficulty)* Build a bridge structure for a company with the following cash flow categories: customer collections, payroll and benefits, rent and facilities, software subscriptions, debt service, and other. Specify the sign convention for each category, the driver source you would check for each, and the stop condition if the bridge does not sum to the total opening-to-closing variance. *What this tests: application of the bridge structure and sum check to a realistic category set.*

5. *(Medium difficulty)* A collections variance is partially explained: $180,000 of the $310,000 miss is matched to two large customers with documented payment delays in the collections aging report. The remaining $130,000 has no matching record. Write the driver attachment record for this variance, including the fully explained portion, the residual, and the escalation flag for the unexplained amount. *What this tests: application of the four-state driver classification to a partially explained variance.*

6. *(Medium difficulty)* A treasury analyst reviews the bridge and says: "The $130,000 collections residual is probably the Henderson account — they always pay late." Write a response explaining why "probably Henderson" is not an acceptable driver record and what the analyst would need to produce to close the residual. *What this tests: understanding that plausible explanations and sourced explanations are different things — and that the recipe's job is to require the latter.*

**Synthesis**

7. *(High difficulty)* A thirteen-week rolling forecast produces a new variance bridge every week. After eight weeks, you notice that collections variances are consistently negative — actual collections consistently fall short of forecast, by varying amounts and with varying explained/unexplained splits. Design a protocol for surfacing this pattern to FP&A for forecast model review: what data from the weekly bridges would you compile, how would you distinguish between one-time customer delays and a systematic forecasting bias, and what would the FP&A team need from the bridge history to make a model revision decision? *What this tests: integration of the week-level bridge analysis into a longer-term pattern recognition and escalation workflow.*

8. *(High difficulty)* The recipe flags an unexplained payroll variance of $47,000. The HR payroll team says the variance is because a supplemental payroll run processed late and will appear in next week's actuals. Evaluate this explanation: what would the recipe need to verify to move this from "unexplained" to "timing — verified," what sources would it check, and what would it do if the supplemental run does not appear in next week's actuals? *What this tests: application of the timing verification logic to a realistic resolution scenario — and the follow-through required to confirm that timing variances actually close.*

**Challenge**

9. *(Advanced)* The "Still Puzzling" section identifies the hardest operational problem in the bridge: distinguishing a one-time timing variance from a systematic forecasting error. Both look the same in a single week's bridge — cash that was forecast in one period arrived in an adjacent period. Design an analytical framework that makes this distinction visible across multiple periods: what signals in the bridge history would indicate systematic bias rather than one-time timing, how would you quantify the bias, and how would you present the finding to FP&A in a form that supports a model revision decision rather than just documenting the pattern? Address explicitly how the framework handles the case where the bias is real but the business condition that drives it is itself changing — meaning the right model correction is not simply "shift all collections by N days." *What this tests: ability to close the loop between variance analysis and forecast improvement — operationalizing the distinction the chapter identifies as genuinely unresolved.*
