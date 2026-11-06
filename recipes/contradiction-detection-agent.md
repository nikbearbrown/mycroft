---
status: RUNNABLE-SAMPLE
todos_open: 0
last_gate: "gate-6 approve, 2026-10-04, logs/RUN_LOG.md#2026-10-04"
attestation: null
recipe_version: 0.2.1
---

# Contradiction_detection_agent

> **Status basis (2026-10-04).** All six step scripts exist and run end to end over a frozen, synthetic
> sample corpus of 16 fictional companies (clean) and 17 catalogued defects (defective). The detector
> (step 5) is a faithful port of the original workflow's JavaScript and matches it on every sample
> company (`scripts/tools/contradiction-detection-agent-parity-check.py`). Every claim below is backed
> by a recorded check in `logs/contradiction-detection-agent/self-test-results.json` (each one: what ran, what was seen, what was expected).
>
> **Not claimed:** anything live. No database, API or model has ever been called by this recipe; live mode
> stops in steps 2 and 5. Nor that the six patterns are good investment signals: adequacy is a human
> judgment (P1). Details worth knowing when reading the flags are under *Notes from porting*.
>
> **Why RUNNABLE-SAMPLE, and no further (2026-10-04).** The full sample run completes, conformance passes,
> and the audits were generated and read. Gates 1-4 and 6 were cleared and gate 5 was denied by Tanmay Kulkarni,
> recorded in `logs/gate-decisions/` and `logs/RUN_LOG.md#2026-10-04`. Both typed TODOs are closed by those
> decisions (`todos_open: 0`). RUNNABLE-LIVE is **not** claimed: live mode is denied, with the preconditions to
> reopen it in the gate-5 record. `attestation: null` because VERIFIED needs live runs first.

## Purpose

