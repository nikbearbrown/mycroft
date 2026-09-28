---
title: HTTP API
slug: api
section: Reference
order: 10
summary: Every route the server exposes, generated from web/server.py, with how authentication and scope apply.
---

The server is a FastAPI app in [[web/server.py]]. FastAPI's own interactive explorer is at `/docs`
on a running server. The table below is generated from the route decorators on every build, so it
can't fall behind the code. The full behaviour of each route (request models, errors, what is
stored) is in the [web server entry](files-web.html#f-web-server-py).

## Authentication and scope

- `POST /api/auth/token` with `{"scope": "auditor"}` or `{"scope": "investor"}` returns a bearer
  JWT ([[web/auth.py]]). Send it as `Authorization: Bearer <token>`, never as a query parameter.
- **Required** on the routes that run agents (`/api/chat`, `/api/compare` and their streams) and
  on the ones that write judgments (`POST .../decisions`, `POST .../flags`, auditor only).
- **Optional** on the run reads: with a token, the run is served at the token's scope; without
  one, at the scope the run was stored under.
- **None** on the rest, including `POST /api/config` and `DELETE /api/runs`. This is recorded as
  an open critical issue ([audit-criticals](ledger.html#audit-criticals)); the server is for
  localhost only.
- The token endpoint issues any scope to any caller. It is a prototype limit, not a login.

## Routes

{{routes}}

## Streams

The two `/stream` routes answer with `text/event-stream`. Events, in order: `run_started`, then
`step_started` and `step_finished` as steps happen, `agent_finished` per agent (compare only),
then `result` or `error`. See [Live runs](f-live.html).

## Examples

```bash
TOKEN=$(curl -s -X POST localhost:8000/api/auth/token -H 'content-type: application/json' \
  -d '{"scope":"auditor"}' | python -c 'import json,sys;print(json.load(sys.stdin)["access_token"])')

curl -s -X POST localhost:8000/api/compare -H "authorization: Bearer $TOKEN" \
  -H 'content-type: application/json' -d '{"ticker":"AAPL","pairing":"lenses"}'

curl -s localhost:8000/api/runs/<run_id> -H "authorization: Bearer $TOKEN"
curl -s localhost:8000/api/runs/<run_id>/export.md -H "authorization: Bearer $TOKEN" -o review.md
```
