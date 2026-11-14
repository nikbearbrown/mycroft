# Step 2 audit: ingest declared inputs (scenariostresstestingagent)

Checked 2026-11-09T00:00:00+00:00. Mode: sample (no live call, no network, no database write). Approval record present: no.

## Requests ingested

| Folder | Read | Rejected |
|---|---|---|
| clean | 12 | 0 |
| defective | 10 | 0 |

Ingest keeps each request body exactly as it was frozen. It rejects only what it cannot read or cannot trust (missing, changed, unlisted or not JSON); whether a request has the right shape is step 3's work, so the defective folder ingests too.

## Sources and credentials the workflow names

| Node | Role | Status | Credential name | Set in the environment | Why |
|---|---|---|---|---|---|
| Webhook Trigger | trigger: POST /stress-test request body | available | none known | n/a | sample mode: the 22 invented requests under data/raw/scenariostresstestingagent/sample/ stand in for webhook bodies |
| When chat message received | trigger: chat message | skipped | none known | n/a | the invented corpus has no chat-message fixture, so the chat entry point is not exercised in sample mode |
| Groq Chat Model | live model call (llama-3.1-8b-instant) | approval-required | GROQ_API_KEY | no | a live model call; sample mode never makes it, and a live run needs an approval record and a credential from the environment |
| Fetch_Data | live HTTP request to www.alphavantage.co | approval-required | ALPHA_VANTAGE_API_KEY | no | a live network call; sample mode never makes it, and a live run needs an approval record and a credential from the environment |

No source marked approval-required was contacted. A credential is reported only as set or not set; its value is never read into a variable or a file.

## Handoff condition (conductor step 2)

Every source is available, skipped with a reason, or approval-required: **met**.
