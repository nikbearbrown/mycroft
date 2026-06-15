# Chapter 2 — The Reallocation Principle
*Why saving time is only half the problem.*

There is a moment in every analyst's week that nobody puts on the agenda: the moment you realize the number you defended in a meeting came from somewhere you didn't fully check. The deck looked right. The formula was tidy. The AI drafted the summary and the summary read like something a person would write. And then someone asked where the $2.3 million variance came from, and you didn't quite know.

This is not a story about AI making a mistake. It is a story about what happened to the three hours you saved.

Here is the thing about automation in finance work that I think gets missed: the problem is not that the recipe ran. The problem is what the recipe was supposed to make room for, and whether that room got used. Execution gets cheaper; review, if you're not careful, gets shorter. Those two things are moving in opposite directions. The analyst spends less time building the report and, freed from that effort, spends the same meeting doing something that looks like review but has the attention span of someone who just coasted.

I want to work through why that happens, what the correct structure looks like, and what it actually means to reallocate effort rather than simply eliminate it.

---

## The Two Layers in Any Finance Workflow

Take a recurring finance task — a variance analysis, a period-end close, an accounts receivable aging, a budget-versus-actual report. If you slow down and inventory what actually happens, step by step, you will find that the work has two distinct textures.

The first texture is mechanical. Someone pulls data from a system. Someone checks that the pull landed cleanly. Someone formats a table, compares this period to last, flags anything over a threshold. These steps can be described precisely. They follow rules. They do not require a professional judgment about what the result means; they require careful execution of a defined procedure. This is the preparation layer.

The second texture is different. Someone looks at the flagged variance and decides whether it is material. Someone explains why revenue came in below forecast — not just that it did, but what drove it, whether it is transient or structural, what it means for the quarter. Someone decides whether the draft accounting treatment is correct. Someone signs off before the artifact moves forward: before it goes to a manager, before it enters a report, before it touches anything external. This is the judgment layer, and it belongs to a person with a name attached.

The distinction matters because finance artifacts are not neutral. A variance report can affect how a business allocates resources. An accounts receivable aging affects credit decisions. A budget-versus-actual lands in front of people who will make plans based on what it says. Getting the preparation layer wrong produces a flawed surface for judgment. Letting the AI cross into the judgment layer without a gate produces something more dangerous: a professional output without professional accountability.

![A vertical two-layer stack: a preparation layer of five nodes below a judgment layer of four nodes, separated by a heavy human gate, with AI arrows moving freely below the gate and one arrow stopping at it.](images/02-the-reallocation-principle-fig-01.png)
*Figure 2.1 — The two layers and the human gate: AI operates freely in preparation and stops at the gate.*

<!-- → [DIAGRAM: Two-layer stack — preparation layer (data pull, normalization, comparison, formatting, threshold flagging) below judgment layer (materiality, causal explanation, accounting treatment, release decision) — separated by a visible gate labeled "human gate"; arrows show AI operating freely below the gate and stopping at it] -->

---

## Why the Boundary Keeps Getting Crossed

Here is the subtle thing. The preparation layer and the judgment layer do not announce themselves with different typefaces. A well-written AI summary looks like a professional assessment. A generated anomaly label looks like a finding. When the output is clean and confident, it is genuinely easy to mistake execution for analysis.

I think this is the core cognitive hazard of language models in finance work, and it is worth being precise about it. The model produces language that has the shape of judgment — it names a variance, it offers a plausible explanation, it writes in the register of a finance professional — but it does not have the thing that makes judgment valuable: accountability, domain knowledge grounded in this specific business, and the ability to be responsible for what happens next.

Consider what the BLS describes as the actual work of a financial analyst: reviewing financial statements, monitoring budget performance, analyzing financial data to produce forecasts, preparing reports for management. And for accountants and auditors: examining financial records, computing amounts owed, maintaining financial records, ensuring accuracy and compliance. The preparation work in these descriptions — data review, period comparison, report preparation — is exactly what a well-designed recipe can accelerate. The judgment work — adequacy, accuracy, compliance, treatment — is exactly what a recipe cannot replace.

The failure mode is not the model generating wrong text. The failure mode is a person treating generated text as though it passed through the judgment layer when it only passed through the preparation layer.

---

## What Verified Evidence Actually Means

