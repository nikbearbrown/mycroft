# Design Decisions

This document records every decision made while designing this pipeline that
required judgment beyond what the case study's public-record findings
disclosed — including deliberate deviations from this project's own standing
conventions. It is repo documentation, not an internal process log: it cites
the case study's confirmed findings by section where relevant, and it exists
so a future maintainer understands *why* the code looks the way it does, not
just what it does.

---

## 1. Human Review Gate — No Shipped Default

**Decision:** the Human Review Gate ships with zero review criteria — no
confidence score, no dollar threshold, no severity rule, anywhere in the
codebase, under any `[DEV]` marker. It raises `TypeError` at construction if
no external decision function is supplied.

**Why:** DBS has not disclosed a review protocol, sign-off requirement, or
approval gate specific to agent-drafted credit memos (case study Sections 3.3
and 6.1). What the public record *does* contain is a direct, on-the-record
statement from DBS's Chief Data and Transformation Officer, Nimish
Panchmatia: capability innovation is currently outpacing governance and
control roughly five to one, and "we need to close this gap before we allow
autonomy" (Section 6.3). Inventing a labeled placeholder here would have made
the Gate easier to demonstrate, and it would also have quietly implied a shape
of answer. A dollar threshold implies DBS's process is exposure-based; a
confidence cutoff implies it is model-score-based. Nothing in the public
record supports either. Where DBS itself states this gap is unresolved, this
implementation does not resolve it.

**Precedent:** the same pattern this series used for Lemonade's Authorization
Gate and HSBC's Human Review Gate, for the same reason — a mechanism the
company reports outcomes for but has never described.

**What this costs:** the repo cannot ship a runnable end-to-end demo that
"just works" out of the box. Every caller must supply a decision function
first. That friction is the point at which an implementer is forced to notice
this is the part DBS never told anyone.

---

## 2. The Gate Validates Its Decision Function's Return Value

**Decision:** `HumanReviewGate.review()` raises `ValueError` if the supplied
decision function returns anything other than the two recognized outcomes.

**Why:** this is distinct from the `TypeError` in Decision 1, which covers
misuse of the construction API — nothing supplied at all. This covers a
supplied function that runs but answers with something unrecognized: a typo,
a refactored constant, a wrapper returning `None` on an internal error. Left
unvalidated, an unrecognized value would fall through and the pipeline would
proceed to finalization **by default rather than by any deliberate answer** —
failing open, which is the exact failure mode a zero-default gate exists to
prevent. A gate that shrugs when it is confused is not a gate.

**Not disclosed by DBS, and not claimed to be.** This is a defensive
engineering measure protecting Decision 1 from a caller's mistake, not a
representation of DBS's system. The test suite exercises it specifically.

---

## 3. Five-Condition State Machine, Not the Four Stages Originally Scoped

**Decision:** the pipeline is
`Intake → Client Lookup → Draft Synthesis → Human Review Gate →
Finalize/Submit`, with five distinct halt conditions.

**Why:** the pre-build scope described four stages, folding client lookup into
draft synthesis. Keeping Draft Synthesis a **pure function** — one that
receives an already-fetched client record rather than fetching data itself —
required client lookup to become its own stage with its own halt condition,
distinct from intake validation. This is recorded as a genuine refinement
discovered during the build, not a departure from the case study's narrative:
the underlying shape Section 4 establishes (raw data in, review-ready draft
out, human review, then handoff to an undisclosed downstream process) is
unchanged. Only the internal decomposition became more precise once the code
had to actually run.

**Scope note:** this decomposition is *ours*. DBS has not disclosed its
internal architecture, and these five stages should not be read as a claim
about it.

---

## 4. `cleared_for_finalization`, Not the Series' Usual `not_authorized`

**Decision:** the Gate's outcomes are `cleared_for_finalization` and
`not_cleared_for_finalization`, deviating from this series' `authorized` /
`not_authorized` convention.

