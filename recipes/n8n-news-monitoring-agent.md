# News Monitoring Agent

## Purpose

News Monitoring Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to news monitoring agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

## Source Inventory

| Source Node | Node Type | Source URL or Path | Human Check |
|---|---|---|---|
| feedparser fetch | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Healthcheck | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| Parse | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| FinBert | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |
| HTTP Request | httpRequest | [TODO: DATA SOURCE] Extract exact URL/path/source contract from original workflow JSON. | Confirm source is allowed, current, and rate-safe before live fetch. |

| Node Name | Node Type | Classification |
|---|---|---|
| feedparser fetch | httpRequest | ingest |
| Schedule Trigger | scheduleTrigger | conductor |
| Healthcheck | httpRequest | ingest |
| Merge1 | merge | conductor |
| Embeddings HuggingFace Inference | embeddingsHuggingFaceInference | gigo |
| Postgres Chat Memory | memoryPostgresChat | gigo |
| When chat message received | chatTrigger | conductor |
| Parse | httpRequest | ingest |
| not null | filter | conductor |
| Remove Duplicates | removeDuplicates | gigo |
| Merge2 | merge | conductor |
| FinBert | httpRequest | ingest |
| Embeddings HuggingFace Inference4 | embeddingsHuggingFaceInference | gigo |
| Sticky Note | stickyNote | gigo |
| Sticky Note1 | stickyNote | gigo |
| Sticky Note2 | stickyNote | gigo |
| View daily KPIs | postgres | gigo |
| Create Qdrant Collection | httpRequest | tool |
| Write metrics | postgres | tool |
| Create METRICS table | postgres | tool |
| Get row(s) | dataTable | gigo |
| Upsert row(s) | dataTable | gigo |
| Split Out | splitOut | conductor |
| Default Data Loader2 | documentDefaultDataLoader | gigo |
| Recursive Character Text Splitter2 | textSplitterRecursiveCharacterTextSplitter | conductor |
| Merge | merge | conductor |
| Google Gemini Chat Model3 | lmChatGoogleGemini | gigo |
| Google Gemini Chat Model4 | lmChatGoogleGemini | gigo |
| Google Gemini Chat Model | lmChatGoogleGemini | gigo |
| Google Gemini Chat Model5 | lmChatGoogleGemini | gigo |
| Google Gemini Chat Model6 | lmChatGoogleGemini | gigo |
| Metaprompt Agentv2 | agent | gigo |
| Metadata Agentv2 | agent | gigo |
| Default Data Loader3 | documentDefaultDataLoader | gigo |
| Recursive Character Text Splitter3 | textSplitterRecursiveCharacterTextSplitter | conductor |
| Embeddings Google Gemini1 | embeddingsGoogleGemini | gigo |
| Postgres Chat Memory1 | memoryPostgresChat | gigo |
| Google Gemini Chat Model7 | lmChatGoogleGemini | gigo |
| Qdrant Vector Store A | vectorStoreQdrant | gigo |
| Qdrant Vector Store B | vectorStoreQdrant | gigo |
| News Articles RAG A | vectorStoreQdrant | gigo |
| News Articles RAG B | vectorStoreQdrant | gigo |
| Embeddings Google Gemini2 | embeddingsGoogleGemini | gigo |
| Merge3 | merge | conductor |
| Structured Output Parser test1 | outputParserStructured | gigo |
| Structured Output Parser2 | outputParserStructured | gigo |
| Metaprompt Agentv | agent | gigo |
| Metadata Agentv | agent | gigo |
| Extract from File | extractFromFile | gigo |
| Merge5 | merge | conductor |
| Convert to File1 | convertToFile | gigo |
| HTTP Request | httpRequest | ingest |
| Read/Write Files from Disk | readWriteFile | tool |
| When clicking ‘Execute workflow’ | manualTrigger | conductor |
| OpenRouter Chat Model3 | lmChatOpenRouter | gigo |
| OpenRouter Chat Model4 | lmChatOpenRouter | gigo |
| OpenRouter Chat Model5 | lmChatOpenRouter | gigo |
| OpenRouter Chat Model6 | lmChatOpenRouter | gigo |
| RAG Agent3 | agent | gigo |
| Google Gemini Chat Model8 | lmChatGoogleGemini | gigo |
| News Articles RAG A2 | vectorStoreQdrant | gigo |
| Embeddings HuggingFace Inference6 | embeddingsHuggingFaceInference | gigo |
| News Articles RAG A3 | vectorStoreQdrant | gigo |
| Embeddings HuggingFace Inference7 | embeddingsHuggingFaceInference | gigo |
| Call rag grader | executeWorkflow | gigo |
| Merge6 | merge | conductor |
| Call rag grader1 | executeWorkflow | gigo |
| Merge4 | merge | conductor |
| Qdrant Vector Store | vectorStoreQdrant | gigo |
| Embeddings HuggingFace Inference8 | embeddingsHuggingFaceInference | gigo |
| AI Agent | agent | gigo |
| OpenRouter Chat Model | lmChatOpenRouter | gigo |
| Sticky Note3 | stickyNote | gigo |
| Metadata structured output | outputParserStructured | gigo |
| Metaprompt structured output | outputParserStructured | gigo |
| Switch - A/B testing | switch | gigo |
| RAG Agent A | agent | gigo |
| RAG Agent B | agent | gigo |
## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Original n8n workflow JSON | JSON | `data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json` | Yes |