There is a standard that auditing has worked out carefully, and it is worth importing into this conversation. The PCAOB's AS 1105 — the standard governing audit evidence — defines evidence by its sufficiency and appropriateness. Sufficiency is about quantity: do you have enough? Appropriateness is about quality: is it relevant, and is it reliable?

A generated summary is not evidence in this sense. It is a transformation of evidence. The underlying source files — the data pulls with version numbers, the period labels, the control totals, the reconciliation paths — are evidence. The model's language about those files is a layer on top of evidence. That layer can be useful. It can surface patterns a human would take longer to find. It can format a review surface that makes the judgment work faster. But it does not inherit the evidentiary standing of the sources it processed.

This matters operationally because when something goes wrong — and in finance work, something eventually goes wrong — the question is always: what is defensible? What can you point to? A logged data pull with a timestamp and a source path is defensible. A control total that reconciles to the general ledger is defensible. An AI-generated narrative that paraphrased three source files without a log of what it read is not defensible.

| Category | Examples | Defensible? |
|---|---|---|
| Verified evidence | Source files, version numbers, control totals, reconciliation paths, logged transformations | Yes |
| Model output | Classification suggestions, anomaly labels, language drafts, formatted summaries | Only if traced to verified evidence |
| Human judgment | Materiality calls, accounting treatment, release decisions, causal explanations | Yes, when owned by a named person |

*Table 1 — What is defensible when something goes wrong. Model output borrows its standing from the evidence beneath it.*

The recipe, properly designed, produces two outputs: a machine-readable log for reproducibility and a human-readable report for decision support. The log is what makes the preparation layer defensible. The report is what the human brings to the judgment layer. Neither is the judgment itself.

---

## The Supervision Structure

If the preparation layer is the recipe, then the judgment layer needs a supervision structure — a way of making sure the gate between them actually functions. I think about this with three questions, and they are worth having explicitly in mind every time you design a workflow.

The first question is scope. What period, entity, source system, and action space is this recipe allowed to touch? A recipe that can read the accounts receivable aging for Q3 of one subsidiary is a different thing than a recipe that can touch all subsidiaries and all periods. Scope is not a bureaucratic constraint; it is the definition of the problem. A recipe without an explicit scope will drift into adjacent data, and when it does, you will not know where the output came from.

The second question is approval. Who clears the gate before the output moves forward? This is a named person, not a role. If the answer is "whoever reviews it," the gate does not exist. Finance work has a tradition of explicit sign-off for good reason: when something is wrong, someone is responsible for having said it was right. The approval question preserves that.

The third question is verification. What source, control total, or owner confirmation would make the finding defensible? This is the question that connects the machine-readable log to the human review. If you can answer it — if you can point to the row in the source, the reconciled total, the confirmation from the data owner — then the preparation layer did its job. If you cannot, the recipe has a gap.

![Three nodes — Scope, Approval, Verification — arranged in a triangular cycle with curved arrows, and a connector dropping from Approval to a small gate glyph below.](images/02-the-reallocation-principle-fig-02.png)
*Figure 2.2 — The supervision loop: scope, approval, and verification, with approval governing the gate.*

<!-- → [DIAGRAM: Supervision loop — three nodes arranged in a cycle: "Scope" (what is this recipe allowed to touch?), "Approval" (who clears the gate?), "Verification" (what makes the finding defensible?) — arrows connecting all three; positioned above the preparation/judgment stack from the earlier diagram, with a line connecting "Approval" to the gate] -->

---

## What the Reallocation Actually Looks Like

Let me be concrete about what it means to reallocate effort rather than simply eliminate it, because I think the word "reallocation" can sound like a policy statement when it is actually a workflow design decision.

Here is a typical pre-automation pattern for a monthly variance analysis. An analyst spends two hours pulling data, one hour formatting, half an hour comparing periods, and thirty minutes writing the summary. Four hours total, mostly preparation, with the judgment compressed into the last sprint before the meeting.

Here is what the reallocation looks like if the preparation layer is automated correctly. The pull, the normalization, the comparison, and a draft summary run through a recipe. The recipe logs every transformation. The output lands on the analyst's desk with source paths, period labels, and flagged items already organized. The analyst now has the same four hours, but the first three are available for something different.

That something different is the point. It is reading the variance and asking whether the explanation makes sense given what you know about the business. It is checking whether the flagged items are the right items — whether the threshold the recipe used is appropriate for this period, this entity, this type of variance. It is deciding whether the draft accounting treatment is correct, or whether this situation is one of the exceptions the recipe does not know about. It is signing off on the artifact before it moves forward, not as a formality but as an informed act.

