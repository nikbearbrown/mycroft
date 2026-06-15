# Chapter 11 — Control-Evidence Completeness Checker
*The binder that looks full and the evidence that isn't ready.*

The control folder has everything in it. Screenshots, system reports, approval emails, reconciliation sign-offs. It is thick. It was assembled carefully. When you flip through it, the tabs are all there and each one has something behind it.

And then someone looks closely at the screenshot behind tab seven and notices the timestamp is from the prior quarter. And the approval behind tab nine has a preparer signature but no reviewer. The binder is full. The evidence is not ready.

This is the completeness problem in internal controls work, and it is worth understanding precisely because it looks so much like a clerical problem — a few missing items, easily fixed — when it is actually a structural one. The question is not whether the binder has content. The question is whether the content, taken together, supports a conclusion about whether the control operated effectively during the period under review. Those are different questions, and the second one requires more than a visual check that the tabs are occupied.

What I want to work through here is what evidence readiness actually means for a control, what a recipe can check, and — critically — where the recipe has to stop.

---

## What a Control Is Trying to Prove

Before you can check evidence completeness, you need to understand what the evidence is supposed to establish. A control in an internal controls framework — the kind that shows up in a SOX 302 or 404 process, or in a financial statement audit, or in an operational review — is not just a procedure. It is a claim: that a specific risk was mitigated during a specific period, for a specific population of transactions or events, by a defined set of actions performed by defined people on a defined schedule.

The evidence for a control has to connect each element of that claim to something observable. The period is covered means the evidence has timestamps that fall within the review period, not before it and not after it. The population is covered means the sample of transactions reviewed is representative of the whole population — not just the easy ones, not just the ones that happened to be in the folder from last quarter. The defined people performed the actions means there is evidence that specifically identifies the preparer and the reviewer — not just a signature, but a signature that can be traced to a person with the authority and the responsibility to perform that control.

When any of these elements is missing or broken, the evidence does not support the claim, regardless of how complete the binder looks. A screenshot that shows the right process but from the wrong period proves the process existed, not that it ran when it was supposed to. An approval without a reviewer proves someone prepared something, not that someone with oversight responsibility signed off. A sample that covers ten transactions when the population was four hundred covers 2.5% of the risk, not the risk.

![Radial decomposition of a control claim that risk was mitigated, with four conditional branches — period, population, people, and process — each ending in a node that the evidence must establish or the claim is unsupported.](images/11-control-evidence-completeness-checker-fig-01.png)
*Figure 11.1 — Control claim decomposition*

<!-- → [DIAGRAM: Control claim decomposition — center node "Control claim: risk was mitigated" — four branches extending outward: "Period" (evidence timestamps fall within review window), "Population" (sample represents the full transaction set), "People" (preparer and reviewer identified and authorized), "Process" (required steps are documented and traceable) — each branch ends in a node labeled "Evidence must establish this or the claim is unsupported"] -->

The recipe's job is to check whether the evidence establishes each of these elements. The auditor's or control owner's job is to decide whether that establishment is sufficient — whether the evidence is not just present but reliable, whether the control design is adequate, whether the exceptions or gaps represent a deficiency and, if so, how severe. Those are two different jobs, and they require two different capabilities.

---

## Eight Checks Worth Running

A completeness checker for control evidence runs against a map: which controls are in scope, what objectives each control addresses, and what attributes each piece of evidence is required to have. Given that map, the recipe can check eight things.

**Period coverage.** Every piece of evidence has an as-of timestamp or a transaction date. The recipe checks that this timestamp falls within the review period. A screenshot from Q2 behind the Q3 tab is not an error message — it is a plausible-looking artifact with the wrong date. Period mismatches are one of the most common completeness failures in control binders, partly because prior-period evidence is sometimes used as a placeholder before the current-period work is done, and the placeholder never gets replaced.

**Evidence existence.** The control map defines what evidence is required for each control — a system report, an approval email, a reconciliation, a sign-off sheet. The recipe checks that each required item exists. Missing evidence blocks the ready status for that control. It does not get logged as "pending" or "expected later"; it gets logged as missing, because an auditor or a reviewer looking at the binder tomorrow needs to know whether the evidence is there or not.

**Preparer and reviewer proof.** Evidence that shows what was done without showing who did it and who reviewed it is incomplete. The recipe checks that each piece of evidence has an identifiable preparer and an identifiable reviewer, and that those identifiers resolve to people in the authorized role list. An approval from someone who was not authorized to approve that control — because they were not in the right role, because the control period predates their assignment, because the approval was a backup or a delegation that was not formally documented — is a flag for human review, not a clean pass.

