---
title: Honest Ledger
slug: ledger
section: Reference
order: 50
summary: Every known issue the system records about itself, generated from web/self_report.py on each build.
---

This page is generated from `KNOWN_ISSUES` in [[web/self_report.py]], the same list the server
serves at `GET /api/self-report` and the review app shows. Entries are never deleted: a fixed
issue is marked `RESOLVED`, with how and when, in its detail. How the ledger works is described
in [Self-checks and the Honest Ledger](f-ledger.html).

{{ledger}}
