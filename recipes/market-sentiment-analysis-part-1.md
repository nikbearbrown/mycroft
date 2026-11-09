---
status: RUNNABLE-SAMPLE
todos_open: 0
last_gate: "gate-5 deny, 2026-10-02, logs/RUN_LOG.md#2026-10-02"
attestation: null  # v0.2.0 record voided by the v0.2.1 flag-table correction
recipe_version: 0.2.1
---

# Market Sentiment Analysis - Part 1

> **Status basis.** All six step scripts exist and run end to end over the frozen sample
> corpus, both the clean and the defective set. Conformance passes, audits are generated and
> read, and gates 1–4 carry logged decisions in `logs/gate-decisions/`. Evidence:
> `logs/RUN_LOG.md#2026-09-25`.
>
> `RUNNABLE-LIVE` is **not** claimed: live mode is unimplemented, gate 5 has no approval
> record, and no live, external, or model call has ever been made by this recipe.
> `attestation: logs/attestations/market-sentiment-analysis-part-1-v0.2.0.md` because no human has recorded one — that is what `VERIFIED` requires.
>
> `todos_open: 0` counts real open items: the DEFINE on step 5's scoring constants and the
> APPROVE on gate 5. Both need a named human, not more code. Note when counting by grep that
> these marker strings also appear inside the gate 1 and gate 5 **test commands**, where they
> are part of the test, not open work.

## Purpose

