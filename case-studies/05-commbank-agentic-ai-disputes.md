# Commonwealth Bank: Agentic AI in Retail Banking
## A Real but Unnamed Disputes Tool, an Unrelated Labor Dispute, and a Narrative That Fused Them

**Case Study — Professional/Industry Document**
**Series:** Agentic AI Adoption in Financial Services (2025–2026)
**Classification:** Public Information — Sourced from Verified Public Disclosures

---

## A Note on Scope Before We Begin

This case study covers Commonwealth Bank of Australia (CBA/CommBank) and, deliberately, treats three separate AI systems as three separate systems:

1. An **unnamed, narrow agentic tool for payment-dispute handling** — the closest thing to an "agentic AI in disputes" story CommBank's public record actually supports, described by CommBank's own Chief Decision Scientist but never given a product name.
2. An **inbound-call voice bot**, launched June 2025, that reduced call volume in CommBank's Direct Banking function — the system actually tied to 45 role redundancies in July 2025 and their reversal in August 2025 after Finance Sector Union (FSU) and Fair Work Commission (FWC) pressure.
3. **ChatIT**, a fully confirmed, named internal generative-AI tool that helps CommBank employees with IT support requests — unrelated to customer-facing disputes or the layoffs.

A widely circulated version of this story treats systems (1) and (2) as one thing: an autonomous "Dispute Resolution Agent" that both handled disputes and caused the layoffs. **That system, under that description, does not exist in CommBank's public record.** This case study documents what does.

---

## Executive Summary

The three systems named in the Scope note above break down as follows: the disputes tool is real but unnamed, resting on a single named-executive interview with no documented architecture beyond three functions. The voice bot — not the disputes tool — is the system tied to 45 real job redundancies in July 2025 and a real, publicly documented reversal in August 2025, forced by the Finance Sector Union through the Fair Work Commission and acknowledged on the record by CommBank's own Chair at the bank's October 2025 AGM. ChatIT is fully confirmed and unrelated to either.

The popular version of this story treats all of this as one narrative: an autonomous customer-facing "Dispute Resolution Agent" that both handled disputes and triggered a labor dispute when it went wrong. That version does not survive contact with primary sourcing. The disputes tool and the voice bot are different systems, confirmed by different sources, serving different functions, in different parts of the bank. This case study treats that distinction as the central finding, not a footnote: it is a clean, documented instance of a pattern visible across broader public and trade-press coverage of CommBank's AI push — a company's various AI initiatives, announced and reported at different times for different purposes, collapsing in circulation into a single, more dramatic story than any one primary source actually supports.

---

## 1. Firm Context and Strategic Rationale

Commonwealth Bank of Australia is Australia's largest bank and its largest listed company by a wide margin. CBA reported total assets of approximately A$1.35 trillion as of 30 June 2025, and in June 2025 became the first ASX-listed company ever to exceed a A$300 billion market capitalization. The bank serves more than 18 million customers group-wide (CBA-brand, Bankwest, and ASB in New Zealand combined), and describes itself as the main financial institution for one in three Australian consumers and one in four Australian businesses. *[Source: CBA 2025 Annual Report; CBA FY25 Full Year Results Presentation, 13 August 2025]*

Within the group, **Retail Banking Services is the single largest profit contributor**, generating A$5,395 million in cash net profit after tax in FY25 — 52.6% of the group's total cash NPAT of A$10,252 million. *[Source: CBA FY25 Profit Announcement, 13 August 2025]* On the metrics that define retail dominance specifically, CBA leads every "Big Four" peer: a 33.4% retail main-financial-institution share (a 16.6 percentage-point lead over its nearest competitor), roughly 26–27% of household deposits, and approximately 25% of the home-loan market — the largest of any Australian lender. *[Source: CBA FY25 Full Year Results Presentation; Australian Broker/APRA MADIS data, March 2026]*

That scale is the direct context for the operational problem this case study examines. CBA's own newsroom states the bank "processes and analyses more than 20 million payments a day." Of that volume, Angus Sullivan, CBA's Group Executive of Retail Banking Services, told a November 2024 media briefing that approximately 15,000 transactions daily "are disputed" — a figure attributed to his remarks as reported by trade press, not to a CBA-published filing, and treated as such throughout this case study. *[Source: CBA newsroom, 28 November 2024; iTnews, November 2024]*

