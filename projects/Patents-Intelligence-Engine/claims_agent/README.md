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
  `test_connection.py`, `test_real_parse.py`, `test_multi_dependent.py`,
  `test_broader_domains.py`, `test_lineage_agent.py`, and
  `test_lineage_broader.py` for the specific publication numbers
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
reading at all. Tested against 3 more real patents spanning mechanical,
robotics, and minimally-invasive-surgery domains — zero refusals on
that batch, so the refusal case is real but not yet common in the
patents tried so far.

## A real parsing gap found and fixed

Broader-domain testing (`test_broader_domains.py`) found a real bug:
`US-12551228-B2` uses `"1 ."` (a space before the period) for claim
numbering instead of the `"1."` format seen in every patent tested up
to that point. The original regex required the period immediately
after the digits, so it silently returned 0 claims for a patent that
genuinely had 14. Fixed by allowing optional whitespace between the
number and the period — verified against both formats before and
after the fix (see `inspect_parse_failure.py` for the investigation).

**Open question, not yet explained**: every independent claim
classified so far across the 3 broader-domain patents came back
"narrow/defensive" — six claims in a row with no "broad" or
"offensive" reading. This could reflect how those particular patents
are actually drafted, or it could be a real bias in the classifier
toward "narrow/defensive" as a safer-sounding default. Worth watching
as more patents are tested, not yet concluded either way.

## Lineage Agent — backward citations

`lineage_agent.py` traces a patent's citation lineage. It currently
covers **backward citations only** — what a patent cites — since
that's a direct field (`citation`, a `REPEATED RECORD`) on the same
row already being queried for claims text, genuinely cheap with no
separate lookup needed.

**Forward citations (who cites this patent) are not implemented.**
That would require searching for a patent's publication number inside
*other* patents' `citation` arrays — a different, likely much more
expensive query pattern that hasn't been tested for real cost on this
table, and is deliberately deferred.

A real bug was found and fixed while building this: BigQuery returns
**empty strings, not `None`**, for missing fields in this table's
`citation` records. The original `is_non_patent_literature` check used
`npl_text is not None`, which is always true here since the field is
never actually `None` — only ever a real string or `''`. Fixed to
check for genuinely non-empty text instead. Verified against real
data (`US-10822628-B2`, 12 real citations: 1 real patent citation, 11
real academic-paper citations, confirmed by hand against the raw
`npl_text` values).

**Broadened to 2 more real patents** (`test_lineage_broader.py`),
chosen for a genuinely different citation profile than the original:
`US-11983488-B1` (OpenAI) came back with 20 citations, 18 of them real
patents — the inverse of the original NPL-heavy patent — including
real non-US publication numbers (`CN-103154936-A`, `WO-2022015730-A1`),
confirming the parser handles international formats correctly without
having been specifically designed to. `US-2024160902-A1` (Shopify)
came back with just 3 citations, the smallest count tested so far.
A genuine zero-citation patent was not found and tested — this remains
untried.

Also observed but not yet acted on: the `category` field sometimes
contains comma-separated values (e.g. `"APP,APP"`, `"SEA,SEA"`) rather
than a single code — worth understanding before using `category` for
anything downstream.

## What's tested, and how confident to be in each part

| Component | Tested against | Confidence |
|---|---|---|
| `claims_parser.py` split/classify | 7 real patents, 82 claims total, verified by hand | High — every claim correct, including a real formatting-variant fix |
| `flag_multi_dependency` | Original 4 patents; one confirmed false-positive found and fixed | High, after the fix |
| `claim_classifier.py` scope reading | 8 real independent claims across 4 patents, 4 domains (semiconductor, mechanical, robotics, medical device) | Moderate — every result was well-reasoned with specific, checkable caveats, but the "always narrow/defensive" pattern is an open question |
| `lineage_agent.py` backward citations | 3 real patents, citation counts from 3 to 20, including 2 non-US formats, verified by hand | Moderate-high — the field-access pattern, the empty-string fix, and international format handling are all confirmed correct across a real range; a genuine zero-citation case is still untested |

## Files

- `claims_parser.py` — split/classify logic, tested, handles two known claim-numbering formats
- `claim_classifier.py` — Claude-based protection-scope classification
- `claims_agent.py` — the real `ClaimsAgent` class wiring both together
- `lineage_agent.py` — the real `LineageAgent` class, backward citations only so far
- `test_connection.py` — verifies BigQuery access end-to-end
- `test_real_parse.py` — pulls and parses one real patent's full claims text
- `test_multi_dependent.py` — stress test against 3 more real patents, exact-match queries only
- `test_broader_domains.py` — broader domain test (mechanical, robotics, medical device) that found the claim-numbering format bug
- `inspect_parse_failure.py` — the investigation that found the real cause of the format bug
- `inspect_independent_claims.py` — structural stats (word count, limitation markers) across known independent claims — the real evidence that these don't cleanly predict scope, which is why classification uses an LLM call rather than a heuristic
- `test_classifier_first_run.py` — first real test of the classifier alone
- `test_claims_agent.py` — real end-to-end test of the full `ClaimsAgent` class
- `test_lineage_agent.py` — first real test of `LineageAgent`, including the field-access verification that found the empty-string bug
- `inspect_all_citations.py` — the investigation that confirmed the empty-string fix was correct, not just coincidentally unchanged
- `test_lineage_broader.py` — broadened `LineageAgent` testing to 2 more real patents with different citation profiles and international formats

## Not built yet

- Wiring `ClaimsAgent` and `LineageAgent` into whatever will actually call them in production (a CLI, a batch job, etc. — currently they're classes with test scripts, not a deployed service)
- Forward citations in the Lineage Agent (who cites this patent) — deliberately deferred, real query cost untested
- Explaining the "always narrow/defensive" pattern in classifier results — more real patents needed before concluding whether it's a real signal or a classifier bias
- A genuine zero-citation patent — not yet found and tested, so `LineageAgent`'s behavior on an empty citation list is unverified
