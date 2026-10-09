# n8n catalogue entry — Private AI Valuations quarterly digest

> **On the path.** `plan.md` says "add the catalogue entry to `n8n_Workflows/README.md`". No
> `n8n_Workflows/` directory exists in this repository — the path refers to a sibling
> Humanitarians AI repo. The entry is written here, beside the workflow it describes, so it
> travels with the thing it documents. Copy the table row below into that repo's catalogue when
> the two are in the same place.

## Catalogue row

| Workflow | Trigger | What it does | Credentials | Source |
|---|---|---|---|---|
| **Private AI Valuations — quarterly digest** | Cron `0 7 20 2,5,8,11 *` | Runs the quarterly analysis graph, gates on the signal's `schema_version`, emails the human note with the machine signal attached | SMTP, by reference from the n8n store | `data/raw/Private_AI_Valuation_Agent/n8n/quarterly_digest.json` |

## Import

1. **Import** `quarterly_digest.json` into n8n.
2. **Set the workflow variables:**
   - `PROJECT_DIR` — absolute path to the project root
   - `DIGEST_FROM`, `DIGEST_TO` — the digest's sender and recipients
3. **Pick an SMTP credential.** The file names one by id and carries no secret, so a fresh n8n
   will ask you to choose. That is intended.
4. **Activate.**

## What it does, node by node

```
Quarterly trigger ─► Run quarterly graph ─┬─► Read signal ─► Parse ─► schema 1.0? ─┬─► Send digest
                                          └─► Read note ───────────────────────────┘   └─► Halt
```

- **Thin on purpose.** Every decision lives in the Python. The workflow schedules it, reads two
  files and sends one email. `plan.md` scopes n8n as "optional, thin" and this is what that
  means in practice.
- **It halts rather than emailing on an unknown `schema_version`.** A contract change is not a
  digest to send — it is something a human should see first.
- **A non-zero exit from the graph writes nothing.** The signal is validated before it reaches
  disk, so a failed run leaves the previous artifacts intact.

## The schedule is the 20th, not the quarter end

Running on 31 March would produce a digest about December. Verified lag is ~55–60 days from a
fund's fiscal period end to its filing, and the DERA bulk sets lag those again. So the trigger
is **07:00 on the 20th of February, May, August and November** — about seven weeks after each
calendar quarter end, which is the earliest point at which the quarter being reported on has
filings in it.

A scheduler that fires on the obvious date and reports the wrong quarter looks like working
software, which is worse than one that does not run.

## You do not need n8n

`scripts/schedule.py` does the same job with nothing installed:

```bash
python -m scripts.schedule --show      # print the platform-native command
python -m scripts.schedule --install   # register it (asks first)
python -m scripts.schedule --run-now   # run the quarterly job once
```

A test asserts that `scripts/schedule.py` and `quarterly_digest.json` carry the **same** cron
expression, so the two cannot drift apart.

## Credentials

The workflow file contains no password, no API key and no `DATABASE_URL`. The SMTP credential
is referenced by id from the n8n store; database access comes from the project's own `.env`,
read by the Python the Execute Command node invokes. A test asserts this against the node
parameters rather than the file text — the file's own notes contain the sentence "this file
carries no password", and a naive string scan fails on its own documentation.
