# Substack drafts — SEC Filings Financial Metrics Agent

Drafts for the Mycroft Project Substack. Written from actual, completed work on
the agent (not speculation). Edit to taste, then publish from your own Substack
account.

## Ready to publish (based on completed work)
1. **[Trust Before Intelligence](01-trust-before-intelligence.md)** — the thesis and
   architecture decision: deterministic-first, no LLM in the critical path,
   provenance on every value. _(Sprint 1)_
2. **[One Number, Many Names](02-one-number-many-names.md)** — the XBRL
   concept-normalization problem (Net Sales vs Revenue from Contracts with
   Customers vs custom extensions) and how the mapping is made auditable. _(Day-1 build)_
3. **[PASS, FAIL, or UNKNOWN](03-pass-fail-unknown.md)** — validation as a
   first-class citizen; why the system is allowed to admit it doesn't know. _(validation)_

## Planned (write once the work is done — keep it honest)
- **Deriving the Ratios You Can Defend** — margins/ROE/ROA/current ratio/D-E with
  provenance footnotes. _(after Day-2)_
- **Benchmarking Against the Filing Itself** — hand-verified ground truth, extraction
  accuracy & coverage, and what the mismatches taught me. _(after Week-2 benchmark)_
- **A Catalog of Things That Break** — custom extensions, restatements, fiscal-year
  quirks; documenting failure as evidence. _(after LIMITATIONS.md)_
