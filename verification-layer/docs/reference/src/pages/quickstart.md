---
title: Running it
slug: quickstart
section: Start
order: 10
summary: Install the dependencies, configure the environment, start the server and the review app, and run the tests.
---

Everything runs locally: a FastAPI server on port 8000, a SQLite file for the record, a local
Ollama model for the agents, and a React review app the server serves at `/app`. Commands below
run from `verification-layer/` unless they say otherwise.

## Prerequisites

| Needed for | What | Notes |
|---|---|---|
| Everything | Python 3.10 or later | `requirements.txt` says 3.10+ is required for runtime `X \| Y` unions; the suites have been run on 3.12 (Windows) and 3.10 (WSL). |
| Live agents | [Ollama](https://ollama.com) with a model pulled | The default model is `llama3.2`. Gemini is used instead when the model name contains `gemini` (needs `GEMINI_API_KEY`). |
| Search tool | A Tavily API key | Optional. Without `TAVILY_API_KEY` each call runs without tools, and the UI warns. |
| Ticker compares | Network access to `sec.gov` | EDGAR companyfacts and filing documents. Set `SEC_USER_AGENT` to identify yourself, as SEC asks. |
| The review app | Node.js and npm | Only to build `web/frontend/`. The API runs without it. |
| Tracing | A self-hosted LangFuse | Optional to run: tracing is a no-op without its keys. The `langfuse` package itself must be installed, because [[pipeline/observability.py]] imports it unconditionally. |

## Install

```bash
python -m venv env
source env/bin/activate        # Windows (Git Bash): source env/Scripts/activate
pip install -r requirements.txt
```

The core engine (parser, validation loop, schemas, directives) is standard-library only, so the
test suite runs on a bare interpreter; `requirements.txt` is for the web app and the live
providers. See [[requirements.txt]].

## Configure

Copy the template and fill in what you need. `.env` is gitignored; never commit it.

```bash
cp .env.example .env
```

Every variable the code reads, with its default, is on the [Configuration](config.html) page.
The most used:

| Variable | Default | What it does |
|---|---|---|
| `LANGCHAIN_MODEL` | `llama3.2` | The model agents run on. |
| `OLLAMA_HOST` | `http://localhost:11434` | Where Ollama listens. |
| `TAVILY_API_KEY` | unset | Enables the agents' search tool. |
| `SEC_USER_AGENT` | a placeholder | Your contact string for SEC's fair-access policy. |
| `MODEL_TIMEOUT_S` | `120` | Seconds a model call may receive nothing before it is abandoned. |
| `CROSS_AGENT_MAX_CONCURRENCY` | `2` | Set to `1` to run a compare's two agents one after the other. |

## Start the server

```bash
scripts/start-server.sh
```

The script activates `env/` if it exists, builds the review app if `web/frontend/dist` is
missing and npm is available, and starts uvicorn on `PORT` (default 8000). The equivalent by
hand:

```bash
python -m uvicorn web.server:app --reload --port 8000
```

Then open `http://localhost:8000/`. It redirects to the review app at `/app/`. Without a build,
`/` returns a page explaining how to make one, and the API still works. FastAPI's generated API
explorer is at `/docs`.

`start-web-server.sh` in the package root does the same with a hard-coded WSL path; see
[[start-web-server.sh]].

## Build the review app

```bash
cd web/frontend
npm ci
npm run build      # type-check, then build into dist/
npm run dev        # or: a Vite dev server with hot reload
```

See [Review app (frontend)](files-frontend.html).

## Run the tests

```bash
python -m unittest discover -s tests -t .      # Python: network-free and model-free
cd web/frontend && npm run verify              # type-check, Vitest, then a build
```

Neither suite needs a model, the network or an API key. See [Python tests](files-tests.html) and
[Review app tests](files-frontend-tests.html).

## Build these docs

```bash
python scripts/build_docs.py            # rebuild docs/reference/
python scripts/build_docs.py --check    # report problems, write nothing
```

A new file without a documentation entry fails `tests/test_docs_coverage.py`. Add its entry to
the right page in `docs/reference/src/files/` (see `docs/reference/src/AUTHORING.md`).

## First things to try

1. Open `/app`, choose **New compare**, enter `AAPL`, and watch both agents work live.
2. Open the finished run: the figure matrix, the accounting checks, the grades and the decision
   gate. Switch the scope to investor and see what is withheld.
3. Open **Honest Ledger** from the top bar for what is known not to work.
