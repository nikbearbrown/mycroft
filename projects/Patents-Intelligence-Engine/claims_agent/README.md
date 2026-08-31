# Claims Agent — Patents Intelligence Engine

`claims_parser.py` splits raw patent claims text (pulled from
`patents-public-data.patents.publications.claims_localized` on BigQuery)
into individual claims, and classifies each as independent or dependent.

**Tested against 4 real patents, 64 total claims, all correctly split and
classified**, verified by hand against the raw text:

- US-11791319-B2 — 20 claims, 3 independent, 17 dependent (including
  3-level-deep dependency chains) — all correct
- US-10822628-B2 — 7 claims — all correct
- US-11197952-B2 — 17 claims — all correct
- US-10265458-B2 — 20 claims — all correct

## Known limitation

The multi-dependency detection heuristic (flagging claims that might
depend on more than one other claim, e.g. "claim 1 or 2") is currently
too eager — it triggers on any "or" appearing anywhere in a claim's
text, not specifically in the dependency reference. This produced one
confirmed false positive during stress-testing (Claim 5 of
US-11197952-B2, flagged because of "bumps or projections" language
elsewhere in the claim, unrelated to its actual single dependency on
Claim 3).

The underlying split/classify logic is correct. This heuristic needs a
narrower regex that only looks for multiple "claim N" references, not
any "or" in the claim body.

## Not built yet

- Protection-scope classification (broad/narrow, defensive/offensive)
- The required confidence caveat on each reading
- Integration into a real `ClaimsAgent` class (this is currently a
  standalone module + test scripts, not yet wired into the agent
  architecture)
- The Lineage Agent's citation-tracing logic (not started)

## Setup

Requires a BigQuery project in Sandbox mode (no billing account needed
for this usage level — queries are narrow, single-patent lookups, well
under the 1 TB/month free tier).

```bash
pip install google-cloud-bigquery
gcloud auth application-default login
gcloud config set project <your-sandbox-project-id>
```

## Files

- `claims_parser.py` — the real split/classify logic
- `test_connection.py` — verifies BigQuery access end-to-end
- `test_real_parse.py` — pulls and parses one real patent's full claims text
- `test_multi_dependent.py` — stress test against 3 more real patents,
  flags possible multi-dependencies for manual review