![Two equal-height stacked bars for the same four-hour total: the pre-automation bar is mostly preparation with a thin judgment cap; the reallocated bar compresses preparation and expands judgment to fill the recovered time.](images/02-the-reallocation-principle-fig-04.png)
*Figure 2.4 — Where the recovered time goes: the total holds constant; the mix shifts from preparation to judgment.*

The failure version of this story is where the analyst uses the three recovered hours to take on three more tasks. The recipe ran; the output looked good; no one spent time on review because the output looked good. Execution got cheaper. Review disappeared.

This is not a hypothetical risk. It is the natural equilibrium of a system that measures productivity by output volume and does not measure quality of the judgment layer. The reallocation principle is a design choice you have to make explicitly, against that gravity.

---

## The Phase Gate

There is one structural element that I want to name directly because it is easy to understand in principle and easy to skip in practice.

The phase gate is the explicit stop point between the preparation layer and the judgment layer. It is not a review in the sense of someone glancing at the output. It is a gate: the artifact cannot proceed until a named person has cleared it, with a record that they did.

In the recipe design, this looks like a stop condition. The recipe prepares the work surface and then stops. It does not send the email. It does not update the record. It does not file the report. It produces an output that a human will evaluate and, if adequate, carry forward. The recipe knows what "adequate" means mechanically — the required fields are present, the numbers parse, the source paths resolve. The human knows what "adequate" means professionally — the variance is explained, the treatment is right, the artifact is ready to represent the work.

![A left-to-right pipeline of three recipe stages — data pull, normalize and compare, draft summary — interrupted by a tall gate bar with a lock notch, after which a single human release stage continues.](images/02-the-reallocation-principle-fig-03.png)
*Figure 2.3 — Pipeline with an explicit stop: the recipe halts at the gate until a named approver clears it.*

<!-- → [DIAGRAM: Linear pipeline with explicit stop — boxes in sequence: "Data pull (recipe)" → "Normalize and compare (recipe)" → "Draft summary (recipe)" → [GATE: named approver] → "Release / file / send (human)" — the gate is visually distinct, perhaps a vertical bar with a lock icon; above the gate a label "preparation layer," below it "judgment layer"] -->

The gate matters most in the cases where the recipe output looks clean. A flagged anomaly invites review; a smooth output invites complacency. The gate makes review non-optional regardless of how confident the output appears.

---

## What AI Cannot Decide

There is a boundary worth stating plainly: AI cannot decide what finance work should matter.

This sounds obvious, but it has a specific operational meaning. The recipe can identify a variance. It cannot decide whether the variance is material — whether it is large enough, in the right account, at the right time, to require disclosure, explanation, or action. Materiality is a professional judgment about the relationship between a number and the decisions it might affect. It depends on context the model does not have: the state of the business, the expectations of the reader, the legal and regulatory environment, the history of how similar items have been treated.

The recipe can draft language. It cannot decide whether the language is adequate for the purpose — whether it accurately characterizes the situation, whether it omits something a reviewer would need to know, whether it creates an impression that the underlying facts do not support.

The recipe can flag items for review. It cannot decide which items actually require action, because action has consequences the model is not accountable for.

This is not a limitation that will be resolved by a better model. It is a structural feature of how accountability works. Accountability requires a person who can be responsible for the outcome, who has the standing to make the call, and who will bear the consequence if the call is wrong. A recipe can prepare the surface for that person. It cannot be that person.

---

## Building the Reallocation Hypothesis

The assessment artifact for this chapter — what I am calling the weekly reallocation hypothesis — is a simple but precise exercise. Take one recurring finance workflow. Inventory every step. Label each step as preparation, evidence, transformation, judgment, approval, or release. Then ask, for each step: what is the minimum human involvement that makes this defensible?

The hypothesis is your answer to what changes when the preparation layer runs automatically. Not a promise — a hypothesis. Where does the recovered time go? What does the judgment layer look like when it has more surface to work with? What are the stop conditions that keep the recipe from crossing the gate?

If the data is thin — if the workflow is new, if the source systems are messy, if the organizational context makes it hard to define scope cleanly — say so in the artifact. A honest assessment of where the evidence is weak is more valuable than a confident plan built on assumptions.