**Timestamp integrity.** Beyond period coverage, the recipe checks that the timestamps within the evidence are internally consistent. An approval email dated before the reconciliation it approves is a logical inconsistency that a human reviewer might miss in a thick binder. A system report with a run timestamp after the close date it is supposed to document is a gap. These are not always errors — there are legitimate explanations for some timestamp anomalies — but they are flags that belong in the evidence ledger, not silent passes.

| Check | What the recipe examines | Flag condition |
|---|---|---|
| Period coverage | Evidence timestamp vs. review window | Timestamp outside review period |
| Evidence existence | Required items per control map | Required item missing |
| Preparer proof | Identified individual in authorized role | Missing or unauthorized preparer |
| Reviewer proof | Identified individual with oversight authority | Missing, unauthorized, or same as preparer |
| Timestamp integrity | Logical sequence of evidence items | Approval before preparation, or report after close date |
| Sample coverage | Transactions reviewed vs. population size | Sample below required threshold or population not defined |
| Stale artifacts | Evidence reused from prior period | Evidence predates current review period by more than one cycle |
| Prior exceptions | Unresolved findings from prior period | Prior exception without documented remediation |

*The eight completeness checks a recipe can run against a control map — and the single condition that trips each into a flag.*

![Eight-row comparison panel, one row per completeness check, with three aligned zones — the check, what the recipe examines, and the flag condition — and the flag-condition zone carrying a blocking accent.](images/11-control-evidence-completeness-checker-fig-02.png)
*Figure 11.3 — The eight completeness checks*

**Sample coverage.** For controls that operate over a population of transactions, the recipe checks that the sample covers the required proportion or count. If the control standard requires 25 samples for a high-frequency control and the binder has 12, the recipe flags the gap. If the population size is not documented — if no one has established how many transactions the control was supposed to cover — that is itself a flag, because you cannot assess sample adequacy without knowing what you are sampling from.

**Stale artifacts.** Prior-period evidence that was carried forward without being replaced is one of the quieter completeness failures. The recipe identifies evidence items where the timestamp predates the current review period by more than one cycle — one quarter back for quarterly controls, one year back for annual ones — and flags them for review. Stale evidence is not automatically wrong; sometimes prior-period documentation is intentionally retained for comparison. But it should be intentional and documented, not an oversight.

**Prior exceptions.** If the prior-period review of this control identified an exception — a gap, a deficiency, a finding that required remediation — the current-period evidence should include documentation of the remediation. The recipe checks whether there is a prior exception on record and, if so, whether the current-period binder includes remediation support. An unresolved prior exception is a flag that blocks ready status regardless of how complete the current evidence looks.

**Remediation support.** When a prior exception exists, the remediation documentation needs to be specific: what changed, who authorized the change, when it took effect, and how the current-period evidence demonstrates that the remediation worked. A note that says "control was remediated" without the supporting documentation is not remediation support — it is an assertion, and assertions are not evidence.

---

## What the Evidence Ledger Looks Like

The assessment artifact for this chapter — the control evidence readiness ledger — is not a pass/fail report. It is a structured accounting of the evidence status for each control, against each of the eight dimensions, so that the auditor or control owner looking at it knows exactly where the gaps are and what needs to be resolved before the binder is ready.

Each control gets a row. Each check dimension gets a column. The cell contains one of four values: pass (the check ran and the evidence is present and consistent), flag (the check identified an anomaly that needs human review), missing (the required evidence does not exist), or not applicable (the check does not apply to this control type). The ledger also includes a coverage notes column for each control — a one-line description of anything the recipe could not determine automatically: population size that was not documented, an authorization structure that was not in the role list, a timestamp anomaly with a plausible explanation that needs human confirmation.

What the ledger does not include is a column for ready or not-ready at the control level, and it certainly does not include a conclusion on effectiveness. Whether a control with two flags and no missings is ready for review is a professional judgment about what those flags mean in context. Whether a control that passed all eight checks operated effectively is an auditing judgment that requires understanding the control design, the risk it addresses, and the reliability of the underlying systems. The recipe checks the surface. The professional reads the surface.

| Control ID | Control description | Period | Evidence existence | Period coverage | Preparer proof | Reviewer proof | Timestamp integrity | Sample coverage | Stale artifact | Prior exception | Remediation support | Coverage notes | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CTL-014 | Monthly bank reconciliation review | 2024-Q3 | PASS | PASS | PASS | PASS | PASS | N/A | PASS | PASS | N/A | — | PASS |
| CTL-022 | Manual journal entry approval | 2024-Q3 | PASS | PASS | PASS | FLAG | PASS | FLAG | PASS | PASS | N/A | Reviewer = preparer on 2 of 25; population not documented | FLAG |
| CTL-031 | Access provisioning review | 2024-Q3 | MISSING | PASS | PASS | PASS | PASS | FLAG | PASS | FLAG | MISSING | Prior exception unremediated; sign-off sheet absent | MISSING |

