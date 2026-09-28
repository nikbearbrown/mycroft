# Authoring the reference docs

The reference site in `docs/reference/` is built by `scripts/build_docs.py` from the
Markdown sources in this folder. The written parts come from here. The inventory under every
file entry (functions, classes, exports, imports, imported-by, line counts), the HTTP route
table, the environment-variable table and the Honest Ledger page are generated from the
source each build, so they can't drift.

`tests/test_docs_coverage.py` fails when a tracked file has no entry, when an entry names a
file that doesn't exist, when a `[[link]]` doesn't resolve, or when the site doesn't build.

## Layout

```
docs/reference/
  src/
    AUTHORING.md        this file
    pages/*.md          narrative pages (overview, architecture, features, decisions, ...)
    files/*.md          one page per layer/folder, one entry per file
  *.html, assets/       built output (committed, so the site opens from disk)
```

## Front matter

Every source file starts with a front-matter block of `key: value` lines:

```
---
title: Core
slug: files-core
section: Files
order: 30
summary: One sentence shown in the sidebar tooltip and on the index.
---
```

- `slug` is the output file name (`files-core` → `files-core.html`). It must be unique.
- `section` groups pages in the sidebar. The sections are: `Start`, `Architecture`,
  `Features`, `Reference`, `Files`, `History`.
- `order` sorts pages within a section (lower first).

## File entries (pages in `files/`)

After the front matter, write an introduction to the layer or folder: what it is for, its
dependency rule, and how its files fit together. Then write one entry per file, using a level-2
heading holding the path relative to `verification-layer/`, in backticks:

```
## `core/parsing.py`

**Role:** structural parsing of an agent's reply into its thought log and conclusion.

What it does and how, in prose. Explain behaviour, edge cases and the reasons for them.

### Key functions
- `_parse_response(raw, *, allow_assessment=False)`: what it accepts, what it rejects, why.

### Design notes
Why it is built this way, citing the record (see "Accuracy" below).

### Limits and open issues
Known gaps, with Honest Ledger ids where one exists (`checks-lexical-coverage`).

Related: [[core/schemas.py]], [[pipeline/middleware.py]]
```

- The `**Role:**` line is required. The other subsections are optional; use the ones the file
  needs, with these names so pages read alike.
- Don't list every function signature by hand. The generated inventory does that. Explain the
  ones a reader needs to understand, and why they behave as they do.
- **Grouped entries.** A heading may hold a glob instead of a path, for files documented as a
  group (fixtures, archived files): ``## `tests/fixtures/*` ``. Use a table with one row per
  file (file, origin, date captured, what uses it). `*` matches within a folder; `**` matches
  across folders.
- Each tracked file must match exactly one entry across all pages.

## Links

- `[[core/parsing.py]]` links to that file's entry wherever it lives. `[[core/parsing.py|the
  parser]]` sets the link text.
- `[text](architecture.html)` or `[text](architecture.html#layers)` links to a page or a
  heading. Heading anchors are the heading text, lowercased, with runs of anything other than
  `a-z0-9` replaced by `-`.
- Ledger ids in backticks are plain text; to link one, use `[id](ledger.html#id)`.

## Markdown supported

Headings `#` to `####`, paragraphs, `-` and `1.` lists (nest by indenting two spaces), fenced
code blocks, pipe tables, `>` blockquotes (rendered as a callout), `**bold**`, `*italic*`,
`` `code` `` and links. Raw HTML passes through, but prefer Markdown.

## Accuracy

The house rules (SNICKERDOODLE.md) apply to documentation as much as to code:

- **Describe only what the code does.** Read the file before writing its entry. When the code
  and another doc disagree, the code wins, and the disagreement goes in the entry's "Limits and
  open issues" as a finding.
- **Never invent a count, rate, date or confidence.** A number in these docs comes from a record
  (a RUN_LOG entry, a test, the database), and the text says which. Test counts, file sizes and
  line counts are generated; don't write them by hand.
- **Say built vs observed.** "Tested with scripted agents" and "seen on a live model" are
  different facts. Say which is true.
- **Cite design decisions.** A reason is either in the code (a comment or docstring: cite the
  file), or in the record (cite `logs/RUN_LOG.md` by entry date and title, or
  `docs/SYSTEM_DESIGN.md` by section). A reason that is neither is labelled
  `(judgment, not recorded)`.
- **Never** quote `.env` or any key, and don't read `scripts/mycroft-main/`, `docs/mycroft-main/`
  or `data/mycroft-main/`.

## Style

Follows `brutalist/DESIGN.md`: sentence case, no emoji, no exclamation marks. Plain words; a
term of art gets a short explanation or a glossary link the first time it appears on a page.