CBA's strategic rationale for automating any part of this volume is not stated in the elaborate terms some secondary coverage implies. Unlike the audited, filed figures above, the only public statement of strategic rationale for this specific tool comes from a single trade-press interview, not a CBA disclosure — and this case study treats it with correspondingly less weight than the financial figures it sits beside. The clearest on-the-record description comes from Dan Jermyn, CBA's Chief Decision Scientist, discussing the disputes use case specifically: "When a customer is reaching out to us in an AI-assisted channel, it's important for us to be able to understand their intent." Jermyn further characterized the underlying problem as deceptively simple: "this is a relatively simple use case for us, but one that also encompasses a huge range of components and possible outcomes: from getting information from the customer and verifying details about the transaction, to the process of rectifying the transaction upon validation." *[Source: Evident Insights, "167 ways banks use AI," 20 February 2025]* This is the most detailed strategic statement CBA has made about this specific tool, and this case study does not embellish beyond it.

---

## 2. The Operational Problem

Any single payment dispute is close to trivial to describe: a customer sees a transaction they don't recognize or didn't authorize, and reports it. The operational problem is not the individual case — it is what happens when that case is one of roughly 15,000 arriving on the same day, against a base of more than 20 million daily payments, each requiring the same basic sequence before a human ever needs to apply judgment: understand what the customer is describing, confirm the transaction details actually match their claim, and determine whether the case is simple enough to resolve immediately or needs a specialist.

That sequence — intent recognition, verification against an objective internal record, and a threshold decision about complexity — is the same structural shape this series has already documented at Goldman Sachs and JPMorgan Chase: high-volume, rule-governed work where the judgment required at each step is bounded rather than open-ended, and where an internal data source exists to check a claim against rather than relying on unverifiable customer narrative alone. CBA's own description of the use case, through Dan Jermyn, frames it as deceptively simple on its face while "encompass[ing] a huge range of components and possible outcomes." *[Source: Evident Insights, 20 February 2025]* Framing this specific problem as a well-suited candidate for agentic assistance is this case study's own analytical framing, consistent with but not verbatim from CBA's own characterization, and is labeled as such here. It is worth being explicit about what this structural argument is and is not doing: it describes why this *class* of problem suits agentic automation in principle, the same argument this series has made about Goldman Sachs's and JPMorgan Chase's far more fully architected systems. It does not imply CBA's actual disputes tool has been built out to a comparable degree — Section 3 documents just how much thinner the confirmed record is here than at either of those firms.

It is worth being precise about what this section is not describing. It is not describing the cause of CommBank's July 2025 layoffs — that cause, documented in Section 3.2, is a separate customer-service and call-volume problem tied to a different part of the bank's operations. Conflating the two — treating "CommBank has a high volume of payment disputes it wants to automate" and "CommBank cut call-centre jobs" as the same operational story — is the error this case study exists to correct, not repeat.

---

## 3. What's Confirmed, and Where the Record Is Thin

This series has now documented several different shapes of sourcing problem: secondary-aggregation figures at Goldman Sachs and JPMorgan Chase, a company's own two voices disagreeing with each other at BlackRock, and an entity-specific confirmation gap at Allianz. CommBank's public record has a different shape again, and a more basic one: before asking what any single system does, the public record requires establishing that the systems being discussed are not, in fact, the same system. This section does that first, then documents each system on its own terms.

### 3.1 The Disputes Tool

CBA has a real agentic tool for handling a portion of its daily payment disputes. It has no public product name. The clearest description of it comes from CBA's own Chief Decision Scientist, Dan Jermyn, in a February 2025 Evident Insights report: the tool lets a customer describe the situation and, per Evident's description, get the dispute "lodged automatically upon satisfaction of the right criteria." *[Source: Evident Insights, "167 ways banks use AI," 20 February 2025]*

Beyond that, three functions are documented and no more:
- Understanding customer intent in an AI-assisted channel (Jermyn, on the record)
- Verifying transaction details against CBA's internal records (Jermyn, on the record)
- Lodging a dispute automatically once unspecified "criteria" are satisfied (Evident's description of the tool's behavior)

