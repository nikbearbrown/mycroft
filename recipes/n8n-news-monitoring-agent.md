# Recipe: News Monitoring Agent

## Executive Summary

This recipe converts the original n8n workflow into an agent-readable recipe for Mycroft. It is primarily for agents to execute or adapt, while giving humans a compact summary of what the workflow does, what evidence it should prefer, and what checks must pass before automation continues.

## Original Workflow

- Source: `data/mycroft-main/n8n-workflows/originals/Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json`
- Imported from pantry path: `Core_Components/news_monitoring_agent/workflows/News Monitoring Agent.json`
- Node count: 78

## Required Reads

1. Check `data/mycroft-main/` for verified local or database data that satisfies the request.
2. Check `scripts/mycroft-main/` for vetted scripts that already perform the needed extraction, transformation, or validation.
3. Read this workflow's original JSON before changing behavior.
4. Only use live web/API lookup when verified local data does not exist or is explicitly stale.

## Phase Gates

1. Data gate: identify the trusted data source, freshness, provenance, and missing fields.
2. Script gate: prefer an existing vetted script; if a new script is needed, write a narrow test before using it in a pipeline.
3. Dry-run gate: execute the smallest non-destructive sample and save logs or outputs.
4. Validation gate: compare outputs against expected schema, row counts, citations, or workflow invariants.
5. Automation gate: only run a full automated pipeline after the previous gates pass.

## Trigger Surface

Schedule Trigger, When chat message received, When clicking ‘Execute workflow’

## Agent/AI Nodes

Embeddings HuggingFace Inference, Postgres Chat Memory, When chat message received, Embeddings HuggingFace Inference4, Default Data Loader2, Recursive Character Text Splitter2, Google Gemini Chat Model3, Google Gemini Chat Model4, Google Gemini Chat Model, Google Gemini Chat Model5, Google Gemini Chat Model6, Metaprompt Agentv2, Metadata Agentv2, Default Data Loader3, Recursive Character Text Splitter3, Embeddings Google Gemini1, Postgres Chat Memory1, Google Gemini Chat Model7, Qdrant Vector Store A, Qdrant Vector Store B, News Articles RAG A, News Articles RAG B, Embeddings Google Gemini2, Structured Output Parser test1, Structured Output Parser2, Metaprompt Agentv, Metadata Agentv, OpenRouter Chat Model3, OpenRouter Chat Model4, OpenRouter Chat Model5, OpenRouter Chat Model6, RAG Agent3, Google Gemini Chat Model8, News Articles RAG A2, Embeddings HuggingFace Inference6, News Articles RAG A3, Embeddings HuggingFace Inference7, Qdrant Vector Store, Embeddings HuggingFace Inference8, AI Agent, OpenRouter Chat Model, Metadata structured output, Metaprompt structured output, RAG Agent A, RAG Agent B

## External Writes or Side Effects

feedparser fetch, Healthcheck, Postgres Chat Memory, Parse, FinBert, View daily KPIs, Create Qdrant Collection, Write metrics, Create METRICS table, Postgres Chat Memory1, Qdrant Vector Store A, Qdrant Vector Store B, News Articles RAG A, News Articles RAG B, HTTP Request, Read/Write Files from Disk, News Articles RAG A2, News Articles RAG A3, Qdrant Vector Store

## Node Type Summary

| Node Type | Count |
| --- | --- |
| agent | 8 |
| chatTrigger | 1 |
| convertToFile | 1 |
| dataTable | 2 |
| documentDefaultDataLoader | 2 |
| embeddingsGoogleGemini | 2 |
| embeddingsHuggingFaceInference | 5 |
| executeWorkflow | 2 |
| extractFromFile | 1 |
| filter | 1 |
| httpRequest | 6 |
| lmChatGoogleGemini | 7 |
| lmChatOpenRouter | 5 |
| manualTrigger | 1 |
| memoryPostgresChat | 2 |
| merge | 7 |
| outputParserStructured | 4 |
| postgres | 3 |
| readWriteFile | 1 |
| removeDuplicates | 1 |
| scheduleTrigger | 1 |
| splitOut | 1 |
| stickyNote | 4 |
| switch | 1 |
| textSplitterRecursiveCharacterTextSplitter | 2 |
| vectorStoreQdrant | 7 |

## Workflow Nodes

