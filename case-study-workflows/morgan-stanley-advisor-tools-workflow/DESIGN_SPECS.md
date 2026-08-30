# Design Specs

Component contracts as built and tested. Where these differ from the
pre-build `/v3` spec cards, this document reflects what was actually built,
per `DESIGN_DECISIONS.md` items 5 and 7 in particular.

---

## Pipeline 1 — Assistant

| Module | Function | Signature | Confirmed / Constructed |
|---|---|---|---|
| `mock_corpus.py` | `get_corpus()` | `() -> list[dict]` | CONSTRUCTED — fabricated corpus standing in for the confirmed ~100,000-document real corpus |
| `retrieval.py` | `retrieve()` | `(query: str, corpus: list[dict]) -> RetrievalResult` | Retrieval capability CONFIRMED; matching mechanism `[DEV]` CONSTRUCTED |
| `synthesis.py` | `synthesize()` | `(matches: list[dict]) -> SynthesisResult` | Synthesis capability CONFIRMED; internal mechanism `[DEV]` CONSTRUCTED |
| `handoff_assistant.py` | `handoff_to_advisor()` | `(synthesis_result, match_found: bool) -> dict` | CONSTRUCTED stub; exposes no send/finalize function |
| `orchestrator_assistant.py` | `run_assistant_pipeline()` | `(query: str) -> dict` | Sequencing mirrors confirmed shape; Query Intake validation CONSTRUCTED |

**Halt map:**

| # | Condition | Halts before | Mechanism |
|---|---|---|---|
| 1 | Empty/missing query | Retrieval | Returns `{"status": "intake_incomplete"}` |
| 2 | No retrieval match | Synthesis | Returns `{"status": "no_match_found"}` |
| 3 | Clean run | — | Reaches `{"status": "handed_off_to_advisor", ...}` |

---

## Pipeline 2 — Debrief

| Module | Function | Signature | Confirmed / Constructed |
|---|---|---|---|
| `mock_transcript_source.py` | `get_transcript()` | `(with_action_items: bool) -> dict` | CONSTRUCTED — fabricated fixtures, no real meeting content |
| `consent_gate.py` | `check_consent()` | `(consent_flag: bool) -> ConsentResult` | Precondition CONFIRMED; data representation `[DEV]` CONSTRUCTED |
| `transcription.py` | `transcribe()` | `(transcript_fixture: dict) -> TranscriptionResult` | Whisper-based transcription CONFIRMED; mock structure `[DEV]` CONSTRUCTED |
| `live_notes.py` | `extract_live_notes()` | `(transcription_result: TranscriptionResult) -> LiveNotesResult` | Note/action-item generation CONFIRMED; extraction mechanism `[DEV]` CONSTRUCTED |
| `post_meeting_draft.py` | `draft_post_meeting_outputs()` | `(live_notes_result: LiveNotesResult) -> PostMeetingDraft` | Summary/email/note existence CONFIRMED; content-generation mechanism `[DEV]` CONSTRUCTED; `email_status`/`salesforce_note_status` distinction CONFIRMED (see DESIGN_DECISIONS.md #5) |
| `handoff_debrief.py` | `handoff_to_advisor()` | `(draft: PostMeetingDraft, consent_cleared: bool) -> dict` | CONSTRUCTED stub; exposes no send/finalize/write function |
| `orchestrator_debrief.py` | `run_debrief_pipeline()` | `(consent_flag: bool, transcript_fixture: dict) -> dict` | Sequencing mirrors confirmed shape |

**Halt map:**

| # | Condition | Halts before | Mechanism |
|---|---|---|---|
| 1 | Consent not given | Transcription | Returns `{"status": "consent_not_given"}` |
| 2 | Clean run | — | Reaches `{"status": "handed_off_to_advisor", "email_status": "awaiting_advisor_action", "salesforce_note_status": "saved", ...}` |

---

## Naming Departures From Series Convention (see DESIGN_DECISIONS.md for full reasoning)

- `consent_gate.py`: `cleared` / not `cleared` — a third, distinct reason for departing from `authorized`/`not_authorized`, separate from HSBC's and DBS's departures.
- No entry uses the Lemonade/HSBC "empty gate" pattern — this entry has no gate on its output side at all, by design (see DESIGN_DECISIONS.md #1).

## What the Tests Prove

- 29 tests across 10 test files, all passing, run both individually and confirmed with no cross-file state leakage.
- Every halt condition in both pipelines is proven via spy assertion that the next stage was never called — not just that the final output looks halted.
- Both orchestrators have an explicit attribute-absence test proving no `send`/`finalize`/`submit`/`dispatch`/`write` function exists anywhere in the module or its imports.
- `test_post_meeting_draft.py` and `test_orchestrator_debrief.py` explicitly assert `email_status != salesforce_note_status` on every clean run — a regression that flattened these back to one status, undoing DESIGN_DECISIONS.md #5, would fail this test immediately.
- A real bug (substring-match false positive in `retrieval.py`) was caught by `test_retrieval.py` during the build, not left latent — see DESIGN_DECISIONS.md #9.