## Phase Gates

1. Source gate: All required source paths are present or explicitly marked with a typed TODO. Test: `test -f "recipes/n8n-news-monitoring-agent.md" && rg -n "\[TODO: DEFINE]" "recipes/n8n-news-monitoring-agent.md" || true`. Human capacity: [TO].
2. Scope gate: The run declares `sample` mode or an approved live mode before ingest begins. Test: `python3 -m json.tool data/raw/n8n-news-monitoring-agent/run-envelope.json`. Human capacity: [PF].
3. Data-shape gate: Every raw and verified JSON output parses before downstream scripts run. Test: `find data/raw/n8n-news-monitoring-agent data/verified/n8n-news-monitoring-agent -name "*.json" -print -exec python3 -m json.tool {} \;`. Human capacity: [PA].
4. Script-readiness gate: Every step script exists or is represented by a typed development TODO. Test: `test -f scripts/ingest/n8n-news-monitoring-agent-ingest-inputs.py || rg --fixed-strings "[TODO: DEV]" "recipes/n8n-news-monitoring-agent.md"`. Human capacity: [IJ].
5. Approval gate: Live network calls, external writes, credentials, production databases, emails, dashboards, publishing, or model calls with sensitive data require an approval record. Test: `test -f logs/gate-decisions/n8n-news-monitoring-agent-approval.json || rg --fixed-strings "[TODO: APPROVE]" "recipes/n8n-news-monitoring-agent.md"`. Human capacity: [EI].
6. Report gate: Agent log and human report are written with the required fields and sections. Test: `test -f logs/n8n-news-monitoring-agent-[DATE].json && test -f reports/generated/n8n-news-monitoring-agent-[DATE].md`. Human capacity: [TO].

## Steps

1. Step name: Verify provenance. Labor: AI with Human gate.
   Script called: `scripts/tools/n8n-news-monitoring-agent-verify-provenance.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-news-monitoring-agent`.
   Output: workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
   Where output goes: `logs/`
2. Step name: Ingest declared inputs. Labor: AI with Human gate.
   Script called: `scripts/ingest/n8n-news-monitoring-agent-ingest-inputs.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-news-monitoring-agent`.
   Output: records, source_name, source_type, fetched_at, sample_mode, rejects.
   Where output goes: `data/raw/n8n-news-monitoring-agent/`
3. Step name: Validate data shape. Labor: AI with Human gate.
   Script called: `scripts/gigo/n8n-news-monitoring-agent-validate-data-shape.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-news-monitoring-agent`.
   Output: record_count, required_fields_present, missing_fields, parse_errors, schema_version.
   Where output goes: `data/verified/n8n-news-monitoring-agent/`
