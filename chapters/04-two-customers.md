# Chapter 4 — Two Customers
*Why every recipe that serves a machine must also serve a human — and why most serve neither.*

Here is a workflow that works perfectly and is completely useless.

An automated reconciliation script runs every night. It pulls the AP aging file, compares it to the payment ledger, flags mismatches above a threshold, and writes a structured JSON log: timestamps, source file versions, row counts, match rates, flagged line IDs. The log is clean. It is machine-readable. It can be re-ingested by another process, audited for completeness, and version-controlled. Every field is populated. Every run is reproducible.

The controller who owns the AP review has never opened it.

Not because the controller is negligent. Because the log was not written for the controller. It was written for the next process in a pipeline that was never built. What the controller needs is a sentence that says what was found, a number that says how large the mismatches are, a period label that confirms this is the right month, and a line that says who needs to act before payment runs. None of that is in the JSON.

Now here is the mirror failure. A different workflow runs before the monthly close commentary goes to the CFO. An analyst prompts a model with last month's actuals, and the model produces a polished four-paragraph memo: clear structure, confident language, specific numbers, plausible explanations. It looks finished. The CFO reads it and makes decisions.

The memo cannot be rerun. There is no source log. There is no record of which actuals file was used, which version, which period boundary. If a number in the memo is wrong — if the period was mislabeled, if the model inferred a driver that the renewal export contradicts — there is no way to reconstruct where the error entered. The memo is a one-way door. It went in as preparation and came out as a record, and no one knows how.

Both workflows failed. Not because AI was involved. Because neither recipe was designed for two customers.

---

## The Two Customers

Every finance recipe has two customers, whether it was designed that way or not.

The first customer is the agent: the automated process, the model, the script, the downstream system. The agent needs the recipe to be precise. It needs inputs specified as file paths with version labels, not descriptions. It needs steps that are deterministic — the same inputs should produce the same outputs every time. It needs schemas that define what a valid output looks like so the process can detect when something went wrong. It needs stop conditions that tell it when to halt rather than proceed on bad data. And it needs a log: a machine-readable record of what ran, what was consumed, what was produced, and what was flagged.

The second customer is the human reviewer: the controller, the CFO, the budget analyst who needs to decide whether the output is ready to go somewhere. The human reviewer needs something entirely different. They need to understand the purpose of the run without reading the code. They need to see the evidence — not the raw log, but a summary of what was found and how confident the recipe is in the finding. They need the caveats made explicit: what the recipe did not check, what it cannot conclude, where it stopped. They need the decisions named: what does the human need to do before this output can move forward? And they need the gates visible: who approves, and what does approval mean?

These two customers have genuinely different needs. A well-formed log entry — `{"flag_id": "AP-2847", "variance": 14200.00, "source": "aging_v3.csv", "period": "2024-Q3"}` — is exactly what the agent needs and nearly useless to the reviewer without translation. A paragraph that says "there were some mismatches in the AP aging this month, you should look at them" is approximately what the reviewer needs and useless to any downstream process that needs to act on specific line items.

Most recipes serve one customer accidentally and ignore the other entirely. The JSON log serves the machine that was never built. The polished memo serves the executive who can't trace it back to source.

<!-- → [DIAGRAM: Two-column visual. Left: "Agent Contract" — file path inputs, deterministic steps, output schema, stop conditions, run log. Right: "Human Report Card" — purpose statement, evidence summary, explicit caveats, decisions named, gate visible. Gap between them labeled "What most recipes skip." Caption: The two customers have genuinely different needs. Designing for one is not designing for both.] -->

---

## What the Agent Contract Requires

The agent contract is the specification layer of the recipe. It answers one question: can this run be reproduced?

Reproducibility in finance is not a technical nicety. It is the difference between a workpaper that supports a conclusion and a process that produced something once and cannot be asked what it did. When a number in a financial report is questioned — six months later, during audit, after a restatement — the question is always the same: where did this come from, and can you show me? A recipe that cannot answer that question is not a finance recipe. It is a shortcut that looks like a process.

The agent contract has five components. First, inputs: every source file specified by path, version or timestamp, and period label. Not "the AP aging file" — the AP aging file as it existed on the morning of October 3rd, version tagged, in the location the recipe expects. If the input changes, the run changes. The contract makes that visible.