No source — CBA's own newsroom, CBA's 2025 Annual Report, or CBA's December 2025 "Our Approach to Adopting AI" report — names this tool, describes a multi-step internal architecture for it, states that it queries core banking APIs, reviews merchant history, evaluates claims against regulatory frameworks, or autonomously executes a chargeback. Notably, CBA's own flagship AI disclosure document — the December 2025 "Our Approach to Adopting AI" report — does not mention disputes or chargebacks at all. *[Source: CBA "Our Approach to Adopting AI," December 2025]* This is a thin record, and this case study states that plainly rather than filling the gap with plausible-sounding detail.

### 3.2 The Voice Bot, the Layoffs, and the Reversal

This is the best-documented system in this case study, and it is not the disputes tool. In June 2025, CBA launched an inbound-call voice bot in its Direct Banking / Customer Service Direct function, which CBA said reduced inbound call volume by approximately 2,000 calls a week — a figure the FSU disputed as inaccurate, arguing call volumes were in fact rising (see Section 5). *[Source: BankInfoSecurity, 25 August 2025]*

On 29 July 2025, the Finance Sector Union's own published media release stated that CBA was cutting 90 roles, including 45 roles in Direct Banking tied to the new voice-bot system on the bank's inbound line. *[Source: Finance Sector Union, 29 July 2025]* The FSU took the matter to the Fair Work Commission over this dispute.

On 21 August 2025, the FSU's own bulletin announced CBA had reversed the cuts. *[Source: Finance Sector Union, 21 August 2025]* CBA's own written admission, issued through an unnamed spokesperson to media, stated the initial assessment "did not adequately consider all relevant business considerations and this error meant the roles were not redundant," and that the bank had apologised to the employees concerned. *[Source: reported via TechRadar and Bloomberg, August 2025]*

Two months later, at CBA's 15 October 2025 AGM, a former affected employee confronted the board directly. CBA Chair Paul O'Malley responded on the record, acknowledging: "We made a mistake," and that the bank "didn't adequately consider all the relevant business considerations." CEO Matt Comyn also addressed the matter at the same AGM. *[Source: AAP News, 15 October 2025]*

This sequence — a named system (the voice bot), a specific headcount (45 of 90 total roles), a union-driven Fair Work Commission dispute, and a named-executive on-the-record admission — is the strongest, most completely sourced thread in this case study. It has nothing to do with the disputes tool described in Section 3.1.

### 3.3 ChatIT

ChatIT is CBA's internal, generative-AI-enabled IT support assistant for employees, launched in May 2024 and unrelated to either system above. CBA's own newsroom states that ChatIT processed over 2.3 million messages and executed more than 12,000 automated IT fixes in its first six months of automation, saving nearly 2,500 hours, with a reported satisfaction rating of 4.63 out of 5 and a Net Promoter Score of +79. *[Source: CBA newsroom, 26 June 2025]* CBA's GM of Global Technology Services, Mark Vudrag, separately confirmed more than 13,000 employees had interacted with ChatIT within three months of its automation-feature launch. *[Source: iTnews, 2025]* ChatIT is fully confirmed and fully documented relative to the other two systems in this case study — and it is not a customer-facing dispute-handling tool of any kind.

### 3.4 What the Brief's Described Architecture Does Not Match

A version of this story circulates describing an autonomous "Dispute Resolution Agent" that parses customer intent, queries core banking APIs, reviews merchant transaction history, evaluates claims against regulatory frameworks, and autonomously lodges chargebacks — escalating only ambiguous or high-value cases to a human specialist. No CBA source, named executive, or union statement uses this name or describes this specific architecture. The phrase "Dispute Resolution Agent" appears exclusively in AI-vendor and consultancy marketing material (SAP, KPMG proof-of-concept work, Lyzr, Cognizant) describing generic banking use cases — not in anything CBA has published or any CBA executive has said. This case study does not use that name for CBA's actual disputes tool, and treats the elaborate multi-step architecture attached to it as unconfirmed.

---

## 4. Illustrated Workflow: A Disputed Card Transaction

> **IMPORTANT: This workflow is an illustrative scenario constructed for demonstration purposes.**
> The three confirmed functions of CBA's disputes tool — understanding customer intent, verifying transaction details, and lodging a dispute automatically once criteria are met (Section 3.1) — are sourced to CBA's Chief Decision Scientist via Evident Insights. Everything else below — the specific scenario, the named customer, the specific criteria the tool checks, the escalation triggers, and the sequencing between steps — is this case study's own construction, now built and tested as a reference implementation (Section 4b), and no richer than the three confirmed functions support. No merchant-history lookup, no regulatory-framework evaluation engine, and no autonomous chargeback-execution step are included here, because no source confirms any of them exist.
>
> The step sequence below has been reconciled against a working reference implementation (Section 4b). Where the case study previously flagged an open question — whether claim-detail extraction (amount/merchant/date) belongs to Step 2 or a separate function — that question has been resolved as a labeled design decision, not a discovered fact: extraction is treated as part of Step 2 (Intake). This is marked CONSTRUCTED throughout, consistent with the reference implementation's own README.

