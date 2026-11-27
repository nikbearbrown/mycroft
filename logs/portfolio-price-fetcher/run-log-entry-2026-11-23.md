# Run-log entry, 2026-11-23: Portfolio Price Fetcher, step 2 (sample mode)

Written as its own file because this change does not edit any existing file, including `logs/RUN_LOG.md`. A maintainer may paste it there.

- **Recipe:** `recipes/portfolio-price-fetcher.md` (status DRAFT, unchanged).
- **Added:** the step 2 script, a self-test, step-2 outputs for six fixture sets (clean, defective, quality-duplicate, quality-missing, quality-move, quality-far), one source check, this change's README and results.
- **Inputs:** the invented sample corpus under `data/raw/portfolio-price-fetcher/sample/` with its two frozen manifests; the run envelope (`as_of` 2026-10-10, sample mode, live calls not approved); the workflow the recipe declares.
- **Result:** clean set 5 ingested, 0 rejected, exit 0; defective set 4 ingested, 1 rejected (not JSON), exit 1; the quality sets ingest in full; self-test 28 of 28 as expected (includes break tests); outputs byte-identical on rerun; the same files as step 3 reads in every set; `node scripts/conformance.mjs` passes on the new paths.
- **Open:** recipe text and status fields not edited (see `README-step-2.md`); no gate cleared, no live call made, no approval record.
