# Morgan Stanley Advisor Tools — Reference Implementation

A working, tested implementation of the two AI tools described in
[`case-studies/10-morgan-stanley-agentic-ai-wealth-management.md`](../../case-studies/10-morgan-stanley-agentic-ai-wealth-management.md):
**AI @ Morgan Stanley Assistant** and **AI @ Morgan Stanley Debrief**.

It runs entirely on fabricated mock data. No external services, no credentials, no network, and
nothing belonging to Morgan Stanley is involved anywhere in this directory.

```bash
cd case-study-workflows/morgan-stanley-advisor-tools-workflow
python3 -m pytest tests -q          # 29 passed
```

---

## What This Is

Morgan Stanley discloses **what** these two tools produce with real specificity — a ~100,000
document corpus, 98% adoption across Financial Advisor teams, retrieval improving from 20% to
80%. It discloses almost nothing about **how** either one works: no retrieval algorithm, no
note-extraction logic, no confidence threshold, no escalation rule.

This implementation is built from the confirmed functions only, with every gap filled by
labelled construction rather than invention dressed as fact. Where the public record stops,
the code stops too, and says so.

## Architecture

**Two independent linear pipelines, not one system with a mode switch.** Assistant and Debrief
are genuinely separate products in Morgan Stanley's own disclosures — launched nine months
apart, serving different functions — and a shared orchestrator would recreate in code the
narrative conflation this series exists to avoid.

```
Pipeline 1 — Assistant
    Query Intake  →  Retrieval  →  Synthesis  →  Handoff

Pipeline 2 — Debrief
    Consent Gate  →  Transcription  →  Live Notes  →  Post-Meeting Draft  →  Handoff
```

The only code shared between them is `tests/helpers.py`, a generic spy-assertion utility with
no narrative content — it describes how to write a Python assertion, not what either tool does.
Mock data stays fully separate, one fixture module per pipeline.

## Module Reference

### `src/assistant/`

| Module | Responsibility |
|---|---|
| `orchestrator_assistant.py` | Runs all four steps in strict order; the only file that knows the full sequence |
| `retrieval.py` | Whole-word keyword match against the mock corpus (**CONSTRUCTED** — the real ranking logic is undisclosed) |
| `synthesis.py` | Assembles a response from retrieved documents (**CONSTRUCTED**) |
| `mock_corpus.py` | Five fabricated research documents standing in for ~100,000 |
| `handoff_assistant.py` | Terminal node — every execution reaches it |

### `src/debrief/`

| Module | Responsibility |
|---|---|
| `orchestrator_debrief.py` | Runs all five steps in strict order |
| `consent_gate.py` | Checks the client-consent precondition before anything else runs |
| `transcription.py` | Stands in for Whisper (**CONSTRUCTED**) |
| `live_notes.py` | Note and action-item extraction (**CONSTRUCTED**) |
| `post_meeting_draft.py` | Produces the summary, the email, and the Salesforce note |
| `mock_transcript_source.py` | Fabricated meeting transcripts |
| `handoff_debrief.py` | Terminal node — every execution reaches it |

## The Central Design Decision: No Authorization Gate

Lemonade's AI Jim and HSBC's coding assistants each required a **structurally empty gate** —
one with zero default approval criteria — because each has a confirmed *category* of restricted
autonomy with an *undisclosed boundary*.

Morgan Stanley's record has a different shape. There is **no confirmed instance, anywhere in
the public record, of either tool taking a client-facing action autonomously** — not a gated
exception, but a stated universal property. Building an evaluative gate here, even an empty
one, would invent an autonomy pathway the record does not support.

So both pipelines terminate at a **structural handoff node** that every execution reaches
unconditionally. There is no gate logic and no bypass path, because there is nothing to gate.

## Naming: `cleared` / `not cleared`, Not `authorized`

`consent_gate.py` departs from this series' usual `authorized` / `not_authorized` convention,
and the reason is specific to this case rather than inherited from the previous two departures.