*Status values: PASS / FLAG / MISSING / N/A — no effectiveness conclusion is drawn from this ledger.*

![Schematic of the evidence readiness ledger as a grid — rows are controls, columns are the eight check dimensions plus identifying fields, and body cells take one of four state swatches (pass, flag, missing, not applicable) with no control-level effectiveness column.](images/11-control-evidence-completeness-checker-fig-03.png)
*Figure 11.4 — Evidence readiness ledger structure*

---

## The Gap Between Readiness and Reliability

There is a distinction worth making explicit because it is easy to blur, especially when time pressure is high and the binder looks complete.

Evidence readiness is a structural check: is the required evidence present, within the right period, with the right signatures, in sufficient quantity? A recipe can assess this. Evidence reliability is a professional judgment: is this evidence credible? Does it actually demonstrate what it claims to demonstrate? Could the evidence have been fabricated or manipulated? Does the control it supports actually address the risk it is supposed to address?

The PCAOB's AS 1105 requires that audit evidence be not just sufficient but appropriate — which means relevant and reliable. Reliability depends on factors the recipe cannot assess from the file contents: the independence of the source, the directness of the evidence relative to the assertion it supports, the controls over the underlying systems that produced the evidence. A system report from a well-controlled ERP system is more reliable evidence than a manually prepared spreadsheet for the same assertion, even if both pass all eight of the recipe's checks.

This is where the phase gate matters in its strongest form. The ledger is the preparation surface. The auditor or control owner looks at the ledger and then asks the reliability question — the question that requires professional judgment about the evidence, not just its presence. The recipe cannot do this. It should not try.

![Two-column comparison divided by a vertical gate line. The left column lists structural readiness checks the recipe performs; the right column lists reliability judgments only a human can make.](images/11-control-evidence-completeness-checker-fig-04.png)
*Figure 11.2 — Readiness vs. reliability: the recipe boundary*

<!-- → [DIAGRAM: Two-column layout — left column "Evidence readiness (recipe)" with bullet points: present, within period, authorized signatures, sufficient sample, no stale artifacts, prior exceptions documented; right column "Evidence reliability (human)" with bullet points: source is independent, evidence is direct not inferred, underlying systems are controlled, evidence is credible given the risk, design is adequate for the assertion — a vertical dividing line labeled "The gate: recipe stops here" between the two columns] -->

---

## What AI Cannot Conclude

The human-only boundary in this chapter is the most technically specific one in the book: AI cannot conclude on control effectiveness.

Control effectiveness has two components in the standard frameworks. Design effectiveness asks whether the control, as designed, is capable of addressing the risk — whether the procedure, the frequency, the sample size, and the authorization structure are adequate for the assertion being supported. Operating effectiveness asks whether the control actually ran as designed during the period — whether the people who were supposed to perform it did perform it, on the schedule they were supposed to follow, with the thoroughness required.

Neither of these conclusions can be drawn from a completeness check. A control that passes all eight checks may still have a design deficiency — perhaps the sample size was adequate for the population size last year but the transaction volume has grown and the sample is now too thin. A control that passes all eight checks may still have an operating deficiency — perhaps the evidence was prepared after the fact, or the reviewer signed off without genuinely reviewing.

These are deficiency determinations, and deficiency determinations have consequences: they affect the overall assessment of internal control over financial reporting, they may require disclosure, they affect the reliance that auditors place on the control environment. Those consequences are why the conclusion belongs to a person with the professional standing and the accountability to make it.

The recipe surfaces the evidence. The professional concludes on it.

---

## Building the Control Evidence Readiness Ledger

The ledger you build as this chapter's assessment artifact should cover at least three controls from a real or sanitized control environment. For each control, document the control ID, the objective it addresses, the required evidence attributes per the control map, and the status of each of the eight checks against the current-period evidence.

Where the evidence is thin — where the control map is not fully defined, where the population size is undocumented, where the authorization structure is unclear — say so in the coverage notes column. A ledger that honestly reports gaps in the underlying documentation is more useful than one that maps incomplete data to confident status calls. The person reviewing the ledger needs to know not just what the recipe checked but what it could not check and why.

The verification checklist for this chapter: missing evidence blocks ready status — not "pending," not "expected," missing. Inconsistent evidence is surfaced, not explained away. No automatic conclusion is drawn on effectiveness from any combination of check results, however clean.

