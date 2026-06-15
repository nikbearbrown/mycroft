# Chapter 3 — The Verified Finance Data Contract

*The numbers might be right. The problem is nobody can prove it.*

Here is a board packet. Three pages, clean formatting, gross margin at 61%, cash runway at fourteen months, a hiring-plan variance of negative $340,000. The CFO presents it with confidence. The board asks a few questions. Everyone nods.

Now ask a different question: which export produced those numbers?

Silence. Or, worse, a long pause and then a vague gesture toward "the model." Which version of the model? The one from Tuesday or the one someone updated Thursday morning? Which period — calendar Q3 or fiscal Q3? Which entity — the consolidated parent or just the operating subsidiary? Did anything get reclassified between the last close and this export?

Nobody knows.

This is not a failure of effort. The finance team worked hard on that packet. It is a failure of something more subtle — a failure of provenance. The preparation work happened, but the evidence trail didn't. And once you lose the thread between a number and its source, you cannot defend the number. You can only assert it.

The verified finance data contract is the discipline that closes that gap. It is not complicated. It is, in fact, almost embarrassingly simple once you see it. But it requires holding a distinction that modern AI tools are very good at blurring: the difference between a fluent summary and a defensible record.

---

## What Evidence Actually Means in Finance

Feynman had a habit of asking what words actually meant before accepting them as explanations. So let's ask that here. What does "evidence" mean in a finance context?

The Public Company Accounting Oversight Board's Auditing Standard 1105 defines audit evidence as information that helps auditors reach conclusions about the financial statements. The standard is specific about what qualifies: source documents, records of transactions, confirmations, reconciliations, physical inspection, reperformance. It is not a list that includes "model output" or "AI-generated summary." It is a list that points, consistently, to traceable sources with identifiable owners and verifiable integrity.

The word "verifiable" is doing real work there. A number is verifiable if someone — a different person, later, with access to the same sources — could reproduce it. That means the number's path has to be documented: where it came from, what period it covers, who owns the source, what transformations were applied, what the control total was, when the source was last refreshed.

Without that path, you have an assertion. An assertion can be correct. It can even be useful. But it is not evidence. And in finance — where the artifacts produced affect reporting, cash, controls, compliance, and the trust of external parties — the difference between a correct assertion and defensible evidence is the difference between a number you can stand behind and a number you are standing in front of.

![A two-column comparison: an assertion column listing a fluent summary, model output, and missing source, version, and owner, beside an evidence column listing source file, period, entity, version, owner, control total, and logged transformation.](images/03-the-verified-finance-data-contract-fig-01.png)
*Figure 3.1 — Assertion versus evidence: the contract is what converts the left column into the right.*

<!-- → [DIAGRAM: Two-column diagram showing "Assertion" vs. "Evidence" — left column lists: fluent summary, model output, no source path, no version, no owner; right column lists: source file, period, entity, version, owner, control total, logged transformation. Caption: the contract is what converts the left column into the right.] -->

---

## The Preparation Layer and the Accountable Layer

Here is the central distinction in this chapter, stated plainly: AI can reliably automate the preparation layer. It cannot substitute for the accountable layer. And the crucial discipline is keeping those two layers from collapsing into each other.

The preparation layer is everything that happens before judgment. Tracing a file path. Comparing schemas across two exports. Identifying missing fields. Flagging a version mismatch. Checking whether a control total reconciles. Pulling the last-modified timestamp on a source file. None of this requires professional judgment. It requires accuracy, consistency, and patience — which are exactly the things AI tools are good at and humans are not.

The accountable layer is everything after. Is this evidence adequate for the decision it supports? Is the variance material? Does the classification reflect the right accounting treatment? Should this go to the board? These questions have the same structure: they ask not just what the data says but whether the data is sufficient, and that sufficiency judgment belongs to a human who can be held responsible for it.

The failure mode is when preparation crosses into judgment without anyone noticing. An AI model generates a fluent paragraph explaining a variance. The paragraph sounds like analysis. It reads like analysis. It gets pasted into the board packet without a gate — without anyone asking whether the underlying data is actually sound, whether the interpretation is defensible, whether the source trail exists. The model is not wrong to produce the paragraph. The error is treating the paragraph as evidence when it is not.