| Order | Node | Type |
| --- | --- | --- |
| 1 | feedparser fetch | httpRequest |
| 2 | Schedule Trigger | scheduleTrigger |
| 3 | Healthcheck | httpRequest |
| 4 | Merge1 | merge |
| 5 | Embeddings HuggingFace Inference | embeddingsHuggingFaceInference |
| 6 | Postgres Chat Memory | memoryPostgresChat |
| 7 | When chat message received | chatTrigger |
| 8 | Parse | httpRequest |
| 9 | not null | filter |
| 10 | Remove Duplicates | removeDuplicates |
| 11 | Merge2 | merge |
| 12 | FinBert | httpRequest |
| 13 | Embeddings HuggingFace Inference4 | embeddingsHuggingFaceInference |
| 14 | Sticky Note | stickyNote |
| 15 | Sticky Note1 | stickyNote |
| 16 | Sticky Note2 | stickyNote |
| 17 | View daily KPIs | postgres |
| 18 | Create Qdrant Collection | httpRequest |
| 19 | Write metrics | postgres |
| 20 | Create METRICS table | postgres |
| 21 | Get row(s) | dataTable |
| 22 | Upsert row(s) | dataTable |
| 23 | Split Out | splitOut |
| 24 | Default Data Loader2 | documentDefaultDataLoader |
| 25 | Recursive Character Text Splitter2 | textSplitterRecursiveCharacterTextSplitter |
| 26 | Merge | merge |
| 27 | Google Gemini Chat Model3 | lmChatGoogleGemini |
| 28 | Google Gemini Chat Model4 | lmChatGoogleGemini |
| 29 | Google Gemini Chat Model | lmChatGoogleGemini |
| 30 | Google Gemini Chat Model5 | lmChatGoogleGemini |
| 31 | Google Gemini Chat Model6 | lmChatGoogleGemini |
| 32 | Metaprompt Agentv2 | agent |
| 33 | Metadata Agentv2 | agent |
| 34 | Default Data Loader3 | documentDefaultDataLoader |
| 35 | Recursive Character Text Splitter3 | textSplitterRecursiveCharacterTextSplitter |
| 36 | Embeddings Google Gemini1 | embeddingsGoogleGemini |
| 37 | Postgres Chat Memory1 | memoryPostgresChat |
| 38 | Google Gemini Chat Model7 | lmChatGoogleGemini |
| 39 | Qdrant Vector Store A | vectorStoreQdrant |
| 40 | Qdrant Vector Store B | vectorStoreQdrant |
| 41 | News Articles RAG A | vectorStoreQdrant |
| 42 | News Articles RAG B | vectorStoreQdrant |
| 43 | Embeddings Google Gemini2 | embeddingsGoogleGemini |
| 44 | Merge3 | merge |
| 45 | Structured Output Parser test1 | outputParserStructured |
| 46 | Structured Output Parser2 | outputParserStructured |
| 47 | Metaprompt Agentv | agent |
| 48 | Metadata Agentv | agent |
| 49 | Extract from File | extractFromFile |
| 50 | Merge5 | merge |
| 51 | Convert to File1 | convertToFile |
| 52 | HTTP Request | httpRequest |
| 53 | Read/Write Files from Disk | readWriteFile |
| 54 | When clicking ‘Execute workflow’ | manualTrigger |
| 55 | OpenRouter Chat Model3 | lmChatOpenRouter |
| 56 | OpenRouter Chat Model4 | lmChatOpenRouter |
| 57 | OpenRouter Chat Model5 | lmChatOpenRouter |
| 58 | OpenRouter Chat Model6 | lmChatOpenRouter |
| 59 | RAG Agent3 | agent |
| 60 | Google Gemini Chat Model8 | lmChatGoogleGemini |
| 61 | News Articles RAG A2 | vectorStoreQdrant |
| 62 | Embeddings HuggingFace Inference6 | embeddingsHuggingFaceInference |
| 63 | News Articles RAG A3 | vectorStoreQdrant |
| 64 | Embeddings HuggingFace Inference7 | embeddingsHuggingFaceInference |
| 65 | Call rag grader | executeWorkflow |
| 66 | Merge6 | merge |
| 67 | Call rag grader1 | executeWorkflow |
| 68 | Merge4 | merge |
| 69 | Qdrant Vector Store | vectorStoreQdrant |
| 70 | Embeddings HuggingFace Inference8 | embeddingsHuggingFaceInference |
| 71 | AI Agent | agent |
| 72 | OpenRouter Chat Model | lmChatOpenRouter |
| 73 | Sticky Note3 | stickyNote |
| 74 | Metadata structured output | outputParserStructured |
| 75 | Metaprompt structured output | outputParserStructured |
| 76 | Switch - A/B testing | switch |
| 77 | RAG Agent A | agent |
| 78 | RAG Agent B | agent |

## Output Contract

- Produce a short run report with inputs, source provenance, scripts used, validations performed, and generated artifacts.
- Store durable outputs under `data/mycroft-main/` when they are data-like and `docs/mycroft-main/` when they are explanatory.
- Note any unverified assumptions, missing credentials, external services, or failed gates.

## Stop Conditions

- Stop if verified local data contradicts live/API data until provenance is resolved.
- Stop if a required credential, endpoint, database, or workflow invariant is missing.
- Stop before bulk external writes, notifications, or trades unless the human explicitly approves that run.