Second, steps: the sequence of operations, specified precisely enough that a future maintainer can understand what the recipe did without running it. Not a narrative description — an actual record of what happened to the data.

Third, output schema: a definition of what a valid output looks like. Row count within expected range. Required fields populated. No nulls in the variance column. Period label matching the input period label. The schema is how the recipe knows when something went wrong before the output reaches a human.

Fourth, stop conditions: the list of states that cause the recipe to halt rather than produce output. Missing source file. Period mismatch. Row count outside expected range. Variance above a hard threshold that requires human review before the run can continue. Stop conditions are not error handling. They are the recipe's way of refusing to produce a misleading output when the inputs are not right.

Fifth, the run log: a machine-readable record of every input consumed, every transformation applied, every flag raised, every stop condition evaluated. The log is what makes the run auditable. It is also what makes the human report meaningful — the reviewer can see not just the conclusion but the basis for it.

<!-- → [TABLE: Five-row table. Columns: Component, What It Specifies, What Goes Wrong Without It. Rows: Inputs (source, version, period — ambiguous pulls from wrong version), Steps (deterministic sequence — unmaintainable, unreproducible), Output Schema (valid output definition — bad output reaches human undetected), Stop Conditions (halt criteria — recipe proceeds on bad data), Run Log (what ran and what was found — conclusion without basis). Caption: The agent contract is what makes a run auditable. Missing any component makes the run a black box.] -->

---

## What the Human Report Card Requires

The human report card is the translation layer. Its job is to make the run legible to someone who was not in the room when it ran and should not need to reverse-engineer the log to understand what to do.

The report card has five components that mirror the agent contract, but answer different questions.

Purpose: what was this recipe trying to find? One sentence. Not "AP aging reconciliation workflow" — "this run checks whether payments scheduled to process this week are supported by approved and reconciled AP records." The purpose tells the reviewer what they're evaluating and whether the scope matches what they need.

Evidence summary: what did the recipe actually find? Not the raw log — a translation of the log into terms the reviewer can evaluate. "The run flagged fourteen line items with variances above the threshold. Twelve are timing differences within the expected range for this vendor. Two are unreconciled items totaling $28,400 that require owner confirmation before the payment batch runs." That is evidence. "See attached JSON" is not.

Caveats: what did the recipe not check, and what can it not conclude? This is the component most recipes omit, and its absence is where the fluency trap enters the human report. Every recipe has scope limits. It checked the AP aging against the payment ledger; it did not check the underlying invoices against the purchase orders. It compared this month's actuals to last month; it did not evaluate whether the period boundary is consistent with how the business closes. The caveats make those limits visible so the reviewer can decide whether the scope was sufficient for the decision they're making.

Decisions: what does the human need to do before this output moves forward? This is where the recipe acknowledges its own limits. Not "the output is ready" — "the two unreconciled items need owner confirmation from the AP manager before the payment batch can run." The decision is named, the owner is named, and the next step is unambiguous.

Gate: who approves, and what does approval mean? The gate is the moment when an accountable human looks at the evidence summary, evaluates whether the caveats are acceptable, confirms that the decisions have been addressed, and decides the output is ready to move. Without a named approver and a defined gate, "ready" is a state that happens by default — someone copies the output forward because it looks finished, and no one has actually decided it was.