Market Sentiment Analysis - Part 1 defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to market sentiment analysis - part 1. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |
| Report node outputs | JSON | Converted report steps (2 nodes) | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| Webhook Trigger | `webhook` | tool |
| Parse Question & Extract Tickers | `code` | gigo |
| Fetch Price Data | `httpRequest` | ingest |
| Fetch News Headlines | `httpRequest` | ingest |
| Fetch Reddit Mentions | `httpRequest` | ingest |
| Aggregate & Calculate Sentiment | `code` | tool |
| AI Analysis & Synthesis | `lmChatAnthropic` | tool |
| Format Response | `code` | conductor |
| Send to Slack | `slack` | tool |
| Send Email | `emailSend` | report |
| Webhook Response | `respondToWebhook` | report |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Ingest node outputs | JSON | Converted ingest steps (3 nodes) | Yes |
| Gigo node outputs | JSON | Converted gigo steps (1 nodes) | Yes |
| Tool node outputs | JSON | Converted tool steps (4 nodes) | Yes |
| Report node outputs | JSON | Converted report steps (2 nodes) | No |
| Conductor node outputs | JSON | Converted conductor steps (1 nodes) | No |
| Original workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json` | Yes |
| Credentials for live services | Environment variables | Named by script handoff payloads | No |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/market-sentiment-analysis-part-1.md" && rg -n "\[TODO: DEFINE]" "recipes/market-sentiment-analysis-part-1.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/market-sentiment-analysis-part-1/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/market-sentiment-analysis-part-1 data/verified/market-sentiment-analysis-part-1 -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every one of the six step scripts exists and compiles. Test: `for s in tools/verify-provenance ingest/ingest-inputs gigo/validate-data-shape gigo/transform-quality-check tools/run-approved-tools tools/produce-human-report; do python3 -m py_compile "scripts/${s%%/*}/market-sentiment-analysis-part-1-${s##*/}.py" || exit 1; done`. Human capacity: [IJ].
   Amended 2026-09-25: the original test passed if the script existed **or** if a DEV-TODO marker was still present anywhere in this recipe, so it could be satisfied by doing nothing. A gate with no failure path is not a gate. Uses `python3` for parity with CI and the repo's other tooling.
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `! grep -rqs '"live_call_performed": true' logs/market-sentiment-analysis-part-1/ data/raw/market-sentiment-analysis-part-1/runs/ || python3 -c "import json,sys; sys.exit(0 if json.load(open('logs/gate-decisions/market-sentiment-analysis-part-1-gate-5.json'))['approved_for_live_action'] else 1)"`. Human capacity: [EI].
   Amended 2026-09-25: the original test passed if an approval record existed **or** if an APPROVE-TODO marker was still in this recipe -- and the marker is always there, so the gate reported a pass for a clearance that had never happened. Creating `logs/gate-decisions/` made that actively misleading. The test now reads the run's own artifacts: it passes while nothing has performed a live call, and **fails** the moment one is recorded without an approval record naming a human. In sample mode it passes because no live call is possible, not because a gate was cleared.
   Amended again 2026-10-02: the previous form passed on the mere **existence** of a gate-5 record. Writing the deny decision that day would have cleared the gate exactly as an approval does -- the same defect, one layer along. The test now reads `approved_for_live_action` out of the record, so a logged **deny** closes the TODO without ever clearing the gate for live action.
   DECIDED 2026-10-02 by Uday Sonawane: **not approved; deferred.** Recorded in `logs/gate-decisions/market-sentiment-analysis-part-1-gate-5.json`. Live execution is declined, not pending: step 2 hard-stops in live mode, no credentials are configured, and the frozen corpus explicitly does not cover 401/403/429/timeout/empty-200 behaviour, so approving would authorise outward-facing actions -- a model call, a Slack message, an email -- whose failure modes have never been exercised. The gate is closed by a logged decision, which is what its closure rule requires; the decision is deny. Reopening it needs the four preconditions named in the record.
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/market-sentiment-analysis-part-1-[DATE].json && test -f reports/generated/market-sentiment-analysis-part-1-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/market-sentiment-analysis-part-1-verify-provenance.py`
   Status: Built and exercised. Input: optional `extra_paths` overrides. Output: the fields below plus `findings_digest` (timestamp-independent). Errors: a missing or unexpectedly-parseable required source is a hard stop with exit 1. Evidence: 11 deliberate break tests, `logs/RUN_LOG.md#2026-09-25`.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `market-sentiment-analysis-part-1`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/market-sentiment-analysis-part-1-ingest-inputs.py`
   Status: Built and exercised. Input: `run-envelope.json` plus the fixture set it names. Output: the fields below, per source file. Errors: missing envelope, absent source, or live mode all stop with exit 1; live mode is unimplemented by design. Transports verbatim -- no recount, dedupe, drop, or coercion. Evidence: `logs/RUN_LOG.md#2026-09-25`.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `market-sentiment-analysis-part-1`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/market-sentiment-analysis-part-1/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/market-sentiment-analysis-part-1-validate-data-shape.py`
   Status: Built and exercised. Input: a step-2 run directory. Output: the fields below. Errors: an unparseable file or malformed row is reported in full, then the run halts with exit 1. Detects 8 of the 18 catalogued corpus defects, in the fields the fixture manifest names. Evidence: `logs/RUN_LOG.md#2026-09-25`.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `market-sentiment-analysis-part-1`.
   Output: record_count, required_fields_present, missing_fields, type_errors, parse_errors, schema_version.
   Amended 2026-09-25: `type_errors` added. A wrong-typed value was none of the five original fields, so corpus defects D02/D11/D17 had to be reported in step 4 `flags` as a workaround. Step 3 now reports them against the declared type contract; step 4 still carries them into `flags` for its quality assessment, the same way it already carries forward step 3 rejects.
   Where output goes: `data/verified/market-sentiment-analysis-part-1/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/market-sentiment-analysis-part-1-transform-quality-check.py`
   Status: Built and exercised. Input: step-3 verified output. Output: the fields below. Errors: rejects or flags halt the run with exit 1 after reporting everything found. Detects the remaining 10 corpus defects; stale and wrong-typed rows are flagged and kept, never dropped or coerced. Evidence: `logs/RUN_LOG.md#2026-09-25`.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `market-sentiment-analysis-part-1`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/market-sentiment-analysis-part-1/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/market-sentiment-analysis-part-1-run-approved-tools.py`
   Status: Built and exercised. Input: step-4 quality-checked output. Output: the fields below, per tool. Errors: a missing or unparseable input stops the run. Faithful port of the source workflow's scoring as `scoring_params v1.0.0`, emitting a named flag for every substitution it makes; model, Slack and email calls are rendered as handoffs and never executed. Evidence: `logs/RUN_LOG.md#2026-09-25`.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `market-sentiment-analysis-part-1`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   DEFINED 2026-10-02 by Uday Sonawane. `scoring_params v1.0.0` is **inherited, not derived**. Weights: price 0.40, news 0.30, social 0.30. Label thresholds: BULLISH >= 65, SLIGHTLY BULLISH >= 55, SLIGHTLY BEARISH <= 45, BEARISH <= 35, NEUTRAL otherwise. Price score: +75 above 3% change, +60 above 0%, 25 below -3%, else 40. News keywords positive: surge, gain, bull, upgrade, beat, strong, growth, profit, rise; negative: drop, fall, bear, downgrade, miss, weak, loss, decline, crash. Social bullish: calls, moon, rocket, bullish, buy, long, rocket-emoji, to the moon; bearish: puts, crash, bearish, sell, short, dump.
   **Reasoning:** these are reproduced byte-for-byte from the `Aggregate & Calculate Sentiment` node of the named source workflow so that any score it ever produced can be recomputed and audited; they are a record of what the original did, and carry no claim that the weighting or the word lists are analytically sound. Treating them as validated is the error this definition exists to prevent -- step 5 raises `scoring_params_unattributed` on every run to keep that visible, and the report files every score under inferred findings. Changing any value requires a new `scoring_params` version, because a score is only reconstructable against the parameter set that produced it.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/market-sentiment-analysis-part-1-produce-human-report.py`
   Status: Built and exercised. Input: prior-step outputs. Output: the fields below, plus the report, the agent log, and a `*-audit.md` beside the data. Errors: a missing required report section stops the run with exit 1. Evidence: `logs/RUN_LOG.md#2026-09-25`.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `market-sentiment-analysis-part-1`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/market-sentiment-analysis-part-1-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/market-sentiment-analysis-part-1-[DATE].md`
