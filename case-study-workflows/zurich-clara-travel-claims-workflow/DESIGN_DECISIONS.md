# Design Decisions

This document records every decision made while designing this pipeline that
required judgment beyond what the case study's public-record findings
disclosed — including deliberate deviations from this project's own standing
conventions. It is repo documentation, not an internal process log: it cites
the case study's confirmed findings by section where relevant, and it exists
so a future maintainer understands *why* the code looks the way it does, not
just what it does.

**A scope note that shapes everything below.** This is the thinnest confirmed
record of any system this series has built against. **Five sentences**, in
total, are all Zurich confirms about Clara (case study §3.2). Every prior
entry's reference implementation had at least one quantified confirmed metric
to anchor against — Lemonade's 96%/55% automation split, HSBC's 60%/5×
productivity figures. This one has none. The decisions below should be read
against that scarcity.

---

## 1. Authorization Gate — No Shipped Default

**Decision:** the Authorization Gate ships with zero approval criteria — no
confidence score, no dollar threshold, no claim-type restriction, anywhere in
the codebase, under any `[DEV]` marker. It raises `TypeError` at construction
if no external decision function is supplied, and `ValueError` if that
function returns anything outside the two valid decisions.

**Why:** Zurich states only that Clara keeps *"humans in control where it
matters most"* (case study §3.2). That is a **category, not a boundary** — it
tells you some claims are within the system's resolution authority and some
are not, and discloses nothing about where the line sits.

Inventing one, even labelled `[DEV]`, would imply a *shape* of answer —
"probably severity-based", "probably a dollar amount" — that nothing in the
public record supports. The absence is the honest representation of what is
known.

Consistent with the Lemonade and HSBC precedent, and with DBS's Human Review
Gate.

**Named exception, deliberately not `[DEV]`-marked.** `demo_decision_fn`
exists solely so the pipeline is runnable end to end. It is not a labelled
illustrative placeholder for a real threshold; it is a logged exception with
no claim to represent Clara's actual authority boundary, and it is documented
as such in the module itself.

---

## 2. Extraction and Translation Confidence Are Two Scores, Not One

**Decision:** extraction confidence and translation confidence are tracked as
**separate values**, checked independently, and produce **different named
halt reasons**.

**Why:** this is not a Zurich disclosure. It is this case study's own
non-negotiable design requirement, and it is the one place the build asserts
something the record does not.

A document can be translated with high linguistic confidence and still yield
low-confidence structured extraction — a clean translation of an ambiguous
receipt. The reverse is equally possible: a confident extraction from a
poorly-translated source. **Collapsing the two into a single score would hide
exactly the failure mode the travel-claims scenario exists to surface**, which
is the multi-language, multi-document problem in case study §2.

**Proven, not asserted.** A test drives each failure independently and
confirms the two produce genuinely different reason strings — so the
separation does functional work rather than existing as an unused field.

**What is `[DEV]`:** the specific thresholds (0.70 / 0.70). No source
discloses what threshold, if any, Zurich or AgentricAI use.

---

## 3. One Halt Condition Deliberately Has No Named Reason

**Decision:** eight conditions send a claim to a human. Seven carry a specific
reason string. The eighth — a structurally incomplete intake — returns
`reason: None`.

**Why:** at that point the pipeline has not extracted enough information to
characterise the failure more specifically. A document arrived without a
language tag; naming *which* substantive problem that represents would be
manufacturing detail.

This asymmetry is consistent with Zurich's stated commitment to an auditable
reasoning trail (§3.2): **a system that invents a specific-sounding reason it
cannot support is undermining the exact property it advertises.** The status
flag is honest; a fabricated reason string would not be.

---

## 4. Coverage Check Runs Its Contradiction Test Before Fetching a Policy

**Decision:** the internal order inside Coverage Check is fixed —
contradiction check first, then policy fetch, then the coverage rules, then
the sub-claim dependency check.

**Why:** design review surfaced a genuine ordering gap that a reading of the
design alone had not caught. A claim can trigger a cross-document
contradiction **and** a missing-policy condition simultaneously. Without a
defined precedence, which one fires is an implementation accident — and the
returned reason would vary with refactoring.

The contradiction check runs first specifically because it **requires no
policy lookup at all**. Checking whether a claim's own documents contradict
each other is cheaper and more fundamental than checking it against a record.

**Locked by construction:** a test drives a claim engineered to trigger both
and asserts the contradiction reason, so the ordering cannot silently change.

---

## 5. Coverage Check Fetches Its Own Policy Data — a Logged Departure

**Decision:** Coverage Check calls `mock_data.get_policy_record()` itself
rather than receiving a pre-fetched record from a separate lookup stage.

**Why:** this departs from this project's usual data/logic separation, and
from the DBS precedent where Client Lookup is its own stage.

The alternative was a sixth pipeline stage the blueprint never specified. For
a build resting on five confirmed sentences, adding an undisclosed module to
gain test-isolation cleanliness was judged the worse trade: it would make the
architecture look more resolved than the record supports.

**Why it does not weaken the guarantees:** the halt-condition test suite
independently proves every escalation path fires correctly regardless of where
the fetch occurs. This is a reasoned, logged choice — not an oversight.

---

## 6. Terminal-State Naming Departs From the Series Convention

**Decision:** the Gate returns `resolved_by_human` / `escalated_to_human`
rather than this series' more common `not_authorized`, and rather than DBS's
`cleared_for_finalization`.

**Why:** grounded in Zurich's own phrase, *"keeping humans in control."* That
frames the question as one of **control locus** — who decides — rather than of
authorization or finalization. Importing an authorization framing the
confirmed record does not use would be adding a concept Zurich never applied.

This is the third such logged naming departure in the series.

---

## 7. Two Sourcing Risks the Build Checked and Disclaimed

**A different, unrelated "Clara" exists.** Agent Workflow, by Digital
Workforce Services Plc, is a claims-orchestration product with a documented
architecture: named agents and **confidence thresholds configurable per
decision class**. That is an answer-shaped object sitting exactly where
Zurich's two open questions are, under the same product name, in the same
domain.

**It was not consulted and does not inform this build.** No detail from it
appears anywhere in this pipeline. Anyone encountering a more detailed
technical description of "Clara" elsewhere should treat it as describing a
different product entirely (case study §3.2, §6.3).

**A "modular AI Agents" count belongs to a different Hyper Challenge winner**
— Wangari Global's Etio — not to Clara (case study §6.4). No agent count
appears in this build.

**AgentricAI's own generic marketing claim** about processing time is not
pilot-specific and is not used in this build's reasoning (case study §3.2).

---

## 8. What This Repository Is Not

This is **not a disclosure of AgentricAI's actual Clara system**. It does not
claim to replicate Clara's agent architecture, agent count, or reasoning-trail
mechanism, and it should not be cited as evidence of how Clara works.

It is built from the five confirmed Zurich sentences in case study §3.2, plus
explicitly labelled construction everywhere the public record stops — with the
Authorization Gate's total absence of default criteria standing, as in prior
entries, as the clearest expression of where that record actually ends.

**Known limitations.** Translation is not a real multi-language NLP system.
Mock fixtures carry pre-computed extracted facts and confidence scores,
consistent with this series' deterministic stand-ins for real AI calls. Mock
data only — the Kwame happy path plus six halt scenarios. The three-sub-claim
dependency structure is one illustrative shape of conditional coverage logic,
not a claim about how any real travel-claims system resolves dependent
coverage questions.
