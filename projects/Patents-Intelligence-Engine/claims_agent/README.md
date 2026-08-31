# Claims Agent — Patents Intelligence Engine

Reads a patent's claims text and produces two things: a structural
reading (which claims are independent, which depend on which, cheap
and reliable), and a protection-scope reading for each independent
claim (broad/narrow, defensive/offensive/exploratory — judgment-based,
uses the Claude API).

## How the data is fetched

Claims text comes from Google's public patent dataset on BigQuery:
`patents-public-data.patents.publications`, specifically the
`claims_localized` array field.

Setup:

```bash
pip install google-cloud-bigquery
gcloud auth application-default login
gcloud config set project <your-project-id>
```

Create a BigQuery project and link a real billing account. The first
1 TiB of query processing per month is free, but **be aware of the
real cost past that**: this specific table has no clustering or
partitioning on `publication_number`, so a lookup for even a single
patent scans the relevant columns across the entire ~98 million row
table — about 116 GB per new lookup in practice, which is roughly
$0.71 at the standard $6.25/TiB on-demand rate.

Two things that make this manageable:
- **Always query by exact `publication_number` match**, using a
  parameterized query (`WHERE publication_number = @pub_number`) —
  never `LIKE`. In practice both cost the same on this table (no
  index either way), but exact match is still safer and clearer.
- **BigQuery caches identical query results.** Re-running the exact
  same query against the same patent is free. All of our test scripts
  reuse the same known set of patents for this reason — check
  `test_connection.py`, `test_real_parse.py`, and
  `test_multi_dependent.py` for the specific publication numbers
  already paid for and cached.

A smaller, cheaper-looking table
(`patents-public-data.uspto_oce_claims.patent_claims_fulltext`, ~29 GB
total) was checked and rejected — it was last updated in 2017 and
doesn't cover any patents granted after that.

## How the Claude API is set up

Protection-scope classification uses the Claude API directly (not
BigQuery's built-in AI functions), since the classification logic
needed to be testable and iterable outside of SQL.

```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key-here"
```

Get a key at `console.anthropic.com` → Settings → API Keys. New
accounts get $5 in trial credit, which comfortably covers this
project's usage — each claim classification call is roughly 700-800
input tokens and under 200 output tokens, a small fraction of a cent
at Claude Sonnet 5's per-token rate.

**A real limitation to know about**: the model will refuse to classify
claims whose subject matter touches certain sensitive categories (we
hit this on a real patent about plant cell cultures producing a
pharmaceutical compound — `stop_reason` came back as `"refusal"`,
category `"bio"`). `claim_classifier.py` handles this by returning an
`"unclear"` classification with an explicit note in the confidence
caveat, rather than crashing — but it means some real patents,
especially in biotech and pharma, won't get an automated scope
reading at all.

## What's tested, and how confident to be in each part

| Component | Tested against | Confidence |
|---|---|---|
| `claims_parser.py` split/classify | 4 real patents, 64 claims, verified by hand | High — every claim correct |
| `flag_multi_dependency` | Same 4 patents; one confirmed false-positive found and fixed | High, after the fix |
| `claim_classifier.py` scope reading | 2 real independent claims so far | Moderate — both results were genuinely well-reasoned with specific, checkable caveats, but this is a small sample |

## Files

- `claims_parser.py` — split/classify logic, tested
- `claim_classifier.py` — Claude-based protection-scope classification
- `claims_agent.py` — the real `ClaimsAgent` class wiring both together
- `test_connection.py` — verifies BigQuery access end-to-end
- `test_real_parse.py` — pulls and parses one real patent's full claims text
- `test_multi_dependent.py` — stress test against 3 more real patents, exact-match queries only
- `inspect_independent_claims.py` — structural stats (word count, limitation markers) across known independent claims — the real evidence that these don't cleanly predict scope, which is why classification uses an LLM call rather than a heuristic
- `test_classifier_first_run.py` — first real test of the classifier alone
- `test_claims_agent.py` — real end-to-end test of the full `ClaimsAgent` class

## Not built yet

- Wiring `ClaimsAgent` into whatever will actually call it in production (a CLI, a batch job, etc. — currently it's a class with test scripts, not a deployed service)
- The Lineage Agent's citation-tracing logic (not started)
- Broader testing of the classifier across more independent claims and patent domains, especially to understand how often the biotech/pharma refusal case actually comes up in real usage
