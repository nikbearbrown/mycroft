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

## Node Classification

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

## Steps

1. Step name: Verify provenance and source intent. Labor: Human.
   Human action: Record approval, rejection, or requested changes with supervisory capacity label [PF].
   Input: data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json.
   Output: provenance fields: workflow_path, exists, parsed_ok, title_matches_pipeline, source_inventory_checked.
   Where output goes: logs/gate-decisions/.
2. Step name: feedparser fetch. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-news-monitoring-agent__feedparser-fetch.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-news-monitoring-agent/.
3. Step name: Healthcheck. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-news-monitoring-agent__healthcheck.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-news-monitoring-agent/.
4. Step name: Embeddings HuggingFace Inference. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__embeddings-huggingface-inference.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
5. Step name: Postgres Chat Memory. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__postgres-chat-memory.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
6. Step name: Parse. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-news-monitoring-agent__parse.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-news-monitoring-agent/.
7. Step name: Remove Duplicates. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__remove-duplicates.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
8. Step name: FinBert. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-news-monitoring-agent__finbert.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-news-monitoring-agent/.
9. Step name: Embeddings HuggingFace Inference4. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__embeddings-huggingface-inference4.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
10. Step name: Sticky Note. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__sticky-note.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
11. Step name: Sticky Note1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__sticky-note1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
12. Step name: Sticky Note2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__sticky-note2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
13. Step name: View daily KPIs. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__view-daily-kpis.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
14. Step name: Create Qdrant Collection. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-news-monitoring-agent__create-qdrant-collection.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
15. Step name: Write metrics. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-news-monitoring-agent__write-metrics.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
16. Step name: Create METRICS table. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-news-monitoring-agent__create-metrics-table.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
17. Step name: Get row(s). Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__get-row-s.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
18. Step name: Upsert row(s). Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__upsert-row-s.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
19. Step name: Default Data Loader2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__default-data-loader2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
20. Step name: Google Gemini Chat Model3. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__google-gemini-chat-model3.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
21. Step name: Google Gemini Chat Model4. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__google-gemini-chat-model4.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
22. Step name: Google Gemini Chat Model. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__google-gemini-chat-model.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
23. Step name: Google Gemini Chat Model5. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__google-gemini-chat-model5.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
24. Step name: Google Gemini Chat Model6. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__google-gemini-chat-model6.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
25. Step name: Metaprompt Agentv2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__metaprompt-agentv2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
26. Step name: Metadata Agentv2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__metadata-agentv2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
27. Step name: Default Data Loader3. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__default-data-loader3.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
28. Step name: Embeddings Google Gemini1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__embeddings-google-gemini1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
29. Step name: Postgres Chat Memory1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__postgres-chat-memory1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
30. Step name: Google Gemini Chat Model7. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__google-gemini-chat-model7.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
31. Step name: Qdrant Vector Store A. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__qdrant-vector-store-a.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
32. Step name: Qdrant Vector Store B. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__qdrant-vector-store-b.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
33. Step name: News Articles RAG A. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__news-articles-rag-a.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
34. Step name: News Articles RAG B. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__news-articles-rag-b.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
35. Step name: Embeddings Google Gemini2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__embeddings-google-gemini2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
36. Step name: Structured Output Parser test1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__structured-output-parser-test1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
37. Step name: Structured Output Parser2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__structured-output-parser2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
38. Step name: Metaprompt Agentv. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__metaprompt-agentv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
39. Step name: Metadata Agentv. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__metadata-agentv.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
40. Step name: Extract from File. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__extract-from-file.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
41. Step name: Convert to File1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__convert-to-file1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
42. Step name: HTTP Request. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/ingest/n8n-news-monitoring-agent__http-request.py`
   Input: approved upstream output or sample fixture.
   Output: raw JSON fields: source_name, source_url_or_path, fetched_at, record_count, records, errors.
   Where output goes: data/raw/n8n-news-monitoring-agent/.
43. Step name: Read/Write Files from Disk. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-news-monitoring-agent__read-write-files-from-disk.py`
   Input: approved upstream output or sample fixture.
   Output: local handoff JSON fields: action, approved_for_live_action:false, input_refs, output_refs, flags, live_call_performed.
   Where output goes: logs/.
