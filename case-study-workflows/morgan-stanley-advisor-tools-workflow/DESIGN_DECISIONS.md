# Design Decisions

This document exists because this series treats deliberate departures from
convention, and genuine trade-offs, as things to log — not absorb silently.
Every entry below is traced to its source: case study text, engineering
necessity, or series convention.

---

## 1. No authorization/settlement gate of the Lemonade/HSBC shape

**Source:** Case study Section 5 (blueprint) / manuscript Section 4's finding
that neither tool is described as acting autonomously on a client-facing or
account-modifying basis under any circumstance.

Lemonade's AI Jim and HSBC's coding assistants each had a confirmed
*category* of restricted autonomy with an *undisclosed boundary* — the
honest engineering response was an empty gate, structurally unable to hide
that absence. Morgan Stanley's confirmed record has a different shape: there
is no confirmed instance of either Assistant or Debrief acting autonomously
on a client-facing basis, stated as a universal property, not a conditional
one. Building an authorization gate here would invent an autonomy pathway
the record doesn't support. Both pipelines instead terminate at a
**structural terminal node** — `handoff_assistant.py` and
`handoff_debrief.py` — that every execution reaches, with no gate logic and
no bypass path.

---

## 2. Two separate `handoff_*.py` files, not one shared module

**Source:** Architecture Section 4 (blueprint) — Assistant and Debrief are
genuinely separate tools, and a shared orchestrator or shared core module
would recreate, in code, the narrative conflation this series' editorial
discipline exists to avoid.

A shared `handoff.py` is shared *infrastructure*, but importing from a
common module creates a real release-cycle coupling between two tools the
case study treats as independent. The duplication cost (two small terminal
stubs) is trivial next to the cost of quietly re-coupling what Section 4
explicitly keeps separate. `handoff_assistant.py` and `handoff_debrief.py`
are separate files with no shared import between them.

---

## 3. Shared test helpers (`tests/helpers.py`), separate mock data per pipeline

**Source:** Engineering necessity, weighed against decision #2's reasoning.

The "no shared code" discipline exists to protect the *narrative* — mock
corpus content, transcript content, and anything describing what either
tool actually does must stay separate, because a shared data fixture would
be a real step toward conflating the two tools. A generic spy-assertion
helper (`assert_never_called`, `assert_called_once`) carries no narrative
content — it describes how to write a Python test assertion, not what
either tool does. Sharing it costs nothing in conflation risk and saves
duplicated boilerplate. Mock data fixtures (`mock_corpus.py`,
`mock_transcript_source.py`) remain fully separate, one per pipeline.

---

## 4. Terminal-state shape: absence, not a guard

**Source:** Blueprint Section 5's requirement that tests prove "no code path
exists" from synthesis/drafting to a sent/finalized state, as a structural
property rather than a business-logic outcome.

Two candidates were considered: (a) no send/finalize function exists
anywhere in either pipeline's codebase, or (b) a send/finalize function
exists but is deliberately never wired into the orchestrator, tested via an
explicit "never called" assertion. (b) was rejected: writing a decoy
send/finalize function this repository has no reason to contain, purely to
prove it isn't used, invents a capability neither Assistant nor Debrief is
confirmed to have in-pipeline at all — Morgan Stanley's own language places
sending and finalizing in the advisor's own separate tools (their email
client, their Salesforce access), not in this pipeline. (a) was built: no
function named `send`, `finalize`, `submit`, `dispatch`, or `write` exists
anywhere in `handoff_assistant.py`, `handoff_debrief.py`, or either
orchestrator. Every test suite for these four modules includes an explicit
attribute-absence check enforcing this, not just the standard spy
assertions.

---

## 5. The Salesforce note is `"saved"`, the email is `"awaiting_advisor_action"` — and neither status implies a real write

**Source:** A contradiction caught in `/review` Pass 1 between the case
study's own workflow table and the blueprint's pipeline description.

The case study's workflow table (Section 4, Scenario B) states the
Salesforce note-save as **"Autonomous (confirmed function)"** — distinct
from the follow-up email, which is confirmed **non-autonomous** ("for an
Advisor to edit and send at their discretion"). The blueprint's Section 4
pipeline description had flattened both into one "draft ... awaiting
advisor edit/send decision" bundle, which misrepresents the Salesforce
note's confirmed autonomy. `post_meeting_draft.py` and `handoff_debrief.py`
were built to reflect the actual distinction: `email_status` is always
`"awaiting_advisor_action"`; `salesforce_note_status` is always `"saved"`.

**Stated plainly, because this is a real limitation, not a footnote:** the
`"saved"` status is asserted by the mock, not produced by an executing
write to any real or mock Salesforce API. No `salesforce_write.py` module
exists in this repository. This was a deliberate choice (reference
implementation illustrating a confirmed distinction between two output
types, not a system that needs to actually perform a Salesforce write to
make that point) — not an oversight. If this codebase were ever extended
toward a production-adjacent context, that write would need to become a
real, independently tested function, not a status string.

---

## 6. `consent_gate.py` uses `cleared` / not `cleared`, not `authorized` / `not_authorized`

**Source:** Case study Section 4 Scenario B Step 1 — "With Mr. Alvarez's
consent, Debrief records and transcribes the meeting" — plus a distinction
surfaced in `/review` Pass 3 from this series' prior naming departures
(HSBC's `not_approved`, DBS's `cleared_for_finalization`).

This is a third, distinct reason for departing from the series' general
`authorized`/`not_authorized` convention — not a restatement of either prior
departure. Consent is a client-granted precondition, not a decision anyone
at Morgan Stanley, or in this code, makes or withholds. Naming it
`authorized`/`not_authorized` would imply an evaluative judgment call that
doesn't exist here; `cleared` reflects a fact being checked, not a decision
being rendered.

---

## 7. Query Intake is a real halt, not an unspecified edge case

**Source:** Caught in `/review` Pass 3 as a gap in the design itself — every
other halt condition in both pipelines had a defined failure state and a
spy-test obligation; Query Intake's validation did not, until this pass.

An empty or missing query now returns `{"status": "intake_incomplete"}`,
and `retrieval.py`/`synthesis.py` are asserted never called via
`test_orchestrator_assistant.py`. This gives Pipeline 1 a three-state halt
map (intake incomplete / no match / clean run), matching the level of
rigor already present in Pipeline 2's halt map.

---

## 8. No series-ordinal or series-position claim appears anywhere in this repository

**Source:** Unresolved discrepancy in the blueprint's own header, which
first stated this as "the eighth entry" (naming Goldman Sachs and JPMorgan
Chase as prior entries not reflected in the "prior reference
implementations" test-count list), then "the tenth entry" on a second,
explicitly uncertain pass ("might have been a typing error").

Given two different unverified counts were offered for the same claim, no
number is used. This entry is referred to only as "the Morgan Stanley
entry" throughout this repository's documentation. If a verified series
position becomes available, this line should be the single place updated.

---

## 9. A real bug the test suite caught before this document was written

**Source:** `retrieval.py`'s initial keyword-matching implementation used a
substring check (`word.lower() in query_lower`) rather than a whole-word
check. This caused a false-positive match: the title word "Net" (from
"Regional Banking Net Interest Margin Trends") matched as a substring
inside the word "Netherlands" in an unrelated test query, incorrectly
returning a match for a query about tulip bulbs. Fixed by matching against
a set of whole query words (`query_words = set(query_lower.split())`)
instead of substring containment. This is exactly the category of gap this
series' retrospectives consistently name: invisible in prose and spec-card
review, caught the moment code actually ran against a real test case.