Machine conformance checks whether the ledger parses and the required fields exist. Human adequacy checks whether the evidence documented in the ledger is sufficient and appropriate for the control assertion it supports.

---

## What Would Change My Mind

The absolute prohibition on recipe-level effectiveness conclusions is the right rule for most control environments. But I can imagine conditions under which a very narrow automated finding might be warranted — not an effectiveness conclusion, but something closer to a structural sufficiency signal.

If a control framework defines, precisely and in advance, that a control with specific attributes (frequency, sample size, authorization level, evidence type) is designed to operate effectively, and if a recipe can verify that all those attributes are present for a given period, then the recipe is implementing a human decision that was made in advance — the same way a pre-approved sweep rule implements a treasury decision. That is different from the recipe exercising judgment about adequacy.

I think this is theoretically coherent but operationally rare. Control frameworks that are specific enough to support this kind of automated sufficiency finding are also complex enough that the edge cases and exceptions multiply quickly. The practical answer is probably that the recipe builds the ledger and a human makes the call, even in well-specified environments. If someone showed me a control framework where the recipe-level signal had been validated against auditor conclusions over multiple cycles and the agreement rate was high, I would want to understand what the exceptions looked like and whether they were random or systematic.

---

## Still Puzzling

The sample coverage check requires knowing the population size, and the population size is often not documented in the evidence binder — it lives in a separate system, or in a prior-period planning document, or in the auditor's workpapers. I have designed the check to flag "population not defined" when this happens, but that flag occurs so often in practice that it may produce noise rather than signal.

The cleaner answer is probably to build population documentation into the data contract — to require that the control map includes a population definition for each sampling-based control, updated each period. But that is a process change, not a recipe change, and it requires buy-in from the control owners and the audit team. I have not worked out how to design the recipe to push for that documentation without creating so many flags that the ledger becomes unreadable.

---

## LLM Exercises

**Exercise 1.** Take a control you own or have worked with. Write out the control objective, the required evidence attributes per your control map, and the evidence you have on hand for the most recent review period. Ask the model to run the eight completeness checks against your description and produce a one-row evidence ledger entry. Review the result: what did the model flag that you would have passed, and what did it pass that you would have flagged?

**Exercise 2.** Write a prompt that instructs an AI to review a control evidence package and produce an evidence readiness ledger without drawing any conclusion on effectiveness. Then ask the model the direct question: "Is this control effective?" Compare what it says to the ledger it produced. What does the gap between the readiness assessment and the effectiveness question reveal about where the model's judgment is being applied?

**Exercise 3.** For one flagged item in your control evidence readiness ledger, write the coverage note that explains what the recipe found, what it could not determine, and what the reviewer needs to resolve before the control can be assessed. Then ask the model to draft a remediation plan for the flagged item. Review the plan: does it address the specific gap, and does it produce evidence that would satisfy the completeness check in the next review period?

---

## Prompts

### Figure 11.1 — Control claim decomposition
**Files:** images/11-control-evidence-completeness-checker-fig-01.svg · d3/11-control-evidence-completeness-checker-fig-01.html
**Prompt:** A radial hierarchy in the brutalist register: one red central claim node ("risk was mitigated") branching to four neutral element nodes — period, population, people, process — each dropping to an ochre-bordered terminal that the evidence must establish or the claim is unsupported. Ink strokes, white canvas, no decoration beyond the single red accent and one ochre conditional band.

### Figure 11.2 — Readiness vs. reliability: the recipe boundary
**Files:** images/11-control-evidence-completeness-checker-fig-04.svg · d3/11-control-evidence-completeness-checker-fig-04.html
**Prompt:** A two-column comparison split by one prominent red gate line. Left column (neutral) lists the structural readiness checks the recipe performs; right column (red-accented) lists the reliability judgments only a human makes. The gate is the loudest mark on the canvas — it says the recipe stops here.

### Figure 11.3 — The eight completeness checks
**Files:** images/11-control-evidence-completeness-checker-fig-02.svg
**Prompt:** An eight-row comparison panel, one row per completeness check, three aligned zones each (check, what the recipe examines, flag condition). The flag-condition zone carries a single blocking accent; rows band subtly for legibility. Flat, ink on white, no icons.

### Figure 11.4 — Evidence readiness ledger structure
**Files:** images/11-control-evidence-completeness-checker-fig-03.svg
**Prompt:** A schematic grid — rows are controls, columns are the eight check dimensions plus identifying fields. Body cells take one of four state swatches (pass, flag, missing, not applicable) shown as fills, with a legend strip and an emphasis band marking the deliberately absent effectiveness column.
