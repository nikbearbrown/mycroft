---
title: Core
slug: files-core
section: Files
order: 20
summary: The innermost layer - the contracts, the directive, the structural parser, the record types, the shared number rule and the assessment validator.
---

`core/` holds the abstractions and domain types every other layer is written against: what an
agent adapter must look like, what an agent's reply must look like, what the system prompt
(the *directive*) says, what a stored record of one attempt contains, and what counts as "a
number". Nothing in it runs a model, opens a socket or touches the database.

## Dependency rule

`core/` imports nothing internal except itself. This is enforced, not just stated:
[[tests/test_layering.py]] reads every file's imports from the syntax tree and fails if a
`core/` module imports from any other package (`test_core_depends_on_nothing_internal_except_itself`),
and its `_ALLOWED` table gives `core` an empty set of allowed internal packages. Every other layer
(`adapters/`, `pipeline/`, `datasources/`, `producers/`, `validation/`, `web/`) may import from
`core/`, so the dependency arrows point inward. The test file's own docstring gives the reason: if
`core/` ever imported outward, every other layer would inherit that dependency.

The rule has a visible cost in [[core/assessment.py]]: its list of metric names is a hand-written
copy of `validation/facts.py`'s `METRICS`, because importing it would break the rule. A test pins
the two lists together (see that entry).

`core/` is also stdlib-only: `json`, `re`, `uuid`, `dataclasses`, `datetime`, `enum`, `typing`,
`functools`. `docs/SYSTEM_DESIGN.md` §4 records the reason: the core engine's tests run on a bare
interpreter with no install step, and dependency risk stays in the web layer and the model
providers.

## How the files fit together

- [[core/directive.py]] defines the versioned directive text that is sent to every agent as its
  system prompt, and which version is active.
- [[core/parsing.py]] checks an agent's raw reply against the structural contract the directive
  asks for (a `<thought_log>` block, then a `<conclusion>` block, nothing else) and produces an
  `AgentResponse`, or raises `StructuralParseError`. It also rejects a conclusion that is empty or
  copies the directive.
- [[core/contracts.py]] names the three call shapes the rest of the system depends on:
  `AgentAdapter` (returns an `AgentResponse`), `ModelCall` and `JsonFetcher`.
- [[core/schemas.py]] defines the stored records: one `ReasoningObject` per attempt and one
  `RunSession` per run, with validation rules and the two-tier serialization (auditor and
  investor scope).
- [[core/numeric.py]] is the single definition of a quantitative token, used by the validation
  layer and by the assessment validator.
- [[core/assessment.py]] validates the optional structured assessment (grade, direction,
  assumptions) and runs the separate extraction call that currently produces it.

The retry-then-halt loop that ties these together (ADR-07) lives one layer out, in
[[pipeline/middleware.py]].

## `core/__init__.py`

**Role:** package marker for `core/`.

The file is empty. It exists so `core` imports as a package; [[tests/test_layering.py]]
(`test_every_package_is_importable_as_a_package`) fails if it goes missing. It re-exports nothing,
so callers import from the submodules directly (`from core.parsing import AgentResponse`).

Related: [[pipeline/__init__.py]]

## `core/assessment.py`

**Role:** validation of an agent's structured assessment (grade, direction, stated assumptions,
key metrics, key points), and the separate extraction call that obtains one from a finished
answer.

A conclusion is free text, and two agents' free-text views can't be compared, counted or gated
on. The module docstring gives the motivating shape: "Bull says BBB/buy on 8% growth, Bear says
BB/sell on 3%" is what the divergence step needs. The assessment is that view as data. There are
two ways one arrives, and this module serves both:

1. **In the agent's own answer**, as a third `<assessment>` block after `</conclusion>`. Only
   directive v1.6.0 asks for this, and v1.6.0 is not active (see [[core/directive.py]]). The
   parser accepts the block only when `expects_assessment` is true for the directive version; the
   block's text is then passed to `parse_assessment`.
2. **From a separate extraction call** ("option 1"), which is what runs today. After an answer
   passes the unchanged two-block check, one more call to the same model reads the finished answer
   and returns only the JSON object. `extract_assessment` makes that call and validates the reply.

Either way, a grade is the model's judgment about the subject, not a verified fact (P8), and it
is internal tier (SEC-01): [[core/schemas.py]] drops every assessment field at investor scope.

### What the module guarantees

- **Closed vocabulary, never coerced.** A value outside the vocabulary is recorded as an issue and
  left out. "A-" is not turned into "A"; "Strong Buy" is not turned into "buy". Only fields that
  passed are kept in `assessment`; the raw text is kept separately in `raw`.
- **Strict JSON, never repaired.** Invalid JSON produces an issue naming the line and column where
  parsing broke.
- **Never a structural failure.** Nothing here raises into the ADR-07 loop. A missing, unclosed,
  invalid or failed assessment gets a status and issues; the attempt's parse status is already
  decided.

### Constants

- `ASSESSMENT_FROM = (1, 6, 0)`: the first directive version that asks for the block.
- `GRADES = ("AAA", "AA", "A", "BBB", "BB", "B", "CCC")`, `DIRECTIONS = ("buy", "hold", "sell")`,
  `MARGIN_TRENDS = ("expanding", "stable", "contracting")`.
