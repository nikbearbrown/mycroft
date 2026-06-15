## Mycroft

Mycroft is **both a book and an agentic Cowork system** — the manuscript explains the method; the repo gives agents and humans a verified way to operate it. It is built on the Snickerdoodle framework (`SNICKERDOODLE.md`), alongside sibling domains like Madison (branding & marketing intelligence) and the-reallocation-engine. Project-specific rules:

- Read `_MANIFEST.md` for the portable read-first map — what is canonical, task-relevant, generated, quarantined, or private (a thin index over `SNICKERDOODLE.md` / `DOMAIN.md`; machine-readable twin in `.ai/manifest.yaml`).
- Use lowercase `scripts/`; never create `SCRIPTS/`.
- Manuscript content lives in `chapters/` — no scripts or data there.
- `scripts/mycroft-main/`, `docs/mycroft-main/`, `data/mycroft-main/` are **quarantined Tier 3** — do not read, load, or treat as source unless explicitly asked for a named file inside them.

### `help` command

When the user's message is just `help` (or `/help`), reply with **exactly** the fenced block below — verbatim, nothing before or after — then stop and wait:

```
MYCROFT — verified agentic operations (a book + an operating system)
Turn work into verified, auditable recipes. The rule of the house:
fluency is the first sign of trouble — the human owns the irreducible judgment.

WHAT YOU CAN DO
  recipes    Read a real recipe + its conductor and run evidence (best first look):
             recipes/ (99 recipes)  +  conductor/  +  logs/
  book       The Mycroft manuscript: chapters/ (17 chapters + appendix)
  data       Two-layer: data/raw -> data/verified (nothing enters verified unvalidated)
  scripts    conformance · to-markdown · build-instructions · svg-to-png
  docs       architecture · phase-gates · workflows · data-and-provenance · labor-separation

HOW IT WORKS
  Every finding traces report -> log -> recipe -> source. Gates are hard stops a named
  human clears. Machines verify conformance; humans verify adequacy. (Constitution: SNICKERDOODLE.md)

TRY
  "show me a recipe and its conductor"   ·   "what's runnable today?"
  "explain the phase gates"              ·   "read the architecture doc"
```