4. Step name: Transform and quality check. Labor: AI with Human gate.
   Script called: `scripts/gigo/n8n-news-monitoring-agent-transform-quality-check.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-news-monitoring-agent`.
   Output: verified_records, record_count, duplicates, rejects, flags, quality_notes.
   Where output goes: `data/verified/n8n-news-monitoring-agent/`
5. Step name: Run approved tools. Labor: AI with Human gate.
   Script called: `scripts/tools/n8n-news-monitoring-agent-run-approved-tools.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-news-monitoring-agent`.
   Output: tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
   Where output goes: `logs/`
6. Step name: Produce human report. Labor: AI with Human gate.
   Script called: `scripts/tools/n8n-news-monitoring-agent-produce-human-report.py` [TODO: DEV] Define input schema, output schema, transformation logic, and error handling for this script before implementation.
   Input: declared recipe inputs, prior step outputs, and gate decisions for `n8n-news-monitoring-agent`.
   Output: summary, sources_checked, gate_results, findings, typed_todos, next_decision.
   Where output goes: `reports/generated/`

## Output Contract

### Agent output
File: `logs/n8n-news-monitoring-agent-[DATE].json`
Fields: workflow, run_id, mode, steps_completed, records_seen, rejects, duplicates, flags, stop_conditions, todo_items, source_files, gate_decisions, generated_at, raw_output_paths, verified_output_paths, report_path.

### Human report
File: `reports/generated/n8n-news-monitoring-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `News Monitoring Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: run summary, purpose, source inventory, inputs used, phase-gate results, steps completed, records seen, rejects, duplicates, flags, typed TODOs, human approvals, verified findings, inferred findings, decision recommendation.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.

## Snickerdoodle

### Run Commands
Full dialogic run:
`snickerdoodle run n8n-news-monitoring-agent --mode dialogic`

Sample mode (no live network calls, no writes):
`snickerdoodle run n8n-news-monitoring-agent --mode dialogic --sample`

### Step Commands

| Step | CLI Command | Flags |
|---|---|---|
| Verify provenance | `snickerdoodle run n8n-news-monitoring-agent --step verify-provenance` | `--sample` `--no-write` |
| Ingest declared inputs | `snickerdoodle run n8n-news-monitoring-agent --step ingest-inputs` | `--sample` |
| Validate data shape | `snickerdoodle run n8n-news-monitoring-agent --step validate-data-shape` | `--sample` |
| Transform and quality check | `snickerdoodle run n8n-news-monitoring-agent --step transform-quality-check` | `--sample` |
| Run approved tools | `snickerdoodle run n8n-news-monitoring-agent --step run-approved-tools` | `--sample` `--no-write` |
| Produce human report | `snickerdoodle run n8n-news-monitoring-agent --step produce-human-report` | `--sample` `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - Source gate | `snickerdoodle gate n8n-news-monitoring-agent --gate 1 --decision approve --note "Sources checked"` |
| Gate 2 - Scope gate | `snickerdoodle gate n8n-news-monitoring-agent --gate 2 --decision approve --note "Scope and mode approved"` |
| Gate 3 - Data-shape gate | `snickerdoodle gate n8n-news-monitoring-agent --gate 3 --decision approve --note "Outputs parse"` |
| Gate 4 - Script-readiness gate | `snickerdoodle gate n8n-news-monitoring-agent --gate 4 --decision approve --note "Scripts ready or TODO DEV accepted"` |
| Gate 5 - Approval gate | `snickerdoodle gate n8n-news-monitoring-agent --gate 5 --decision approve --note "Live or sensitive actions approved"` |
| Gate 6 - Report gate | `snickerdoodle gate n8n-news-monitoring-agent --gate 6 --decision approve --note "Report and log complete"` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| Verify provenance | `scripts/tools/n8n-news-monitoring-agent-verify-provenance.py` | tools |
| Ingest declared inputs | `scripts/ingest/n8n-news-monitoring-agent-ingest-inputs.py` | ingest |
| Validate data shape | `scripts/gigo/n8n-news-monitoring-agent-validate-data-shape.py` | gigo |
| Transform and quality check | `scripts/gigo/n8n-news-monitoring-agent-transform-quality-check.py` | gigo |
| Run approved tools | `scripts/tools/n8n-news-monitoring-agent-run-approved-tools.py` | tools |
| Produce human report | `scripts/tools/n8n-news-monitoring-agent-produce-human-report.py` | tools |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-news-monitoring-agent/` | JSON |
| Verified data | `data/verified/n8n-news-monitoring-agent/` | JSON |
| Agent log | `logs/n8n-news-monitoring-agent-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-news-monitoring-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

| Source | Verification command | Notes |
|---|---|---|
| `data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json` | `test -f "data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json"` | Referenced source/evidence path from prior recipe text. |

## Existing Recipe Notes Preserved For Implementation

### Extracted Notes

News Monitoring Agent defines a Mycroft pipeline for collecting, transforming, or reviewing finance and intelligence signals related to news monitoring agent. It answers whether the available local evidence and approved live sources are sufficient for a human decision without relying on unapproved external writes or unsupported analytical claims.

1. Source identity gate: Original workflow JSON exists and is the intended source. Test: `test -f "data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json"`.
   Human capacity: [PF].
2. Input readiness gate: Every required input in this recipe exists or is marked with a typed TODO. Test: `rg -n "TODO:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-news-monitoring-agent.md`.
   Human capacity: [PA].
