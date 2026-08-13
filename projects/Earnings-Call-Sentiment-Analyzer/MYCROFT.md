# Mycroft Integration — Earnings Call Sentiment Analyzer

## Provenance

- Original user-supplied project: `/Users/adwaitchangan/Study/Mycroft/Earnings_Call_Sentiment_Analyzer/`
- Imported into Mycroft: 2026-07-24
- Imported project path: `projects/Earnings-Call-Sentiment-Analyzer/`
- Original source folder was read and copied without modification.
- User-created sample transcript: `sample-data/sample-transcript.txt`
- Mycroft raw-data copy: `data/raw/earnings-call-sentiment-analyzer/northstar-cloud-systems-q3-fy2026.txt`

The Northstar Cloud Systems transcript is a user-created sample. It is not represented as an authentic issuer transcript, filing, or investment record.

## Mycroft Lifecycle

- Recipe: `recipes/earnings-call-sentiment-analyzer.md`
- Conductor: `conductor/earnings-call-sentiment-analyzer.md`
- Human report template: `reports/templates/earnings-call-sentiment-analyzer.md`
- Status: `DRAFT`

The application remains a self-contained full-stack project. Mycroft-native files define its evidence contract, phase gates, report shape, and lifecycle without duplicating the application source.

## Verified During Import

- The copied project contains 84 durable source/configuration files.
- The raw-data copy is byte-identical to the supplied sample transcript.
- Nine worker parser and upload-path tests pass.
- Docker Compose builds and starts PostgreSQL, RabbitMQ, the Spring Boot API, the FinBERT worker, and the React frontend.
- A real API upload of the Northstar sample completed with 25 evidence chunks and 25 persisted model results.
- The frontend production build and lint pass; the live transcript list, dashboard, evidence search, and upload page render correctly.
- The backend Maven test lifecycle compiles all 36 sources successfully.

## Not Yet Verified

- Human adequacy review of chunk attribution and sentiment evidence
- A defined acceptable unknown-attribution rate and labeled-corpus accuracy threshold
- An immutable pinned/persisted FinBERT model revision
- Backend unit/integration tests and frontend automated tests; neither test suite currently exists

The technical pipeline works, but these are open adequacy gates. No local result should be described as an approved sentiment finding until a named human review is completed and logged.

## Completed Sample Run

- Machine log: `logs/earnings-call-sentiment-analyzer-20260724-050407-ncs-q3fy2026.json`
- Human report: `reports/generated/earnings-call-sentiment-analyzer-20260724-050407-ncs-q3fy2026.md`
- Result: `COMPLETED_PENDING_HUMAN_REVIEW`
- Parser gaps: 4 of 25 chunks have an unknown section and 2 of 25 have an unknown speaker.
- Presentation issue found during verification: the dashboard explanation conflated FinBERT argmax evidence labels with ±5% aggregate net-tone bands. The copy was corrected before the feature-branch commit.

## Development Credentials

`docker-compose.yml` contains documented local-development database and RabbitMQ defaults. They are not production secrets and must be replaced with managed secrets before any deployed use.
