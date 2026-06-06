# ComparativeAnalysisAgent

## Purpose

ComparativeAnalysisAgent compares peer companies within an AI subsector using financial fundamentals, price momentum, recent news sentiment, and AI patent activity so a human analyst can see relative position without treating any single signal as an investment decision.

## Inputs

| Input | Type | Source | Required? |
|---|---|---|---|
| Subsector | String | Recipe default: `Cloud Infrastructure` | Yes |
| Peer company list | JSON | `scripts/gigo/comparative_peer_company_list.py` | Yes |
| Financial overview | JSON | Alpha Vantage or local export | Yes |
| Financial time series | JSON | Alpha Vantage or local export | Yes |
| News articles | JSON | NewsAPI or local export | No |
| Patent results | JSON | SerpAPI Google Patents or local export | No |
| API credentials | Environment variables | `ALPHA_VANTAGE_API_KEY`, `NEWSAPI_KEY`, `SERPAPI_KEY` | No for local/export mode |

## Phase Gates

1. Peer gate: subsector must map to a bounded peer list. Verification: run `python3 scripts/gigo/comparative_peer_company_list.py`. Human capacity: [PF], [PA].
2. Credential gate: live API calls must use env vars only. Verification: run each ingest script without credentials and confirm credential-required specs. Human capacity: [TO].
3. Financial gate: metric records must preserve missing values instead of inventing numbers. Verification: run `python3 scripts/tools/calculate_comparative_financial_metrics.py`. Human capacity: [PA].
4. Signal gate: news and patent summaries must show counts and source limitations. Verification: run `python3 scripts/tools/analyze_comparative_news_sentiment.py` and `python3 scripts/tools/analyze_comparative_patents.py`. Human capacity: [IJ], [PA].
5. Aggregation gate: final aggregates must separate financial metrics from news/patent signals. Verification: run `python3 scripts/tools/aggregate_comparative_financials.py` and `python3 scripts/tools/aggregate_comparative_signals.py`. Human capacity: [EI].

## Steps

1. Trigger analysis. Labor: AI. Script called: none; conductor trigger. Input: manual run. Output: run ID. Where output goes: `logs/`.
2. Select peers. Labor: AI. Script called: `scripts/gigo/comparative_peer_company_list.py`. Input: subsector. Output: peer records. Where output goes: `data/verified/`.
3. Attach configuration. Labor: AI. Script called: `scripts/gigo/comparative_store_variables.py`. Input: peer records. Output: metadata and env-var names. Where output goes: `logs/`.
4. Fetch financial data. Labor: AI. Script called: `scripts/ingest/fetch_comparative_financial_overview.py` and `scripts/ingest/fetch_comparative_financial_timeseries.py`. Input: peer records. Output: raw financial payloads or credential-required specs. Where output goes: `data/raw/`.
5. Calculate financial metrics. Labor: AI. Script called: `scripts/tools/calculate_comparative_financial_metrics.py`. Input: financial payloads. Output: financial metric records. Where output goes: `data/verified/`.
6. Fetch and analyze news. Labor: AI. Script called: `scripts/ingest/fetch_comparative_news.py` and `scripts/tools/analyze_comparative_news_sentiment.py`. Input: peer records and news payloads. Output: news sentiment summaries. Where output goes: `data/verified/`.
7. Fetch and analyze patents. Labor: AI. Script called: `scripts/ingest/fetch_comparative_patents.py` and `scripts/tools/analyze_comparative_patents.py`. Input: peer records and patent payloads. Output: patent summaries. Where output goes: `data/verified/`.
8. Aggregate outputs. Labor: AI. Script called: `scripts/tools/aggregate_comparative_financials.py` and `scripts/tools/aggregate_comparative_signals.py`. Input: metrics and signal records. Output: aggregate reports. Where output goes: `reports/generated/`.
9. Human review. Labor: Human. Human action required: compare peers, inspect missing data, and decide what conclusions are defensible. Output: decision notes. Where output goes: `reports/generated/`.

## Output Contract

### Agent output

Agent output goes to `logs/comparativeanalysisagent/<run-id>.json`. It must include subsector, peer list, credential status, financial payload status, metric records, news article counts, patent counts, aggregate records, scripts used, missing fields, and stop conditions.

### Human report

The human report goes to `reports/generated/comparativeanalysisagent-<date>.md`. It surfaces relative financial health, news sentiment, patent signal strength, missing-data caveats, and recommended analyst follow-up.

## Stop Conditions

- Stop if subsector is not mapped to a peer group.
- Stop if live API calls are requested without env-var credentials and approval.
- Stop if financial metric payloads are missing for every peer.
- Stop if any script invents financial values rather than marking them missing.
- Stop before investment conclusions without human interpretation.

## Provenance

Original n8n JSON: `data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Comparative_Analysis_Agent/ComparativeAnalysisAgent.json`
