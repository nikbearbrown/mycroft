---
title: Validation
slug: files-validation
section: Files
order: 70
summary: The verification stack for agent answers - claim extraction and citation checks, the two-agent comparison, figure-by-figure facts, accounting checks, divergence synthesis, the human decision gate and the audit export.
---


`validation/` is where the subsystem judges what agents said, after the structural loop in
[[pipeline/middleware.py]] has accepted or halted a reply. Everything here scores, compares,
counts or withholds. Nothing here decides which agent is right. Where a decision is needed, the
code opens a gate for a named human (SNICKERDOODLE P1 and P4).

## Dependency rule

`tests/test_layering.py` pins what this package may import: `core`, `pipeline` and `web`. The
`web` import is allowed only as a lazy, function-level import of [[web/db.py]] (used by
[[validation/cross_validation.py]] to persist and scan runs), and the layering test asserts that
separately. The same test names [[validation/verification.py]] as the one known network egress
point outside `datasources/` and `adapters/`: it fetches the source a citation names.

## How the files fit together

There are two groups.

**ADR-06 mitigations for a single agent** (used by the chat route and, since 2026-09-11, by the
compare route in [[web/server.py]]):

- [[validation/claims.py]] turns an agent's thought log and conclusion into typed claims.
- [[validation/verification.py]] fetches each cited URL and checks whether any of the answer's
  figures appear there.
- [[validation/consistency.py]] asks the same question again and scores how far the two answers
  drift.

**The cross-agent path** (roadmap phases B1 to B6 and BG, named below by those ids because the
code and `logs/RUN_LOG.md` use them):

1. [[validation/cross_validation.py]] runs two agents independently through the ADR-07 loop and
   assembles the comparison. It calls everything below.
2. [[validation/facts.py]] (B1) extracts every figure with a metric and a period and produces the
   figure-by-figure rows (`metric_comparisons`).
3. [[validation/concept_linkage.py]] is the `concept_aware` contradiction rule, one of three rules
   that can decide `contradiction_flag`.
4. [[validation/constraints.py]] (B3) runs the accounting checks (`structural_flags`).
5. [[validation/divergence.py]] (B5) classifies why the agents' views differ and proposes a
   consensus grade only when one exists (`synthesis`).
6. [[validation/gate.py]] (BG) turns mismatches, failed hard checks and grade disagreements into
   gate items, validates human decisions, and redacts a run for investor-scope readers.
7. [[validation/audit.py]] (B6) renders the redacted run as an audit record in JSON and Markdown.

Each stage that writes into a stored run stamps its own policy or format id, so a reader can tell
which rules produced a record:

| Constant | Value | Where |
|---|---|---|
| `CHECKS_POLICY` | `b3-v1` | [[validation/constraints.py]] |
| `SYNTHESIS_POLICY` | `b5-v1` | [[validation/divergence.py]] |
| `GATE_POLICY` | `v3` | [[validation/gate.py]] (stamped on the run by [[web/server.py]]) |
| `AUDIT_FORMAT` | `audit-v1` | [[validation/audit.py]] |

`validation/__init__.py` is empty: a package marker only.

## `validation/__init__.py`

**Role:** package marker for `validation`. The file is empty; it defines and re-exports nothing,
so every caller imports from the submodule it needs.

## `validation/claims.py`

**Role:** turns an agent's free text into a list of typed claims (citation, quantitative, hedge,
causal) that can be stored and checked, instead of trusting the thought log as narrative. An
ADR-06 partial mitigation.

The module splits text into sentences (on `.`, `!` or `?` followed by whitespace) and records, in
this order:

- **Citations.** Every `[SOURCE: label, url]` bracket (`_CITATION_RE`, case-insensitive). The
  claim's text is `label — url`, its context is up to 100 characters before and 40 after the
  bracket, and `source_label` / `source_url` are set. Citations are de-duplicated by lowercased
  label, so two brackets with different labels but the same URL are two claims.
- **Quantitative.** Every token matched by `QUANTITATIVE_RE` from [[core/numeric.py]], one claim
  per distinct lowercased token, with its sentence as context. The regex used to be copied into
  this file, `consistency.py` and `verification.py`; the module comment records the move to one
  shared definition.
- **Hedges.** A sentence containing any word in `_HEDGE_WORDS` ("estimated", "may", "likely",
  "unverified", "subject to" and others). The claim text is the sorted list of hedges found; one
  claim per sentence (keyed by its first 80 characters).
- **Causal.** A sentence containing any phrase in `_CAUSAL_PHRASES` ("because", "due to",
  "driven by" and others). The claim text is the first phrase found in the tuple's order.

### Key functions and types

- `ExtractedClaim`: a mutable dataclass. `verified` is `True` (confirmed), `False` (source
  reached, not found) or `None` (not checked, or could not be checked). `to_dict()` omits
  `source_label` and `source_url` when they are `None`.
- `extract_claims(thought_log)`: the parser above. Returns `[]` for `None` or an empty string, so
  it is always safe to call.
- `extract_claims_from_response(thought_log, conclusion)`: joins both blocks with a newline and
  calls `extract_claims`. Its docstring gives the reason: the directive words the citation
  instruction under the conclusion block, callers had only scanned the thought log, and so no
  citation claim had ever been extracted from a stored run. Recorded in `logs/RUN_LOG.md`,
  2026-09-22, "Make citation verification actually fire: fix the code-side block mismatch, add
  DIRECTIVE_V1_3_0".

### Design notes

- Extraction never judges truth. It produces the input for [[validation/verification.py]]; the
  module docstring names citation URL verification as the next layer.
- De-duplication keys are `(type, value)`, so the same figure restated twice is one claim. That
  choice is left to this module on purpose: `extract_numbers` in [[core/numeric.py]] keeps
  duplicates so each caller can decide (its docstring says so).

### Limits and open issues

- Hedge and causal detection are substring tests on the lowercased sentence, not word matches:
  "may" also matches inside "dismay", and "pending" inside "spending". Nothing in the code or the
  record says whether that was intended (judgment, not recorded).
- The bare-decimal alternative in `QUANTITATIVE_RE` also matches section numbers like "2.1". That
  is an accepted trade-off recorded in [[core/numeric.py]] and pinned by
  `tests/test_claims.py` (`test_known_false_positive_tradeoff_is_accepted_not_hidden`).
- Tested by `tests/test_claims.py` (citations, each quantitative form, hedges, causal phrases,
  empty input, serialisation). Its live use is recorded in the 2026-09-22 RUN_LOG entry above,
  which also warns that the rate of citation extraction on real models is not a proven rate.

Related: [[validation/verification.py]], [[core/numeric.py]], [[web/server.py]]

## `validation/verification.py`

**Role:** for each citation claim with a URL, fetches the source and checks whether any of the
answer's figures appear in it. Stdlib only (`urllib`), per the ADR stated in the module docstring.

### How it works

1. `verify_claims(claims)` pools every quantitative claim in the list, normalised with
   `normalize_number` from [[core/numeric.py]], into one set of claim numbers.