44. Step name: OpenRouter Chat Model3. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__openrouter-chat-model3.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
45. Step name: OpenRouter Chat Model4. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__openrouter-chat-model4.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
46. Step name: OpenRouter Chat Model5. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__openrouter-chat-model5.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
47. Step name: OpenRouter Chat Model6. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__openrouter-chat-model6.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
48. Step name: RAG Agent3. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__rag-agent3.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
49. Step name: Google Gemini Chat Model8. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__google-gemini-chat-model8.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
50. Step name: News Articles RAG A2. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__news-articles-rag-a2.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
51. Step name: Embeddings HuggingFace Inference6. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__embeddings-huggingface-inference6.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
52. Step name: News Articles RAG A3. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__news-articles-rag-a3.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
53. Step name: Embeddings HuggingFace Inference7. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__embeddings-huggingface-inference7.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
54. Step name: Call rag grader. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__call-rag-grader.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
55. Step name: Call rag grader1. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__call-rag-grader1.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
56. Step name: Qdrant Vector Store. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__qdrant-vector-store.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
57. Step name: Embeddings HuggingFace Inference8. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__embeddings-huggingface-inference8.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
58. Step name: AI Agent. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__ai-agent.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
59. Step name: OpenRouter Chat Model. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__openrouter-chat-model.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
60. Step name: Sticky Note3. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__sticky-note3.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
61. Step name: Metadata structured output. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__metadata-structured-output.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
62. Step name: Metaprompt structured output. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__metaprompt-structured-output.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
63. Step name: Switch - A/B testing. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__switch-a-b-testing.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
64. Step name: RAG Agent A. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__rag-agent-a.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
65. Step name: RAG Agent B. Labor: AI with Human gate.
   Script called: `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__rag-agent-b.py`
   Input: approved upstream output or sample fixture.
   Output: verified JSON fields: record_count, records, rejects, duplicates, missing_fields, validation_flags.
   Where output goes: data/verified/n8n-news-monitoring-agent/.
66. Step name: Produce human report. Labor: AI with Human review.
   Script called: `[TODO: DEV] Create or map script path: scripts/tools/n8n-news-monitoring-agent__produce-human-report.py`
   Input: agent log plus raw and verified outputs.
   Output: markdown report sections: run summary, source inventory, inputs used, validation results, flags, typed TODOs, decision recommendation.
   Where output goes: reports/generated/.

## Output Contract

### Agent output
File: `logs/n8n-news-monitoring-agent-[DATE].json`
Fields: `workflow`, `run_id`, `mode`, `steps_completed`, `records_seen`, `rejects`, `duplicates`, `flags`, `stop_conditions`, `todo_items`, `source_files`, `gate_decisions`, `live_call_performed`, `generated_at`.