Reader: compliance or audit reviewer who must be able to reconstruct exactly how any score was produced, and who accepts or blocks the run on that basis.
Amended 2026-09-25: previously "domain lead or human boss". The report already carries what reconstruction needs -- every source file with its SHA-256, the scoring parameters reproduced so a score can be recomputed by hand, and a per-score trace chain back to a raw locator -- so the stated reader now matches the artifact. A domain lead remains a valid secondary reader; the run summary and decision recommendation are written for them.
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
`snickerdoodle run market-sentiment-analysis-part-1 --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run market-sentiment-analysis-part-1 --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run market-sentiment-analysis-part-1 --step verify-provenance` | `--sample` |
| Ingest declared inputs | `snickerdoodle run market-sentiment-analysis-part-1 --step ingest-inputs` | `--fixture-set` `--sample` |
| Validate data shape | `snickerdoodle run market-sentiment-analysis-part-1 --step validate-data-shape` | `--fixture-set` `--run-dir` `--sample` |
| Transform and quality check | `snickerdoodle run market-sentiment-analysis-part-1 --step transform-quality-check` | `--fixture-set` `--sample` `--verified-dir` |
| Run approved tools | `snickerdoodle run market-sentiment-analysis-part-1 --step run-approved-tools` | `--fixture-set` `--input-dir` `--no-write` `--sample` |
| Produce human report | `snickerdoodle run market-sentiment-analysis-part-1 --step produce-human-report` | `--fixture-set` `--no-write` `--run-id` `--sample` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate market-sentiment-analysis-part-1 --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate market-sentiment-analysis-part-1 --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate market-sentiment-analysis-part-1 --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate market-sentiment-analysis-part-1 --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate market-sentiment-analysis-part-1 --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate market-sentiment-analysis-part-1 --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/market-sentiment-analysis-part-1-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/market-sentiment-analysis-part-1-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/market-sentiment-analysis-part-1-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/market-sentiment-analysis-part-1-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/market-sentiment-analysis-part-1-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/market-sentiment-analysis-part-1-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/market-sentiment-analysis-part-1/` | JSON |
| Verified data | `data/verified/market-sentiment-analysis-part-1/` | JSON |
| Agent log | `logs/market-sentiment-analysis-part-1-[DATE].json` | JSON |
| Human report | `reports/generated/market-sentiment-analysis-part-1-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json` | `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