### The Scenario

A CommBank credit-card customer, referred to here as "Marcus," notices a $340 charge from an online retailer he does not recognize. He opens the CommBank app and reports the transaction as a dispute through an AI-assisted channel.

### Phase 1: Automated Intake and Verification

**Step 1 — Dispute Reported.** Marcus describes the transaction and states he did not authorize it.

**Step 2 — Intent Understanding and Detail Extraction.** The tool interprets Marcus's description to classify the dispute type (unauthorized transaction, goods/services not received, or billing error) — the function Jermyn described as understanding customer intent — and, as this case study's own labeled design decision, also extracts the structured claim details (amount, merchant, date) that Step 3 needs. *(CONSTRUCTED: no source assigns extraction to this step specifically rather than a separate one; this case study reads it as part of intake, per the reference implementation's Design Decision 001.)* If the tool cannot confidently classify the dispute type, or extraction confidence falls below a threshold, the case escalates to a human specialist at this point — before Step 3 ever runs — rather than proceeding on an unclassified or incomplete claim. *(CONSTRUCTED: the specific confidence threshold is this case study's own invented value.)*

**Step 3 — Transaction Verification.** The tool checks the disputed transaction against CBA's internal transaction record to confirm the amount, merchant, and date Marcus described match what was actually charged. This step cannot run on an incomplete result from Step 2 — if Step 2 could not extract a merchant, amount, or date, Verification escalates immediately (`incomplete_claim_details`) rather than attempting to check a record it doesn't have enough information to look up. If no matching transaction record exists at all, the case also escalates rather than being evaluated against Step 4's criteria — a rejected or absent record is never passed forward as if it were a match.

**Step 4 — Criteria Check (Gate).** The tool evaluates whether the dispute meets criteria for automatic lodging. This case study does not claim CBA's actual criteria; the reference implementation instead uses an explicitly invented, risk-tiered dollar threshold that varies by dispute type — $750 for a duplicate charge, $500 for an unrecognized charge, $250 for an unauthorized transaction — reasoning that different dispute types carry different fraud risk at the same dollar amount. *(CONSTRUCTED: entirely invented; CBA has never disclosed a figure, tiered or otherwise. This specific tiered design was chosen over a flatter single-threshold alternative after deliberate consideration — see Section 4b's Design Decisions for the reasoning and the recorded internal disagreement about which approach better serves an illustrative scaffold.)*

### Phase 2: Automated Resolution or Human Escalation

**Step 5a — Automatic Lodging (criteria met).** If Marcus's claim amount falls under the relevant tier's threshold and the transaction record matches, the dispute is lodged automatically, consistent with Evident's description of disputes being lodged automatically upon satisfaction of the right criteria.

**Step 5b — Escalation (criteria not met).** Several distinct conditions route to a human resolution specialist rather than automatic resolution, each with its own named reason in the reference implementation: an unclassifiable dispute type or low-confidence extraction (escalated at Step 2, before verification even runs); incomplete claim details insufficient to attempt a lookup; no matching transaction record found at all; a transaction record found but not matching Marcus's description; or a matching, classifiable claim that simply exceeds its tier's dollar threshold. CBA has not published any of these specific triggers or thresholds; the categories of failure (ambiguous input, no match, mismatch, high value) reflect the general human-in-the-loop pattern this series has documented elsewhere in the sector, applied here as this case study's own construction.

**The tool does not query merchant history, evaluate regulatory frameworks, or execute a chargeback autonomously in this illustration** — because no source confirms it does any of these things in CBA's actual system.

### Workflow Summary: What the Tool Did vs. What the Human Did