3. Sample run gate: Ingest and tool steps run without live side effects before live mode. Test: `snickerdoodle run n8n-news-monitoring-agent --mode dialogic --sample`.
   Human capacity: [TO].
4. Data-shape gate: Raw and verified outputs parse as JSON where applicable. Test: `find data/raw/n8n-news-monitoring-agent data/verified/n8n-news-monitoring-agent -name "*.json" -print -exec python3 -m json.tool {} \;`.
   Human capacity: [IJ].
5. Report contract gate: Human report defines reader, decision enabled, and sections. Test: `rg -n "Reader:|Decision enabled:|Sections:" /Users/bear/Documents/CoWork/bear-textbooks/books/mycroft/recipes/n8n-news-monitoring-agent.md`.
   Human capacity: [EI].

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: feedparser fetch. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-news-monitoring-agent-feedparser-fetch.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-news-monitoring-agent/.
3. Step name: Healthcheck. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-news-monitoring-agent-healthcheck.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-news-monitoring-agent/.
4. Step name: Embeddings HuggingFace Inference. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-embeddings-huggingface-inference.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
5. Step name: Postgres Chat Memory. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-postgres-chat-memory.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
6. Step name: Parse. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-news-monitoring-agent-parse.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-news-monitoring-agent/.
7. Step name: Remove Duplicates. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-remove-duplicates.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
8. Step name: FinBert. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-news-monitoring-agent-finbert.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-news-monitoring-agent/.
9. Step name: Embeddings HuggingFace Inference4. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-embeddings-huggingface-inference4.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
10. Step name: Sticky Note. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-sticky-note.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
11. Step name: Sticky Note1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-sticky-note1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
12. Step name: Sticky Note2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-sticky-note2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
13. Step name: View daily KPIs. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-view-daily-kpis.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
14. Step name: Create Qdrant Collection. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-news-monitoring-agent-create-qdrant-collection.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
15. Step name: Write metrics. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-news-monitoring-agent-write-metrics.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
16. Step name: Create METRICS table. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-news-monitoring-agent-create-metrics-table.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
17. Step name: Get row(s). Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-get-row-s.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
18. Step name: Upsert row(s). Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-upsert-row-s.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
19. Step name: Default Data Loader2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-default-data-loader2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
20. Step name: Google Gemini Chat Model3. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-google-gemini-chat-model3.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
21. Step name: Google Gemini Chat Model4. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-google-gemini-chat-model4.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
22. Step name: Google Gemini Chat Model. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-google-gemini-chat-model.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
23. Step name: Google Gemini Chat Model5. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-google-gemini-chat-model5.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
24. Step name: Google Gemini Chat Model6. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-google-gemini-chat-model6.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
25. Step name: Metaprompt Agentv2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-metaprompt-agentv2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
26. Step name: Metadata Agentv2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent-metadata-agentv2.py`
   Input: a