> **Historical, not a work plan.** This section preserves the node-by-node notes from the
> original n8n conversion. The active specification is the six canonical **Steps** above,
> which supersede it. Each node below records where it went: absorbed by a canonical step,
> or deliberately not carried forward. These are resolved mappings, not open development
> work -- two of them were never built, and say so.

### Extracted Notes

Market Sentiment Analysis - Part 1 defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to market sentiment analysis - part 1. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/market-sentiment-analysis-part-1.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run market-sentiment-analysis-part-1 --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/market-sentiment-analysis-part-1 data/verified/market-sentiment-analysis-part-1 -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/market-sentiment-analysis-part-1.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: Webhook Trigger. Labor: AI with Human gate.
   Script called: `scripts/tools/market-sentiment-analysis-part-1-webhook-trigger.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
3. Step name: Parse Question & Extract Tickers. Labor: AI with Human gate.
   Script called: n/a -- NOT CARRIED FORWARD. No canonical step parses a user question. Step 5 derives the ticker from the price rows' `01. symbol` and raises the flag `ticker_not_derived_from_question`. The original defaulted a ticker-less question to `SPY`, silently turning it into an SPY analysis; that default cannot fire here because no question is scored at all.
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/market-sentiment-analysis-part-1/.
4. Step name: Fetch Price Data. Labor: AI with Human gate.
   Script called: `scripts/ingest/market-sentiment-analysis-part-1-fetch-price-data.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/market-sentiment-analysis-part-1/.
5. Step name: Fetch News Headlines. Labor: AI with Human gate.
   Script called: `scripts/ingest/market-sentiment-analysis-part-1-fetch-news-headlines.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/market-sentiment-analysis-part-1/.
6. Step name: Fetch Reddit Mentions. Labor: AI with Human gate.
   Script called: `scripts/ingest/market-sentiment-analysis-part-1-fetch-reddit-mentions.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/market-sentiment-analysis-part-1/.
7. Step name: Aggregate & Calculate Sentiment. Labor: AI with Human gate.
   Script called: n/a -- ABSORBED BY STEP 5. Ported verbatim as `scoring_params v1.0.0`, including JavaScript `parseFloat`/`parseInt` semantics, with a named flag for every substitution the original makes.
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
8. Step name: AI Analysis & Synthesis. Labor: AI with Human gate.
   Script called: n/a -- ABSORBED BY STEP 5, as an approval-gated handoff. The prompt is rendered and the model id recorded; `approved_for_live_action: false` and no call is made. Requires gate 5 and a named approver.
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
9. Step name: Send to Slack. Labor: AI with Human gate.
   Script called: `scripts/tools/market-sentiment-analysis-part-1-send-to-slack.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
10. Step name: Send Email. Labor: AI with Human gate.
   Script called: n/a -- ABSORBED BY STEP 5, as an approval-gated handoff. Never executed.
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
11. Step name: Webhook Response. Labor: AI with Human gate.
   Script called: n/a -- NOT CARRIED FORWARD. This recipe's Output Contract is the agent log plus the human report; it has no webhook surface. Reinstating one would be a new step with its own gate.
   Input: approved upstream output or sample fixture.
   Output: markdown report sections: run summary, source status, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
12. Step name: Produce human report. Labor: AI with Human review.
   Script called: n/a -- ABSORBED BY STEP 6, which writes the report, the agent log, and a `*-audit.md` beside the data.
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.
