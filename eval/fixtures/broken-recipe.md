---
recipe: example
status: DRAFT
recipe_version: 0.1.0
todos_open: 0

# Example Recipe (intentionally broken fixture for eval task T4)

The YAML front-matter above is **unterminated** — it is missing its closing `---`
line, so `node scripts/conformance.mjs eval/fixtures` reports a malformed-front-matter
error. The T4 repair task is to add the closing `---` (and nothing else).

## Steps

1. Placeholder body content so the file looks like a real recipe.
2. A balanced code fence below proves only the front-matter is at fault.

```bash
echo "balanced fence — not the problem"
```