Mycroft's finance rule makes this concrete: automate the preparation layer, preserve the accountable layer. The rule sounds obvious. The practice is harder, because fluent output creates the illusion of completion.

---

## What a Data Contract Contains

A data contract is a structured record of where a number came from and who is responsible for it. The minimum elements are not arbitrary — they are the fields that make verification possible.

**Source** is the specific file or system the data came from. Not "the accounting system" but the path, the export name, the table. If you cannot name the source, you cannot verify the number.

**Period** is the date range the data covers. Gross margin for Q3 means nothing without knowing whether that is calendar Q3 or fiscal Q3, and whether it is actuals, accruals, or estimates.

**Entity** is which legal or operating entity the data represents. A holding company with three subsidiaries produces at least four versions of most financial metrics — one per subsidiary and one consolidated. Which one?

**Version** is which instance of the source file or export was used. Files get updated. Exports get regenerated. The version field is how you distinguish the Tuesday export from the Thursday one.

**Owner** is the human who is responsible for the accuracy of the source. Not the AI tool that processed it. Not the model that summarized it. The accountable person.

**Freshness** is when the source was last updated, and whether that recency is adequate for the decision. A cash balance from six days ago may be fine for a quarterly review. It is not adequate for a wire authorization.

**Schema** is the structure of the data — what fields exist, what they mean, what units they are in. A schema comparison between two exports is often how you catch the silent reclassification that makes a variance look like performance.

**Control total** is the checksum that confirms the data arrived intact. If you pulled 10,000 transaction records and the source system shows 10,000, that match is evidence of integrity. If it shows 10,014, something happened in transit.

**Transformation** is a log of every operation applied to the data between source and report. Filters, aggregations, joins, reclassifications, currency conversions. Each one is a step where an error can enter and a step that needs to be reproducible.

**Log** is the machine-readable record of what the AI agent did. Not a summary. Not a paragraph. A structured record, replayable, that shows exactly which operations were performed in which order.

**Report** is the human-readable output produced for review. Useful for decision support. Not itself evidence — it is a surface for judgment, not a replacement for it.

**Approval record** is the gate: who reviewed the work, what they confirmed, and when. This is the moment the accountable layer takes ownership of what the preparation layer produced.

| Field | What it contains | Why it matters for verification |
|---|---|---|
| Source | The specific file, system, export, or table | Without a named source, the number cannot be reproduced |
| Period | The exact date range covered | Distinguishes calendar from fiscal, actuals from accruals |
| Entity | The legal or operating entity | A parent and its subsidiaries produce different numbers |
| Version | Which instance of the export was used | Separates the Tuesday pull from the Thursday one |
| Owner | The human responsible for the source's accuracy | Locates accountability with a person, not a tool |
| Freshness | When the source was last updated | Tests whether recency is adequate for the decision |
| Schema | The structure, fields, meanings, and units | Catches silent reclassifications that masquerade as performance |
| Control total | The checksum confirming data arrived intact | A row-count or sum match is direct evidence of integrity |
| Transformation | A log of every operation applied | Each step is reproducible and a place an error can enter |
| Log | The machine-readable record of agent actions | Replayable proof of what was done, in what order |
| Report | The human-readable output for review | A surface for judgment — useful, but not itself evidence |
| Approval record | Who reviewed, what they confirmed, and when | The moment the accountable layer takes ownership |

*Table 1 — The data contract field inventory. Every field is a verification handle; missing fields are missing accountability.*

![An inventory diagram of twelve data-contract fields — source, period, entity, version, owner, freshness, schema, control total, transformation, log, report, approval record — arranged as labeled cells, each a handle on verification.](images/03-the-verified-finance-data-contract-fig-02.png)
*Figure 3.2 — The data contract field inventory: each field is a handle the next reviewer can grab.*

---

## The Recipe That Stops at the Right Place

A useful finance recipe has a shape. It is narrow — it covers a defined scope, a specific period, a particular entity. It is source-bound — every output traces to a named file with a version and a timestamp. It is reviewable — the log is legible to the human who has to sign off on it. And it stops.

That last part is where most recipes fail. A recipe that prepares a variance analysis and then offers a causal explanation has crossed the line. A recipe that checks control totals and then recommends an accounting treatment has crossed the line. The recipe's job is to produce a clean, documented work surface. The finance human's job is to evaluate whether that surface is adequate and to make the judgment call.