### Human report
File: `reports/generated/n8n-news-monitoring-agent-[DATE].md`
Reader: domain lead or human boss responsible for accepting the `News Monitoring Agent` run.
Decision enabled: approve the run for the next phase, request source/schema fixes, or block live execution.
Sections: Run summary, source inventory, inputs used, steps completed, records seen, rejects, duplicates, flags, typed TODOs, gate decisions, evidence-backed findings, decision recommendation.

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
| feedparser fetch | `snickerdoodle run n8n-news-monitoring-agent --step feedparser-fetch` | `--sample` |
| Healthcheck | `snickerdoodle run n8n-news-monitoring-agent --step healthcheck` | `--sample` |
| Embeddings HuggingFace Inference | `snickerdoodle run n8n-news-monitoring-agent --step embeddings-huggingface-inference` |  |
| Postgres Chat Memory | `snickerdoodle run n8n-news-monitoring-agent --step postgres-chat-memory` |  |
| Parse | `snickerdoodle run n8n-news-monitoring-agent --step parse` | `--sample` |
| Remove Duplicates | `snickerdoodle run n8n-news-monitoring-agent --step remove-duplicates` |  |
| FinBert | `snickerdoodle run n8n-news-monitoring-agent --step finbert` | `--sample` |
| Embeddings HuggingFace Inference4 | `snickerdoodle run n8n-news-monitoring-agent --step embeddings-huggingface-inference4` |  |
| Sticky Note | `snickerdoodle run n8n-news-monitoring-agent --step sticky-note` |  |
| Sticky Note1 | `snickerdoodle run n8n-news-monitoring-agent --step sticky-note1` |  |
| Sticky Note2 | `snickerdoodle run n8n-news-monitoring-agent --step sticky-note2` |  |
| View daily KPIs | `snickerdoodle run n8n-news-monitoring-agent --step view-daily-kpis` |  |
| Create Qdrant Collection | `snickerdoodle run n8n-news-monitoring-agent --step create-qdrant-collection` | `--no-write` |
| Write metrics | `snickerdoodle run n8n-news-monitoring-agent --step write-metrics` | `--no-write` |
| Create METRICS table | `snickerdoodle run n8n-news-monitoring-agent --step create-metrics-table` | `--no-write` |
| Get row(s) | `snickerdoodle run n8n-news-monitoring-agent --step get-row-s` |  |
| Upsert row(s) | `snickerdoodle run n8n-news-monitoring-agent --step upsert-row-s` |  |
| Default Data Loader2 | `snickerdoodle run n8n-news-monitoring-agent --step default-data-loader2` |  |
| Google Gemini Chat Model3 | `snickerdoodle run n8n-news-monitoring-agent --step google-gemini-chat-model3` |  |
| Google Gemini Chat Model4 | `snickerdoodle run n8n-news-monitoring-agent --step google-gemini-chat-model4` |  |
| Google Gemini Chat Model | `snickerdoodle run n8n-news-monitoring-agent --step google-gemini-chat-model` |  |
| Google Gemini Chat Model5 | `snickerdoodle run n8n-news-monitoring-agent --step google-gemini-chat-model5` |  |
| Google Gemini Chat Model6 | `snickerdoodle run n8n-news-monitoring-agent --step google-gemini-chat-model6` |  |
| Metaprompt Agentv2 | `snickerdoodle run n8n-news-monitoring-agent --step metaprompt-agentv2` |  |
| Metadata Agentv2 | `snickerdoodle run n8n-news-monitoring-agent --step metadata-agentv2` |  |
| Default Data Loader3 | `snickerdoodle run n8n-news-monitoring-agent --step default-data-loader3` |  |
| Embeddings Google Gemini1 | `snickerdoodle run n8n-news-monitoring-agent --step embeddings-google-gemini1` |  |
| Postgres Chat Memory1 | `snickerdoodle run n8n-news-monitoring-agent --step postgres-chat-memory1` |  |
| Google Gemini Chat Model7 | `snickerdoodle run n8n-news-monitoring-agent --step google-gemini-chat-model7` |  |
| Qdrant Vector Store A | `snickerdoodle run n8n-news-monitoring-agent --step qdrant-vector-store-a` |  |
| Qdrant Vector Store B | `snickerdoodle run n8n-news-monitoring-agent --step qdrant-vector-store-b` |  |
| News Articles RAG A | `snickerdoodle run n8n-news-monitoring-agent --step news-articles-rag-a` |  |
| News Articles RAG B | `snickerdoodle run n8n-news-monitoring-agent --step news-articles-rag-b` |  |
| Embeddings Google Gemini2 | `snickerdoodle run n8n-news-monitoring-agent --step embeddings-google-gemini2` |  |
| Structured Output Parser test1 | `snickerdoodle run n8n-news-monitoring-agent --step structured-output-parser-test1` |  |
| Structured Output Parser2 | `snickerdoodle run n8n-news-monitoring-agent --step structured-output-parser2` |  |
| Metaprompt Agentv | `snickerdoodle run n8n-news-monitoring-agent --step metaprompt-agentv` |  |
| Metadata Agentv | `snickerdoodle run n8n-news-monitoring-agent --step metadata-agentv` |  |
| Extract from File | `snickerdoodle run n8n-news-monitoring-agent --step extract-from-file` |  |
| Convert to File1 | `snickerdoodle run n8n-news-monitoring-agent --step convert-to-file1` |  |
| HTTP Request | `snickerdoodle run n8n-news-monitoring-agent --step http-request` | `--sample` |
| Read/Write Files from Disk | `snickerdoodle run n8n-news-monitoring-agent --step read-write-files-from-disk` | `--no-write` |
| OpenRouter Chat Model3 | `snickerdoodle run n8n-news-monitoring-agent --step openrouter-chat-model3` |  |
| OpenRouter Chat Model4 | `snickerdoodle run n8n-news-monitoring-agent --step openrouter-chat-model4` |  |
| OpenRouter Chat Model5 | `snickerdoodle run n8n-news-monitoring-agent --step openrouter-chat-model5` |  |
| OpenRouter Chat Model6 | `snickerdoodle run n8n-news-monitoring-agent --step openrouter-chat-model6` |  |
| RAG Agent3 | `snickerdoodle run n8n-news-monitoring-agent --step rag-agent3` |  |
| Google Gemini Chat Model8 | `snickerdoodle run n8n-news-monitoring-agent --step google-gemini-chat-model8` |  |
| News Articles RAG A2 | `snickerdoodle run n8n-news-monitoring-agent --step news-articles-rag-a2` |  |
| Embeddings HuggingFace Inference6 | `snickerdoodle run n8n-news-monitoring-agent --step embeddings-huggingface-inference6` |  |
| News Articles RAG A3 | `snickerdoodle run n8n-news-monitoring-agent --step news-articles-rag-a3` |  |
| Embeddings HuggingFace Inference7 | `snickerdoodle run n8n-news-monitoring-agent --step embeddings-huggingface-inference7` |  |
| Call rag grader | `snickerdoodle run n8n-news-monitoring-agent --step call-rag-grader` |  |
| Call rag grader1 | `snickerdoodle run n8n-news-monitoring-agent --step call-rag-grader1` |  |
| Qdrant Vector Store | `snickerdoodle run n8n-news-monitoring-agent --step qdrant-vector-store` |  |
| Embeddings HuggingFace Inference8 | `snickerdoodle run n8n-news-monitoring-agent --step embeddings-huggingface-inference8` |  |
| AI Agent | `snickerdoodle run n8n-news-monitoring-agent --step ai-agent` |  |
| OpenRouter Chat Model | `snickerdoodle run n8n-news-monitoring-agent --step openrouter-chat-model` |  |
| Sticky Note3 | `snickerdoodle run n8n-news-monitoring-agent --step sticky-note3` |  |
| Metadata structured output | `snickerdoodle run n8n-news-monitoring-agent --step metadata-structured-output` |  |
| Metaprompt structured output | `snickerdoodle run n8n-news-monitoring-agent --step metaprompt-structured-output` |  |
| Switch - A/B testing | `snickerdoodle run n8n-news-monitoring-agent --step switch-a-b-testing` |  |
| RAG Agent A | `snickerdoodle run n8n-news-monitoring-agent --step rag-agent-a` |  |
| RAG Agent B | `snickerdoodle run n8n-news-monitoring-agent --step rag-agent-b` |  |
| Produce human report | `snickerdoodle run n8n-news-monitoring-agent --step produce-human-report` | `--no-write` |

