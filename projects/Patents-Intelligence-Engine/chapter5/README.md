# Investment Research Desk

A personal research desk for interrogating investment theses before they become trades. The desk splits fluent claims from verified evidence, tracks what would need to be true for each claim to hold, and keeps the buy/hold/sell decision where it belongs — with a human who can defend it.

This is process, not picks. Nothing in this repository is investment advice.

## How this repo is organized

**This is not one folder per chapter.** Each chapter's exercises build directly on the files the previous chapter produced — the same way the book itself is designed. Chapter 2 extends Chapter 1's thesis; Chapter 3 fixes where Chapter 2's claims are allowed to come from; Chapter 4 binds a recipe to Chapter 3's sources. So the working files accumulate in place, chapter by chapter, rather than existing as separate snapshots.

Here's what each file resolves, and which chapter added it:

| File | Added in | What it is |
|---|---|---|
| `CANNOT-KNOW.md` | Ch.1 | The charter — risk tolerance, time horizon, exit signal — written by the human, never AI. |
| `theses/STM.md` | Ch.1, updated in Ch.2 and Ch.5 | The claim-audit: every claim in the thesis, tagged verified/inferred/unsupported/taste/needs-a-source. Ch.2 added real evidence that upgraded one claim's tag. Ch.5's adequacy audit then corrected that same tag downward after finding the comparison set was only half-complete. |
| `theses/effort-plan-STM.md` | Ch.2 | Ranks the open items from the claim-audit by whether they'd actually change the decision. Separates signal from noise. |
| `BACKLOG.md` | Ch.2 | The noise items relocated out of the effort plan, kept visible instead of deleted. |
| `sources-of-truth.md` | Ch.3 | Ranks every source actually used so far into source-of-truth / context-only / not-a-source. |
| `evidence/*.md` (contract stubs) | Ch.3 | One data-contract template per decision-moving metric from the effort plan — source, period, entity, version, owner — cells deliberately left blank until a human ties them to the real source. |
| `theses/agent-recipe-STM.md` | Ch.4 | The machine's job only: gather + compute, with named inputs and explicit stop conditions. Ends in a STOP before any interpretation. |
| `theses/human-card-STM.md` | Ch.4, updated in Ch.5 | The human's job only: purpose, caveats, open questions, and an empty decision block. Reads the agent recipe's output; never fills its own decision. Ch.5 updated the open-questions log after the evidence audit corrected a prior claim's evidentiary status. |
| `theses/evidence-audit-STM.md` | Ch.5 | Audits each metric and signal on the human card against six adequacy dimensions (completeness, freshness, control totals, mapping, threshold logic, contradiction). Caught a real error: claim 5 in `STM.md` had been tagged more confidently than the evidence supported. |
| `evidence/ch*-ex5-validation-record.md` | Each chapter's Ex.5 | A record of validating that chapter's own artifact against its checklist — kept separate per chapter since each one validates a specific prior output. |

**The rule of thumb:** working files (`theses/`, `sources-of-truth.md`, `CANNOT-KNOW.md`) accumulate and get updated by later chapters. Validation records (`evidence/ch*-ex5-*`) are chapter-specific snapshots and don't get overwritten — each one documents a decision made at a point in time.

## Contents

- `theses/` — the claim-audit, effort plan, agent recipe, and human card — one evolving thread per ticker
- `evidence/` — data-contract stubs and per-chapter validation records
- `signals/` — reserved for options-chain and market-signal data (empty until a signal-based thesis exists)
- `CANNOT-KNOW.md` — the charter of what no model or market chatter can determine for me
- `sources-of-truth.md` — the ranked list of what counts as evidence on this desk
- `CLAUDE.md` — the standing rules governing AI's role in this desk, one added per chapter
