# Returns vs. Benchmark — META, AAPL, SPY (paper portfolio)

Chapter 6 CLI exercise. Read-only against `book/positions.csv` and `benchmark/spy.csv`. No brokerage connection. No trade placed, modified, or suggested. Weights were assigned by the assistant at the human's request, since no real allocation was specified — they are illustrative, not a recommendation.

## Inputs

- `book/positions.csv` — entry date 2026-05-01 for all three positions, entry/current prices as supplied by the human, weights assigned (0.40 / 0.35 / 0.25, summing to 1.00).
- `benchmark/spy.csv` — SPY close on 2026-05-01 (721.25) and 2026-07-23 (738.18), same prices already used as the SPY position, since SPY is both a holding and the chosen benchmark here.

No row had a missing price or weight, so no halt condition was triggered.

## Ranked contribution table (largest absolute contribution first)

| Ticker | Weight | Entry price | Current price | Position return | Contribution to portfolio return |
|---|---|---|---|---|---|
| AAPL | 0.35 | 278.00 | 321.66 | +15.7050% | +5.4968% |
| SPY | 0.25 | 721.25 | 738.18 | +2.3473% | +0.5868% |
| META | 0.40 | 614.69 | 606.10 | −1.3975% | −0.5590% |

## Headline figures

- **Total portfolio return:** +5.5246%
- **Benchmark (SPY) return:** +2.3473%
- **Active return (portfolio − benchmark):** +3.1773%

## Verification step

Independently re-summed the three contribution figures: −0.5590% + 5.4968% + 0.5868% = 5.5246%, matching the total portfolio return above.

**PASS** — residual: 0.0000% (exact match to displayed precision; underlying floating-point residual is 0 to 10 decimal places).

## Notes

- SPY appears both as a 25%-weighted position and as the benchmark. Because the same entry/current prices are used for both, SPY's own contribution to active return is necessarily zero in isolation — the entire +3.1773% active return here comes from AAPL and META relative to their own weights, not from holding SPY itself.
- This is a paper portfolio built for the exercise, using human-supplied entry/current prices for a hypothetical 2026-05-01 purchase date. No real capital is committed, and this file does not constitute or imply investment advice, consistent with CLAUDE.md and CANNOT-KNOW.md for this desk.
- Weights were assigned by the assistant, not chosen by the human for any real strategic reason — if this becomes a real or ongoing paper book, replace them with weights you actually decide on.
