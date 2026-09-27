# Stub Data — Read This First

Every record in this folder is **invented**, for demonstrating the pipeline end-to-end.
Nothing here is real BlackRock data, real Preqin data, or a real portfolio.

- `stub_private_credit.json` — two fictional assets: "Example Industrial Holdings" (healthy)
  and "Riverside Distribution Partners" (deliberately distressed, used to exercise the
  guardrail's escalation path — see the design docs' dry-run trace #2).
- `stub_portfolio.json` — matching fictional portfolio positions for the same two funds.

Field names are illustrative too — see `src/adapters.py`'s module docstring for what to
change if you're mapping this to a real internal data source.