- `ASSUMPTIONS`: the three permitted assumption keys and their kind: `revenue_growth_pct`
  (number), `margin_trend` (one of `MARGIN_TRENDS`), `horizon_months` (number).
- `KEY_METRICS`: the canonical metric names. The comment says they are the financial families of
  `validation/facts.py`'s `METRICS`, copied rather than imported because `core/` may import nothing
  internal and `pipeline/` (which validates the block) may import only `core/`.
  `tests/test_assessment.py` (`test_key_metrics_track_the_comparators_metric_names`) fails if the
  two drift apart.
- `MAX_KEY_POINTS = 3`, `MAX_POINT_CHARS = 240`.
- `Status`: the closed set of outcomes, as a `Literal`:

| Status | Meaning |
|---|---|
| `valid` | every field usable, no issues |
| `partial` | some fields usable, issues listed |
| `invalid_fields` | parsed as JSON, nothing usable |
| `invalid_json` | the block's text is not JSON |
| `unclosed` | `<assessment>` with no `</assessment>`; whatever parsed is still kept |
| `empty` | the block had no content |
| `absent` | no block was given |
| `abstained` | the extraction said the answer states no view; kept as an honest answer |
| `extraction_failed` | the extraction call itself raised |

- `EXTRACTION_PROMPT_VERSION = "assess-extract-v2"` and `EXTRACTION_SYSTEM`, the extraction
  prompt. It is recorded on every extracted assessment as `assessment_source`, so a stored grade
  names the prompt that produced it.

### Key functions

- `expects_assessment(directive_version)`: true only for a version string of the form `vX.Y.Z`
  that is at least `ASSESSMENT_FROM`. `None`, `"corrective"` (the retry directive in
  [[pipeline/middleware.py]]) and any string that doesn't parse as dotted integers return false,
  so the corrective retry is never asked for a block. Used by the parser's caller in
  [[adapters/langchain_adapter.py]], and by [[pipeline/middleware.py]] to decide between the
  in-answer path and the extraction path.