Contradiction_detection_agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to contradiction_detection_agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (7 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (2 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| Manual Trigger | `manualTrigger` | conductor |
| Set Company Input | `set` | conductor |
| DB: Fetch Earnings Guidance Signals | `postgres` | ingest |
| DB: Fetch Risk Admissions | `postgres` | ingest |
| DB: Fetch QA Pressure Map | `postgres` | ingest |
| DB: Fetch News Signals | `postgres` | ingest |
| DB: Fetch Tech Stack Signals | `postgres` | ingest |
| Aggregate All Signals | `code` | conductor |
| Run Pattern Detection Engine | `code` | conductor |
| Build Groq Prompt | `code` | tool |
| LLM Needed? | `if` | conductor |
| Groq: Analyse Contradictions | `httpRequest` | tool |
| Process Groq Response | `code` | gigo |
| No-Flag Passthrough | `code` | conductor |
| DB: Insert Contradiction Report | `postgres` | report |
| Fan Out Flags | `code` | conductor |
| DB: Insert Contradiction Flag | `postgres` | gigo |
| Build Final Report | `code` | report |
| Execute a SQL query | `postgres` | gigo |
| Execute a SQL query1 | `postgres` | gigo |
| Execute a SQL query2 | `postgres` | ingest |
| Execute a SQL query3 | `postgres` | gigo |
| HTTP Request | `httpRequest` | ingest |
| Process News Response | `code` | gigo |
| DB: Save News Signals | `postgres` | gigo |
| Merge | `merge` | conductor |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (7 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (7 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (2 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (2 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (8 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source gate: Every declared source is present, parses, and is the one this recipe describes (the node table matches the workflow; every fixture matches its frozen SHA-256). Test: `python3 scripts/tools/contradiction-detection-agent-gate-check.py --gate 1`. Human capacity: [TO].
   Updated 2026-10-04 so the test checks this gate's condition directly and can fail. The test now requires step 1's report for the run to say ok and a fresh provenance check to find no drift since. Previous test, kept for the record: `test -f "recipes/contradiction-detection-agent.md" && rg -n "\[TODO: DEFINE]" "recipes/contradiction-detection-agent.md" || true`.
   Previous condition, kept for the record: All required source paths are present or explicitly marked with a typed TODO.
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 scripts/tools/contradiction-detection-agent-gate-check.py --gate 2`. Human capacity: [PF].
   Updated 2026-10-04 so the test checks this gate's condition directly and can fail. The test now checks that the envelope declares sample mode, or live mode with a gate-5 approval, as well as parsing. Previous test, kept for the record: `python3 -m json.tool data/raw/contradiction-detection-agent/run-envelope.json`.
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `python3 scripts/tools/contradiction-detection-agent-gate-check.py --gate 3`. Human capacity: [PA].
   Updated 2026-10-04 so the test checks this gate's condition directly and can fail. The test now requires every output of the run to parse and step 3 to report ok. Previous test, kept for the record: `find data/raw/contradiction-detection-agent data/verified/contradiction-detection-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
4. Script-readiness gate: Every one of the six step scripts exists and compiles, and the detector matches the original workflow's JavaScript. Test: `python3 scripts/tools/contradiction-detection-agent-gate-check.py --gate 4`. Human capacity: [IJ].
   Updated 2026-10-04 so the test checks this gate's condition directly and can fail. The test now requires all six step scripts to exist and compile, and the detector to match the original JavaScript (parity check). Previous test, kept for the record: `test -f scripts/ingest/contradiction-detection-agent-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/contradiction-detection-agent.md"`.
   Previous condition, kept for the record: Every step script exists or is represented by a typed development TODO.
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `python3 scripts/tools/contradiction-detection-agent-gate-check.py --gate 5`. Human capacity: [EI].
   Updated 2026-10-04 so the test checks this gate's condition directly and can fail. The test now requires a decision record naming a human, and fails if any artifact records a live call that decision did not approve. Previous test, kept for the record: `test -f logs/gate-decisions/contradiction-detection-agent-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/contradiction-detection-agent.md"`.
   DECIDED 2026-10-04 by Tanmay Kulkarni ("D2 deny"): **not approved.** Recorded in
   `logs/gate-decisions/contradiction-detection-agent-gate-5.json`. Live mode stays declined, not pending: the live paths have
   never been exercised here, and live failure modes have no fixtures. Reopening needs the four preconditions named in the
   record, then a new decision by a named human. The gate test reads the record, so a recorded deny closes the TODO without
   ever clearing the gate for live action.
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `python3 scripts/tools/contradiction-detection-agent-gate-check.py --gate 6`. Human capacity: [TO].
   Updated 2026-10-04 so the test checks this gate's condition directly and can fail. The test now checks the run's dated report for every contract section and its agent log for every contract field. Previous test, kept for the record: `test -f logs/contradiction-detection-agent-[DATE].json && test -f reports/generated/contradiction-detection-agent-[DATE].md`.
   DECIDED 2026-10-04 by Tanmay Kulkarni ("D5 approve"): the reports and agent logs of both sample runs were read and
   approved. Recorded in `logs/gate-decisions/contradiction-detection-agent-gate-6.json`, which hashes the four files.

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/contradiction-detection-agent-verify-provenance.py`
   Closed 2026-10-04 (the script above is built and exercised). Original note, kept for the record: `[TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.`
   Status: Built and exercised. Input: the recipe, the original workflow JSON, the run envelope, the fixture manifest (with a SHA-256 per fixture) and the gate-5 record. Output: the fields below plus `findings_digest`. Errors: a missing or unparseable source, a node-table mismatch between this recipe and the workflow, or a fixture changed since the manifest froze it stops the run (exit 1). Evidence: self-test section C.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `contradiction-detection-agent`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-ingest-inputs.py`
   Closed 2026-10-04 (the script above is built and exercised). Original note, kept for the record: `[TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.`
   Status: Built and exercised. Input: `run-envelope.json` and the fixture set it names. Output: one raw envelope per source (records carried verbatim, SHA-256, `fetched_at` from the frozen clock). Errors: missing envelope or source, or live mode, stop with exit 1; live mode is unimplemented by design and names the credentials it would need. An unparseable file is carried through, not dropped. Evidence: self-test section C.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `contradiction-detection-agent`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/contradiction-detection-agent/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent-validate-data-shape.py`
   Closed 2026-10-04 (the script above is built and exercised). Original note, kept for the record: `[TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.`
   Status: Built and exercised. Input: step 2's raw envelopes. Output: shape-clean rows promoted per source, every finding listed (missing or null required field, type error, value outside its allowed set or bounds, row not an object, unparseable source). Errors: all findings are reported first, clean rows still promoted, then status stop (exit 1). Field contracts are the original SQL SELECT lists. Evidence: self-test section A (13 shape defects, 0 false findings).
   Input: declared recipe inputs, prior step outputs, and gate decisions for `contradiction-detection-agent`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/contradiction-detection-agent/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent-transform-quality-check.py`
   Closed 2026-10-04 (the script above is built and exercised). Original note, kept for the record: `[TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.`
   Status: Built and exercised. Input: step 3's verified rows and the envelope. Output: one bundle per declared company holding exactly what the original queries return (same WHERE, ORDER BY, LIMIT). Withheld with reasons: duplicates, `schema_valid` not true, undeclared tickers. Reported but kept, as the original keeps them: rows older than the declared lookback and rows cut by a LIMIT. Errors: a missing source stops the step, and it writes no bundles. Evidence: self-test sections A and C.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `contradiction-detection-agent`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/contradiction-detection-agent/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/contradiction-detection-agent-run-approved-tools.py`
   Closed 2026-10-04 (the script above is built and exercised). Original note, kept for the record: `[TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.`
   Status: Built and exercised. Input: step 4's bundles. Output: per company, the six-pattern detection (flags, pattern results, skipped patterns, overall confidence level) and the original's LLM prompt as an approval-required handoff (`approved_for_live_action: false`), never sent. Errors: no bundles, or any mode but sample, stop with exit 1. Evidence: parity check (every company matches the original JS) and self-test section B (three deliberately broken ports are caught).
   Input: declared recipe inputs, prior step outputs, and gate decisions for `contradiction-detection-agent`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   DEFINED 2026-10-04 by Tanmay Kulkarni ("D3 keep"): every constant is kept at the original workflow's value and
   recorded as **inherited, unvalidated**. Values and reasoning:
   - guidance confidence ≥ 0.6 (patterns 1, 4) and ≥ 0.7 (pattern 6): kept so the port matches its source exactly; whether 0.6 separates confident from tentative guidance has not been tested.
   - Q&A pressure ≥ 7 (pattern 3): kept; the pressure scale isn't documented in the export, so the cut-off can't be justified here (see *Notes from porting*).
   - news direction ±0.2 on the average score: kept; it differs from the original's ±0.15 per-article label, and that inconsistency is recorded, not resolved.
   - ≥ 5 articles (pattern 6): kept as a minimum-evidence floor; its size is unvalidated.
   - ≥ 2 declining languages or ≥ 5 stale repos (pattern 4), velocity z ≥ 2.0 (pattern 5): kept; they are the original's heuristics for "decline" and "burst".
   - confidence ladder (≥ 2 HIGH, ≥ 1 HIGH, ≥ 2 MEDIUM): kept; see *Notes from porting* on patterns 1 and 6.
   Changing any of them is a new decision, because it breaks parity with the original on purpose.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/contradiction-detection-agent-produce-human-report.py`
   Closed 2026-10-04 (the script above is built and exercised). Original note, kept for the record: `[TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.`
   Status: Built and exercised. Input: the run's step reports, detections, envelope, manifest, expected flags and gate records. Output: the human report (all contract sections), the agent log (all contract fields) and the audit beside the verified data. Flags are reported as detected disagreements, with a short reading note beside the flags whose wording is easy to over-read. Evidence: gate 6 test; self-test section E (byte-identical reruns).
   Input: declared recipe inputs, prior step outputs, and gate decisions for `contradiction-detection-agent`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/contradiction-detection-agent-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/contradiction-detection-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `Contradiction_detection_agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: run summary, purpose, source inventory, inputs used, phase-gate results, steps completed, records seen, rejects, duplicates, flags, typed TODOs, human approvals, verified findings, inferred findings, decision recommendation.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.
- Stop before any live run until every query passes its values as parameters rather than inside the SQL text.

## Notes from porting

Things I noticed while porting `Contradiction_detection_agent.json` (nikbearbrown/mycroft `main` @ f596c75) that
help when reading this recipe's output. The port keeps the original's behaviour exactly, so its results can be
checked against the source (P6). Whether any of it should change is for the maintainers to decide, in a separate change.

**Reading the flags**

| Where | Note | Seen in |
|---|---|---|
| Pattern 3 | Counts questions whose topic was repeated (`is_repeated_topic`, selected as `evasion_flag`) or whose pressure score is 7 or more, and words the flag "Management evaded N topics". It reads best as "asked repeatedly or under pressure". Kept as ported by decision D4 (Tanmay Kulkarni, 2026-10-04) | Fixture `FXG`; step 6 adds a reading note |
| Pattern 2 | News is matched to a risk by comparing tag text, so tags written differently (`supply chain`, `supply_chain`) don't match | Fixture `FXF`; step 6 adds a reading note |
| Patterns 1 and 6 | One "strengthened guidance vs negative news" situation can raise both, so two HIGH flags may describe one disagreement | Fixture `FXC`; step 6 adds a reading note |
| Pattern 5 | Pivot keywords match as substrings ("contract renewals" contains "new") | Fixture `FXM` |
| The five queries | They select without a date filter, so rows older than the declared `lookback_days` are included; step 4 counts them | Defect `D05` |
| Risk query | It sorts by `severity` before its `LIMIT`; how that orders depends on the live column type, which the export doesn't show | — |
| Thresholds | Kept at the original's values and recorded as inherited, unvalidated (step 5, decision D3) | — |
| Timestamps | The port takes every timestamp from the envelope's frozen clock, so reruns compare byte for byte | Self-test section E |

**Before any live run** (the preconditions in the gate-5 record)

- Every query passes its values as parameters rather than inside the SQL text.
- Every API key is read from the environment.
- The model request carries the built prompt. (In the exported workflow JSON, the Groq node's body parameters are empty; this may be an export detail, so it is worth confirming on the live workflow.)
- Live failure modes (timeouts, 401/403/429, empty pages) have fixtures and tests.

## Sample corpus and evidence

- **Corpus:** `data/raw/contradiction-detection-agent/sample/`. Synthetic and fictional (tickers `FXA`…`FXR`); see
  `FIXTURE_MANIFEST.md`. `clean/` gives every pattern a must-fire case and a must-not near-miss, plus boundary and
  port-fidelity cases. `defective/` holds catalogued defects, each naming the step that must catch it.
  `expected-flags.json` was written from the original JavaScript **before** any port existed.
- **Run it** (sample mode, no network): `python3 scripts/tools/contradiction-detection-agent-run-sample.py --fixture-set clean`
  (and `--fixture-set defective`, which halts at step 3 by design and still writes its report and audit).
- **Parity with the original:** `python3 scripts/tools/contradiction-detection-agent-parity-check.py` runs the original
  `Aggregate All Signals` and `Run Pattern Detection Engine` JavaScript (extracted from the workflow JSON at run time,
  under a minimal Node shim) beside the Python port and the expected flags. Needs `node`.
- **Every check, recorded:** `python3 scripts/tools/contradiction-detection-agent-self-test.py` writes
  `logs/contradiction-detection-agent/self-test-results.{json,md}` (ran, saw, expected, for each check).
- **Counting TODOs:** a typed marker inside a code span (backticks) is a quotation, such as an original gate test kept
  for the record, not an open item. `todos_open` counts the markers outside code spans.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run contradiction-detection-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run contradiction-detection-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run contradiction-detection-agent --step verify-provenance` | `--envelope` |
| Ingest declared inputs | `snickerdoodle run contradiction-detection-agent --step ingest-inputs` | `--envelope` `--fixture-set` |
| Validate data shape | `snickerdoodle run contradiction-detection-agent --step validate-data-shape` | `--envelope` `--fixture-set` |
| Transform and quality check | `snickerdoodle run contradiction-detection-agent --step transform-quality-check` | `--envelope` `--fixture-set` |
| Run approved tools | `snickerdoodle run contradiction-detection-agent --step run-approved-tools` | `--envelope` `--fixture-set` |
| Produce human report | `snickerdoodle run contradiction-detection-agent --step produce-human-report` | `--envelope` `--fixture-set` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate contradiction-detection-agent --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate contradiction-detection-agent --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate contradiction-detection-agent --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate contradiction-detection-agent --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate contradiction-detection-agent --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate contradiction-detection-agent --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/contradiction-detection-agent-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/contradiction-detection-agent-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/contradiction-detection-agent-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/contradiction-detection-agent-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/contradiction-detection-agent-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/contradiction-detection-agent-produce-human-report.py` | tools |

### Supporting Scripts

| Purpose | Script Path | Layer |
|---|---|---|
| Run steps 1-6 in order (dialogic: never clears a gate) | `scripts/tools/contradiction-detection-agent-run-sample.py` | tools |
| Phase-gate tests (called by the six gate tests above) | `scripts/tools/contradiction-detection-agent-gate-check.py` | tools |
| Parity with the original JavaScript | `scripts/tools/contradiction-detection-agent-parity-check.py` | tools |
| Self-test: every check, recorded | `scripts/tools/contradiction-detection-agent-self-test.py` | tools |

The 16 per-node scripts generated for this recipe on 2026-06-06 (e.g. `scripts/gigo/contradiction-detection-agent-process-groq-response.py`)
are left unchanged. They belong to the historical per-node outline below and are not called by the six steps.

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/contradiction-detection-agent/` | JSON |
| Verified data | `data/verified/contradiction-detection-agent/` | JSON |
| Agent log | `logs/contradiction-detection-agent-[DATE].json` | JSON |
| Human report | `reports/generated/contradiction-detection-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json"` | Referenced source/evidence path from prior recipe text. |
| `data/raw/contradiction-detection-agent/sample/fixture-manifest.json` | `python3 scripts/tools/contradiction-detection-agent-verify-provenance.py` | Synthetic corpus; SHA-256 per fixture, checked by step 1 on every run. Values invented, companies fictional. |

## Existing Recipe Notes Preserved For Implementation

> **Historical, not a work plan (2026-10-04).** The per-node outline below is the original workflow node by node,
> kept as written. The six Steps above supersede it: the five `DB: Fetch …` nodes and the news fetch are absorbed by
> steps 2-4, `Aggregate All Signals` and `Run Pattern Detection Engine` by step 5 (ported), `Build Groq Prompt` by
> step 5 (handoff only), and the report nodes by step 6. The `INSERT` / `CREATE TABLE` nodes and `Execute a SQL query2`
> (a single-ticker query) are not carried forward: sample mode writes no database rows.

### Extracted Notes

Contradiction_detection_agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to contradiction_detection_agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/contradiction-detection-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run contradiction-detection-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/contradiction-detection-agent data/verified/contradiction-detection-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/contradiction-detection-agent.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Contradiction_Detection_Agent/Contradiction_detection_agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: DB: Fetch Earnings Guidance Signals. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-db-fetch-earnings-guidance-signals.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
3. Step name: DB: Fetch Risk Admissions. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-db-fetch-risk-admissions.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
4. Step name: DB: Fetch QA Pressure Map. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-db-fetch-qa-pressure-map.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
5. Step name: DB: Fetch News Signals. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-db-fetch-news-signals.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
6. Step name: DB: Fetch Tech Stack Signals. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-db-fetch-tech-stack-signals.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
7. Step name: Build Groq Prompt. Labor: AI with Human gate.
   Script called: `scripts/tools/contradiction-detection-agent-build-groq-prompt.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Groq: Analyse Contradictions. Labor: AI with Human gate.
   Script called: `scripts/tools/contradiction-detection-agent-groq-analyse-contradictions.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Process Groq Response. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent-process-groq-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
10. Step name: DB: Insert Contradiction Report. Labor: AI with Human gate.
   Script called: closed 2026-10-04, not carried forward: sample mode writes no database rows; the report is step 6. Original note, kept for the record: `[TODO: DEV] Create or map script path: scripts/tools/contradiction-detection-agent-db-insert-contradiction-report.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
11. Step name: DB: Insert Contradiction Flag. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent-db-insert-contradiction-flag.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
12. Step name: Build Final Report. Labor: AI with Human gate.
   Script called: closed 2026-10-04, absorbed by step 6 (produce human report). Original note, kept for the record: `[TODO: DEV] Create or map script path: scripts/tools/contradiction-detection-agent-build-final-report.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
13. Step name: Execute a SQL query. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-execute-a-sql-query2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
14. Step name: Execute a SQL query1. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent-execute-a-sql-query1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
15. Step name: Execute a SQL query2. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-execute-a-sql-query2.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
16. Step name: Execute a SQL query3. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent-execute-a-sql-query3.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
17. Step name: HTTP Request. Labor: AI with Human gate.
   Script called: `scripts/ingest/contradiction-detection-agent-http-request.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/contradiction-detection-agent/.
18. Step name: Process News Response. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent-process-news-response.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
19. Step name: DB: Save News Signals. Labor: AI with Human gate.
   Script called: `scripts/gigo/contradiction-detection-agent-db-save-news-signals.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/contradiction-detection-agent/.
20. Step name: Produce human report. Labor: AI with Human review.
   Script called: closed 2026-10-04, absorbed by step 6 (produce human report). Original note, kept for the record: `[TODO: DEV] Create or map script path: scripts/tools/contradiction-detection-agent-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