<!-- → [TABLE: Five-row table. Columns: Component, What It Answers, Example. Rows: Purpose (what was this trying to find — "checks whether payments are supported by reconciled AP records"), Evidence Summary (what did it find — "fourteen flags, two unreconciled items totaling $28,400"), Caveats (what it didn't check — "invoices not checked against POs"), Decisions (what the human must do — "AP manager confirms two items before batch runs"), Gate (who approves and what that means — "Controller signs off: evidence adequate, caveats acceptable"). Caption: The human report card is not a summary of the log. It is a translation that makes the run legible to someone who carries accountability for the conclusion.] -->

---

## Why Most Recipes Serve Neither

If the two-customer design is straightforward — agent contract here, human report card there — why do most recipes fail to serve either customer?

The agent contract fails because the recipe was written for human readers, not for machines. The inputs are described in plain language ("use the latest AP file") rather than specified as paths and versions. The steps are narrative ("compare the files and flag big differences") rather than deterministic. There is no output schema, so bad output reaches the human undetected. There are no stop conditions, so the recipe runs on malformed inputs and produces something that looks like an output but isn't grounded in valid data. There is no log, so the run is invisible to any future reviewer.

The human report card fails because the recipe was written for machines, not for human readers. The output is a JSON file with field names that require domain knowledge to interpret. The caveats are implicit in the code rather than stated in the report. The decisions are not named — the reviewer is expected to read the log and decide what it means for the business. The gate is not defined.

There is a third failure mode that is subtler and more common: the recipe was written for the person who built it, not for either customer. The builder knows what the inputs mean, knows the scope limits, knows what the output is supposed to do. That knowledge is not in the recipe. When the builder moves to a different role, or the recipe runs six months later, or someone else needs to audit the run, the knowledge is gone. What remains is a process that produces output and a report that looks finished, and no way to connect them.

This is the maintainability problem, and it is where the two-customer design pays off in ways that are not immediately obvious. A recipe designed for two customers is also, necessarily, designed for a future maintainer. The agent contract documents the run in enough detail that someone else can reproduce it. The human report card explains the purpose and scope in enough detail that someone else can evaluate it. The two-customer design is not just about the current run. It is about whether the work survives the person who built it.

<!-- → [DIAGRAM: Three-column visual showing three recipe types. Left: "Written for machines" — full agent contract, no human report, log readable by no reviewer. Center: "Written for humans" — polished output, no agent contract, irreproducible. Right: "Written for the builder" — implicit knowledge, neither customer served when builder leaves. Arrow pointing down from all three to: "Both customers unserved." Caption: The three failure modes all share a common cause: the recipe was not designed with a second customer in mind.] -->

---

## The Two-Customer Recipe Note

The practical tool that makes this design visible is the two-customer recipe note. It is not the recipe itself. It is the annotation layer — the document that travels with the recipe and makes both customers legible.

The note has two sections. The first is the agent contract summary: inputs (file paths, versions, periods), the output schema in plain terms, the stop conditions listed as a checklist, and a pointer to the run log. The second is the human report card: purpose, evidence summary, caveats, decisions, and gate.

The note is written before the recipe runs the first time, not after. This is not a documentation-after-the-fact exercise. Writing the note before the run forces clarity about what the recipe is supposed to do, what counts as valid output, who the reviewer is, and what the reviewer will need to know. If those questions cannot be answered before the run, the recipe is not ready to run.

The note is also the artifact that gets reviewed at the gate. The approver reads the purpose: does this scope match what I need to decide? The approver reads the evidence summary: does this finding reflect what the run actually found? The approver reads the caveats: are these limits acceptable for this decision? The approver reads the decisions: have the named actions been completed? If the answer to any of those questions is no, the gate does not open.

<!-- → [TABLE: Two-section table representing a sample two-customer recipe note. Section 1 (Agent Contract): Input — "AP_aging_2024-Q3_v2.csv, pulled 2024-10-03 06:00 UTC"; Output Schema — "flags table, required fields: flag_id, variance, source_line, period, threshold_used"; Stop Conditions — "halt if source file missing, period mismatch, or row count < 50"; Log pointer — "/logs/ap-recon-2024-Q3-run-001.json." Section 2 (Human Report Card): Purpose — "checks whether payments scheduled for 2024-10-04 batch are supported by reconciled AP records for Q3"; Evidence — "14 flags; 12 timing differences within range; 2 unreconciled items totaling $28,400"; Caveats — "invoices not checked against POs; threshold set at $5,000, not audited"; Decisions — "AP manager confirms two items before batch"; Gate — "Controller: evidence adequate, caveats acceptable, decisions complete." Caption: The two-customer recipe note is written before the run, not after. It is the artifact reviewed at the gate.] -->

---

## The Accountability Thread

There is a reason the two-customer design matters beyond workflow hygiene. Finance artifacts affect things that matter — payments, reports, disclosures, decisions with real consequences. When those artifacts are wrong, someone needs to be accountable. And accountability requires a thread: a chain from the conclusion back to the evidence, from the evidence back to the source, from the source back to the run.

The agent contract is what makes the thread traceable. The human report card is what makes the thread legible. The gate is what makes the thread accountable — the moment when a human looks at the thread and decides it is solid enough to support the conclusion.

A recipe that produces a polished output without an agent contract has no thread. A recipe that produces a perfect log without a human report card has a thread no one can read. A recipe without a gate has a thread that never reached an accountable human.

The two-customer design is not a complexity tax. It is the minimum structure required for a finance recipe to be useful in the way that finance work needs to be useful: not just accurate in this run, but defensible in the next review, reproducible for the next maintainer, and accountable to the human who carries responsibility for the conclusion.

Mycroft's finance rule holds: automate the preparation layer, preserve the accountable layer. The two-customer recipe is how you build a preparation layer that is worth preserving.

---

## What Would Change My Mind

If the tools that generate finance recipes also generated agent contracts and human report cards automatically — if the scaffolding came with the workflow rather than requiring a separate documentation step — the friction of the two-customer design would drop significantly. The failure mode would shift from "no one built the report card" to "the generated report card is wrong about scope or caveats," which is a narrower and more tractable problem. The design principle would still hold; the effort to apply it would be lower.

## Still Puzzling

The two-customer recipe note is clear as a structure. What is less clear is how to calibrate the evidence summary — how much translation is enough, and when does translating the log for the reviewer start to introduce the same interpretive gap that the raw log avoided? There is a real tension between "legible to the reviewer" and "faithful to what the run actually found," and the right balance probably depends on the reviewer's domain knowledge and the consequence of the decision. That calibration is currently implicit in practice.

---

## Exercises

**Warm-up**

1. *(Low difficulty)* Given a recipe described as "pulls Q3 receivables, compares to prior quarter, flags items over $10,000," identify what is missing from the agent contract (inputs not specified, no output schema, no stop conditions, no log) and what is missing from the human report card (no purpose, no caveats, no decisions, no gate). *What this tests: recognition of the two-customer components in a realistic recipe description.*

2. *(Low difficulty)* Write a one-sentence purpose statement for each of these three recipes: (a) a monthly AP aging reconciliation, (b) a budget vs. actuals variance analysis, (c) a duplicate payment detection scan. *What this tests: ability to state recipe purpose in reviewer-legible terms rather than technical process descriptions.*

3. *(Low difficulty)* For the AP reconciliation scenario in this chapter, list three stop conditions the recipe should have. Explain what would happen without each one. *What this tests: understanding of stop conditions as a mechanism for preventing bad output from reaching a human.*

**Application**

4. *(Medium difficulty)* Take a workflow you know or can describe — a reconciliation, a close process step, a variance report — and write the agent contract summary for it: inputs (path, version, period), output schema, stop conditions, log pointer. *What this tests: application of the agent contract structure to a realistic finance workflow.*

5. *(Medium difficulty)* For the same workflow, write the human report card: purpose, evidence summary (hypothetical but specific), caveats, decisions, gate. *What this tests: translation from agent contract terms to reviewer-legible terms for the same workflow.*

6. *(Medium difficulty)* A colleague argues: "The run log is the evidence summary — reviewers should just read the log." Write a response that explains why this argument fails and what the log cannot do for a human reviewer. *What this tests: understanding of why translation between machine output and human legibility is a design requirement, not a documentation preference.*

**Synthesis**

7. *(High difficulty)* A finance team has been running a monthly close workflow for two years. The analyst who built it has left. No two-customer recipe note exists. Design a process for reconstructing one: how do you recover the agent contract from what was built, and how do you construct the human report card from institutional knowledge and current reviewer needs? *What this tests: application of the two-customer framework to a reverse-engineering scenario — what the framework reveals about what was never documented.*

8. *(High difficulty)* The two-customer design adds documentation effort to every recipe. A manager argues that for low-stakes, routine workflows, the overhead is not worth it. Evaluate this argument: under what conditions, if any, is a single-customer recipe acceptable in finance work? What criteria would you use to make that judgment, and what risks does a single-customer recipe introduce even in low-stakes contexts? *What this tests: ability to apply the two-customer principle with calibration rather than as a blanket rule — and to identify where the threshold is.*

**Challenge**

9. *(Advanced)* The "Still Puzzling" section identifies a real tension: translating the run log for the reviewer risks introducing interpretive gaps, but leaving the raw log for the reviewer sacrifices legibility. Design a protocol for calibrating evidence summary depth based on (a) the reviewer's domain knowledge, (b) the consequence of the decision the output supports, and (c) the reversibility of the action the output authorizes. What would a tiered evidence summary look like across three consequence levels — routine, material, disclosure-supporting? *What this tests: ability to operationalize the calibration problem the chapter leaves open, producing a workable standard rather than a theoretical framework.*