The scope parameters that make a recipe trustworthy are simple to state. What period is allowed? What entities are in scope? What source systems can the recipe read? What actions can it take — can it write files, or only read them? What are the stop conditions — the situations where the recipe halts and waits for a human before proceeding?

A recipe with clear scope parameters is a recipe that can be supervised. A recipe that reaches beyond its scope — that decides its own entity coverage, that generates its own period definitions, that takes action on data without a gate — is a recipe where the accountable layer has been hollowed out without anyone explicitly deciding to hollow it out.

![A boundary diagram: preparation-layer tasks (file tracing, schema comparison, control total check, version logging, report generation) on the left, separated by a vertical gate from accountable-layer tasks (materiality, adequacy, treatment, release) on the right.](images/03-the-verified-finance-data-contract-fig-03.png)
*Figure 3.3 — The recipe boundary: the recipe stops at the gate; the finance professional crosses it.*

<!-- → [DIAGRAM: Recipe boundary diagram — left side shows "preparation layer" tasks: file tracing, schema comparison, control total check, version logging, report generation; right side shows "accountable layer" tasks: materiality judgment, adequacy assessment, accounting treatment, release decision; a vertical gate line separates them with the label "human approval required before crossing." Caption: the recipe stops at the gate; the finance professional crosses it.] -->

---

## Three Questions for Supervision

Supervising an AI finance agent is not a vague instruction to "check the work." It is a structured inquiry with three specific questions.

The first question is scope: what period, entity, source system, and action space is the agent operating in? If you cannot answer this question precisely, you cannot supervise the agent. You are hoping it stays within appropriate limits rather than verifying that it does.

The second question is approval: who clears the gate before the output moves forward? This question identifies the accountable human and the specific moment when the preparation layer hands off to the accountable layer. If there is no named person and no defined gate, the handoff is informal, which means it may not happen at all.

The third question is verification: what source, control total, or owner confirmation would make this finding defensible? This question forces the supervisor to think concretely about what evidence would be required if someone challenged the output. If the answer is "the model said so," the output is not yet verified.

These three questions are a gate, not a checklist. The gate exists to prevent fluent output from moving forward without scrutiny. The model is very good at producing fluent output. Fluency is not a proxy for accuracy, and accuracy is not a proxy for adequacy.

---

## Where the Boundary Lives

The evidence boundary in finance is not a philosophical line. It is a practical one, defined by what would happen if the output were wrong.

Verified evidence — source files, versions, periods, owners, control totals, support paths, logged transformations — is what you defend with when someone asks how you got the number. You can point to it. You can reproduce it. You can show your work.

Model judgment — classification suggestions, language drafts, anomaly labels — is useful as a starting point. A model that flags a transaction as potentially miscategorized is doing real work. But the model does not decide whether the transaction is miscategorized. The finance human does, based on the actual accounting standards, the actual facts of the transaction, and the actual materiality of the difference. The model's flag is a prompt for judgment, not a substitute for it.

Human judgment is everything downstream of evidence: materiality assessments, causal explanations, accounting treatments, release decisions, external filings, investor communications. None of these can be delegated to a recipe. All of them depend on a person who understands the context, is accountable for the outcome, and has the professional standing to make the call.

The reason this boundary matters is not theoretical. Finance artifacts affect things that are real: cash flows in and out of accounts, financial statements that external parties rely on, regulatory filings that have legal weight, investor communications that affect trust and capital. A generated artifact that looks like evidence but is not traceable to source is a risk that does not announce itself as a risk. It announces itself as a clean, formatted output that someone forgot to verify.

| Layer | What it contains | Who is responsible | What makes it adequate |
|---|---|---|---|
| Verified evidence | Source files, control totals, logs, support paths | Preparation layer (AI-assisted) | Traceability and reproducibility |
| Model judgment | Classification suggestions, language drafts, anomaly flags | The AI agent | Usefulness as a prompt, not as a conclusion |
| Human judgment | Materiality, treatment, release, filing | The accountable finance professional | Professional standing and accountability |

*Table 2 — The three-layer evidence taxonomy. The contract governs the first layer; supervision governs the transitions between layers.*

---