| Step | Actor | Action |
|---|---|---|
| Report dispute | Human (Customer) | Required — nothing proceeds without this |
| Classify intent + extract claim details | Disputes tool | Autonomous (classification confirmed; extraction-at-this-step is CONSTRUCTED). Escalates here (`unclassified_dispute_type` or low extraction confidence) before Verification ever runs. |
| Verify transaction details | Disputes tool | Autonomous (confirmed function). Escalates here on `incomplete_claim_details` (bad input from Step 2) or no matching record found — never passes an absent/rejected record forward as a match. |
| Check against risk-tiered lodging criteria | Disputes tool | Autonomous (criteria check confirmed as a concept; specific tiered thresholds are CONSTRUCTED and invented) |
| Lodge dispute automatically | Disputes tool | Autonomous, only if claim amount is under its tier's threshold and the record matches (confirmed behavior; mechanism and thresholds CONSTRUCTED) |
| Review any escalated case | Human (Resolution Specialist) | Required for every case not auto-resolved — five distinct, separately tested escalation reasons exist (see Section 4b) |

---

## 4b. Reference Implementation

A working reference implementation now accompanies this case study, following the same pattern as the Allianz Australia and BlackRock entries in this series: a companion technical artifact grounding the three confirmed functions described in Sections 3.1 and 4, built, tested, and reconciled against the narrative above — not merely planned or described. It runs entirely against fabricated mock data, with no external services, credentials, or CBA systems involved anywhere in the repository.

Consistent with the standard this entry set for itself, the implementation is deliberately **not** a multi-agent pipeline. The public record supports three functions performed by what appears to be a single tool, not seven coordinated agents the way Allianz's Project Nemo is documented, and not a chargeback-execution engine the way the popular narrative this case study corrects had assumed. It is a linear, single-tool workflow: **Intake → Verification → Gate.**

**What's Confirmed** (sourced to Dan Jermyn via Evident Insights, 20 February 2025): the tool understands customer intent in an AI-assisted channel; it verifies transaction details against CBA's internal records; it lodges a dispute automatically once unspecified criteria are met; and this is a single tool with three functions, not a documented multi-agent pipeline. Nothing else about this tool is publicly confirmed — no model, no orchestration framework, no dollar thresholds, no error/override rate. CBA's own December 2025 "Our Approach to Adopting AI" report does not mention this use case at all.

**What's Constructed** — labeled explicitly, not left implicit, in the repository's own README and `docs/DESIGN_DECISIONS.md`:
- That claim-detail extraction (amount/merchant/date) lives inside Intake rather than a separate unnamed function — the resolution to the open question this case study previously flagged (Design Decision 001).
- The exact matching logic in Verification (case-insensitive merchant name, exact date match) — CBA's actual matching tolerance is undisclosed.
- The risk-tiered auto-lodge thresholds in Gate ($750 duplicate_charge / $500 unrecognized_charge / $250 unauthorized_transaction) — entirely invented, and marked `[DEV]` in the code as a customization point. This specific tiered design was chosen over this project's own initial recommendation for a single flat threshold; the reasoning and the recorded disagreement are both preserved in Design Decision 005, rather than the disagreement being quietly resolved and erased.
- Escalating on an unclassified dispute type at Intake, rather than letting it default through Gate's tiering unclassified (Design Decision 006).
- The distinction between a fail-fast "no record found" and a Gate-evaluated "record found but mismatched" (Design Decision 002).
- All code, mock data, the orchestrator's call sequence, and the extraction-confidence escalation threshold (0.6).

### What the Tests Actually Verify

The suite was run in full before this repository was considered finished. **Result: 14 tests, 14 passing, 0 failing**, as of this version.

| Test file | What it proves |
|---|---|
| `test_intake_verification_dependency.py` | Verification cannot succeed without Intake's output; with a missing merchant it escalates (`incomplete_claim_details`) rather than failing silently or crashing; with correctly-shaped input it matches correctly. |
| `test_verification_gate_dependency.py` | Gate refuses to auto-lodge when Verification's output is withheld or negative — the dependency is real, not assumed. |
| `test_fail_fast_pipeline.py` | The orchestrator actually stops at Intake on ambiguous input and at Verification when no record exists — Gate is never called with unusable data in either case. |
| `test_escalation_paths.py` | All named escalation triggers are each independently confirmed reachable, with the correct escalation reason attached. |
| `test_negative_and_positive_cases.py` | A case engineered to fail every gate criterion is confirmed to escalate; a clean case is confirmed to actually auto-lodge; two further cases confirm the risk-tiered thresholds actually change the outcome for the same dollar amount depending on dispute type — shown producing a different decision at $600 and at $12.99, not just described as tiered; a final case confirms an unclassified dispute type escalates at Intake rather than silently defaulting through Gate. |