**Consent is a client-granted precondition, not a decision anyone at Morgan Stanley makes.**
Naming it `authorized` would imply an evaluative judgement call that does not exist here.
`cleared` reflects a fact being checked, not a decision being rendered.

## The Email/Salesforce Distinction — and Why It Has Its Own Test

Morgan Stanley's launch release does not treat Debrief's two post-meeting outputs identically:

> After the meeting, it summarizes key points, **creates an email for an Advisor to edit and
> send at their discretion**, and **saves a note into Salesforce**.

Three parallel verbs, and a ten-word qualifier on exactly one of them. The email waits for a
person; the note does not. It is the only one of Debrief's outputs confirmed **finished**
rather than pending, and it is bounded to internal record-keeping — nothing client-facing.

An early pass at this build treated both outputs alike before a review pass against the source
surfaced the difference. The code now reflects it — `email_status` is always
`"awaiting_advisor_action"`, `salesforce_note_status` is always `"saved"` — and one test exists
purely so it cannot quietly collapse again:

```python
assert result["email_status"] != result["salesforce_note_status"]
```

That line checks neither value. Other tests do that. It asserts only that the two can never
become the same thing, so a future tidy-up cannot merge them without the suite failing.

## What the Tests Prove

**29 tests across 10 files.** Sequencing is proven by **spy assertion**, not inferred from
output shape — an incomplete query or a failed consent check is shown to halt the pipeline
*before* any downstream function is invoked.

| | |
|---|---|
| **Halt maps** | Assistant has three states (intake incomplete / no match / clean run); Debrief halts at a failed consent gate |
| **The distinction** | the two statuses are asserted never equal on a clean run |
| **Structural absence** | four modules carry an attribute-absence check proving no `send`, `finalize`, `submit`, `dispatch` — or `write`, on the Debrief side — function exists |

### A real bug the suite caught

`retrieval.py` originally matched titles by substring, so the corpus title word **"Net"**
matched inside **"Netherlands"** — returning a bank net-interest-margin document for a query
about tulip bulbs. Fixed by matching against a set of whole query words. It was invisible in
prose and in spec review, and appeared the moment code ran against a real test case.

## Known Limitations

**The Salesforce note's `"saved"` status is a label, not a receipt.** No code in this directory
writes to a real or mock Salesforce API; there is no `salesforce_write.py`. The status exists
to represent Morgan Stanley's own disclosed characterisation of Debrief's behaviour, not to
claim this implementation performs that write. Extending this toward production would require
that write to become a real, independently tested function.

**The absence check reads a module's own namespace.** It catches `from x import send`; it would
not catch `import x` followed by `x.send()`. Every module here uses from-imports, so the check
does see through today — but that is a property of the current import style, not of the test.

**The `write` guard is asymmetric.** It is enforced on the two Debrief modules and not on the
two Assistant ones. The property holds on all four — the full word list returns no matches
anywhere — but on the Assistant side it holds by construction rather than by guard. Recorded
here rather than quietly corrected, because the gap between *true* and *enforced* is the more
useful thing to see.

## Explicit Non-Claims

- **Not a disclosure of Morgan Stanley's architecture.** Nothing here should be cited as
  evidence of their technical design.
- **Does not replicate** the Assistant's real retrieval or synthesis mechanism, Debrief's real
  transcription or note-extraction process, or any real data infrastructure.
- **The mock corpus and transcripts are fabricated.** Five documents stand in for ~100,000.
- **No confidence threshold, escalation trigger, or error-handling path is invented**, because
  Morgan Stanley discloses what each tool produces, not how it handles ambiguity or failure.

## Further Reading

- [`DESIGN_DECISIONS.md`](DESIGN_DECISIONS.md) — nine logged departures and trade-offs, each traced to its source
- [`DESIGN_SPECS.md`](DESIGN_SPECS.md) — module contracts and signatures
- [`../../case-studies/10-morgan-stanley-agentic-ai-wealth-management.md`](../../case-studies/10-morgan-stanley-agentic-ai-wealth-management.md) — the case study this implements
