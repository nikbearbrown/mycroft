---
title: The validation loop
slug: f-validation-loop
section: Features
order: 20
summary: The output contract every agent reply must meet, the directives that state it, and the one-retry-then-halt loop that enforces it (ADR-07).
---

Every agent attempt, in chat and in both lanes of a compare, goes through one loop:
`run_validation_loop` in [[pipeline/middleware.py]]. It is the oldest part of the system and the
best tested.

## The output contract

A valid reply is exactly two blocks, in order, with nothing outside them:

```
<thought_log>
... the agent's reasoning, with [SOURCE: label, url] citations ...
</thought_log>
<conclusion>
... the answer ...
</conclusion>
```

[[core/parsing.py]] checks this structurally ([D-06](decisions.html#d-06)):

- both blocks must be present, each starting on its own line;
- `<conclusion>` is searched only after `</thought_log>`, so a model describing the format inside
  its reasoning doesn't produce a false match;
- any text outside the two blocks is a failure;
- a conclusion that is empty, or copies eight or more consecutive words of the directive, is a
  failure too ([D-09](decisions.html#d-09)). Copying was seen live: 7 of 10 stored v1.5.0 compare
  conclusions echoed the directive, per the record;
- for a directive that asks for it, an `<assessment>` block may follow `</conclusion>`. No active
  directive asks for it today (see below).

A failure raises `StructuralParseError` with the raw text attached, so the record keeps what the
model actually said.

## Directives

The directive is the system prompt that states the contract. Directives are code, versioned in
[[core/directive.py]], and never edited in place: a change is a new version
([D-08](decisions.html#d-08)). Each attempt records the directive version and text it was given,
so a stored run shows exactly what the model was told.

- **Active: v1.5.2.** `ACTIVE_DIRECTIVE` in [[core/directive.py]].
- **Registered but reverted: v1.6.0**, which asked the model to write the assessment block itself.
  Made active on 2026-09-26, it cut format compliance to 2 of 10 live runs and was reverted the
  same day ([D-10](decisions.html#d-10)). Assessments now come from a separate call
  ([D-11](decisions.html#d-11)).
- **The corrective directive** used on a retry lives in [[pipeline/middleware.py]].

## One retry, then halt (ADR-07)

1. **Attempt 1** runs with the active directive.
2. If the reply parses, the loop returns it: status `SUCCESS`.
3. If not, the attempt is recorded as `PARSE_FAILURE`, and **attempt 2** runs with the corrective
   directive: a fixed instruction that the previous response failed structural validation and
   must use the two blocks exactly. It doesn't say what was wrong with the first reply.
4. If attempt 2 fails too, it is recorded as `HALT` and the loop raises `HaltError` carrying every
   attempt's reasoning object. The route stores the run as halted.

Every attempt, successful or not, becomes a `ReasoningObject` ([[core/schemas.py]]) with its
directive, inputs, raw output, parse status and a timestamp ([D-13](decisions.html#d-13)).

**Observed on real models.** The stored runs show 13 retries in 48 real-model agent runs between
2026-09-22 and 2026-09-24: 4 recovered on attempt 2 and 9 halted
([retry-halt-unproven](ledger.html#retry-halt-unproven), resolved 2026-09-27). Nobody has yet
reviewed the 9 halts one by one.

## What the loop doesn't do

- It checks **structure, not truth.** A well-formed reply with a wrong number passes; catching
  that is the job of the [cross-agent comparison](f-compare.html), the
  [accounting checks](f-checks.html) and claim verification.
- **Confidence is not computed.** `confidence_score` is a configured starting value that
  degrades only when a data source is weak; the "computed, not self-reported" intent in a code
  comment isn't implemented (noted in [[core/schemas.py]]).

## Where it lives

| Piece | File |
|---|---|
| The loop, the corrective directive, the extraction hook | [[pipeline/middleware.py]] |
| Parsing and the echo check | [[core/parsing.py]] |
| Directive versions | [[core/directive.py]] |
| Attempt records and statuses | [[core/schemas.py]] |
| Tests | [[tests/test_phase2_agent.py]], [[tests/test_directive_echo.py]], [[tests/test_phase1_schemas.py]] |
