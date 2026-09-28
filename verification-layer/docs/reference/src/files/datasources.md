---
title: Data sources
slug: files-datasources
section: Files
order: 50
summary: The SEC EDGAR clients: period-aware fact selection from companyfacts, and locating a figure in its filing's inline XBRL.
---

`datasources/` is the ingest layer: the code that reads SEC EDGAR. Every figure an agent is given in
a ticker run comes from here, and so does the filing excerpt a reviewer opens to see where a figure
sits. Under the constitution's P2 (only ingest code touches the network), this package and
`adapters/` (the model and its search tool) are the network egress points, with one named exception,
[[validation/verification.py]], which fetches the source a citation points to.
`tests/test_layering.py` (`test_datasources_is_the_only_package_that_opens_a_socket`) fails if
`urllib.request` or `requests` appears anywhere else in `core/`, `pipeline/`, `producers/`,
`validation/` or `web/`.

**Dependency rule.** `datasources/` may import only from `core/` (`tests/test_layering.py`). It
needs the `core.contracts.JsonFetcher` contract and nothing more.

**How the files fit together.**

- [[datasources/edgar.py]] resolves a ticker to a CIK (SEC's company identifier), fetches the
  companyfacts JSON (every XBRL fact a company has filed), and selects, for each concept, the most
  recent value of the right period kind as a `Fact` carrying its period, unit, form and accession
  number.
- [[datasources/filings.py]] takes such a `Fact` and finds it in the filing document itself, using
  inline XBRL, to return the table row or paragraph the number sits in. It reuses `edgar.py`'s tag
  fallbacks and default user agent.
- [[datasources/__init__.py]] is empty.

Both clients use stdlib `urllib` only, send the `SEC_USER_AGENT` environment variable as the
User-Agent (SEC's fair-access policy asks for a real contact), and accept an injected fetcher so
that the test suite never touches the network.

## `datasources/__init__.py`

**Role:** empty package marker.

The file has no content. Callers import the modules directly (`datasources.edgar`,
`datasources.filings`).

## `datasources/edgar.py`

**Role:** the SEC EDGAR companyfacts client: ticker to CIK, the companyfacts fetch, and period- and
unit-aware selection of each concept's current value.

### Fetching

- `http_get_json(url)` is the default `JsonFetcher`. It sends a GET with the User-Agent from
  `SEC_USER_AGENT`, or the placeholder `_DEFAULT_USER_AGENT` when unset, a 10 s timeout
  (`_TIMEOUT_S`), and reads at most `_MAX_BYTES` (10,000,000) bytes; the comment notes that a
  large company's companyfacts JSON can exceed 4 MB. A network error, a timeout or an HTTP error
  status (urllib raises `HTTPError`, a subclass of `URLError`) raises `EdgarFetchError`, and so does a body that is not
  valid JSON.
- `lookup_cik(ticker, fetch_fn=None)` reads `https://www.sec.gov/files/company_tickers.json`,
  matches the ticker case-insensitively after trimming, and returns the CIK zero-padded to ten
  digits. An unknown ticker raises `EdgarFetchError`.
- `fetch_company_facts(ticker, cik, fetch_fn=None)` fetches
  `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` and returns the whole payload. One call
  serves every lens: each producer reads a different slice of the same payload rather than fetching
  its own (docstring).

Both lookups are decorated with LangFuse's `@observe(as_type="tool")`, so each appears as a tool
span in a trace. The decorators come from the one deliberate non-stdlib dependency and are no-ops
when LangFuse is not configured (module docstring).

### Fact selection

`select_fact(facts, concept, *, basis="auto")` returns the most recent value of `concept` as a
`Fact`, or `None`. It replaced a rule that took the entry with the latest `end` date across all
entries and returned a bare number. Against Apple's real payload, fetched 2026-09-24, that rule
handed agents FY2018 revenue as current (Apple stopped using the `us-gaap:Revenues` tag after FY2018)
and a nine-month year-to-date diluted EPS as the quarter, because a 10-Q tags both durations with the
same `end` date (comment above the section; `logs/RUN_LOG.md`, 2026-09-24, "B0: period- and
unit-aware facts; a retired revenue tag; tool errors recorded as "ok""). `tests/test_edgar_facts.py`
pins both the old rule's wrong picks and the fix, against a fixture trimmed from that live payload.

How it chooses:

1. **Candidate tags.** `CONCEPT_TAGS` lists fallbacks for a concept. Only `Revenues` has any:
   `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax` (the ASC 606 tag), then
   `SalesRevenueNet`. Every candidate tag is read and the most recent period wins, so a retired tag
   cannot win on age. Any other concept is read under its own name only.
2. **Candidates.** Every entry, in every unit bucket, under the `us-gaap` taxonomy, with a numeric
   `val` and an `end` date. A payload without `facts.us-gaap` returns `None`.
3. **Period kind**, from `_period_kind`, by the actual duration between `start` and `end`: 80 to 100
   days is a `quarter` (a fiscal quarter is 13 weeks), 350 to 380 days is `annual` (52- or 53-week
   years), any other duration is `ytd` (year-to-date). An entry with no start date is an `instant`
   if it carries a `form` or `frame`, otherwise `unknown`; the comment explains that an entry with
   nothing but `end` and `val` (hand-built test fixtures) says nothing either way.
4. **Which kind.** With `basis="auto"`, the first kind present in the order instant, quarter, annual,
   unknown, ytd (`_AUTO_ORDER`). A stock concept such as `Assets` has only instants; a flow concept
   such as revenue or EPS gets its latest standalone quarter; a year-to-date figure is used only when
   nothing else exists, and is labelled so. An explicit `basis` of `instant`, `quarter` or `annual`
   returns `None` when the payload has none of that kind; it does not fall back.
5. **Which entry.** Among the chosen kind, the latest `end`, then the latest `filed` (so a restatement
   supersedes the original), then the earlier tag in `CONCEPT_TAGS`.

### The `Fact` record

`Fact` is a frozen dataclass: `concept` (what the lens asked for), `tag` (the tag the value came
from; they differ when a fallback tag was used), `value`, `unit`, `start`, `end`, `fy` and `fp` (the
filer's own fiscal labels: Apple's FY2026 Q3 ends in June), `form`, `frame` (SEC's calendar-aligned
period key, such as CY2026Q2), `accn` (accession number), `filed` and `period_kind`. Both the fiscal
labels and the frame are kept because an agent should cite the former and a comparator can key on
the latter (docstring).

- `period_label`: "as of END", "3 months ending END", "12 months ending END", "N months ending END
  (year-to-date)" (N is the day count divided by 30.44, rounded), or "period unknown".
- `describe()`: `value unit (FY2026 Q3, 3 months ending ..., 10-Q, frame CY2026Q2, tag ..., accn
  ...)`. The value stays first because [[producers/lens.py]]'s context format depends on it. The tag
  appears only when it differs from the concept.
- `to_dict()`: the fields plus `period_label` and `duration_days`, for the compare payload.

`latest_value(facts, concept)` is kept for callers that only need the number; its docstring advises
`select_fact` instead, because "a bare float is exactly how the period was lost".

### How other layers use it
- [[producers/lens.py]] calls `fetch_company_facts` in `run_lens` and `select_fact` for every concept
  a lens reads.
- [[web/server.py]] calls `lookup_cik` and `fetch_company_facts` once per ticker compare run (both
  producers use the one payload) and catches `EdgarFetchError`.
- [[datasources/filings.py]] imports `CONCEPT_TAGS` and `_DEFAULT_USER_AGENT`.

### Design notes
- The module was split out of the old `financial_grader.py`, which had been an HTTP client, a
  summariser and an orchestrator at once. The split removed a producer importing its sibling to
  reach shared code, and a copied latest-value helper that, if changed in one place only, would have
  made the two producers disagree about what "latest" means, and the comparator would have reported
  that as a contradiction between the agents (module docstring; `logs/RUN_LOG.md`, 2026-09-04,
  "SOLID restructure: layered packages, no loose root modules, three duplications removed").
- The fetch is injectable (`JsonFetcher`) so no test needs the network (module docstring;
  [[core/contracts.py]]).

### Limits and open issues
- A response larger than 10,000,000 bytes is cut off at that size and then fails to parse, so it is
  reported as "Non-JSON response" rather than as too large.
- There is no rate limiter and no cache here: `lookup_cik` downloads the full ticker map on every
  call. [[datasources/filings.py]] has both; this module has neither.
- `CONCEPT_TAGS` covers `Revenues` only. Any other concept whose filer changed tags would return the
  old tag's last value, labelled with its period.
- Quarterly figures only for flow concepts under `auto`. Not exercised, per the B0 entry: a filer
  whose 10-K has no standalone fourth-quarter figure (after the 10-K, the latest quarter is the third
  while the latest annual figure is newer), and 20-F or 40-F filers.
- Only the `us-gaap` taxonomy is read.
- [[validation/constraints.py]] keeps its own copy of the revenue fallbacks in `SOURCE_TAGS`
  (the layering rule does not let `validation/` import `datasources/`); the two lists must be kept
  in step by hand.
- `@observe` is imported from `langfuse` at module level, so the `langfuse` package must be installed
  for this module to import, even when tracing is not configured.
- Documentation disagreements: the module docstring calls this "the subsystem's only network
  egress", but [[datasources/filings.py]], the adapters and [[validation/verification.py]] also reach
  the network. `README.md` lists only `lookup_cik`, `fetch_company_facts` and `latest_value`, and
  does not mention `select_fact`, `Fact` or [[datasources/filings.py]].

Related: [[datasources/filings.py]], [[producers/lens.py]], [[core/contracts.py]],
[[tests/test_edgar_facts.py]], [[tests/test_financial_grader.py]]

## `datasources/filings.py`

**Role:** locates a companyfacts figure in its filing's primary document through inline XBRL, and
returns the table row (or paragraph) it sits in, so a reviewer can see the number in context.

companyfacts is numbers only: no text and no table. Since 2019 the primary 10-Q or 10-K document is
inline XBRL: ordinary HTML whose figures are wrapped in `ix:nonFraction` elements naming a us-gaap
tag, a `contextRef` and a `scale`, with each context defined once (its period and any dimension) in
an `xbrli:context`. A companyfacts `Fact` (concept, period, accession number) can therefore be
located exactly: the same tag, in a context with the same period and no dimension (module
docstring). It was built as roadmap phase BP (`logs/RUN_LOG.md`, 2026-09-25, "BP + U4: figures
located in the filing, and live compare runs in /app").

### Fetching and the cache

- `_get(url, limit=MAX_BYTES)` sends a GET with the same `SEC_USER_AGENT` (or `edgar.py`'s default)
  and `Accept-Encoding: gzip`, a 20 s timeout, and a per-process rate limit: a lock holds requests at
  least `_MIN_INTERVAL_S` (0.12 s) apart, which the comment puts at about 8 requests a second, under
  SEC's 10 a second. It reads at most `limit + 1` bytes, decompresses a gzip response, and raises
  `FilingFetchError` for a network error, a timeout, an `OSError`, or a body over the limit
  (`MAX_BYTES` is 25,000,000; the comment notes a large 10-K's primary document runs to about 10 MB).
- `primary_document(cik, accn, ...)` reads the company's submissions index,
  `https://data.sec.gov/submissions/CIK##########.json`, and returns the filing's primary document
  name, form, filing date, report date and inline-XBRL flag. It returns `None` when the accession is
  not in the index's `recent` list (the comment: older than the most recent filings, about 1,000).
  A found entry is cached as `ACCN.meta.json`, since a filing's entry never changes once filed, so
  only the first lookup per filing reads the large index. A `None` result is not cached.
- `load_document(cik, accn, name, ...)` returns the document text, from `ACCN.htm.gz` in the cache,
  or fetched from `https://www.sec.gov/Archives/edgar/data/CIK/ACCN-without-dashes/NAME` and then
  written there gzipped.
- The cache directory, `CACHE_DIR`, is `web/data/filing_cache/`. It is gitignored and can be
  regenerated by deleting it. Tests pass their own `cache_dir` and `fetch`.
- `filing_index_url(cik, accn)` is the filing's human-readable index page, which always exists, and
  is returned with every result so "Open filing" always works.

So one excerpt costs at most two SEC requests per filing (the index and the document), and none once
both are cached.

### The inline-XBRL parser

`_IxParser` is a single streaming pass with stdlib `html.parser` (no new dependency). It collects:

- **Contexts.** Each `xbrli:context`'s id, `start`, `end` or `instant`, and whether it has a
  `xbrli:segment` or `xbrli:scenario` (a dimension, meaning a breakdown such as a product line).
- **Facts.** Every `ix:nonFraction` whose tag, with its prefix removed, is one of the wanted tags,
  with its id, context, `scale`, `sign`, `format` and displayed text.
- **Where each fact sits.** Table structure is tracked row by row with `colspan`, so a column header
  can be matched to the value's column. Only the innermost table is tracked (the comment: filings
  do not nest financial tables). Outside a table, the enclosing `p` or `div` is tracked as a
  paragraph. A `br` becomes a space, so "As of" and "June 30" do not run together.

For a fact in a table (`_finish_table`):

- the **row label** is the row's first cell text that is not purely digits and punctuation;
- the **column header** joins the texts of cells above the value's column, from the rows before the
  first row containing a figure. Column 0 is skipped because it holds row labels and section titles
  such as "ASSETS:", never a column header. `_is_figure_cell` does not count a bare year or a date
  like "March 31," as a figure, so date rows stay in the header;
- the **excerpt** is the row's non-empty cell texts joined with ` | `, and the **highlight** marks
  the value's own cell, searched for only after the cells to its left, so an equal number elsewhere
  in the row is not marked instead.

For a fact in a paragraph (`_finish_para`), the excerpt is up to 240 characters either side of the
first place the displayed text appears in the paragraph, and the highlight marks that place.

`_number(displayed, fmt)` turns the filed text into a number: a dash means 0, a `zerodash` format
means 0, a `comma-decimal` format swaps the separators (European 1.234,5), otherwise commas are
dropped. The value is then multiplied by 10 to the `scale` and negated when `sign="-"`, giving an
`Occurrence` with both `displayed` ("94,930") and `value`.

### Finding a figure

- `find_in_document(html, concept, start, end)` returns every occurrence whose context matches the
  period with no dimension (`_period_matches`: `start` and `end` equal for a duration, `instant`
  equal to `end` for a point in time), statements before prose and otherwise in document order, plus
  the tag that matched first. The tags searched are `CONCEPT_TAGS` from [[datasources/edgar.py]], so
  the same revenue fallbacks apply.
- `find_excerpt(cik, accn, concept, start, end, *, fetch, cache_dir, max_occurrences=5)` is the entry
  point. It never raises for a missing or odd filing; it returns an `Excerpt` whose `status` says what
  happened, always with the filing's index URL and a message:

| Status | When |
|---|---|
| `found` | at least one consolidated occurrence for the period |
| `not_found` | the document has no such tag for the period without a dimension |
| `no_inline_xbrl` | the submissions index says the filing is not inline XBRL |
| `too_large` | the document exceeded `MAX_BYTES` |
| `fetch_failed` | any other fetch error, or an unreadable cached index entry |
| `not_in_index` | the accession is not in the company's recent-filings index |

`Excerpt` also carries the form, filing date, document URL, matched tag, the period as text, the
first `max_occurrences` occurrences with the total count (statements, notes and MD&A repeat a
figure), and `scale_words` ("thousands", "millions" or "billions" for scales 3, 6 and 9).
`to_dict()` adds `best`, the first occurrence.

### How other layers use it
[[web/server.py]]'s `GET /api/facts/excerpt` calls `find_excerpt`. The route checks every parameter
against its exact format (CIK, accession number, concept name, dates) before it can reach a URL or a
cache file name. Nothing is fetched until a reviewer asks: the route is lazy (module docstring). The
review app calls it from `web/frontend/src/api/client.ts`, behind the source popover.

### Tests and live record
`tests/test_filings.py` runs against a real, trimmed Apple 10-Q (`aapl_10q_2026q3_trimmed.htm`,
accession 0000320193-26-000020) with an injected fetcher and a temporary cache. It checks the
quarterly revenue row and its column header, the other figures the agents were given, that the
highlight marks the value's own cell, that the nine-month figure and the product/service breakdown
are not taken for the quarterly consolidated figure, sign, scale and a figure in prose, that the
document is fetched once and then read from the cache, and every non-found status. The BP entry
records a live check: for the 24 figures four agents were given (AAPL, MSFT, NVDA, GOOGL), all 24
were found in the real filings, and every filed value equalled the companyfacts value. The same
entry lists the parser bugs found on real filings and fixed then: period contexts stored under raw
element names, a section title read as a column header, date rows taken for figure rows, and `br`
joined without a space.

### Limits and open issues
- `filing-excerpt-coverage` (OPEN): only recent inline-XBRL primary documents are covered. Filings
  older than the recent-filings index, figures that appear only in exhibits, and pre-2019 filings
  without inline XBRL are reported, not located. Row labels and column headers come from layout
  heuristics checked on four filers.
- In a paragraph, the highlight marks the first place the same characters appear, not necessarily
  the fact's own position. The parser records a `para_offset` for the fact but does not use it.
- The parser counts `ix:header` depth (`_hidden_depth`) but never consults it, so a matching fact
  inside the hidden header section would be collected as an occurrence outside any table, sorted
  after table occurrences. Whether any tested filing has one was not checked.
- The byte ceiling is applied to the bytes read before decompression and again to the result; a
  compressed response cut off at the ceiling would fail in `gzip.decompress` with `EOFError`, which
  is not caught and converted to `FilingFetchError`, so `find_excerpt` would raise instead of
  returning a status. This is read from the code; no test covers it.
- `not_in_index` results are not cached, so each request for such a filing reads the submissions
  index again.
- It imports `_DEFAULT_USER_AGENT`, a private name, from [[datasources/edgar.py]].

Related: [[datasources/edgar.py]], [[web/server.py]], [[tests/test_filings.py]]