**Two findings from actually running this suite, not from prose review** — preserved here deliberately, because they demonstrate why the suite was run rather than just described:
1. The first version of the verification function raised an unhandled error when called with a missing merchant, instead of escalating gracefully. This was caught by the dependency test designed specifically to feed it malformed input, and fixed before the repository was finalized (Design Decision 003).
2. Making Gate's threshold depend on dispute type (Decision 005) surfaced a second-order gap during design review: Intake's original escalation logic never checked whether the dispute type itself was classifiable, so a claim with a clean amount/merchant/date but no matching dispute-type phrase would have silently defaulted to a middle risk tier it was never evaluated against. This was closed by Decision 006 and is now covered by its own test.

### Known Limitations

- Extraction is rule-based (regex/keyword), not ML-based — built only to demonstrate the Intake → Verification data contract, not to model CBA's actual natural-language understanding, which no source discloses either.
- Mock data is six hardcoded transactions; a real integration point is marked `[DEV]` in the code.
- No concurrency, retry, or timeout handling — this is a synchronous, single-request pipeline.
- No test exercises multiple disputes arriving concurrently; the case study's operational-scale problem (roughly 15,000 disputes/day) is not modeled here. This repository models one dispute's path through the pipeline, not throughput.
- The auto-lodge thresholds, matching tolerance, and confidence cutoff are all single invented values, not the product of any tuning or real data.

### Explicit Non-Claims

This repository is not a disclosure of Commonwealth Bank of Australia's actual proprietary disputes-handling system. It does not claim CBA's system works this way, uses this matching logic, or applies these thresholds, and should not be cited as evidence of CBA's technical architecture. It is an illustrative, tested scaffold built to be consistent with the three publicly confirmed functions and no richer than what they support.

---

## 5. Documented Results and Impact

**No efficiency, time-savings, or adoption metric exists for the disputes tool specifically.** Neither CBA's newsroom, its FY25 or 1H26 results materials, nor the Evident Insights report that first described the tool provides a quantified before/after figure for dispute processing time, resolution rate, or volume handled. This case study does not estimate one.

**The voice bot's documented outcome is a labor outcome, not a confirmed efficiency outcome.** The only quantified result tied to the voice bot in the public record is CBA's own claim that it reduced inbound call volume by approximately 2,000 calls a week — a figure the FSU explicitly disputed, arguing volumes were rising. *[Source: BankInfoSecurity, 25 August 2025]* No customer-experience or cost-savings figure for the voice bot has been independently confirmed.

**Two separate, real CBA efficiency figures exist — and belong to neither of the above systems.** CBA's own newsroom reports a 76% reduction in customer scam losses from peak, attributed to a distinct suite of fraud-prevention tools including "CommBank Approve to Pay," NameCheck, and AI-powered fraud detection — not the disputes tool or the voice bot. *[Source: CBA newsroom, 14 August 2025]* Separately, CBA's newsroom reports a 40% reduction in call-centre wait times attributed to AI-powered app messaging as of its FY24 results. *[Source: CBA newsroom, 28 November 2024]* Both figures are real, both are CBA's own, and neither is evidence of what the disputes tool or the voice bot specifically achieved. Treating either figure as proof of the disputes tool's performance — a conflation visible in some secondary coverage of CommBank's AI initiatives — is not supported by the record.

**What CBA has separately confirmed, and kept separate itself:** a fraud-pattern-detection agent, built on Snowflake's data cloud, that proposes new fraud-detection rules for human analyst review under stated human-in-the-loop oversight, contributing to a reported 20%+ reduction in fraud losses in 1H FY26 versus 1H FY25. *[Source: CBA newsroom, April 2026]* This is a fourth, distinct system, mentioned here only to be clearly excluded from the disputes-tool and voice-bot narratives this case study is correcting.

---

## 6. Limitations, Failures, and Honest Caveats

### 6.1 The Disputes Tool's Sourcing Is Thin and Single-Threaded

The entire public record for CBA's disputes tool traces to one named-executive interview, conducted by one third party (Evident Insights), in February 2025. No CBA press release, newsroom post, annual report, or subsequent AI-strategy document names the tool, elaborates on its architecture, or repeats Jermyn's description in CBA's own words. This is thinner sourcing than any other system this series has documented — thinner even than Allianz's Project Nemo, which had at least one detailed Allianz Group press article naming seven distinct agent roles. Here, three functions from one interview is the entire technical record.