- `parse_assessment(text, *, closed)`: validates the block's inner text. `text=None` gives
  `absent`. An unclosed block with no content gives `unclosed`; an unclosed block with content is
  still parsed, and the result is `unclosed` with whatever fields passed. Empty content gives
  `empty`. A JSON error gives `invalid_json` (or `unclosed` if the tag wasn't closed). A JSON value
  that isn't an object gives `invalid_fields`. `{"abstain": true}` gives `abstained`, with the
  model's `reason` as the issue if it gave a string. Otherwise each field is checked on its own:
  - `grade` and `direction` must be exact members of their vocabularies (case-sensitive: "Buy" is
    an issue). Missing ones are issues too ("No grade given.").
  - `assumptions` must be an object; each key must be one of `ASSUMPTIONS`; number kinds reject
    booleans explicitly (`isinstance(value, bool)` is checked first, because `True` is an `int` in
    Python).
  - `key_metrics` must be a list; unrecognised names are listed in one issue and the recognised
    ones kept.
  - `key_points` must be a list of strings; blanks are dropped, only the first three are kept, and
    any of those longer than 240 characters is dropped with an issue.
  - Unknown top-level keys are reported as ignored.
  The final status is `valid` only with no issues at all; otherwise `partial` if anything survived,
  `invalid_fields` if nothing did.
- `extract_assessment(call, subject, conclusion, thought_log, context)`: runs the extraction and
  never raises. `call` is a `ModelCall` from [[core/contracts.py]]. If the call raises, the result
  is `extraction_failed` with the exception type and message as the issue, and the run goes on.
  The reply is passed through `_json_object`, which reads the outermost `{...}` if the model
  wrapped the object in prose or a code fence; the wrapping is then reported as the first issue and
  a `valid` result is downgraded to `partial` ("valid" is reserved for "nothing to report"). The
  parsed result is then passed to `ground_in` against the agent's conclusion, thought log and
  context.
- `ground_in(parsed, *texts)`: removes what the extraction added that the agent never wrote. Each
  removal is an issue naming the figure.
  - A key point is dropped if any quantitative token in it (per [[core/numeric.py]]) has no match,
    within 0.5% relative tolerance, among the figures in the given texts.
  - A `revenue_growth_pct` or `horizon_months` assumption is dropped if its value appears nowhere
    in the texts, counting bare numbers as well as quantitative tokens.
  - A `revenue_growth_pct` that survives is dropped anyway unless some sentence in the texts both
    contains that number and matches the forward-looking word list `_FORWARD` ("expect", "guidance",
    "will", "next year", "fiscal 20xx" and similar). A past growth rate is a result, not an
    assumption.
  If anything was dropped, the status becomes `partial` (fields left) or `invalid_fields` (none
  left); if nothing was dropped the status is unchanged.
- `extraction_user_prompt(subject, conclusion, thought_log)`: the user message for the extraction
  call. It includes the agent's reasoning (or "(none recorded)") and answer, and not the context.

### Design notes

- **Why a separate extraction call instead of the in-answer block.** Directive v1.6.0 asked for the
  block inside the answer and was reverted the same day it was made active: live, 2 of 10 first
  attempts passed the format check under it, against 7 of 8 under v1.5.2 the day before, and in 7
  of the 8 failures the model never closed `</thought_log>` (`logs/RUN_LOG.md`, 2026-09-26 (continued),
  "B4 + U7: structured assessments and bull/bear, built and reverted as the default"). The human
  then chose the separate call, which leaves ADR-07's two-block contract untouched
  (`logs/RUN_LOG.md`, 2026-09-26 (continued), "Option 1 (assessment extraction) + B5 + U8"). The
  module comment above `EXTRACTION_PROMPT_VERSION` records the same.
- **Why prompt v2 and the forward-looking check.** Live, prompt v1 reported past growth ("up 16%
  year over year", NVDA's 106%) as `revenue_growth_pct`, which the divergence step then read as a
  difference in assumptions. v2 tells the model a past rate is not an assumption, and `ground_in`
  enforces it deterministically (module comment; same "Option 1" entry).
- **Why `ground_in` exists.** Under v1.6.0, one failed attempt's key points misquoted its context
  by 10x (operating income "$6.373 billion" against $63.7B given), and nothing checked key points
  (`ground_in` docstring; "B4 + U7" entry).
- **Why nothing is coerced.** Coercing "A-" to "A" would put a value in the record that the model
  never gave (P3), per the module docstring.
- Behaviour is tested with scripted replies in `tests/test_assessment.py` (in-answer path, parser
  flag, recording, redaction) and `tests/test_synthesis.py` (extraction, abstention, wrapping,
  failure, grounding). The extraction has also been observed live: the "Option 1" entry records 5 of
  5 successful answers getting a usable assessment, all `partial`, on llama3.2.

### Limits and open issues

- The forward-looking check is a word list (`_FORWARD`), and the "Option 1" entry lists it as an
  open issue. A forward sentence phrased without those words loses its growth assumption; a past
  sentence that happens to contain "will" keeps it.
- The extraction is the same model judging its own answer (open issue in the "Option 1" entry).
- `ground_in` checks only figures that [[core/numeric.py]]'s pattern recognises, so a key point
  quoting a bare integer ("revenue grew 16 percent") is not checked.
- The extraction prompt's `key_metrics` list is shorter than `KEY_METRICS`; a name outside the
  prompt's list but inside `KEY_METRICS` is still accepted.
- The evidence behind the extraction is thin: one model, few runs (`synthesis-thin-and-lexical`,
  and the resolved `assessment-not-produced` ledger entry).

Related: [[core/parsing.py]], [[core/contracts.py]], [[core/schemas.py]], [[pipeline/middleware.py]], [[validation/divergence.py]]

## `core/contracts.py`

**Role:** the three call shapes the rest of the system is written against, as
`typing.Protocol`s: `AgentAdapter`, `ModelCall` and `JsonFetcher`.

Before this module existed, the adapter signature lived in a two-line comment in
`adapters/__init__.py` and the HTTP fetcher existed only as repeated `Callable[[str], dict]`
annotations (module docstring). Naming them lets both sides depend on an abstraction:
adapters implement `AgentAdapter`, [[pipeline/middleware.py]] consumes one, and neither imports
the other. All three are decorated `@runtime_checkable`, and conformance is structural: an object
satisfies a protocol by having the right `__call__` shape, with no base class to inherit.

### Key classes

- `AgentAdapter.__call__(subject, context, directive) -> AgentResponse`: what every adapter in
  `adapters/` returns and what `run_validation_loop` calls. The docstring states the contract an
  implementation must keep: return a structurally valid `AgentResponse`, or raise
  `core.parsing.StructuralParseError`. Raising is the signal the retry-then-halt loop is built on,
  so an adapter must not swallow the error and must not invent a well-formed response to hide it.
  Implemented by [[adapters/langchain_adapter.py]] and [[adapters/fixture_adapter.py]], built by
  [[adapters/registry.py]], and taken as a parameter by the producers.
- `ModelCall.__call__(system, user) -> str`: one plain model call returning the raw reply. It is
  used only for the assessment extraction in [[core/assessment.py]]. The docstring says it is kept
  apart from `AgentAdapter` on purpose: it has no directive, no tool use and no structural
  contract, so it cannot disturb ADR-07. It raises on a connection failure and never invents a
  reply. The live implementation is `make_langchain_model_call` in [[adapters/langchain_adapter.py]].
- `JsonFetcher.__call__(url) -> dict`: a URL to parsed JSON. Every network read is injected as one
  of these, which is why the test suite can be network-free without patching module globals. The
  only default implementation lives in [[datasources/edgar.py]], which is how P2 (only ingest code
  touches the network) is kept.

### Design notes

- **Why the directive is a parameter of `AgentAdapter`.** ADR-07's retry passes a different
  `DirectiveVersion` to the same adapter on attempt 2, so an adapter can't capture the directive at
  construction time (module docstring, citing ADR-01b and ADR-07).
- **Why `Protocol`, not a base class.** `docs/SYSTEM_DESIGN.md` §4: the loop depends on a shape,
  not on any adapter's identity, and a new provider needs no inheritance.
- `AgentAdapter` and `JsonFetcher` were introduced in the SOLID restructure (`logs/RUN_LOG.md`,
  2026-09-04, "SOLID restructure: layered packages, no loose root modules, three duplications
  removed"). `ModelCall` was added with the assessment extraction (2026-09-26 (continued),
  "Option 1 (assessment extraction) + B5 + U8").

### Limits and open issues

- The protocols fix the call signature only. `runtime_checkable` makes `isinstance` check that
  `__call__` exists, not its parameters or return type, so any callable passes such a check. Nothing
  enforces the "raise, don't invent" rule; it is a documented obligation.
- `README.md`'s Layout table describes this file as holding "the two contracts" (`AgentAdapter`
  and `JsonFetcher`). The code has three; `ModelCall` is missing from the README.
- The 2026-09-04 entry names a persistence port here as the honest fix for `validation/`'s upward
  import of `web.db`; it has not been added.

Related: [[core/parsing.py]], [[core/directive.py]], [[pipeline/middleware.py]], [[datasources/edgar.py]]

## `core/directive.py`

**Role:** the versioned, hardcoded directive (the system prompt injected into every agent), the
registry of every version ever deployed, and the pointer to the active one.

The directive tells the agent to answer in exactly two XML blocks and, from v1.2.0 on, where its
facts may come from and how to cite them. It is source code, not configuration. The module
docstring cites three rules: ADR-01b (the layer actively modifies agent behaviour through this
text), ADR-05 (the text is stored verbatim per run, not by pointer) and SEC-04 (no runtime
parameter can modify directive content). A change to the wording is a new version and a code
deployment.

### How it works

- `DirectiveVersion(version, text)` is a frozen dataclass.
- `_register(version, text)` builds one and stores it in the module-level `_DIRECTIVE_REGISTRY`
  dict. Every version is registered at import time and none is ever removed, so a stored run can be
  checked against the exact text that was active for it (registry comment).
- Later versions are derived from earlier ones by text substitution where the change is small:
  v1.5.2 is `DIRECTIVE_V1_5_1.text` with two `.replace()` calls, and v1.6.0 is v1.5.2 with the
  `V1_6_0_CHANGES` pairs applied by `_apply`. `_apply` raises `AssertionError` at import time if
  any anchor string doesn't occur exactly once, so a derived version can't be built silently from
  an anchor that has moved.
- `ACTIVE_DIRECTIVE` is the version attempt 1 uses by default.

### Registered versions

| Version | Change | Reason recorded |
|---|---|---|
| `v1.0.0` | The initial prototype: "financial analysis agent", two blocks, citations as `[SOURCE: <label>, <url or N/A>]`. | Kept for historical audit (code comment). |
| `v1.1.0` | "Begin your response immediately with `<thought_log>`", a ban on preamble and on mentioning tag names outside the blocks, and a Rules list (first character `<`, last character `>`). | Gemini models wrote numbered reasoning as plain text before `<thought_log>`, which caused false tag matches (code comment). |
| `v1.2.0` | A GROUNDING RULE: the Context is the only source of fact; do not invent a number, date, percentage or URL; "insufficient context" is a correct answer. Citations must name a source in the Context. | Live llama3.2 calls with empty or thin context invented numbers, a fiscal quarter and homepage URLs as citations (code comment; `logs/RUN_LOG.md`, 2026-09-22, "Add DIRECTIVE_V1_2_0: explicit grounding rule, in response to observed fabrication"). The text was proposed to the user for approval before it was added (same entry). |
| `v1.3.0` | A top-level CITATION RULE with the exact bracket format, "in either block", and a worked example. | The model cited inconsistently across seeds, and no run had yet produced the bracket format (code comment; 2026-09-22, "Make citation verification actually fire: fix the code-side block mismatch, add DIRECTIVE_V1_3_0"). |
| `v1.4.0` | "verification agent" instead of "financial analysis agent"; domain-neutral wording and citation example. Rules otherwise unchanged. | The finance framing was sent to every agent, including non-financial chat questions (code comment; 2026-09-23, "Generalize the accountability layer + Cross-Agent Validation beyond finance"). |
| `v1.5.0` | Each block's in-tag instruction prefixed "(Instruction — do not copy this into your response)", plus a rule naming the phrases seen leaking. | A live conclusion opened with the block's own instruction text (code comment; 2026-09-24 (continued), "Stop the model echoing the directive's own instructions into <conclusion>"). |
| `v1.5.1` | Block descriptions moved out of the tags into a "WHAT EACH BLOCK MUST CONTAIN" section before an empty-tag template; "Neither may be empty"; the thought log asks for the reporting period of each figure. | v1.5.0 did not work: 7 of 10 stored v1.5.0 compare conclusions still echoed, now including the "do not copy" marker. The root cause was that every version put instructions where the answer goes (code comment; 2026-09-24 (continued), "Directive echo, properly: v1.5.1 (nothing inside the tags) + a machine check"). |
| `v1.5.2` | The exact closing tags `</thought_log>` and `</conclusion>` stated in the template heading and the rules ("never square brackets like [/conclusion]"). Otherwise v1.5.1. | `[/conclusion]` closed 3 of 22 v1.5.1 first attempts and never appeared under v1.4.0 (0/33) or v1.5.0 (0/12) (code comment; 2026-09-24 (continued), "B1 + U2: figure-by-figure comparison"). |
| `v1.6.0` | An optional third `<assessment>` block with grade, direction, assumptions, key metrics and key points; one narrow exception to the GROUNDING RULE for the grade, direction and assumption values. Everything else is v1.5.2. | Structured assessments for the divergence step (code comment; 2026-09-26 (continued), "B4 + U7"). |

The corrective directive used on the ADR-07 retry is not in this registry. It is built in
[[pipeline/middleware.py]] as a `DirectiveVersion` with version `"corrective"`.

### Which version is active, and why

`ACTIVE_DIRECTIVE` is `DIRECTIVE_V1_5_2`. The code comment above it records that v1.6.0 was made
active on 2026-09-26 and reverted the same day: live, 2 of 10 first attempts passed the format
check under v1.6.0 (the model mostly left `</thought_log>` unclosed and nested the other blocks
inside it), against 7 of 8 under v1.5.2 the day before. The full record is the 2026-09-26
(continued) "B4 + U7" entry in `logs/RUN_LOG.md`. v1.6.0 stays registered, and parser, recording
and UI support for it remain in place. Assessments are now obtained by a separate extraction call
instead ([[core/assessment.py]]).

### Key functions

- `get_directive(version)`: the registered `DirectiveVersion`, or `KeyError` for an unknown
  version string. `web/server.py`'s replay route uses it to re-run a stored run against the
  directive it was recorded under, and falls back to the active directive on `KeyError`.
- `get_active_directive()`: returns `ACTIVE_DIRECTIVE`. [[pipeline/middleware.py]] calls it when
  no directive is passed; `web/server.py` and [[validation/cross_validation.py]] call it to record
  the directive on a `RunSession`.

### Design notes

- New versions are added, never edited in place. The v1.5.0 entry cites "this file's own
  versioning discipline: old versions stay retrievable for historical run audit".
- The parser is deliberately not loosened to accept `[/conclusion]`: that would change ADR-07's
  structural contract, which is a human decision (v1.5.2 code comment).
- The echo problem is handled in two halves: prevention here (v1.5.1's empty tags) and detection in
  [[core/parsing.py]] (`reject_unusable_conclusion`).
- Tests pin the text: `tests/test_directive_echo.py` checks that v1.5.2 is active, that the
  template tags are empty, that the closing tags are named, and (`test_v152_changes_nothing_else`)
  that v1.5.2 differs from v1.5.1 only as described. `tests/test_assessment.py` checks that v1.6.0
  is registered, not active, and differs from v1.5.2 only by `V1_6_0_CHANGES`.
  `tests/test_phase1_schemas.py` covers registry lookup, the unknown-version `KeyError` and
  immutability.

### Limits and open issues

- The corrective retry replaces the whole directive with a one-paragraph format reminder, so
  attempt 2 runs without the GROUNDING and CITATION rules. It was found and left unchanged because
  changing it alters ADR-07's contract (`logs/RUN_LOG.md`, 2026-09-24 (continued), "Directive echo,
  properly", open issues; repeated in the "B1 + U2" entry, which links it to second-attempt halts).
- The v1.5.1 code comment names the machine check `reject_directive_echo`; the function in
  [[core/parsing.py]] is `reject_unusable_conclusion` (the echo finder is `find_directive_echo`).
- `docs/SYSTEM_DESIGN.md` §2.3 and §2.4 say the active directive is v1.1.0 and that two versions
  exist. The code registers nine and v1.5.2 is active.
- `README.md`'s Layout table says this file holds "the corrective directive used on retry". It
  doesn't; that text is `CORRECTIVE_DIRECTIVE_TEXT` in [[pipeline/middleware.py]].
- The live evidence behind each version is small: for example, the v1.5.1 entry notes that n = 8
  live conclusions does not establish an echo rate.

Related: [[core/parsing.py]], [[core/assessment.py]], [[pipeline/middleware.py]], [[core/schemas.py]]

## `core/numeric.py`

**Role:** the one definition of "a quantitative token", plus the magnitude-suffix table,
normalisation to a float and a relative-tolerance comparison.

### How it works

`QUANTITATIVE_RE` is a case-insensitive alternation. Alternatives are tried in this order, which
matters only when two could match the same text:

1. `$`-prefixed amounts with an optional magnitude word or letter (`$383.266 billion`, `$4.2M`);
2. percentages (`106%`, `12.5 %`);
3. multiples (`2.3x`);
4. basis points (`25 bps`);
5. comma-grouped numbers with no prefix or suffix, requiring proper three-digit groups
   (`13,971,000,000.0`), so a bare short integer never matches;
6. bare decimals (`0.34`, `14.41`).

A bare integer ("2025") matches none of them, so years and counts don't become quantitative
claims.

### Key functions

- `extract_numbers(text)`: every match, stripped and lowercased, in order, with duplicates kept.
  The docstring says de-duplication is left to callers on purpose: `validation/claims.py`
  de-duplicates by (type, value), while `validation/consistency.py` builds a set.
- `normalize_number(token)`: a token to a float, or `None` if it doesn't parse. Commas and `$` are
  removed; a trailing magnitude from `SUFFIX_MAP` multiplies (`"$383.266 billion"` becomes
  383266000000.0); otherwise trailing `%`, `x`, `b`, `p`, `s` characters are stripped. A
  percentage stays in percent units (`"106%"` becomes 106.0, not 1.06) and basis points stay as a
  count. Moved here from `validation/verification.py` so claim verification and the cross-agent
  comparator in [[validation/facts.py]] normalise the same way (docstring).
- `close_enough(a, b, tol=0.01)`: true when the difference relative to the larger magnitude is at
  most `tol`; two zeros are equal. [[core/assessment.py]] calls it with a tighter 0.005.
- `SUFFIX_MAP`: trillion/t, billion/b, million/m to their multipliers.

### Design notes

- **Why one copy.** The pattern used to exist verbatim in three validation modules, each with a
  comment asking the reader to keep it in sync by hand. All three feed evidence (which figures
  become claims, which count when comparing agents, which get checked against the source), so a
  drifted copy would be a P3 violation that raises no error (module docstring; `logs/RUN_LOG.md`,
  2026-09-04, "SOLID restructure"). `tests/test_numeric.py` asserts the validation modules share
  one pattern object, not merely equal patterns, and that no module defines its own copy.
- **Why bare decimals are accepted.** The fabricated AAPL debt-to-equity figure "0.34" went
  unextracted on 2026-08-29 because it had no unit suffix. The widening also matches a section
  number like "2.1"; that false positive was accepted once, here (module docstring;
  `logs/RUN_LOG.md`, 2026-08-29, "Widen the quantitative-number regex"). `tests/test_numeric.py`
  asserts the false positive rather than hiding it.
- **Why the comma-grouped alternative.** Before 2026-09-11, `\d+` could not cross a comma, so an
  echoed XBRL value "13,971,000,000.0" was extracted as "000.0". Found by replaying stored runs
  (run `515f263a`, ticker V) and fixed by a dedicated alternative tried before the bare-decimal
  fallback (module docstring; ledger `regex-truncates-comma-grouped-numbers`, RESOLVED).

### Limits and open issues

- The pattern is lexical: it cannot tell a financial ratio from a version string or section
  number, and it misses figures written in words or as bare integers.
- `normalize_number` strips any trailing run of the characters `% x b p s`, so it does not check
  that the suffix is a real unit.
- No test in `tests/` imports `normalize_number` or `close_enough` directly; they are exercised
  through their callers.

Related: [[validation/claims.py]], [[validation/consistency.py]], [[validation/verification.py]], [[validation/facts.py]], [[core/assessment.py]]

## `core/parsing.py`

**Role:** structural parsing of an agent's reply into its thought log and conclusion (and,
when asked, an assessment block), and the content check that rejects an empty conclusion or one
that copies the directive.

The module is provider-agnostic: it knows only the structural contract, two XML blocks and
nothing outside them (module docstring). It was `parser.py` at the root until the 2026-09-04
restructure, renamed because that name shadowed a stdlib module.

### The structural contract

`_parse_response(raw, *, allow_assessment=False)` returns an `AgentResponse` or raises
`StructuralParseError`. It fails when:

- both blocks are missing ("Response missing both <thought_log> and <conclusion> blocks");
- `<thought_log>` is missing;
- `<conclusion>` is missing;
- anything other than whitespace remains once the matched blocks are removed ("Response contains
  text outside XML blocks").

How it matches:

- Both block patterns are anchored with `^\s*` under `re.MULTILINE`, so a tag counts only at the
  start of a line (after optional whitespace). The comment says this avoids false matches on a tag
  name mentioned mid-sentence or in backticks.
- Content is matched lazily up to the first closing tag.
- `<conclusion>` is searched for only after the end of the thought log. A model that describes the
  format inside its reasoning can't produce a false conclusion match (docstring). One consequence
  is that block order is enforced: a conclusion placed before the thought log is reported as a
  missing conclusion.
- The remainder check removes every matched span by position rather than by string replacement,
  so fake tags inside the thought log's content aren't re-matched (code comment).
- The block contents are stripped; `raw_text` keeps the reply byte for byte, for the audit record.

With `allow_assessment=True` (passed only for directives where
`core.assessment.expects_assessment` is true), an `<assessment>` block is also accepted, but only
directly after `</conclusion>` with nothing but whitespace between. An unclosed one runs to the end
of the reply. It is never required. With the flag off, which covers every directive up to v1.5.2
and the corrective retry, the two-block contract is unchanged and a third block is "text outside
XML blocks" (docstring).

### Key types

- `StructuralParseError(message, raw_response)`: carries the raw reply so the loop can record it as
  a `PARSE_FAILURE` attempt. This is the only exception the ADR-07 loop catches.
- `AgentResponse`: frozen dataclass with `thought_log`, `conclusion`, `raw_text`,
  `assessment_text` and `assessment_closed`. The last two are `None` when the parser wasn't asked
  to look; `assessment_text=None` with `assessment_closed=False` means it looked and found nothing.

### Content checks beyond structure

- `reject_unusable_conclusion(response, directive_text)`: raises `StructuralParseError` if the
  conclusion is empty or whitespace, or if `find_directive_echo` finds a copied run. Only the
  conclusion is checked: a thought log that quotes a rule it is applying is reasoning, not an echo
  (docstring). It is called on every attempt by [[pipeline/middleware.py]] (the authoritative
  check) and by `web/step_trace.py`'s adapter wrapper, so the trace step reads `parse_failure`
  instead of `ok`.
- `find_directive_echo(conclusion, directive_text)`: the first run of `_ECHO_WINDOW` (8)
  consecutive words in the conclusion that also appears in the directive, after lowercasing and
  keeping only `[a-z0-9]+` words; otherwise `None`. It is deterministic, so every hit is a verbatim
  copy that can be shown to a reviewer.
- `_directive_windows(directive_text)`: the set of 8-word windows of the directive, minus the
  windows of `_PERMITTED_ANSWER_WORDING`. Cached with `lru_cache(maxsize=32)`, keyed on the
  directive text.
- `_PERMITTED_ANSWER_WORDING`: three sentences in which the directive tells the model what to say
  when the Context is thin. A compliant answer may reuse that wording ("the Context does not
  contain what is needed to answer"), so windows drawn only from them are exempt.

### Design notes

- **Why an echo is a structural failure.** Measured on 2026-09-24: 7 of 10 stored v1.5.0
  cross-agent conclusions opened with the directive's own instruction text, and all passed the
  parse and were delivered. A conclusion that restates the directive is no more an answer than a
  missing block, so it takes the same retry-then-halt path and is recorded as `PARSE_FAILURE` (code
  comment; `logs/RUN_LOG.md`, 2026-09-24 (continued), "Directive echo, properly").
- **Why 8 words.** Replaying every stored conclusion (135) against the directive that produced it,
  windows of 6, 8, 10 and 12 words all flagged the same 17 and none of the other 118; 8 sits inside
  that plateau (code comment; same entry). The 17 include 2 NFLX runs that had copied v1.3.0's
  citation example as a finding. Whole-sentence matching missed a partial copy, which is why
  windows are used (same entry).
- **Why the exemption list.** A test for a compliant "insufficient context" answer caught it being
  flagged before the exemption existed (same entry).
- **Structure only, then content.** `docs/SYSTEM_DESIGN.md` §2.2 describes the parser as a
  structural check that says nothing about correctness; semantic checks are layered on top in
  `validation/`.
- Tested with scripted replies in `tests/test_phase2_agent.py` (every structural failure case,
  whitespace between blocks, multiline content, the empty string), `tests/test_directive_echo.py`
  (real stored echoes, clean answers, partial copies, empty conclusions, retry and halt, the trace
  label) and `tests/test_assessment.py` (the flag, closed/unclosed/absent blocks, position).

### Limits and open issues

- A legitimate conclusion that quotes 8 or more consecutive words of the active directive is
  rejected. The replay found no such case, which the log notes is not a guarantee (2026-09-24
  (continued), "Directive echo, properly", open issues).
- The live rejection path had not fired when that entry was written; detection was proven by
  replay and unit tests.
- Because content is matched lazily to the first closing tag, a thought log that writes the literal
  line-start `</thought_log>` text inside itself ends the block early, and the leftover text fails
  the remainder check.
- `docs/SYSTEM_DESIGN.md` §2.2 says the structural check is "deliberately the only thing the parser
  checks". Since 2026-09-24 this module also holds the empty-conclusion and echo checks, and since
  2026-09-26 the optional assessment block.
- `README.md` calls this "the best-tested module here", a judgment that no record here measures.

Related: [[core/directive.py]], [[core/contracts.py]], [[core/assessment.py]], [[pipeline/middleware.py]], [[web/step_trace.py]], [[adapters/langchain_adapter.py]]

## `core/schemas.py`

**Role:** the stored record types: `ReasoningObject` (one per agent per attempt) and
`RunSession` (one per run), their sub-models and enums, the validation rules they enforce at
construction, and the two-tier serialization.

Every model is a frozen dataclass, so a record cannot be changed after it is built, which mirrors
the append-only store (module docstring, citing ADR-03 and SEC-03). Validation runs in
`__post_init__` and raises the module's own `ValidationError` (a plain `Exception` subclass, not
Pydantic's). The docstring notes the field names are kept compatible with a later move to Pydantic
v2.

### Enums

All are `str` enums, so they serialise as their value.

- `AgentID`: `financial`, `patent`, `earnings`, `competitive`, `AAN`, `external` (any third-party
  or provider-agnostic agent), `generic_a` and `generic_b` (the two sides of the domain-agnostic
  compare path; two IDs rather than `external` twice, because code that looks up "the record for
  agent X" must tell them apart), and `bull` and `bear` (the opposite-brief pairing).
- `ParseStatus`: `SUCCESS`, `PARSE_FAILURE`, `HALT`.
- `DataSourceStatus`: `live`, `simulated`, `failed`, `cached`.
- `RunStatus`: `OPEN`, `COMPLETE`, `HALTED`.
- `ConfidenceClassification`: `STANDARD`, `HIGH_UNCERTAINTY_SPECULATIVE` (member name
  `HIGH_UNCERTAINTY`).

### Sub-models

- `DataSource(source, status, url, fetched_at, provenance_note)`: one source an agent consulted
  (BN-03). `source` must be non-blank, and `status` must be a `DataSourceStatus` instance (a plain
  string is rejected).
- `Citation(label, url, excerpt)`: a source cited in a conclusion. `label` must be non-blank;
  `excerpt` at most 500 characters.

### `ReasoningObject`

Required: `run_id`, `agent_id`, `attempt_number`, `parse_status`, `confidence_score`. Optional:
the thought log, conclusion, reasoning steps, citations, data sources, raw output, token usage,
data-quality warnings, the directive version and text actually used for this attempt, the context
window, the four assessment fields, and `created_at` (defaults to now, UTC).

Rules enforced at construction:

- `confidence_score` within 0.0 to 1.0. The docstring cites ADR-04: computed, not self-reported.
- `attempt_number` is 1 or 2.
- Attempt 2 can't be `PARSE_FAILURE`: it is `SUCCESS` (retry worked) or `HALT` (retry also
  failed). This makes ADR-07's shape a property of the type as well as of the loop
  (`docs/SYSTEM_DESIGN.md` §2.3).
- `SUCCESS` requires a conclusion (F-01).
- Data-quality warnings require a `confidence_degradation_reason` (ADR-04).
- `created_at` must be timezone-aware.

Per-attempt directive and context: `directive_version` and `directive_text` record the directive
actually used for this attempt. They exist because attempt 2 uses the corrective directive, not
the one named on the `RunSession`, and recording it only at session level lost that distinction
(field comment; `logs/RUN_LOG.md`, 2026-09-22, "Feature: expose per-attempt context window").
`context_window` is the `{subject, context}` inputs handed to the adapter. The comment is explicit
that this is the input side, not a capture of the bytes sent to the model, since an adapter may
truncate or reformat.

Assessment fields: `assessment` (only fields that passed [[core/assessment.py]]),
`assessment_status`, `assessment_issues`, and `assessment_source` (`"directive"` for an in-answer
block, or the extraction prompt version).

`confidence_score_rounded` rounds to 4 places and is what serialization writes.

### Tiered serialization (auditor and investor scope)

`to_dict(*, investor_scope=False)` and `to_json(...)` build the public record. At investor scope
(SEC-01) the following keys are left out of the dict entirely, not set to null:

| Internal-tier key | Why it is internal |
|---|---|
| `thought_log` | LLM-generated reasoning, evidence rather than verified reasoning (ADR-06) |
| `raw_output` | the reply verbatim, plus any assessment extraction reply |
| `llm_tokens` | provider usage metadata |
| `directive_text` | part of how the agent was instructed (field comment) |
| `context_window` | the inputs assembled into the prompt |
| `assessment`, `assessment_status`, `assessment_issues`, `assessment_source` | a model judgment, withheld until a human has ruled on it |

Both scopes carry the IDs, attempt number, parse status, rounded confidence, degradation reason,
reasoning steps, conclusion, citations, data sources, warnings, `created_at` and
`directive_version` (the version is public metadata; the text is not).

Omitting keys rather than nulling them lets a reader tell "not available at your scope" from "the
model produced nothing here" (`docs/SYSTEM_DESIGN.md` §2.8 and §4). `validation/gate.py`'s
`redact_for_scope` applies the same cut to stored payloads; `tests/test_assessment.py`
(`test_redact_for_scope_drops_what_to_dict_drops`) checks the two drop exactly the same keys. That
test was added after investor reads were found carrying `assessment_status` because the gate's key
list hadn't been updated (`logs/RUN_LOG.md`, 2026-09-26 (continued), "B4 + U7").

### `RunSession`

Required: `ticker`, `directive_version`, `directive_text`. The ticker is uppercased and stripped
in `__post_init__` (through `object.__setattr__`, since the dataclass is frozen), then must be
non-empty and at most 10 characters. `directive_text` is stored verbatim (ADR-05), so a session
records the exact text rather than a version pointer that could later resolve to something else.
Other rules:

- `completed_at` can't be set while `status` is `OPEN`.
- If both `run_confidence_score` and `confidence_classification` are set, they must agree with
  the ADR-08 threshold: below 0.4 is `HIGH_UNCERTAINTY_SPECULATIVE`; 0.4 and above is `STANDARD`
  (`tests/test_phase1_schemas.py` checks exactly 0.4 is `STANDARD`).

`RunSession.to_dict()` takes no scope argument and serialises its nested reasoning objects at
auditor scope.

### Who uses it

[[pipeline/middleware.py]] builds a `ReasoningObject` per attempt. `web/server.py` and
[[validation/cross_validation.py]] build `RunSession`s. The producers use `AgentID` and
`DataSource`; the validation layer reads the records.

### Limits and open issues

- `RunSession.to_dict()` always writes the nested reasoning objects at auditor scope. This is
  `session-scope-leak` (OPEN): since 2026-09-25 investor reads strip the nested copy through
  `validation/gate.py`, but storage is still full and a read with no token is served at the scope
  the run was stored under.
- `confidence_score` is range-checked but nothing here checks how it was produced.
  [[pipeline/middleware.py]] defaults it to a constant 0.7, and [[producers/lens.py]] doesn't pass
  one, so lens runs record 0.7 regardless of the run. The ADR-04 "computed, not self-reported"
  comment describes an intent, not a computation in this code.
- `RunSession.ticker` is capped at 10 characters and uppercased, although the chat and generic
  compare paths aren't tickers; callers reduce the subject first (`web/server.py`'s `_ticker`,
  [[validation/cross_validation.py]]'s `_extract_ticker`).
- `docs/SYSTEM_DESIGN.md` §2.8 and §5 list only `thought_log`, `raw_output` and `llm_tokens` as
  investor-excluded. The code also excludes `directive_text`, `context_window` and the four
  assessment fields.
- `patent`, `competitive` and `AAN`, and `RunSession`'s `aan_triggered` and `aan_affidavit`, have no
  producer or route that sets them: a search of the non-test Python finds no use of those three
  IDs and no caller passing either AAN field.

Related: [[pipeline/middleware.py]], [[validation/gate.py]], [[validation/cross_validation.py]], [[core/assessment.py]], [[web/db.py]]