## The Provenance Note

The assessment artifact for this chapter is a provenance note. Not a financial analysis. Not a variance report. A record that documents the source, period, entity, version, owner, stop conditions, and at least one human gate for a single finance dataset you actually work with — or a sanitized sample if the real data is confidential.

The provenance note is deliberately narrow. Its purpose is to demonstrate that you can apply the contract vocabulary to a real situation. A complete provenance note for a thin or incomplete dataset is more valuable than a confident-sounding note for a well-documented one. If the data is thin, the note should say so, explicitly, with a clear statement of what would be needed to make the source adequate for the decision it is meant to support.

This is the Feynman move: say what you know, say what you don't know, and do not blur the line between them. A finance professional who can write an honest provenance note is a finance professional who has internalized the contract. The contract is not a form to fill out. It is a habit of mind — a refusal to let preparation masquerade as judgment, and a refusal to let fluent output substitute for traceable evidence.

---

## What the Gate Actually Does

A phase gate is not a bureaucratic hurdle. It is the structural mechanism that keeps the preparation layer and the accountable layer separate. Without a gate, the model's output flows directly into the decision surface. With a gate, the output stops, waits, and is evaluated by someone who is accountable for what happens next.

The gate asks one question: is this work surface adequate for the decision it supports? Not "is it plausible" or "does it look right." Adequate. Meaning: if this decision later turns out to be wrong, is there a defensible evidence trail that shows the decision was made on reasonable grounds?

AI cannot answer that question. The model cannot assess its own adequacy. It can check whether the required fields exist. It can flag missing versions. It can compare control totals. It can produce a log. But it cannot decide whether the work is good enough, because "good enough" is a judgment about the stakes of the decision, the standards of the profession, and the sufficiency of the evidence for those stakes. That judgment requires a human.

The gate is where the recipe ends and the finance professional begins. It is not a formality. It is the point of the whole system.

![A linear flow from source files through AI preparation to a gate where a human checks scope, approval, and verification, then on to the accountable layer; a stop-condition branch loops back to preparation while an adequate path continues right.](images/03-the-verified-finance-data-contract-fig-04.png)
*Figure 3.4 — The phase gate flow: the gate is not overhead — it is what makes automation trustworthy.*

<!-- → [DIAGRAM: Phase gate flow — linear sequence: source files → AI preparation (tracing, schema check, control total, log) → gate (human reviews: scope confirmed? approval identified? verification possible?) → accountable layer (materiality, treatment, release). Gate shown as a vertical bar with "stop conditions" branching left back to preparation and "adequate" continuing right to accountable layer. Caption: the gate is not overhead — it is the mechanism that makes automation trustworthy.] -->

---

The board packet with gross margin at 61% and cash runway at fourteen months might be exactly right. The numbers might trace cleanly to the right export, the right period, the right entity, the right version. The control totals might match. The owner might be named. The gate might have been crossed by the right person at the right moment.

Or none of that might be true, and the packet might still look exactly the same.

The data contract is how you tell the difference. Not by reading the numbers. By reading the trail.

---

## Exercises

**Warm-up**

1. *Difficulty: Low* — Name the eleven fields of a data contract and give a one-sentence explanation of why each field is necessary for verification. Which field would you check first if you suspected a number had changed between Tuesday and Thursday?
*What this tests: recall of the contract vocabulary and understanding of why each field is a verification handle, not just a label.*

2. *Difficulty: Low* — A colleague hands you a gross margin figure and says it came from "the model." Using the preparation layer / accountable layer distinction, explain what is missing and what would need to be supplied before you could treat the number as evidence.
*What this tests: ability to apply the core two-layer distinction to a realistic workplace scenario.*

3. *Difficulty: Low* — State the three supervision questions for an AI finance agent. For each, write one sentence explaining what goes wrong if that question is never asked.
*What this tests: retention of the supervision framework and understanding of its failure modes.*

**Application**

4. *Difficulty: Medium* — A recipe pulls revenue data from an accounting export, computes a period-over-period variance, and then generates a paragraph explaining why the variance occurred. Identify exactly where the recipe crossed from the preparation layer into the accountable layer, and rewrite the recipe's scope so that it stops at the right place.
*What this tests: ability to locate the boundary violation in a realistic recipe description and correct it.*