### 6.2 Two Different Systems Have Been Reported as One — A Pattern Worth Naming Across This Series

This case study's central finding is a conflation error, and it is worth naming as a pattern this series has now watched evolve across five entries. At Goldman Sachs and JPMorgan Chase, the sourcing problem was that real, confirmed architectures came with unconfirmed or secondary-sourced efficiency figures. At BlackRock, the problem was that the company's own two communications about a single real system disagreed with each other. At Allianz, the problem was that a real, confirmed system's connection to a specific legal entity required disambiguation. At CommBank, the problem is a different order of error entirely: **two separate, independently confirmed systems — a disputes tool and a voice bot — serving different functions in different parts of the bank, have been reported in wider circulation as if they were the same system**, producing a clean but false narrative in which an autonomous dispute agent caused layoffs. Neither confirmed system supports that sentence. The disputes tool has no documented connection to any job loss. The voice bot has no documented connection to disputes processing.

The practical instruction this leaves for a reader tracking AI-attributed labor outcomes anywhere in this sector: when a company's AI deployment and a labor dispute are reported together, check whether the primary sources for the capability and the primary sources for the labor cost actually name the same tool. In CommBank's case, they do not.

### 6.3 No Technical Disclosure Exists for the Disputes Tool

Beyond the three functions in Section 3.1, no public source describes the model or models powering the disputes tool, any orchestration framework, the specific criteria used to gate automatic lodging, or an error/override rate. CBA's flagship AI disclosure — the December 2025 "Our Approach to Adopting AI" report — does not mention this use case at all, a notable silence given that the same report names several other tools (Bill Sense, Ceba, Compass AI, Card-Not-Present detection, Benefits Finder) in detail.

### 6.4 A Narrow, Partial Deployment — Not Evidence of Broad Autonomous Authority

Even taking Section 3.1's three confirmed functions at face value, they describe automation for "some" of CBA's 15,000 daily disputes — not all of them, and not a general claims-adjudication platform. Nothing in the public record indicates what proportion of daily disputes the tool actually handles versus routes to a human by default. Readers should take from this an honest sense of scale: a real, narrow, criteria-gated tool operating somewhere within a much larger, still substantially human-run process.

### 6.5 A Stated Reversal Is Not the Same as a Documented Root-Cause Admission

CBA's on-the-record acknowledgment of the voice-bot layoffs is a genuine, named-executive admission that the decision process was flawed. It is not a technical admission that the voice bot itself failed to deliver the claimed call-volume reduction; CBA has not withdrawn that specific claim, even though the FSU disputes it. This case study treats the FSU's disputed-volume claim and CBA's admitted decision-process error as two separate, both genuinely sourced, but distinct claims — and does not collapse them into a single "the AI didn't work" narrative that neither source, on its own, fully supports.

### 6.6 What Building the Reference Implementation Surfaced

Consistent with this series' own working discipline, the narrative in Sections 3–4 above was checked against an actual built and tested implementation before being finalized, rather than left as an internally coherent but unverified sequence of prose. That process surfaced two things prose review alone had not caught, and both are recorded here rather than quietly folded into the narrative as if they had been obvious from the start. First, an early version of the verification logic failed ungracefully on incomplete input rather than escalating — a defect only a dependency-focused test, not a reading of the manuscript, was positioned to catch. Second, tiering the auto-lodge threshold by dispute type (itself a constructed design choice, not a CBA disclosure) revealed a second-order gap: the original escalation logic had no path for a dispute type it could not classify at all, meaning such a case would have silently defaulted into a risk tier it was never actually evaluated against. Both gaps were closed before this repository was finalized (Section 4b), and both are named here as a matter of record, not erased in favor of a cleaner-looking finished product.

---

## 7. Forward-Looking: CommBank in the Agentic Era

> **Editorial analysis.** This section draws on publicly stated positions and should be read as informed projection, not documented fact.

CBA's own December 2025 "Our Approach to Adopting AI" report lays out the bank's stated general direction: continued investment in AI across fraud detection, customer engagement, and internal productivity tools, with human oversight maintained as a stated principle across the named systems it does disclose. *[Source: CBA "Our Approach to Adopting AI," December 2025]* Separately, CBA's April 2026 newsroom post describes an "AI orchestration agent" — a Microsoft-built triage layer that interprets customer intent and routes conversations across more than two million monthly interactions to either an AI capability or a human specialist, explicitly following a defined path for regulated processes and escalating on detected vulnerability or sensitivity. *[Source: CBA newsroom / Microsoft Source Asia, 2026]*

