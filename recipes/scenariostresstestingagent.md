---
status: DRAFT
todos_open: 3
last_gate: null
attestation: null
recipe_version: 0.3.1
---

# ScenarioStressTestingAgent

## Purpose

ScenarioStressTestingAgent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to scenariostresstestingagent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (1 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| Webhook Trigger | `webhook` | tool |
| Parse Input | `set` | gigo |
| Edit Fields | `set` | conductor |
| Validate Portfolio | `code` | conductor |
| Custom Scenario? | `if` | conductor |
| Load_Template_Scenario | `code` | conductor |
| When chat message received | `chatTrigger` | conductor |
| Basic LLM Chain | `chainLlm` | tool |
| Groq Chat Model | `lmChatGroq` | tool |
| Parse_LLM_Response | `code` | tool |
| Stress_Test_Engine | `code` | tool |
| Respond to Webhook | `respondToWebhook` | report |
| Fetch_Data | `httpRequest` | ingest |
| Merge | `merge` | conductor |
| Merge1 | `merge` | conductor |
| Save_Portfolio_Before_LLM | `code` | tool |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (1 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (1 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (6 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (1 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (7 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/scenariostresstestingagent.md" && rg -n "\[TODO: DEFINE]" "recipes/scenariostresstestingagent.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/scenariostresstestingagent/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/scenariostresstestingagent data/verified/scenariostresstestingagent -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/scenariostresstestingagent-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/scenariostresstestingagent.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/scenariostresstestingagent-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/scenariostresstestingagent.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/scenariostresstestingagent-[DATE].json && test -f reports/generated/scenariostresstestingagent-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/scenariostresstestingagent-verify-provenance.py`
   Closed 2026-10-25 (the script above is built and exercised). Original note, kept for the record: `[TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.`
   Status: Built and exercised. Input: this recipe (its node table and its declared workflow JSON), that workflow, the sample fixture manifest (a SHA-256 per fixture) and the approval record, if any. Output: the fields below plus node_table_match, chain_match, ported_nodes_ok, fixtures_ok and findings, in `logs/scenariostresstestingagent-provenance-<date>.json`. Errors: a missing or unparseable workflow, a node-table mismatch, connections that differ from the 18-edge wiring the step-5 port assumes (the custom-scenario branch, the template branch and the two merges included), a ported node whose language is not the one the port copies, or a fixture changed since the manifest froze it stops the run (exit 1); the record is still written. Evidence: self-test (provenance as declared, and three deliberate breaks: a renamed node, a rewired connection, a tampered fixture).
   Input: declared recipe inputs, prior step outputs, and gate decisions for `scenariostresstestingagent`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/scenariostresstestingagent-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `scenariostresstestingagent`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/scenariostresstestingagent/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/scenariostresstestingagent-validate-data-shape.py`
   Closed 2026-10-25 (the script above is built and exercised). Original note, kept for the record: `[TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.`
   Status: Built and exercised (sample mode: reads a fixture folder from `data/raw/scenariostresstestingagent/sample/` directly, since step 2 is still open). Contract, taken from the workflow's Validate Portfolio node: holdings must exist (the node's own message: Portfolio must have holdings array), every holding needs a ticker (Each holding must have a ticker), weights default to 0 and are rescaled to 1.0 when the total is more than 0.01 from it (the node's own rules, shared with the step-5 port so the two cannot drift apart); one stated addition at this gate, marked in every reason that comes from it: holdings a non-empty array of objects; every weight present, finite and not negative with a positive total; scenario_type one of the five templates (or absent, when the workflow's default applies); custom_scenario a string. Output: the fields below plus the accepted and the rejected requests in `data/verified/scenariostresstestingagent/<clean|defective>/validated.json`, with a `validate-audit.md` beside it. Errors: any rejected request makes the run exit 1 (the files are still written); a fixture changed since the manifest froze it stops the run before anything is read (exit 2). Evidence: self-test (clean set 12/12 accepted; defective set 10/10 rejected, each for its own reason).
   Input: declared recipe inputs, prior step outputs, and gate decisions for `scenariostresstestingagent`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/scenariostresstestingagent/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/scenariostresstestingagent-transform-quality-check.py`
   Closed 2026-11-01 (the script above is built and exercised). Original note, kept for the record: `[TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.`
   Status: Built and exercised (sample mode). Input: the step-3 `validated.json` and the step-5 `stress-results.json` for one sample folder (default `clean`), plus the workflow's own template shocks, sector map and risk lines read from the step-5 script as data (its engine is never called). Output: `quality-check.json` (verified_records, handed_off, record_count, duplicates, rejects, flags, quality_notes, the checks run, failures) and `quality-notes.md`, beside the data. What it does: re-derives every position's shock from the template and recomputes each loss, final value, total, drawdown and risk level with exact decimals, and checks the weights (within 0.01 of 1.0 after the workflow's rescale), the ordering of positions and the top losers, and that the scenario name is the template's; looks for duplicates by id and by content (same holdings under the same scenario); and raises advisory flags for a human (weights rescaled, a majority holding, at least half the book in tickers the sector map does not list, a drawdown within 0.05 points of a risk line, a defaulted scenario, a handoff). How it stops: exit 1 if anything was rejected at step 3, a result fails a check or a duplicate is found (the files are still written); exit 2, nothing written, if `validated.json` is missing or unparseable. Evidence: on the 12 clean requests, 11 stress results reconcile on every check and 1 stops at the Groq handoff; on the 10 defective requests, 10 rejects and nothing to check; `scripts/tools/scenariostresstestingagent-report-self-test.py` breaks a result in eight ways and every one is caught.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `scenariostresstestingagent`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/scenariostresstestingagent/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/scenariostresstestingagent-run-approved-tools.py`
   Closed 2026-10-25 (the script above is built and exercised). Original note, kept for the record: `[TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.`
   Status: Built and exercised. A Python port of four of the workflow's five code nodes in the workflow's own order, with the set node (Edit Fields) and the IF node (Custom Scenario?) modelled between them: Validate Portfolio, then, for a template scenario, Load_Template_Scenario and Stress_Test_Engine, or, for a custom scenario, Save_Portfolio_Before_LLM and then the Groq handoff. It copies what JavaScript does where it differs from Python in Validate Portfolio (`||` defaults, Math.abs, division by zero giving NaN, NaN becoming null between nodes); it does not model JavaScript's string arithmetic, which the step-3 gate refuses first. Parse_LLM_Response is not ported: it only runs after the Groq call. Checked against the original code, extracted from the workflow JSON at run time (Validate Portfolio under node; the three Python nodes by exec inside a small shim), on all 21 sample requests and 3 direct engine inputs: every node output identical, or the same error message. Input: the sample folder; every request first goes through the step-3 gate and the tools refuse the folder if any request was rejected (exit 1, nothing written). Output: the fields below, plus `stress-results.json` beside the validated file. The Alpha Vantage request (Fetch_Data), the Groq call (Basic LLM Chain, Groq Chat Model) and the webhook reply are recorded as handoffs with approved_for_live_action false and are never made. Evidence: `scripts/tools/scenariostresstestingagent-parity-check.py` (24 of 24 compared cases identical; one defective request, a string weight, is not modelled and is refused by the gate) and the self-test (eight deliberate breaks of the port, each caught).
   Input: declared recipe inputs, prior step outputs, and gate decisions for `scenariostresstestingagent`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/scenariostresstestingagent-produce-human-report.py`
   Closed 2026-11-01 (the script above is built and exercised). Original note, kept for the record: `[TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.`
   Status: Built and exercised (sample mode). Input: the verified files of steps 3, 4 and 5 for one sample folder, the run envelope, the latest step-1 and step-5 logs and this recipe. Output: the report `reports/generated/scenariostresstestingagent-<DATE>.md` (the reader, the decision it enables and the Output Contract's fifteen sections, in order) and the agent log `logs/scenariostresstestingagent-<DATE>.json` (the contract's sixteen fields); the defective folder writes the same pair with `-defective` added. How the report is made: each phase gate is judged from evidence and not from the recipe's shell lines; findings the data supports (every figure re-read or recomputed from the files, with the path) are kept apart from readings of the invented sample, which are labelled inferred; the recommendation can only approve a sample-mode next phase and always blocks live execution while no approval record exists. How it stops: exit 2, nothing written, if step 4's output is missing or does not account for exactly the requests step 3 accepted and step 5 ran, or if the run envelope declares live calls, network or database writes. The recipe's four stop conditions are judged from evidence and recorded in the agent log, each with its own evidence string (a scan of this recipe's scripts, raw data and recipe for a hardcoded credential, the run envelope and the approval record, the sample folder and its manifest, and the report's provenance sections), and the report's run summary says how many triggered; if any does, the recommendation to approve turns to NO. `--now` pins the date. Evidence: the report and log for both folders, two runs giving identical bytes, and `scripts/tools/scenariostresstestingagent-report-self-test.py`, whose checks include a hardcoded key planted in a script, which must trip condition 1.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `scenariostresstestingagent`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/scenariostresstestingagent-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/scenariostresstestingagent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `ScenarioStressTestingAgent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: run summary, purpose, source inventory, inputs used, phase-gate results, steps completed, records seen, rejects, duplicates, flags, typed TODOs, human approvals, verified findings, inferred findings, decision recommendation.

## Stop Conditions

- Stop if credentials, API keys, database destinations, email addresses, or tokens are hardcoded instead of read from environment variables.
- Stop if live external calls, database writes, notifications, trades, or publication actions are requested without explicit human approval.
- Stop if required local source data is missing and no approved live-call path is available.
- Stop if generated outputs omit provenance or make unsupported analytical claims.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run scenariostresstestingagent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run scenariostresstestingagent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run scenariostresstestingagent --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run scenariostresstestingagent --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run scenariostresstestingagent --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run scenariostresstestingagent --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run scenariostresstestingagent --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run scenariostresstestingagent --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate scenariostresstestingagent --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate scenariostresstestingagent --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate scenariostresstestingagent --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate scenariostresstestingagent --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate scenariostresstestingagent --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate scenariostresstestingagent --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/scenariostresstestingagent-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/scenariostresstestingagent-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/scenariostresstestingagent-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/scenariostresstestingagent-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/scenariostresstestingagent-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/scenariostresstestingagent-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/scenariostresstestingagent/` | JSON |
| Verified data | `data/verified/scenariostresstestingagent/` | JSON |
| Agent log | `logs/scenariostresstestingagent-[DATE].json` | JSON |
| Human report | `reports/generated/scenariostresstestingagent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

ScenarioStressTestingAgent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to scenariostresstestingagent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/scenariostresstestingagent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run scenariostresstestingagent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/scenariostresstestingagent data/verified/scenariostresstestingagent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/scenariostresstestingagent.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Scenario_Stress_Testing_Agent/ScenarioStressTestingAgent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Webhook Trigger. Labor: AI with Human gate.
   Script called: `scripts/tools/scenariostresstestingagent-webhook-trigger.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Parse Input. Labor: AI with Human gate.
   Script called: `scripts/gigo/scenariostresstestingagent-parse-input.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/scenariostresstestingagent/.
4. Step name: Basic LLM Chain. Labor: AI with Human gate.
   Script called: `scripts/tools/scenariostresstestingagent-basic-llm-chain.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
5. Step name: Groq Chat Model. Labor: AI with Human gate.
   Script called: `scripts/tools/scenariostresstestingagent-groq-chat-model.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
6. Step name: Parse_LLM_Response. Labor: AI with Human gate.
   Script called: `scripts/tools/scenariostresstestingagent-parse-llm-response.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
7. Step name: Stress_Test_Engine. Labor: AI with Human gate.
   Script called: `scripts/tools/scenariostresstestingagent-stress-test-engine.py`
   Also covered 2026-10-25 by the step-5 port in `scripts/tools/scenariostresstestingagent-run-approved-tools.py` (a faithful port of this node, parity-checked against the original); the generated script above is unchanged.
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: Respond to Webhook. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/scenariostresstestingagent-respond-to-webhook.py`
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
9. Step name: Fetch_Data. Labor: AI with Human gate.
   Script called: `scripts/ingest/scenariostresstestingagent-fetch-data.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/scenariostresstestingagent/.
10. Step name: Save_Portfolio_Before_LLM. Labor: AI with Human gate.
   Script called: `scripts/tools/scenariostresstestingagent-save-portfolio-before-llm.py`
   Also covered 2026-10-25 by the step-5 port in `scripts/tools/scenariostresstestingagent-run-approved-tools.py` (ported and parity-checked; the custom-scenario route stops after it at the Groq handoff); the generated script above is unchanged.
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
11. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/scenariostresstestingagent-produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
