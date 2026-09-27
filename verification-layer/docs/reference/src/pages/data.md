---
title: Records and statuses
slug: data
section: Reference
order: 30
summary: The shape of what is stored — attempts, sessions, runs, comparison rows, checks, gate state — and every status value, with where each is defined.
---

## An attempt: `ReasoningObject`

One per agent per attempt, defined in [[core/schemas.py]] as a frozen dataclass that validates
itself when built.

| Field | Notes | Investor scope |
|---|---|---|
| `run_id`, `agent_id`, `attempt_number` (1 or 2) | identity | shown |
| `parse_status` | `SUCCESS`, `PARSE_FAILURE`, `HALT`; attempt 2 is never `PARSE_FAILURE` | shown |
| `confidence_score` | 0 to 1, rounded to 4 places | shown |
| `conclusion`, `reasoning_steps`, `citations`, `data_sources` | `SUCCESS` requires a conclusion | shown, except while a gate is pending |
| `directive_version` | the directive actually used for this attempt | shown |
| `directive_text`, `context_window` | what the agent was told and given | **omitted** |
| `thought_log`, `raw_output`, `llm_tokens` | the reasoning, the verbatim reply, usage | **omitted** |
| `assessment`, `assessment_status`, `assessment_issues`, `assessment_source` | a model judgment | **omitted** |
| `created_at` | timezone-aware UTC | shown |

Internal-tier keys are left out at investor scope rather than set to null, so a reader can tell
"withheld" from "the model produced nothing" ([D-44](decisions.html#d-44)).

## A run: `RunSession` and the stored payload

`RunSession` ([[core/schemas.py]]) holds the ticker (uppercased, at most 10 characters), the
directive version and verbatim text, the status (`OPEN`, `COMPLETE`, `HALTED`), the timestamps,
the run confidence and its classification, and the reasoning objects.

The stored run ([[web/db.py]], `runs.payload_json`) is the route's whole response:

| Key | Chat | Compare |
|---|---|---|
| `run_id`, `subject`, `scope`, `halted`, `error`, `session`, `reasoning_objects`, `steps` | yes | yes |
| `conclusion`, `thought_log`, `confidence_*`, `data_sources`, `config_snapshot`, `consistency` | yes | |
| `claims`, `verification_rate` | one | `{a, b}` |
| `ticker`, `producers`, `contexts`, `facts` | | yes |
| `cross_agent_comparison` | | yes: status, rule, flag, `metric_comparisons`, `structural_flags`, `synthesis` |
| `gate_policy`, `gate` | | yes (the gate is computed on read) |
| `tool_capability_warning` | yes | yes |

## Status values

| Vocabulary | Values | Defined in |
|---|---|---|
| Attempt parse status | `SUCCESS`, `PARSE_FAILURE`, `HALT` | [[core/schemas.py]] |
| Run status | `OPEN`, `COMPLETE`, `HALTED` | [[core/schemas.py]] |
| Confidence class | `STANDARD`, `HIGH_UNCERTAINTY_SPECULATIVE` (below 0.4) | [[core/schemas.py]] |
| Data source status | `live`, `simulated`, `failed`, `cached` | [[core/schemas.py]] |
| Agent ids | `financial`, `earnings`, `bull`, `bear`, `external`, `generic_a`, `generic_b`, `patent`, `competitive`, `AAN` | [[core/schemas.py]] |
| Figure row status | `MATCH`, `MISMATCH`, `DIFFERENT_PERIODS`, `UNVERIFIABLE_PERIOD`, `CITED_BY_ONE`, `ONE_SIDED`, `UNCORROBORATED`, `DERIVED_OK`, `DERIVED_WRONG` | [[validation/facts.py]] |
| Check outcome | `pass`, `fail`, `skipped`; kind `hard` or `heuristic`; scope `agent_a`, `agent_b`, `source` | [[validation/constraints.py]] |
| Conflict driver | `data`, `assumption`, `weighting`, `insufficient`, `none` | [[validation/divergence.py]] |
| Assessment status | `valid`, `partial`, `invalid_fields`, `invalid_json`, `unclosed`, `empty`, `absent`, `abstained`, `extraction_failed` | [[core/assessment.py]] |
| Grade / direction | `AAA` … `CCC` / `buy`, `hold`, `sell` | [[core/assessment.py]] |
| Gate status | `NOT_GATED`, `NO_DECISION_NEEDED`, `AWAITING_DECISION`, `DECIDED` | [[validation/gate.py]] |
| Gate item kind | `figure`, `check`, `grade` | [[validation/gate.py]] |
| Decision | `accept_a`, `accept_b`, `both_wrong`, `not_a_conflict`, `override_value`, `confirmed_error`, `set_grade` | [[validation/gate.py]] |
| Reviewer flag | `Hallucinated`, `Incorrect`, `Other` | [[web/db.py]] |
| Step phase / kind | `shared`, `agent_a`, `agent_b`, `compare`, `chat` / `fetch`, `llm`, `extract`, `tool`, `compare` | [[web/step_trace.py]] |
| Ledger status | `OPEN`, `UNVERIFIED`, `RESOLVED`, `BY_DESIGN` | [[web/self_report.py]] |

## Policy and format ids

A stored run records which rules produced it:

| Id | Value | Set by |
|---|---|---|
| directive | `v1.5.2` (active) | [[core/directive.py]] |
| extraction prompt | `assess-extract-v2` | [[core/assessment.py]] |
| lens versions | `v2` (financial, earnings), `v1` (bull, bear) | [[producers/lens.py]] |
| checks | `b3-v1` | [[validation/constraints.py]] |
| synthesis | `b5-v1` | [[validation/divergence.py]] |
| gate | `v3` | [[validation/gate.py]] |
| audit format | `audit-v1` | [[validation/audit.py]] |

The type the review app reads is [[web/frontend/src/api/types.ts]]; every field added after the
first release is optional there, so older records still render.