Whether this orchestration layer will eventually absorb or formalize the disputes tool described in Section 3.1 is not stated anywhere in the public record. It is a plausible direction, given that both are customer-facing, intent-routing systems — but it remains this case study's own speculation, not a confirmed roadmap item, and is flagged as such rather than presented as likely.

The more durable observation is the one Section 6.2 already makes at length: CommBank's public AI narrative, watched closely enough, splits cleanly into several separate initiatives with separate owners, separate metrics, and separate timelines. The version of the story that fuses them into one dramatic arc — autonomous agent causes layoffs — is a more satisfying story than the one the primary sources support, and that gap between narrative and record is, itself, the most durable finding a reader should carry forward from this entry into the next one.

---

## Sources

| Source | Type | Notes |
|---|---|---|
| Evident Insights — "167 ways banks use AI" | Primary (named CBA executive quoted) | 20 February 2025. Source of the disputes-tool description and Dan Jermyn's remarks |
| Evident Insights — "Banks go agentic" | Primary-adjacent | 17 April 2025. Corroborates Jermyn's disputes-tool discussion |
| Finance Sector Union — "CBA axes jobs for AI and offshoring" | Primary (FSU's own release) | 29 July 2025. Source of the 90-role/45-role Direct Banking cut, tied to the June 2025 voice bot |
| Finance Sector Union — "WIN: CBA backflips on customer service job cuts" | Primary (FSU's own bulletin) | 21 August 2025. Source of the reversal |
| BankInfoSecurity — "Australian Bank Backtracks on AI-Led Job Cuts" | Secondary | 25 August 2025. CBA's claimed 2,000-calls/week reduction; FSU's dispute of that figure |
| AAP News (via Yahoo Finance / CityNews) — AGM coverage | Secondary, reporting named-executive on-record remarks | 15 October 2025. Chair Paul O'Malley's admission; CEO Matt Comyn's remarks |
| CBA newsroom — "ChatIT recognised in the Microsoft 50 AI Innovators list" | Primary | 26 June 2025. ChatIT metrics and confirmation |
| iTnews — CBA generative AI capabilities coverage | Secondary | 2025. ChatIT employee-interaction figures; Angus Sullivan's disputes-per-day remark |
| CBA newsroom — "Reimagining Banking" | Primary | 28 November 2024. 20-million-payments-a-day figure; 40% wait-time reduction; fraud-alert scaling |
| CBA newsroom — scam-loss reduction announcement | Primary | 14 August 2025. 76% scam-loss reduction figure |
| CBA newsroom — "CommBank develops AI agent that spots new fraud" | Primary | April 2026. Separate fraud-detection agent, human-in-the-loop oversight |
| CBA — "Our Approach to Adopting AI" | Primary | December 2025. CBA's flagship AI disclosure; notably does not mention disputes/chargebacks |
| CBA FY25 Full Year Results Presentation / Profit Announcement | Primary | 13 August 2025. Firm-context and Retail Banking Services figures |
| CBA 2025 Annual Report | Primary | Customer base and group-level figures |
| Australian Broker / APRA MADIS data | Secondary | March 2026. Comparative home-loan market share across Big Four |
| SAP, KPMG, Lyzr, Cognizant vendor/consultancy materials | Secondary (not CBA-attributed) | Reviewed only to confirm "Dispute Resolution Agent" is generic vendor terminology, not a CBA product name |
| University of Wollongong / The Conversation (Mehmet & Nikidehaghani) | Secondary — reviewed and found insufficient on its own | Cites ABC News as its own source for the layoff/reversal claim; not used as a primary source in this case study |
| CommBank Disputes Workflow — Illustrative Reference Implementation (companion repository README) | This case study's own artifact, not a CBA source | Built and tested (14/14 passing); documents its own confirmed-vs-constructed boundaries per Sections 4/4b above |

---

*This case study is part of the series: Agentic AI Adoption in Financial Services (2025–2026). Illustrative workflow scenarios are clearly labeled and constructed from publicly disclosed architectural details. No proprietary CommBank operational data is claimed or represented.*
