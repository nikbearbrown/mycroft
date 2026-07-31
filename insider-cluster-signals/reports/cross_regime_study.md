# Cross-Regime Study — Corporate Insiders (Form 4) vs Congress (STOCK Act)

Generated 2026-07-24T17:11:23Z by `cross_regime.py`. Research only — no investment advice.

Two cluster-buy detectors built on the same core methodology (>=2 distinct buyers,
same ticker, 30-day window, 30-day SPY-adjusted alpha) applied to two disclosure
regimes. Sources: this module's `data/verified/scored_signals.json` and the
congressional-signals module's cluster output imported from upstream PR #3
(`data/raw/congressional-import/` — provenance + sha256 in PROVENANCE.md; the import
is that contributor's claim, shape-validated here, **not independently verified**).

## The two regimes

| | Corporate insiders (this module) | Congress (PR #3 module) |
|---|---|---|
| Disclosure law | SEC Form 4, 17 CFR 240.16a | STOCK Act |
| Filing deadline | **2 business days** after trade | **<= 45 days** after trade |
| Alpha anchor | **transaction date** | **disclosure date** |
| Alpha window | 30 calendar days vs SPY | 30 calendar days vs SPY |
| Tier rule | trade-time info only (size, roles, value); **alpha never classifies** | `cluster_size >= 2 AND avg_alpha > 1% AND score >= 1.5` -> STRONG |

## Populations compared

| Metric | Corporate (ours) | Congressional (imported) |
|---|---|---|
| Clusters | 6 | 425 |
| Corpus | 1 trading day (2026-03-02) + samples | multi-year scrape (2023–2026) |
| Mean cluster size | 3 | 2.24 |
| Max cluster size | 4 | 5 |
| Mean 30d alpha | 10.25% (n=6) | 0.38% (n=369) |
| Median 30d alpha | 14.73% | -0.51% |
| Clusters with positive alpha | 66.7% | 48.0% |

## Findings

1. **The tier definitions are not comparable — and that is the headline.** The
   congressional scorer uses realized alpha to classify (`avg_alpha > 1%` is a STRONG
   condition). Selecting signals on their outcome guarantees flattering tier statistics
   (look-ahead bias): a congressional STRONG has positive alpha *by construction*. This
   module classifies from trade-time information only and reports alpha as the
   scoreboard — which is why it can (and does) show negative-alpha STRONG clusters
   (LRMR -5.43). Any cross-regime claim that compares tier hit-rates directly would be
   methodologically void; population-level alpha (above) is the only fair comparison.
2. **Disclosure freshness differs by design.** A Form 4 cluster is knowable within ~2
   business days of the trades; a STOCK Act cluster can surface up to 45 days later,
   and its alpha is anchored at disclosure. The two alphas therefore measure different
   questions: 'what happened after insiders traded' vs 'what happened after the public
   could know'. Neither is wrong; they are not the same number.
3. **Population alpha is directionally consistent** across both regimes on the data
   available (means above), with the corporate sample far too small (see limitations)
   to claim anything stronger than 'not inconsistent'.

## Limitations (read before citing any number)

- Corporate corpus is **one complete trading day** (6 clusters with
  matured alpha) — illustrative, not statistical. A tier-level backtest is deferred
  until the corpus grows (remaining 9 gated days, future sprint).
- The congressional numbers are reproduced from an **unmerged, un-gated PR** — their
  pipeline's own audits/attestation have not been performed. Shape-validated only.
- Sector composition differs (their corpus concentrates in semiconductor/AI clusters).
- No transaction costs, no sector adjustment, 30-day window only, single benchmark (SPY).

## Provenance

corporate numbers -> `data/verified/scored_signals.json` -> cluster/enrichment chain ->
EDGAR accessions (SHA-256 manifests). congressional numbers ->
`data/raw/congressional-import/cluster_signals.json` (sha256 + source commit in
`PROVENANCE.md`) -> upstream PR #3.