The verification checklist for this chapter is worth keeping close. The plan names the human decision that improves — not just the task that gets faster, but the judgment that gets better. The saved time is reinvested into review — explicitly, not aspirationally. No approval gate disappears — if a gate existed before the recipe, it exists after it.

Machine conformance checks whether the file parses and the required fields exist. Human adequacy checks whether the work is good enough for the finance decision it supports. The recipe handles the first. You handle the second.

That division is the reallocation principle.

---

## What Would Change My Mind

The argument in this chapter rests on a claim that the preparation and judgment layers are genuinely separable — that you can automate the first without corrupting the second. I believe that is true for most recurring finance workflows, but I am not certain it is always true.

There are workflows where the boundary is genuinely fuzzy: where deciding what data to pull is itself a judgment call, where the scope of the analysis changes based on what early results show, where a human would naturally loop between preparation and judgment several times before the work settles. In those cases, the clean two-layer model is a simplification, and treating it as exact could produce a gate that blocks the right kind of iteration.

If someone showed me a class of finance workflows where the looping between preparation and judgment is so tightly coupled that separating them degrades the output — not just slows it down, but produces worse professional work — I would revise the model. The principle is not that automation always belongs only in the preparation layer. The principle is that judgment and accountability must stay with a named person, wherever in the process they occur.

---

## Still Puzzling

The verification checklist draws a line between machine conformance and human adequacy. But adequacy for what, exactly? The standard shifts depending on whether the artifact is internal (a manager's review surface) or external (a regulatory filing, an investor communication, an auditor's request). I have described the distinction, but I have not worked out a clean decision rule for where on that spectrum a given artifact falls, or how the gate design should change as the stakes rise.

That question connects to Chapter 3, which is about the finance data contract — the discipline that makes the evidence layer reliable enough that the gate can actually do its job.

---

## LLM Exercises

**Exercise 1.** Paste a description of a recurring finance workflow you own or have worked in. Ask the model to label each step as preparation, transformation, judgment, approval, or release. Review the labels: where does the model draw the boundary? Where do you disagree, and why?

**Exercise 2.** Take the variance analysis scenario from the opening. Write a prompt that instructs an AI to produce a draft summary with explicit uncertainty markers — places where the model cannot determine the answer from the source data and flags the gap for human review. Compare the output to a prompt that does not include that instruction.

**Exercise 3.** Design a phase gate for one step in your reallocation hypothesis artifact. Specify: who is the named approver, what does the recipe hand them, what are the stop conditions, and what would make the finding defensible if someone asked tomorrow. Then ask the model to review your gate design and identify any scope or verification gaps.

---

## Prompts

### Figure 2.1 — The two layers and the human gate
**Files:** images/02-the-reallocation-principle-fig-01.svg · d3/02-the-reallocation-principle-fig-01.html
**Prompt:** A brutalist vertical two-layer stack on white — a preparation layer of five neutral nodes below a judgment layer of four nodes — separated by a single heavy red human gate, with neutral arrows flowing between preparation nodes and one upward arrow stopping at the gate. Hairline borders, one red accent for the gate.

### Figure 2.2 — The supervision loop
**Files:** images/02-the-reallocation-principle-fig-02.svg · d3/02-the-reallocation-principle-fig-02.html
**Prompt:** A brutalist three-node cycle on white — Scope, Approval, Verification — joined by neutral curved arrows in one direction, with the Approval node ringed in red and a red connector dropping to a small gate glyph. Neutral fills, one red accent on approval and the gate.

### Figure 2.3 — Pipeline with an explicit stop
**Files:** images/02-the-reallocation-principle-fig-03.svg · d3/02-the-reallocation-principle-fig-03.html
**Prompt:** A brutalist left-to-right pipeline on white — three neutral recipe stages interrupted by a tall red gate bar with a notch, then one human release stage — with neutral layer brackets above. Hairline borders, single red accent for the gate.

### Figure 2.4 — Where the recovered time goes
**Files:** images/02-the-reallocation-principle-fig-04.svg · d3/02-the-reallocation-principle-fig-04.html
**Prompt:** A brutalist two-bar stacked chart on white with a zero baseline, both bars the same four-hour height: preparation in neutral gray shrinking from the pre-automation bar to the reallocated bar while judgment in red expands to fill the recovered time. JetBrains Mono axis ticks, one red accent for the judgment segment.
