# Watchlist governance & versioning (Week 11)

The watchlist is the universe against which cross-entity log normalization occurs,
so it is a **design decision, not just configuration**. Selection favors a
material public Hacker News profile and a public ticker; a few private comparables
(Anthropic, Mistral) are included for context and marked non-investable
(`ticker: null`).

- **Source of truth today:** the `WatchList` code node. `config/watchlist.v1.json`
  is the externalized mirror; keep the two in sync until the node is wired to read
  the file.
- **Owner:** a single maintainer; changes are reviewed in the PR that introduces
  each version.

## Version boundaries are clean breaks

The list is held static within a version and versioned (v1, v2, …). Additions or
removals occur **only at a version boundary**, where the normalization baseline is
treated as discontinuous — so a viral entity added mid-series cannot silently
reset every other entity's baseline.

### Version guard — current mechanism (structurally closed)

Cross-version comparison is prevented in the live pipeline:

- The snapshot table carries a `watchlist_version` column.
- `Build Run Row` stamps each run with its version, and the insert persists it.
- `Get Previous Run` filters on `watchlist_version = 'v1'` and takes the most
  recent **complete** row — so velocity/normalization never baseline a new
  version against pre-change history.

Mechanism is a version column + version-filtered lookup (not a sentinel row).

### Open residual

The active version is a **fixed literal** in two places — the writer
(`Build Run Row`, `"watchlist_version": "v1"`) and the reader (`Get Previous Run`,
`WHERE watchlist_version = 'v1'`). They are not yet fed from a shared dynamic
value, so a version bump must update **both in lockstep**. If only one changes,
the reader filters on the old version while new rows carry the new one, and
velocity silently reverts to cold-start for every entity.

## v2 expansion protocol (Week 11 deliverable — a human gate, P4)

Expanding to watchlist v2 is a governance gate cleared by the named owner and
logged, not an automatic step. When approved:

1. Add/remove entities in a new `config/watchlist.v2.json` with `"version": "v2"`.
2. Update the writer (`Build Run Row`) to stamp `"v2"` **and** the reader
   (`Get Previous Run`) filter to `'v2'` — in the same change.
3. Expect every entity to `cold_start` on the first v2 run (velocity = 0); this is
   correct — the baseline is intentionally discontinuous across the break.
4. Re-run a full pipeline and verify scores, velocity (cold-start), and the JSON
   signal's top-level `watchlist_version` all read `v2`.

**Status:** v2 is **not** activated in this pass. It requires the owner's approval
and the lockstep writer/reader edit above (a canvas change to the two nodes). The
config file and protocol are staged; the gate is open pending a logged decision.