2. It keeps the citation claims whose `source_url` is set and is not `"N/A"` or empty. With none,
   it returns the claims unchanged and a rate of `0.0`.
3. Each distinct URL is fetched once (`_fetch`: 10 second timeout, the first 300 KB of the body,
   decoded as UTF-8 with replacement; any exception returns `None`).
4. `_check_url` extracts the source's numbers. A URL containing `sec.gov` or `edgar` whose body
   starts with `{` is parsed as SEC companyfacts JSON and every numeric `val` in every concept and
   unit is collected (`_numbers_from_edgar`). Anything else is searched as text with
   `QUANTITATIVE_RE` (`_numbers_from_text`).
5. The URL is `True` if any claim number is within 1% (`close_enough`'s default) of any source
   number, `False` if the source had numbers but none matched, and `None` if there were no claim
   numbers, the fetch failed or was empty, or the source yielded no numbers.
6. Every citation claim for that URL gets that value in `verified` (as a new `ExtractedClaim`);
   other claims pass through unchanged.

### Key functions

- `verify_claims(claims) -> (claims, verification_rate)`: the entry point above.
- `_normalize` and `_close_enough` are aliases for the shared implementations in
  [[core/numeric.py]]; the comment says the private names were kept so call sites read as before,
  after B1 moved the functions out of this file (RUN_LOG 2026-09-24, "B1 + U2").

### Design notes

- `None` is kept distinct from `False`: "could not check" and "checked, not found" are different
  facts (`docs/SYSTEM_DESIGN.md` §4, the `verify_claims` row).
- Since 2026-09-11 the compare route calls this for each producer's own successful attempt,
  independently, so one agent's figures are never checked against the other's citations
  ([[web/server.py]] comment; ledger [fabrication-not-caught](ledger.html#fabrication-not-caught)).
  The ledger records a replay of the historic AAPL case producing `verification_rate=0.0`.

### Limits and open issues

- **The rate's numerator and denominator count different things.** The docstring says
  `verified_citations / total_citations`. The code divides the number of distinct URLs that
  verified by the number of citation claims. Two citations with different labels and the same
  verified URL give 0.5, not 1.0. Found by reading the code; no test covers it.
- The check is permissive by construction: numbers from the whole answer are pooled, and any
  single one within 1% of any number on the page verifies every citation to that page. It says a
  cited source backs at least one figure somewhere, not which figure. The ledger entry
  [fabrication-not-caught](ledger.html#fabrication-not-caught) states the same limit.
- It fetches the URL the model wrote. A `True` confirms consistency with a source the model
  named, not with the input it was given (RUN_LOG 2026-09-22, "Fix: 'X% citations verified'
  collapses 'no citations found' into 'checked, 0 verified'").
- The body is capped at 300 KB before JSON parsing. A companyfacts payload longer than the cap is
  truncated, fails to parse, yields no numbers and reads as `None`. How often real payloads exceed
  the cap is not recorded.
- No test exercises the fetch-and-match path directly: a search of `tests/` for `_check_url`,
  `_fetch` and `urlopen` finds nothing. `tests/test_numeric.py` pins that this module uses the
  shared regex; `tests/test_compare_route.py` checks that the compare route returns a rate per
  producer.

Related: [[validation/claims.py]], [[core/numeric.py]], [[web/server.py]]

## `validation/consistency.py`

**Role:** the consistency probe. Runs the same query through the same agent a second time and
scores how much the two conclusions agree. Also supplies the overlap scoring that
[[validation/cross_validation.py]] reuses for two different agents.

### How it works

`run_consistency_probe(...)` calls `run_validation_loop` again with a fresh UUID, the same
adapter, context, confidence and data sources. The probe run is never written to the database; it
becomes metadata on the primary run (`payload["consistency"]` in the chat route).

The score (`_compute_score`):

- **Word overlap:** Jaccard similarity of content words (lowercase runs of three or more letters,
  minus `_STOPWORDS`). Two empty sets score 1.0.
- **Number overlap:** Jaccard similarity of the two sets of quantitative tokens. When neither
  conclusion has a number, it scores 1.0 so a figure-free answer is not penalised.
- **Combined:** `0.4 × word + 0.6 × number`, rounded to three places. The docstring's reason for
  the weighting: numbers are objectively checkable and the hardest to confabulate consistently.

`_classify` maps the combined score to an agreement: `HIGH` at 0.70 or above, `MEDIUM` at 0.40 or
above, `LOW` below. `UNKNOWN` comes only from `_unknown`, when the probe halts, raises any other
exception, or returns no final response. `number_divergence_flag` is set when any number appears
in one run and not the other.

### Key functions and types

- `ConsistencyResult`: score, agreement, the probe's conclusion, both number lists, the divergent
  numbers, both overlaps, `probe_halted`, `probe_error`, `number_divergence_flag`.
- `ConsistencyAgreement`: `HIGH | MEDIUM | LOW | UNKNOWN`.
- `_extract_numbers`, `_compute_score`, `_classify`: imported by name by
  [[validation/cross_validation.py]]. The `_extract_numbers` docstring says the named wrapper is
  kept for exactly that import.

### Design notes

- The docstring is explicit about what the score does not prove: two identical confabulations
  still agree. High consistency is weak positive evidence; low consistency is strong negative
  evidence.
- The probe is not persisted because it is a self-check on the primary run, not evidence in its
  own right (`docs/SYSTEM_DESIGN.md` §4).
- The chat route enables the probe when the `consistency_probe` setting is on or the model name
  does not contain "gemini" ([[web/server.py]] comment: Ollama-family determinism is documented as
  unreliable, ledger [ollama-determinism](ledger.html#ollama-determinism)).

### Limits and open issues

- `_unknown` defaults to `halted=True`, so a probe that failed with an ordinary exception (for
  example a connection error) is reported as `probe_halted: true` with the exception in
  `probe_error`. Found by reading the code.
- The probe goes through the same traced adapter, so its call shows in the trace as "LLM attempt
  2" and the live view says "Retrying" when nothing retried
  ([consistency-probe-shown-as-retry](ledger.html#consistency-probe-shown-as-retry), open).
- There is no dedicated unit test of the probe or the scoring functions; `tests/test_numeric.py`
  pins that the module uses the shared extractor, and the cross-agent tests exercise the scoring
  through [[validation/cross_validation.py]].

Related: [[validation/cross_validation.py]], [[pipeline/middleware.py]], [[core/numeric.py]]

## `validation/cross_validation.py`

**Role:** runs two agents independently on the same subject, each through the unmodified ADR-07
loop, and assembles everything the comparison produces: the verdict, the figure-by-figure rows,
the accounting checks and the synthesis. Also builds and persists the stored run. Implements the
Cross-Agent Validation SDD v1 (module docstring).

### How a comparison runs

`run_cross_agent_validation(subject, context_a, context_b, agent_a_id, agent_b_id, call_agent_a_fn,
call_agent_b_fn, *, ...)`:

1. **Both agents run, sharing one `run_id`.** Each has its own context. By default they run on
   two threads (`concurrent=True`); `CROSS_AGENT_MAX_CONCURRENCY=1` forces A then B (an
   unparseable value keeps the default of 2). Each thread gets its own copy of the context
   variables because LangFuse's nesting lives there (code comment). `on_agent_finished(slot,
   conclusion, halted)` fires from each agent's thread when it is done, which is how the live
   stream shows one agent finishing first. Agent B always runs, whatever A does.
2. **A halt is evidence.** `_run_one_agent` catches `HaltError` and keeps its reasoning objects.
   The result's `reasoning_objects` are always A's attempts then B's.
3. **Status.** `ComparisonStatus` is `COMPARED` (both concluded), `AGENT_A_HALTED`,
   `AGENT_B_HALTED` or `BOTH_HALTED`.
4. **Numbers.** Each surviving conclusion's quantitative tokens are reported even when no
   comparison was possible.
5. **When `COMPARED`:** the overlap score and agreement come from
   [[validation/consistency.py]]. The canonical rows from [[validation/facts.py]] are always
   computed (`metric_comparisons`), whichever rule decides the flag. Then `contradiction_rule`
   decides `contradiction_flag` and `divergent_numbers` (below).
6. **When not compared:** score, overlaps, agreement and `metric_comparisons` are `None`,
   `divergent_numbers` is empty, and `contradiction_flag` is `None`, never `False`.
7. **Accounting checks** (`structural_flags`, [[validation/constraints.py]]) run for whichever
   agents produced a conclusion, compared or not: the comment's reason is that an agent
   misquoting its input is an error whether or not the other agent halted.
8. **Synthesis** ([[validation/divergence.py]]) runs only when `COMPARED`, from the rows, the
   checks, and each agent's last successful reasoning object's `assessment`.

### The three contradiction rules

| `contradiction_rule` | What decides the flag | `divergent_numbers` |
|---|---|---|
| `symmetric_difference` (the function's default) | A token present in exactly one conclusion. With `concepts_expected_to_overlap=True` any such token flags; with `False`, only when both sides cited at least one number | The full symmetric difference, always reported |
| `concept_aware` | [[validation/concept_linkage.py]]: untagged tokens by presence/absence, shared lens concepts by value, other tagged tokens excluded | Only the tokens that drove the flag |
| `canonical_facts` | [[validation/facts.py]]: any `MISMATCH` or `UNCORROBORATED` row | The raw figures on flagging rows |

Which rule a live run uses is set in [[web/server.py]], not here: the ticker `lenses` pairing
defaults to `concept_aware`, the `bull_bear` pairing and generic (subject) runs default to
`canonical_facts` (generic with `include_years=True`), and a request may name a rule explicitly.
The rule used is stored as `contradiction_rule` so a reader can see where the verdict came from.

### Key types and functions

- `CrossAgentComparisonResult`: not frozen (follows `ConsistencyResult`); `to_dict()` gives the
  flat dict stored as `cross_agent_comparison`. `structural_flags` and `synthesis` are `None` only
  on results built before B3 and B5.
- `build_run_payload(result, reasoning_objects, *, scope)`: the stored payload and its
  `RunSession`. Reasoning objects are serialised at auditor scope (`investor_scope=False`)
  regardless of `scope`; redaction happens at read time in [[validation/gate.py]].
- `persist_cross_agent_run(..., extra=None)`: writes via [[web/db.py]], merging `extra` keys
  (producers, contexts, facts, claims, steps, `gate_policy`) without overwriting keys the payload
  already set. The comment records that until 2026-09-24 a stored compare run kept only 7 keys.
- `list_contradictions(ticker=None, limit=50)`: an in-process scan of `get_runs()` for
  `contradiction_flag is True`. It exists because the comparison lives inside the payload JSON,
  not in its own column (SDD §7.3's accepted trade-off, quoted in the docstring).

### Design notes

- `contradiction_flag=None` when nothing was compared: `False` would claim "checked, found
  nothing", which P3 forbids (class docstring; `docs/SYSTEM_DESIGN.md` §3.3).
- `symmetric_difference` stays the function default so existing callers and tests are unchanged
  (comment on `ContradictionRule`; `docs/SYSTEM_DESIGN.md` §4).
- `concepts_expected_to_overlap` came from live runs, not up-front design: under the
  presence/absence rule every live ticker with numbers flagged (RUN_LOG 2026-08-29, "Comparator
  semantics for information-asymmetric agents"; the function docstring cites
  `divij/model-test-report-2026-08-29.md`, Test 5).
- `canonical_facts` is opt-in for the lens pairing because it failed the plan's acceptance bar on
  the labelled corpus: it flags 6 of 16 disjoint-concept runs against `concept_aware`'s 1, and the
  5 extra are ratios whose inputs the corpus never recorded (RUN_LOG 2026-09-24, "B1 + U2";
  pinned in `tests/test_facts.py`, `TestAgainstLabeledCorpus`).

### Limits and open issues

- Only `HaltError` is caught per agent. Any other exception (a rate limit, a fetch failure)
  aborts the whole comparison and discards the other agent's records; there is no `ERROR` status
  (module docstring, "a design decision, not something to improvise").
- Comparison is numeric: two answers that disagree in substance but cite the same figures are not
  flagged (module docstring, SDD §14).
- The legacy `symmetric_difference` + `concepts_expected_to_overlap=False` combination still
  suppresses a flag when one side has no numbers, the failure mode that once hid the AAPL 0.34
  fabrication. Production no longer requests it
  ([asymmetry-fix-suppresses-historic-true-positive](ledger.html#asymmetry-fix-suppresses-historic-true-positive)).
- Storage is always full; the nested `session` copy is only stripped on investor reads
  ([session-scope-leak](ledger.html#session-scope-leak), open).
- **Doc disagreements found.** `docs/SYSTEM_DESIGN.md` §3.6 says the two agents run sequentially;
  the code runs them concurrently by default. §3.2 describes the two lenses as disjoint; since
  lens v2 (RUN_LOG 2026-09-25, "B2 + B3") they share `NetIncomeLoss` and
  `EarningsPerShareDiluted`. §3.4 says production uses `concept_aware`; that is true only for the
  `lenses` pairing. The docstring of `run_cross_agent_validation` says `concept_aware` is "the rule
  /api/compare uses", with the same caveat.
- Tested with scripted and fixture agents in `tests/test_cross_validation.py` (agreement,
  contradiction, halt paths, both rules, shared run ids, serialisation, persistence, same-source
  runs, `list_contradictions`) and `tests/test_concurrency_and_stream.py`. Live runs are recorded
  from 2026-08-29 onward in `logs/RUN_LOG.md`.

Related: [[validation/facts.py]], [[validation/concept_linkage.py]], [[validation/constraints.py]],
[[validation/divergence.py]], [[pipeline/middleware.py]], [[web/server.py]], [[web/db.py]]

## `validation/concept_linkage.py`

**Role:** the `concept_aware` contradiction rule. Tags each figure in a conclusion with the lens
concept named nearest to it, then compares only what the two agents could both have been asked
about.

### How it works

- `CONCEPT_KEYWORDS` maps six XBRL concepts (`Assets`, `Revenues`, `NetIncomeLoss`,
  `EarningsPerShareDiluted`, `EarningsPerShareBasic`, `OperatingIncomeLoss`) to prose keywords and
  the raw tag name lowercased. The tag names are there because lens contexts are literal
  `Concept: value` lines and models echo them; the comment records that leaving them out halved
  the hit rate during development.
- `tag_numbers(conclusion)` finds each `QUANTITATIVE_RE` token, finds its sentence, and tags it
  with the concept whose keyword occurrence ends closest to the token (`_nearest_concept`), or
  `None`. Distance is measured from the end of the keyword because names precede their values;
  measuring from the start made a long keyword look farther away, a bug the Diluted/Basic EPS
  regression test caught (code comment).
- Sentences split only on `.`, `!` or `?` followed by whitespace, so a decimal point never ends a
  sentence (the comment cites GOOGL's diluted EPS pair 14.41 vs 14.24).
- `contradiction_flag_concept_aware(a, b, *, shared_concepts=())`:
  - Untagged tokens keep the presence/absence rule: the symmetric difference of the two untagged
    sets is divergent.
  - For each concept in `shared_concepts` that both agents cite, if no value on one side matches
    any value on the other (to the cent for EPS, within 0.5% otherwise, `_same_value`), all those
    tokens are divergent. A shared concept only one agent cites is not flagged.
  - Any other tagged token is excluded: the other agent was never given that concept.
  - Returns `(flag, divergent_numbers, {"a": tagged_a, "b": tagged_b})`, so a caller can see why.

### Design notes

- Built to fix the disjoint-concepts over-flag: 16 of 31 real runs flagged only because the two
  lenses read different concepts (module docstring, citing
  `divij/cross-agent-validation-disjoint-concepts-diagnosis.md`). Measured on the stored corpus:
  15 of those 16 are no longer flagged and the one confirmed true positive still is
  (`tests/test_concept_linkage.py`, `tests/test_real_run_corpus.py`; ledger
  [disjoint-concepts](ledger.html#disjoint-concepts)).
- `shared_concepts` (B2, 2026-09-25) is derived by the caller from the lens definitions
  (`producers.lens.shared_concepts`), not assumed here. The default, no shared concepts, is the v1
  behaviour the corpus tests pin (RUN_LOG 2026-09-25, "B2 + B3").

### Limits and open issues

- The tagging is a substring match, not an entity linker. The RUN_LOG found part of the measured
  15-of-16 to be an artifact: "Return on **Assets** 18.85%" is tagged `Assets` and excluded, which
  also hid two wrong asset-turnover figures (RUN_LOG 2026-09-24, "B1 + U2").
- An untagged ratio is the same shape whether it is a sound derived metric or a fabrication; this
  rule cannot tell them apart (module docstring).
- Periods are not considered: a quarterly and an annual net income for a shared concept read as a
  conflict (function docstring; that is `canonical_facts`' job).
- **Stale docstring.** The module docstring says it "is not called from web/server.py or anywhere
  in the production /api/compare path" and that [[validation/verification.py]] is "not currently
  wired into the cross-agent path". Both are out of date: [[validation/cross_validation.py]] calls
  this rule when `contradiction_rule="concept_aware"`, which [[web/server.py]] uses by default for
  the `lenses` pairing, and the compare route has called `verify_claims` since 2026-09-11
  ([fabrication-not-caught](ledger.html#fabrication-not-caught)).
- `tests/test_facts.py` (`TestSingleSourceOfAliases`) checks these keywords against the alias list
  in [[validation/facts.py]].

Related: [[validation/cross_validation.py]], [[validation/facts.py]], [[producers/lens.py]]

## `validation/facts.py`

**Role:** canonical facts (B1). Turns each conclusion into figures tagged with what they measure
and when, then compares the two agents metric by metric and labels every pairing with one status.
These rows are the figure matrix a reviewer reads, and the only rows that can open the gate.

### Extraction (`extract_facts`)

`extract_facts(conclusion, *, include_years=False)` works sentence by sentence:

1. **Masking.** `[SOURCE: ...]` brackets and URLs are blanked first, so digits in them never become
   figures.
2. **Candidates.** Every `QUANTITATIVE_RE` token. With `include_years`, bare four-digit years
   (1800 to 2099) that don't overlap a token or a period expression are added as `year` facts.
3. **Metric.** `_metric_for` picks the nearest alias that ends before the figure in the same
   clause; else the nearest after it in the clause; else the nearest earlier in the sentence. Ties
   go to the longer alias ("diluted eps" beats "eps"). Clauses break on `;`, `,` and " and ",
   " while ", " whereas ", " but ". Year aliases are only considered for year candidates.
4. **Reclassification**, in this order:
   - a `self_report` metric (confidence, certainty) is dropped: a model's rating of itself is not a
     claim about the subject;
   - a figure followed by "per share", "a share" or "/share" becomes EPS, whatever word precedes it;
   - a lens-family or untagged figure whose clause contains "ratio" becomes `unnamed_ratio`
     (derived);
   - a `%` figure on a lens or market metric becomes that metric's change (`revenue_change`,
     family `percent_change`);
   - an untagged `%` figure in a sentence with a change word ("up", "grew", "year over year")
     becomes `untagged_change`.
5. **Period.** The nearest period expression in the sentence (`_PERIOD_PATTERNS`: "Q3 FY2026",
   "FY2026 Q3", "third quarter of 2026", bare "Q3", TTM, "nine months ended" or YTD, "fiscal 2025").
   Years never get a period. No expression means `unknown`.

`METRICS` is the dictionary: each `MetricDef` has a name, a plain label, a family and its aliases,
plus XBRL tags for lens metrics. The families are `currency` and `per_share` (the lens metrics),
`derived` (margins, ROA, ROE, asset turnover, debt-to-equity, current ratio), `market` (market
cap, share price: never in a filing lens), `year` (release and founding year, generic subjects
only), `self_report`, and the fallback `untagged`. `context_facts(context)` runs the same
extraction line by line over an agent's context, to learn what it was handed.

`Period.compatible` treats a missing fiscal year as "not stated", not "different": kind and quarter
must match, and years must match only if both are stated.

### Comparison statuses (`compare_facts`)

`compare_facts(a_facts, b_facts, a_inputs=None, b_inputs=None)` groups each side's tagged facts by
metric. Two merges happen first: an unspecified "EPS" equal to a specific EPS on the same side is
dropped as the same figure, and an unspecified EPS that remains pairs with whichever specific EPS
the other side gives (the closer value). Then every metric gets one row:

| Status | Exact condition in the code | Flags? |
|---|---|---|
| `MATCH` | Both sides cite the metric; the closest compatible pairing is within tolerance. Also: neither side stated any period (compared as the shared filing period, with a note, except for years); or only one side stated a period and some pair of values agrees (with a note). Also an untagged figure whose value matches an untagged figure on the other side | No |
| `MISMATCH` | Both sides cite the metric, a compatible pairing exists (or neither side stated a period), and the closest pairing is outside tolerance | Yes |
| `DIFFERENT_PERIODS` | Both sides stated periods for the metric, and no pair of stated periods is compatible | No |
| `UNVERIFIABLE_PERIOD` | Only one side stated a period, no compatible pair exists, and no pair of values agrees | No |
| `ONE_SIDED` | One side cites a `currency` or `per_share` metric that is not among the metrics found in both agents' contexts | No |
| `CITED_BY_ONE` | One side cites a `currency` or `per_share` metric that appears in both agents' contexts (lens v2's shared figures) | No |
| `UNCORROBORATED` | One side cites a figure of any other family (derived that can't be recomputed, market, percent change, year), or an untagged figure with no value match on the other side | Yes |
| `DERIVED_OK` | One side cites a derived ratio in `DERIVATIONS`, both components are found in that side's own figures or inputs, and the stated value is within 2% of the recomputed fraction or percentage | No |
| `DERIVED_WRONG` | The same, but outside 2% | No |

"Flags" means the status is in `FLAGGING_STATUSES` and so raises `contradiction_flag` when the
run's rule is `canonical_facts`. Rows are sorted by `_SEVERITY` (`MISMATCH` first, `MATCH` last),
then label. `variance_pct` (difference over the larger value, in percent) is set only on `MATCH`
and `MISMATCH` rows.

**Tolerances** (`TOLERANCE`, each with its reason in the code): currency 0.5% relative, per-share
$0.005 absolute ("EPS is reported to the cent"), percent change 0.1 points absolute, derived,
market and untagged 1% relative, years exact. Derivations use a looser 2% because agents round both
inputs before dividing (the comment's example: ROA 18.85% against 18.96% unrounded).

`DERIVATIONS` recomputes net, operating and gross margin, ROA, ROE, asset turnover,
debt-to-equity (`total_liabilities / equity`) and current ratio. The row's note shows the
recomputed value in the form the agent used.

### Key functions

- `extract_facts`, `compare_facts`, `context_facts`: above.
- `contradiction_flag_canonical(a, b, *, include_years, context_a, context_b)`: runs extraction
  and comparison and returns `(flag, divergent raw figures, rows)`. Called for every compared run
  by [[validation/cross_validation.py]].
- `CanonicalFact.to_dict()` and `MetricComparison.to_dict()` (which adds `flags`) are what gets
  stored.
- `METRICS` and `TOLERANCE` are reused by [[validation/constraints.py]].

### Design notes

- Why it exists: bare-string rules cannot say "both agents cite diluted EPS for Q3 FY26 and the
  values differ", and they misread things that are not claims, like a model's "Confidence level:
  90%", which flagged NVDA on 2026-09-24 (module docstring; RUN_LOG 2026-09-24, "B1 + U2").
- `UNCORROBORATED` flags on purpose: it keeps the presence/absence rule for untagged figures
  because that is what catches the corpus's one confirmed fabrication, AAPL's "debt-to-equity
  ratio of 0.34" (module docstring).
- A recomputable one-sided ratio is checked rather than flagged. The docstring records two AAPL
  runs whose "asset turnover of 0.13" is wrong by 5x against the same conclusion's revenue and
  assets; `DERIVED_WRONG` shows that as one agent's internal error, not a cross-agent
  contradiction.
- `CITED_BY_ONE` was added with lens v2 so a shared figure one agent skipped is not mislabelled
  "Only one agent was given this" (RUN_LOG 2026-09-25, "B2 + B3").
- Only `MISMATCH` is a two-sided conflict; that is why it alone gates (see
  [[validation/gate.py]]).

### Limits and open issues

- Tagging is lexical. An unrecognised phrasing ("earnings were $109.4 billion") stays untagged;
  "earnings" is deliberately not an alias because it is ambiguous (RUN_LOG 2026-09-24, "B1 + U2").
- The derivation check takes the first figure of each component on that side, and ignores period
  and annualisation: a quarterly net income over point-in-time assets is a quarterly ROA (same
  entry).
- **`ONE_SIDED` is broader than its description.** The docstring says it is expected "when only
  that agent's lens carries it", and [[validation/audit.py]] labels it "Only one agent was given
  this". The code only checks that the metric is not in both contexts: a dollar figure that
  neither agent was given, or any one-sided dollar figure when contexts are empty, is also
  `ONE_SIDED`, and so never flags. Found by reading the code.
- The module docstring says `MISMATCH` and `UNCORROBORATED` raise `contradiction_flag`. That is
  true only under `canonical_facts`; under `concept_aware` the rows are shown but do not decide the
  flag.
- Coverage of the accounting checks inherits this tagger's coverage
  ([checks-lexical-coverage](ledger.html#checks-lexical-coverage)).
- Tested by `tests/test_facts.py` (extraction, periods, comparison rules, derivations, years, the
  labelled corpus). Observed live on 2026-09-24 (RUN_LOG "B1 + U2"): an NVDA revenue row
  `DIFFERENT_PERIODS`, AAPL, MSFT and GOOGL flagged only by `UNCORROBORATED` rows, an Inception
  release year `MATCH`. The same entry's MSFT `MATCH` line was a unit test, not a live run
  (RUN_LOG 2026-09-26, "Correction: two claims in earlier entries were wrong").

Related: [[validation/constraints.py]], [[validation/cross_validation.py]], [[validation/gate.py]],
[[core/numeric.py]]

## `validation/constraints.py`

**Role:** the accounting checks (B3). Asks of each agent on its own, and of the filing it was
given, whether the figures add up. Results are stored as `cross_agent_comparison.structural_flags`;
a failed hard check about an agent's figures is a gate item.

### The three passes

`run_checks(a_conclusion, b_conclusion, *, given_facts=None, source_payload=None)` runs, for each
agent with a conclusion:

1. **Internal consistency** (`_agent_rules`). Each rule in `RULES` whose metrics the agent stated
   is tried on every combination of that agent's figures whose stated periods are compatible
   (figures with no stated period count as the shared filing period). Any passing combination
   passes the rule; it fails only if every combination fails. No compatible combination means
   `skipped`, with the reason. A rule whose figures the agent didn't state is not shown at all.
2. **Claim versus source** (`_claims_vs_source`). For each fact the agent was given (a
   `datasources.edgar.Fact` dict, see [[datasources/edgar.py]]), mapped to a metric through
   `CONCEPT_METRIC`, the agent's cited figures for that metric are compared with the given value.
   Figures with a different stated period are set aside; if none remain, the check is `skipped`.
   One agreeing figure passes, because agents often cite the prior period beside the current one.
   A figure agrees if it is within the family tolerance from [[validation/facts.py]], or within one
   unit of the last digit the agent wrote (`_precision`: "$94.9B" allows $0.1B), because rounding
   or truncating is not misquoting.
3. **Source sanity** (`_source_rules`), once per run, only with a `source_payload`. `SOURCE_RULES`
   run over the companyfacts JSON already fetched (no new HTTP call), using `SOURCE_TAGS`. Where a
   concept was filed more than once for a period the latest filing wins. Each rule uses the latest
   period all its figures share (the shortest span for the same end date); none shared means
   `skipped`.

Results are sorted fail, skipped, pass; hard before heuristic. The return value is
`{"policy": "b3-v1", "checks": [...], "gating": [keys of gating checks]}`.

### The checks

| Rule id | Kind | Passes | Where it runs |
|---|---|---|---|
| `eps_basic_ge_diluted` | hard | Diluted EPS is at most basic EPS plus $0.005; with a loss (basic below zero), the two are within $0.005 | Agents and filing |
| `fcf_identity` | hard | Stated free cash flow is within 1% of operating cash flow minus the absolute capital expenditure | Agents only (FCF is not a filed concept) |
| `balance_sheet` | hard | Total assets within 2% of total liabilities plus equity | Agents only |
| `balance_sheet_filed` | hard | Filed `Assets` within 0.1% of filed `LiabilitiesAndStockholdersEquity` | Filing only |
| `matches_source` | hard | A cited figure agrees with the filing value that agent was given | Agents only |
| `net_le_operating` | heuristic | Net income at most operating income | Agents and filing |
| `operating_le_gross` | heuristic | Operating income at most gross profit | Agents and filing |
| `gross_le_revenue` | heuristic | Gross profit at most revenue | Agents and filing |

Each `CheckResult` carries a stable `key` (`check:agent_a:<rule>`, `source:agent_b:<metric>` or
`check:source:<rule>`), the rule, kind, scope (`agent_a`, `agent_b` or `source`), outcome (`pass`,
`fail` or `skipped`), the rule in words, the arithmetic shown (`math`), a reason (why skipped, or a
failed heuristic's rationale) and the metrics involved. `to_dict()` adds `gates` and `who`
("Agent A", "Agent B", "The filing").

**What gates:** `gates` is true only when the kind is hard, the outcome is fail and the scope is
not `source`. Heuristic failures and every filing check are shown and never gate.

### Design notes

- Only definitional relationships are hard. "Net income at most operating income" is not an
  identity, since a one-off gain or tax benefit legitimately breaks it, so it and its siblings are
  heuristics shown as "unusual, worth a look" (module docstring, "the approved plan says so").
- The balance-sheet check allows 2% because a stated shareholders' equity often excludes
  noncontrolling interest (rule rationale). The filing check uses the filer's own total instead of
  adding two figures a filer may define differently (code comment).
- Different stated periods skip a rule rather than fail it (module docstring).
- Revenue's source tags include the same fallbacks as [[datasources/edgar.py]] because AAPL stopped
  filing `us-gaap:Revenues` in FY2018 (code comment).
- Nothing here decides the right figure: a check states what it computed and the human decides
  (module docstring).

### Limits and open issues

- The checks only see figures [[validation/facts.py]] tags: an unrecognised phrasing is never
  checked, EPS without "basic" or "diluted" is not checked against the filing (`CONCEPT_METRIC`
  has no entry for plain `eps`), and "...$2.02 and $2.03, respectively" yields one figure. A check
  that doesn't run isn't shown, so no failure is not evidence of a correct figure
  ([checks-lexical-coverage](ledger.html#checks-lexical-coverage), open).
- Source sanity may check a different period than the agents were given (MSFT on 2026-09-25:
  agents given Q3, filing checked on the fiscal year). The period is printed on every result (same
  ledger entry).
- Tested by `tests/test_constraints.py` (each rule, rounding, prior-period citations, different
  periods, source sanity on a real filing sample, the gate, the decisions-table migration, the
  route). Observed live on 2026-09-25 (RUN_LOG "B2 + B3"): AAPL's claim-vs-source and filing
  checks passed; GOOGL's `net_le_operating` heuristic failed on agent B and on the filing itself,
  read as a real non-operating gain and not gated; no gate opened in that batch. The B5 entry
  (RUN_LOG 2026-09-26, "Option 1 (assessment extraction) + B5 + U8") records a failed
  claim-vs-source check on NVDA run `9b1a9e0e`'s agent A net income.

Related: [[validation/facts.py]], [[validation/gate.py]], [[datasources/edgar.py]]

## `validation/divergence.py`

**Role:** the synthesis (B5). From the rows, the checks and each agent's assessment, says why the
two views differ, counts what each agent has behind it, and proposes a consensus grade only when
one exists. It calls no model and decides nothing.

### Divergence classification

`synthesize(rows, structural_flags, assessments)` sets `primary_conflict_driver` by the first test
that holds:

| Driver | Condition in the code |
|---|---|
| `data` | Any row is `MISMATCH` or `DIFFERENT_PERIODS` |
| `assumption` | Both agents gave an assessment and their stated assumptions differ: `revenue_growth_pct` more than 1.0 point apart, or a different `margin_trend` or `horizon_months` (only keys both stated are compared) |
| `weighting` | Both agents gave a grade, and the grades or directions differ, with neither of the above |
| `insufficient` | Fewer than two grades |
| `none` | Both graded, same grade and direction, no data conflict or assumption difference |

Each driver comes with a template `audit_recommendation` (for example, for `data`, settle which
figure the filing supports before weighing either grade, naming up to three conflicting metrics).
The docstring calls `weighting` a residual, "never ... a finding about which agent is right".

### Evidence counts

Each `grade_candidates` entry carries the agent's grade, direction, assumptions and five counts
(`_counts`), counted and never weighted:

- `match_filing` and `contradict_filing`: that agent's `matches_source` checks that passed and
  failed;
- `unchecked`: rows the agent cited whose metric had no `matches_source` check, other than
  `UNCORROBORATED` rows;
- `unbacked`: rows the agent cited with status `UNCORROBORATED` or `DERIVED_WRONG`;
- `hard_check_failures`: that agent's failed hard checks.

### Consensus rule

`consensus_grade` is `{grade, direction}` only when both agents gave a grade, grade and direction
are equal, and no hard check failed for either agent. Otherwise it is `None`, with
`consensus_reason` saying which condition failed. `needs_decision` is true when both graded and
they differ in grade or direction; [[validation/gate.py]] turns that into a `grade` gate item. A
failed hard check blocks the consensus but does not set `needs_decision`.

The return value also carries `policy` (`b5-v1`), `data_conflicts` (the metrics of the `data` rows)
and `assumption_differences`.

### Design notes

- Evidence is counted, never scored: "a number no record produced is not evidence" (module
  docstring, P3).
- A grade reaches an investor only when a human records one; the agents' grades are model
  judgments (P1, P8; module docstring). Investor-scope redaction of the synthesis is in
  [[validation/gate.py]].
- Assessments come from the separate extraction call chosen by the human for B4 ([[core/assessment.py]];
  RUN_LOG 2026-09-26, "Option 1 (assessment extraction) + B5 + U8").

### Limits and open issues

- The evidence behind the classes is thin. Both live grade conflicts recorded on 2026-09-26 (AAPL
  `8ecb0922`, NVDA `9b1a9e0e`) were classed `assumption` from extraction v1, which had reported
  past growth rates as assumptions, so the class was wrong. v2's forward-looking check is a word
  list ([synthesis-thin-and-lexical](ledger.html#synthesis-thin-and-lexical), open).
- A proposed consensus cannot be confirmed as the published grade: only a disagreement opens a
  grade decision (same ledger entry).
- A `DERIVED_WRONG` row is counted in both `unchecked` and `unbacked`, because `unchecked` excludes
  only `UNCORROBORATED`. Found by reading the code.
- Tested by `tests/test_synthesis.py` (the driver order, the residual, the consensus rule, the
  counts, the grade gate and the route).

Related: [[validation/gate.py]], [[validation/constraints.py]], [[validation/facts.py]],
[[core/assessment.py]]

## `validation/gate.py`

**Role:** the human decision gate (BG). Decides what in a compare run needs a named human's
decision, validates each decision before it is stored, reports the gate's state, and redacts a run
for investor-scope readers while a decision is open.

### Gate policy and what opens the gate

`GATE_POLICY = "v3"`. The history is in the code comment:

- **v1** (BG, 2026-09-25): mismatched figures gate.
- **v2** (B3, 2026-09-25): failed hard checks gate too.
- **v3** (B5, 2026-09-26): both agents graded and disagree; a human sets the grade.

A run is gated under the policy stored with it; [[web/server.py]] stamps `gate_policy` on each new
compare run. A run stored without the key is `NOT_GATED` and is never gated retroactively, even if
its rows contain a `MISMATCH` (the approved plan's rule, module docstring).

`gate_items(payload)` builds the items, keyed the way decisions cite them:

| Kind | Source | Item key (`metric`) | `status` |
|---|---|---|---|
| `figure` | A `metric_comparisons` row with status in `GATING_STATUSES` (only `MISMATCH`), on a `COMPARED` run | The metric name | `MISMATCH` |
| `check` | A `structural_flags` check with `gates` true | The check key | `CHECK_FAILED` |
| `grade` | `synthesis.needs_decision` | `grade` | `NO_CONSENSUS` |

A grade item also carries both candidates (grade, direction, assumptions) and the conflict driver.

### Decisions allowed per kind

| Decision | Meaning | `figure` | `check` | `grade` |
|---|---|---|---|---|
| `accept_a` | Agent A's figure (or grade) is right | yes | | yes |
| `accept_b` | Agent B's figure (or grade) is right | yes | | yes |
| `both_wrong` | Both figures are wrong | yes | | |
| `not_a_conflict` | Not a real conflict | yes | yes | |
| `override_value` | Set the correct value | yes | yes | |
| `confirmed_error` | The check is right: the agent's figure is wrong | | yes | |
| `set_grade` | Set the grade | | | yes |

A decision citing items of several kinds may only use a decision valid for all of them.

### Validating a decision (`validate_decision`)

It returns the cleaned fields or raises `DecisionError` with the reason in words. It never repairs
a bad value (P3). A decision is refused when:

- the run has no `gate_policy`, or no gate items;
- the decision is not one of `DECISIONS`;
- `decided_by`, trimmed, is shorter than `MIN_NAME` (2) characters, or the rationale is shorter than
  `MIN_RATIONALE` (20);
- `cited_items` is empty, not a list, or names something that is not a gate item in this run
  (repeats are dropped);
- the decision doesn't fit every cited kind;
- `set_grade` has no grade from `GRADES` (AAA, AA, A, BBB, BB, B, CCC, the closed vocabulary of
  [[core/assessment.py]]), or any other decision carries a grade;
- `accept_a` / `accept_b` on the grade alone, when that agent gave no grade (otherwise its grade
  becomes `final_grade`);
- `override_value` has no numeric value (booleans are refused) or cites more than one item, or any
  other decision carries a value.

### Gate state (`gate_state`)

`gate_state(payload, decisions)` takes decisions oldest first. The last decision citing an item
decides it; earlier ones are marked `superseded` and stay in the history (returned newest first).
The status is one of:

- `NOT_GATED`: stored before the gate existed;
- `NO_DECISION_NEEDED`: no gate items (compared with nothing gating, or not compared at all);
- `AWAITING_DECISION`: at least one item has no decision (`pending` lists them);
- `DECIDED`: every item has one.

`decided_grade` is the grade a human recorded on the `grade` item, with who and when: "the only
grade investors are ever shown" (code comment). Every state carries `identity_note`
(`IDENTITY_NOTE`): `decided_by` is the typed name, not an authenticated person.

### Investor-scope redaction (`redact_for_scope`)

`redact_for_scope(payload, scope, gate)` returns a copy with the gate attached. An auditor gets
everything. For an investor:

**Always withheld**, whatever the gate says:

- SEC-01's internal tier from every reasoning object, top-level and in `session`:
  `thought_log`, `raw_output`, `llm_tokens`, `directive_text`, `context_window`, `assessment`,
  `assessment_status`, `assessment_issues`, `assessment_source` (`_INTERNAL_KEYS`);
- the session's `directive_text` and the payload's top-level `thought_log`;
- the synthesis, replaced by `{policy, primary_conflict_driver, data_conflicts, withheld: true}`:
  an investor sees what kind of disagreement it is, not the grades, directions, assumptions,
  consensus or recommendation;
- the candidates on a grade gate item.

**Also withheld while the gate is `AWAITING_DECISION`:**

- each reasoning object's `conclusion`, `reasoning_steps` and `citations`;
- the comparison's `agent_a_conclusion` and `agent_b_conclusion` (set to `None`), and
  `agent_a_numbers`, `agent_b_numbers` and `divergent_numbers` (emptied);
- for every contested metric (the metrics of all pending items), the row's values, raw figures and
  variance, with `withheld: true` (status and periods stay);
- the arithmetic of each pending check, on the gate item and in `structural_flags`, and of any
  agent-scope check about a contested metric. Checks on the filing itself keep their arithmetic,
  because they state filed values, not an agent's claim;
- `claims` (emptied);
- search-result text in the trace: `strip_search_content` keeps a tool step's query and URLs,
  removes the result preview in `detail` and the per-result titles and snippets, and marks the
  step `result_withheld`; an agent step's `error` keeps only its exception type, because
  parse-failure messages can quote model output;
- a `withheld_pending_review` note (`PENDING_NOTE`) announces it.

Agreed rows, the given filing facts and the contexts stay visible. A pending grade item alone is
enough to withhold both conclusions.

### Design notes

- The handoff condition is specific and testable (P4): every gated item cited by at least one
  recorded decision (module docstring).
- Only a real two-sided conflict gates. `UNCORROBORATED` rows raise the flag but are shown, not
  gated; heuristic warnings and filing checks never gate (module docstring; RUN_LOG 2026-09-25,
  "BG + U3: the human decision gate, backend and inline UI").
- The module has no database code; the caller passes decisions in, so it is testable without
  SQLite. Decisions are stored in [[web/db.py]]'s append-only `gate_decisions` table (module
  docstring).
- `strip_search_content` exists because the investor read of gated run `ec1a3b44` still carried
  agent A's disputed "1998" inside a search result in the trace (RUN_LOG 2026-09-26, "Correction:
  two claims in earlier entries were wrong; the trace leak they hid is fixed"; ledger
  [trace-leaks-disputed-values](ledger.html#trace-leaks-disputed-values), resolved after it was
  observed on a restarted server).
- The assessment keys joined `_INTERNAL_KEYS` after investor reads were found carrying
  `assessment_status`; a test now checks that `redact_for_scope` drops what
  `ReasoningObject.to_dict(investor_scope=True)` drops (RUN_LOG 2026-09-26, "B4 + U7"; code
  comment; [[core/schemas.py]]).
- `PENDING_NOTE` is general because since B3 and B5 the open item may be a check or the grade
  (code comment; RUN_LOG 2026-09-27, "B6 + U9").
- The AI sessions that built the gate recorded no decision on a live gated run: "An AI clearing a
  human gate is exactly what P4 forbids" (RUN_LOG 2026-09-25, "BG + U3").

### Limits and open issues

- Identity is self-declared: any auditor-scoped token can decide, and anyone can mint one
  ([gate-identity-self-declared](ledger.html#gate-identity-self-declared),
  [audit-criticals](ledger.html#audit-criticals), both open).
- The withholding is only as strong as read auth: a read with no token is served at the run's
  stored scope, and storage holds everything (same ledger entries; RUN_LOG 2026-09-25, "BG + U3").
- Text a user supplied as a generic run's context is still shown to investors as the input
  ([trace-leaks-disputed-values](ledger.html#trace-leaks-disputed-values)).
- **Mixed decisions can clear the grade without a grade.** `accept_a` or `accept_b` citing the
  grade item together with a figure passes validation (both kinds allow it), but `final_grade` is
  only filled in when the grade is the only kind cited. The grade item is then decided and
  `decided_grade` is `None`. Found by reading the code; no test covers it.
- Because `override_value` needs exactly one item, a decision covering a figure and a check can in
  practice only be `not_a_conflict`.
- **Stale docstring.** The module docstring says B5's "no consensus" trigger "is not implemented
  here"; policy v3 implements it as the `grade` item. The ledger entry
  [escalation-undefined](ledger.html#escalation-undefined) likewise still lists the B3 and B5
  triggers as not covered.
- A failed check's refusal messages are worded for figures in places ("Pick at least one mismatched
  figure this decision is about").
- `gate_state` for a `NOT_GATED` run returns no `decided_grade` key.
- `docs/DATA_CONTRACT.md`'s run-store table lists `runs`, `sessions` and `flags` but not
  `gate_decisions`.
- Tested by `tests/test_gate.py` (states, validation, redaction, the decision store and its
  append-only triggers, routes), `tests/test_constraints.py` (check items), `tests/test_synthesis.py`
  (grade items) and `tests/test_trace_withholding.py` (trace stripping, including the real gated
  run). Observed live: run `ec1a3b44` (a generic question, agents answering 1998 and 1996) entered
  `AWAITING_DECISION` on 2026-09-25 (RUN_LOG "BG + U3").

Related: [[validation/facts.py]], [[validation/constraints.py]], [[validation/divergence.py]],
[[validation/audit.py]], [[web/db.py]], [[web/server.py]], [[web/auth.py]]

## `validation/audit.py`

**Role:** the audit record of one compare run (B6), as JSON for machines and Markdown for people.
A view of the stored record: nothing is recomputed and nothing stored is changed.

### The record (`audit_record`)

`audit_record(run, *, scope)` expects a run already passed through `redact_for_scope`
([[web/server.py]] does that), so an investor's export can never carry more than an investor's read.
The fields:

| Field | Read from |
|---|---|
| `format` | `audit-v1` |
| `run_id`, `subject` | the run (`ticker`, else `subject`) |
| `generated_at` | the time of the export (UTC, seconds) |
| `scope` | the reader's scope |
| `directive_version` | the session |
| `producers` | the run |
| `comparison_status`, `contradiction_flag`, `contradiction_rule`, `metric_comparisons`, `structural_flags` | `cross_agent_comparison` |
| `primary_conflict_driver`, `grade_candidates`, `consensus_grade`, `consensus_reason`, `audit_recommendation` | the synthesis |
| `grades_withheld` | whether the synthesis was withheld (investor scope) |
| `gate_status`, `gate_pending`, `decided_grade`, `decisions`, `decider_identity` | the gate |
| `filings` | one row per accession number in the run's given facts: form, filing date, the concepts drawn from it, and the EDGAR index URL when a CIK is recorded in the trace |
| `withheld_pending_review` | the redaction note, if any |

### The Markdown export (`to_markdown`)

A reviewer's report, every line from a recorded field:

- a title with subject and run id, and a line giving the scope, directive and format and saying
  that figures and checks are machine-verified conformance while adequacy is a human judgment;
- a callout when material is withheld pending review;
- **Summary:** comparison status and recorded verdict with its rule, the conflict driver in words,
  the recommendation, the human-set grade with who and when (or, at investor scope, that no grade
  is published), and the gate status with open items;
- **Figures, agent by agent:** a table of label, A, B, difference and a plain status label; withheld
  values read "withheld";
- **Accounting checks:** one line per check, marked pass, fail (hard or heuristic) or skipped, with
  "needs a decision" on gating checks and "unusual, not an error on its own" on failed heuristics;
- **Grade candidates (model judgments):** grade, direction and the five evidence counts, then the
  proposed consensus ("not a published grade until a reviewer sets it") or the reason there is
  none;
- **Decisions (append-only; newest first):** when, who, what, the grade or value set, the items
  cited, superseded marks, the rationale, and the identity note;
- **Sources:** each filing with its accession number and URL.

Table cells escape `|` and are kept to one line (`_cell`).

### Design notes

- Built after redaction, so export and read cannot diverge (module docstring; tested in
  `tests/test_audit.py`, `test_an_investor_export_carries_what_an_investor_read_carries`).
- Markdown is the default human export per the repository's "default to Markdown for humans" rule
  (module docstring, citing AGENTS.md).
- Served by `GET /api/runs/{id}/audit` (JSON) and `GET /api/runs/{id}/export.md` (a download named
  `review-<id>-<scope>.md`), compare runs only ([[web/server.py]]; RUN_LOG 2026-09-27, "B6 + U9").

### Limits and open issues

- The status labels in `_STATUS` inherit [[validation/facts.py]]'s `ONE_SIDED` imprecision: "Only
  one agent was given this" is also shown for a one-sided dollar figure neither agent was given.
- `generated_at` is the only field not read from the record; two exports of the same run differ in
  it.
- Tested by `tests/test_audit.py` (the shape, the Markdown, decisions and a human grade, cell
  escaping, the routes, that exporting changes nothing stored). Observed live: the investor export
  of `8ecb0922` downloaded with no agent grade (RUN_LOG 2026-09-27, "B6 + U9").

Related: [[validation/gate.py]], [[validation/divergence.py]], [[web/server.py]]