### Gate Commands

| Gate | CLI Command |
|---|---|
| Gate 1 - source/input readiness | `snickerdoodle gate n8n-news-monitoring-agent --gate 1 --decision approve --note "..."` |
| Gate 2 - sample run | `snickerdoodle gate n8n-news-monitoring-agent --gate 2 --decision approve --note "..."` |
| Gate 3 - report contract | `snickerdoodle gate n8n-news-monitoring-agent --gate 3 --decision approve --note "..."` |

### Script Locations

| Step | Script Path | Layer |
|---|---|---|
| feedparser fetch | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-news-monitoring-agent__feedparser-fetch.py` | ingest |
| Healthcheck | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-news-monitoring-agent__healthcheck.py` | ingest |
| Embeddings HuggingFace Inference | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__embeddings-huggingface-inference.py` | gigo |
| Postgres Chat Memory | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__postgres-chat-memory.py` | gigo |
| Parse | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-news-monitoring-agent__parse.py` | ingest |
| Remove Duplicates | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__remove-duplicates.py` | gigo |
| FinBert | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-news-monitoring-agent__finbert.py` | ingest |
| Embeddings HuggingFace Inference4 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__embeddings-huggingface-inference4.py` | gigo |
| Sticky Note | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__sticky-note.py` | gigo |
| Sticky Note1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__sticky-note1.py` | gigo |
| Sticky Note2 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__sticky-note2.py` | gigo |
| View daily KPIs | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__view-daily-kpis.py` | gigo |
| Create Qdrant Collection | `[TODO: DEV] Create or map script path: scripts/tools/n8n-news-monitoring-agent__create-qdrant-collection.py` | tool |
| Write metrics | `[TODO: DEV] Create or map script path: scripts/tools/n8n-news-monitoring-agent__write-metrics.py` | tool |
| Create METRICS table | `[TODO: DEV] Create or map script path: scripts/tools/n8n-news-monitoring-agent__create-metrics-table.py` | tool |
| Get row(s) | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__get-row-s.py` | gigo |
| Upsert row(s) | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__upsert-row-s.py` | gigo |
| Default Data Loader2 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__default-data-loader2.py` | gigo |
| Google Gemini Chat Model3 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__google-gemini-chat-model3.py` | gigo |
| Google Gemini Chat Model4 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__google-gemini-chat-model4.py` | gigo |
| Google Gemini Chat Model | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__google-gemini-chat-model.py` | gigo |
| Google Gemini Chat Model5 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__google-gemini-chat-model5.py` | gigo |
| Google Gemini Chat Model6 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__google-gemini-chat-model6.py` | gigo |
| Metaprompt Agentv2 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__metaprompt-agentv2.py` | gigo |
| Metadata Agentv2 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__metadata-agentv2.py` | gigo |
| Default Data Loader3 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__default-data-loader3.py` | gigo |
| Embeddings Google Gemini1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__embeddings-google-gemini1.py` | gigo |
| Postgres Chat Memory1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__postgres-chat-memory1.py` | gigo |
| Google Gemini Chat Model7 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__google-gemini-chat-model7.py` | gigo |
| Qdrant Vector Store A | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__qdrant-vector-store-a.py` | gigo |
| Qdrant Vector Store B | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__qdrant-vector-store-b.py` | gigo |
| News Articles RAG A | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__news-articles-rag-a.py` | gigo |
| News Articles RAG B | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__news-articles-rag-b.py` | gigo |
| Embeddings Google Gemini2 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__embeddings-google-gemini2.py` | gigo |
| Structured Output Parser test1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__structured-output-parser-test1.py` | gigo |
| Structured Output Parser2 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__structured-output-parser2.py` | gigo |
| Metaprompt Agentv | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__metaprompt-agentv.py` | gigo |
| Metadata Agentv | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__metadata-agentv.py` | gigo |
| Extract from File | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__extract-from-file.py` | gigo |
| Convert to File1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__convert-to-file1.py` | gigo |
| HTTP Request | `[TODO: DEV] Create or map script path: scripts/ingest/n8n-news-monitoring-agent__http-request.py` | ingest |
| Read/Write Files from Disk | `[TODO: DEV] Create or map script path: scripts/tools/n8n-news-monitoring-agent__read-write-files-from-disk.py` | tool |
| OpenRouter Chat Model3 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__openrouter-chat-model3.py` | gigo |
| OpenRouter Chat Model4 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__openrouter-chat-model4.py` | gigo |
| OpenRouter Chat Model5 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__openrouter-chat-model5.py` | gigo |
| OpenRouter Chat Model6 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__openrouter-chat-model6.py` | gigo |
| RAG Agent3 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__rag-agent3.py` | gigo |
| Google Gemini Chat Model8 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__google-gemini-chat-model8.py` | gigo |
| News Articles RAG A2 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__news-articles-rag-a2.py` | gigo |
| Embeddings HuggingFace Inference6 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__embeddings-huggingface-inference6.py` | gigo |
| News Articles RAG A3 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__news-articles-rag-a3.py` | gigo |
| Embeddings HuggingFace Inference7 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__embeddings-huggingface-inference7.py` | gigo |
| Call rag grader | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__call-rag-grader.py` | gigo |
| Call rag grader1 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__call-rag-grader1.py` | gigo |
| Qdrant Vector Store | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__qdrant-vector-store.py` | gigo |
| Embeddings HuggingFace Inference8 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__embeddings-huggingface-inference8.py` | gigo |
| AI Agent | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__ai-agent.py` | gigo |
| OpenRouter Chat Model | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__openrouter-chat-model.py` | gigo |
| Sticky Note3 | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__sticky-note3.py` | gigo |
| Metadata structured output | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__metadata-structured-output.py` | gigo |
| Metaprompt structured output | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__metaprompt-structured-output.py` | gigo |
| Switch - A/B testing | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__switch-a-b-testing.py` | gigo |
| RAG Agent A | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__rag-agent-a.py` | gigo |
| RAG Agent B | `[TODO: DEV] Create or map script path: scripts/gigo/n8n-news-monitoring-agent__rag-agent-b.py` | gigo |
| Produce human report | `[TODO: DEV] Create or map script path: scripts/tools/n8n-news-monitoring-agent__produce-human-report.py` | tool |

### Output Locations

| Output | Path | Format |
|---|---|---|
| Raw ingest | `data/raw/n8n-news-monitoring-agent/` | JSON |
| Verified data | `data/verified/n8n-news-monitoring-agent/` | JSON |
| Agent log | `logs/n8n-news-monitoring-agent-[DATE].json` | JSON |
| Human report | `reports/generated/n8n-news-monitoring-agent-[DATE].md` | Markdown |
| Gate decisions | `logs/gate-decisions/` | JSON |

## Provenance

Original workflow JSON: `data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json`
