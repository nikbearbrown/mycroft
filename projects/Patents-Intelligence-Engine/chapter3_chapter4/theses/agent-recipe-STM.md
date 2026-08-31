# Agent Recipe: STM

**Job:** gather and compute only. This recipe must STOP before any interpretation, conclusion, or decision.

## Inputs
- STM official Q2 2026 earnings press release (source-of-truth, per `sources-of-truth.md`) — already retrieved, used in `theses/STM.md`
- STM Q2 2026 earnings call transcript, July 23, 2026, Geneva (source-of-truth) — already retrieved
- STM official Q3 2026 earnings press release — **not yet released**, expected ~Sept 26, 2026
- NXPI and ASML close price, specifically July 23, 2026 — **no source-of-truth provider named yet** (see `evidence/NXPI-ASML-july23-price-action.md`)

No options-chain inputs — no options thesis exists for STM on this desk yet.

## Steps (deterministic)
1. Pull STM's reported non-GAAP gross margin figure from the Q3 2026 press release once available.
2. Compare that figure against the two fixed thresholds set in `CANNOT-KNOW.md`: ≥37% (weakens thesis) vs. <35% (confirms thesis).
3. Pull NXPI and ASML closing prices for July 23, 2026 specifically, from a named source-of-truth provider (not yet selected).
4. Compute % change for NXPI and ASML on that date; compare against STM's reported -13% premarket move the same day.
5. Do not compute any options metric (no term structure, no put/call ratio) — out of scope; no options thesis exists.

## Output schema
A valid run must produce:
- `q3_gross_margin_pct` (float, populated only once the Q3 release exists)
- `q3_margin_signal` (enum: "weakens" / "confirms" / "inconclusive" — mechanically derived from step 2's threshold comparison, not interpreted)
- `nxpi_july23_pct_change` (float)
- `asml_july23_pct_change` (float)
- `sector_comparison_signal` (enum: "STM-specific" / "sector-wide" / "inconclusive" — mechanically derived by comparing STM's -13% to NXPI/ASML's same-day moves, not interpreted)

## Stop conditions
- STOP if the Q3 press release has not yet been published (current state, as of this writing).
- STOP if no source-of-truth price provider has been named for NXPI/ASML data.
- STOP if any retrieved figure cannot be tied to a specific, named source document.
- STOP — do not proceed to any statement about whether the thesis is "confirmed," "weakened," or whether STM is a buy/hold/sell. That is the human card's job, not this recipe's.

## STOP — hand to human

This recipe, as of today, cannot run to completion: the Q3 release doesn't exist yet, and no price-data provider has been chosen. Current status: **all steps pending real-world events and one human decision (choosing a price provider).**