**Why:** "authorize" implies a credit decision this gate does not make.
Section 4, Step 5 states that a finalized memo enters DBS's separate,
undisclosed credit-approval process *after* this point — a process this code
does not model. What the gate decides is narrower: whether the draft is fit to
proceed into that process at all. The naming reflects Section 4's own language
("finalises the memo") rather than importing a stronger word from a sibling
repo.

**Worth stating precisely rather than smoothing over:** Section 4's illustrated
workflow **never depicts a rejection.** The relationship manager reviews,
edits, finalizes, and submits along one continuous path; nobody is ever turned
down. The `not_cleared_for_finalization` outcome is therefore constructed from
Panchmatia's governance-gap statement, not from a worked rejection scenario in
the case study. The *naming* is source-grounded; the *existence of a rejection
path* is a reasoned construction, and this document states that distinction
rather than blurring it.

---

## 5. Draft Synthesis Does Not Decompose Into 70 Tasks

**Decision:** `synthesize_draft()` is a deterministic stand-in that produces a
draft from a client record. It does not enumerate, simulate, or orchestrate 70
discrete tasks.

**Why:** DBS describes specialised agents tackling "more than 70 different
tasks" in aggregate and discloses no breakdown of what those tasks are, what
data sources they query, or how they divide labour (Sections 3.3 and 6.2).
Inventing a 70-item task list would fabricate the most-requested detail in the
entire disclosure. The confirmed capability is treated as a single unit
because that is how it was confirmed.

**A distinction this repo does not blur:** "70+" is a **task** count, not an
agent count. No DBS source states how many agents exist. A secondary source
characterises it as "70 to 80 agents"; that is a journalist's rendering of an
interview, and Section 6.2 keeps the two figures apart rather than merging
them. This code makes no claim about agent count at all.

---

## 6. Constructed Mechanisms, Each Labeled In Place

**Decision:** four mechanisms are inventions, and each is marked `CONSTRUCTED`
in its own source file rather than only in documentation:

| Mechanism | Why it exists | What DBS disclosed |
|---|---|---|
| Intake schema (`client_id`, `facility_type`, `requested_action`) | a memo has to start somewhere | no request schema |
| Client lookup against mock records | Draft Synthesis must receive a record | no data-source list beyond "raw data" |
| Data-gap detection | DBS calls the output "review-ready", implying a completeness check precedes review | no gap-handling behaviour |
| Finalize/Submit stub | Section 4 ends at handoff | no downstream process description |

**Why label in the file rather than only here:** documentation is read once;
source is read every time someone changes it. A reader who opens
`intake.py` without this document should still see immediately that the three
required fields are ours.

---

## 7. One Deliberately Incomplete Mock Record

**Decision:** `mock_data.py` contains one client record with a missing field,
used to exercise the gap-flagged halt path.

**Why:** without it, the data-gap branch would be untested code. Its presence
is a test fixture, not a claim that DBS's client data is incomplete.

---

## 8. Standard-Library `unittest`, No Dependencies

**Decision:** each module has a companion test file using only the standard
library; each test file runs standalone.

**Why:** consistent with the sibling workflows in this series, and it keeps the
repo runnable with no install step. Tests assert **sequencing via mock spies**
— that a downstream stage was never called once an earlier stage halted — not
merely that the returned status looks right. A pipeline can return the correct
final status while still having executed work it should have skipped.

---

## 9. What This Repository Does Not Model

- DBS's actual agent architecture, agent count, task breakdown, or data sources
- Any real LLM call, credit data, or DBS system
- Throughput at institutional-banking scale — this models one memo's path
- DBS's downstream credit-approval process, which begins after this pipeline ends
- Any autonomous approval or settlement step. DBS has not disclosed that the
  system extends any credit decision, approves any facility, or finalises a
  memo without human review, and Panchmatia's governance statement is a direct
  signal against assuming one.

This repository is **not** a disclosure of DBS's actual credit-memo system. It
is built from what DBS has publicly confirmed, plus explicitly labeled
construction everywhere the public record stops — with the Human Review Gate's
total absence of default criteria standing as the clearest expression of where
that record actually ends.