5. *Difficulty: Medium* — You are reviewing a provenance note for a cash-runway figure used in a board presentation. The note includes source path, period, entity, and a control total. It does not include version, owner, or transformation log. Write the two sentences you would add to the note to flag these gaps, following the chapter's standard for intellectual honesty about thin data.
*What this tests: ability to produce an honest provenance note that names what is missing rather than papering over it.*

6. *Difficulty: Medium* — A control total check shows that 10,014 transaction records arrived from the source system but only 10,000 were processed by the recipe. Write the stop condition you would add to the recipe, and describe what a human reviewer would need to confirm before the output could proceed.
*What this tests: application of the control total concept to a concrete discrepancy and ability to design a gate response.*

**Synthesis**

7. *Difficulty: High* — A finance team uses an AI agent to prepare monthly close packages. The agent traces source files, checks control totals, flags schema mismatches, and produces a formatted report. A senior accountant reviews the report and approves it for distribution. Using all three evidence layers (verified evidence, model judgment, human judgment), map each activity to its layer and identify any activity in the description that is ambiguous — where the layer assignment is unclear and why.
*What this tests: ability to apply the three-layer taxonomy to a full workflow and to identify ambiguity rather than forcing false clarity.*

8. *Difficulty: High* — The chapter argues that "fluent output creates the illusion of completion." Choose a specific finance task — budget variance analysis, accounts receivable aging, or cash flow reconciliation — and construct a scenario in which fluent AI output advances to decision use without passing through a gate. Then redesign the workflow with an explicit gate, naming the scope parameters, the approval owner, and the verification standard.
*What this tests: integration of the preparation/accountable distinction, the gate mechanism, and the three supervision questions into a designed workflow.*

**Challenge**

9. *Difficulty: Advanced* — PCAOB Auditing Standard 1105 defines audit evidence but was written before AI-generated outputs existed as a category of finance artifact. The chapter treats AI output as non-evidence by default. Construct the strongest counterargument: under what conditions, if any, could a logged, reproducible AI output meet the standard's implicit criteria for evidence? What would need to be true about the log, the transformation record, and the approval chain? Then evaluate your own argument — does it hold, or does it dissolve under scrutiny?
*What this tests: ability to engage with the chapter's most contestable empirical and professional claim, reason from the underlying standard rather than the chapter's summary, and apply the intellectual honesty norm to your own argument.*

---

## Prompts

### Figure 3.1 — Assertion versus evidence
**Files:** images/03-the-verified-finance-data-contract-fig-01.svg · d3/03-the-verified-finance-data-contract-fig-01.html
**Prompt:** A brutalist two-column comparison on white — an assertion column of unsupported claims (fluent summary, model output, no source, no version, no owner) beside an evidence column (source, period, entity, version, owner, control total, logged transformation) — joined by a single red arrow labeled "contract." Hairline borders, one red accent for the arrow.

### Figure 3.2 — The data contract field inventory
**Files:** images/03-the-verified-finance-data-contract-fig-02.svg · d3/03-the-verified-finance-data-contract-fig-02.html
**Prompt:** A brutalist grid of twelve monospaced data-contract field cells on white — source, period, entity, version, owner, freshness, schema, control total, transformation, log, report, approval record — neutral fills with the approval-record cell outlined in red as the gate field. JetBrains Mono labels, one red accent.

### Figure 3.3 — The recipe boundary
**Files:** images/03-the-verified-finance-data-contract-fig-03.svg · d3/03-the-verified-finance-data-contract-fig-03.html
**Prompt:** A brutalist boundary diagram on white — a preparation-layer column of recipe tasks on the left, a tall red gate down the middle, and an accountable-layer column of judgment tasks on the right — with neutral arrows entering and leaving the gate. Hairline borders, single red accent for the gate.

### Figure 3.4 — The phase gate flow
**Files:** images/03-the-verified-finance-data-contract-fig-04.svg · d3/03-the-verified-finance-data-contract-fig-04.html
**Prompt:** A brutalist left-to-right flow on white — source files, AI preparation, a red gate carrying three checks (scope, approval, verify), then the accountable layer — with a dashed neutral stop-condition loop returning to preparation. Inter labels, JetBrains Mono annotations, one red accent for the gate.
