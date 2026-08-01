# LLM Narrative Layer — Design & Model Decision (Week 7)

**Date:** 2026-07-16 · **Author:** Om Mali · **Reference implementation:** `llm_narrative.py`

This layer adds the **qualitative** signals on top of the deterministic Buzz Score:
a one-paragraph **narrative**, a **theme** tag, and a technical-community **reception
tone**. The score says *how much* attention an entity gets; this layer says *what the
attention is about* and *how it's being received*. Consistent with the Week 6 backtest
(`signal_validation.md`), buzz is framed as an **attention** signal, so "tone" is
technical-community reception — **not** a stock call.

---

## 1. The "free LLM" decision (plan.md's open Phase-2 question — now resolved)

The decision was made **empirically**, not from memory: I listed the models the project's
`GROQ_API_KEY` can actually reach (`GET /openai/v1/models`) and smoke-tested JSON mode.

| Question | Decision | Why |
|---|---|---|
| Provider / hosting | **Groq cloud API** (not local) | Free tier, zero infra, OpenAI-compatible endpoint. Matches the "single free source, simple flow" ethos. |
| Default model | **`llama-3.3-70b-versatile`** | Strongest **free** Llama on Groq today; better nuance on financial-adjacent titles than the 8B. Confirmed available + JSON-mode works with the project key. |
| Fast/cheap fallback | **`llama-3.1-8b-instant`** | Set `GROQ_MODEL=llama-3.1-8b-instant` to trade quality for speed/quota. This is the literal "Llama 3.1" the plan named. |
| Drop-in alternative | **Claude** (`claude-3-5-haiku-latest`) | `--provider claude` / `ANTHROPIC_API_KEY`. Same prompt, parsed the same way. |
| Rate limits | Not a constraint here | One call per entity = **~12 calls/run**, ~300 tokens each — far under Groq's free per-minute request/token caps. If a cap is ever hit, that entity **degrades to a null narrative** without failing the run. |
| Quality assessment | Spot-check + guardrails | Low `temperature=0.3` for consistency; a grounding instruction ("use only the given titles, never invent"); controlled-vocabulary coercion for theme/tone. See §4. |

`GROQ_MODEL` and `CLAUDE_MODEL` are env-overridable, so the model choice is config, not code.

## 2. Inputs and outputs

**Input per entity:** entity name, ticker (optional), and the top-N HN stories this window
(title + points). The reference CLI fetches these live from Algolia (reusing the Week-5
quoted/`advancedSyntax` exact-phrase fix and `metric_generation.parse_hit`); in the n8n
workflow they come from the leaderboard's `topStory` field.

**Output per entity** (structured JSON):
```json
{
  "narrative": "one paragraph, <= 70 words, grounded in the titles",
  "theme": "launch | outage | funding | research | controversy | hiring",
  "tone":  "bullish | bearish | neutral",
  "enumCoerced": false,          // true if the model returned an off-vocab value we snapped
  "entity": "...", "ticker": "...",
  "provider": "groq", "model": "llama-3.3-70b-versatile",
  "degraded": false
}
```

## 3. Prompt design

- **System message** frames the role (technical-community analyst), states *buzz = attention,
  not price direction* (so an outage and a launch both read as "high buzz"), and demands
  **grounding** ("never invent facts/numbers not implied by the titles") and **JSON-only** output.
- **User message** gives the entity, ticker, and the numbered top stories (points + title),
  then specifies the three exact keys and the controlled vocabularies inline.
- **Controlled vocabularies** come straight from plan.md's "Signals produced": themes =
  {launch, outage, funding, research, controversy, hiring}; tones = {bullish, bearish, neutral}.
- **`temperature=0.3`** — low, for repeatable, non-embellished output.
- **JSON mode** — Groq `response_format={"type":"json_object"}`; Claude is instructed to emit
  only the object and the parser defensively extracts the outermost `{...}`.

## 4. Graceful degradation (plan.md requirement)

The layer **never crashes the run** — the deterministic score/digest must ship regardless:

| Situation | Behavior |
|---|---|
| No `GROQ_API_KEY` and no `ANTHROPIC_API_KEY` | `degraded=true`, `narrative/theme/tone=null`, `reason` set |
| Chosen provider's key missing | `degraded=true` with the specific reason |
| API error / timeout / rate-limit | Caught → `degraded=true` with the exception summary |
| Model returns non-JSON / empty narrative | `ValueError` caught → `degraded=true` |
| Model returns an **off-vocabulary** theme/tone | Snapped to a safe fallback (`research`/`neutral`) and **flagged** `enumCoerced=true` — a judgment about a judgment, surfaced not hidden (SNICKERDOODLE P3) |

Verified with three tests (see RUN_LOG 2026-07-16): live NVIDIA, offline GPT-5 fixture, and the
no-key path; plus unit checks for enum coercion, prose-wrapped JSON, and garbage input.

## 5. Using the reference implementation

```bash
python llm_narrative.py --demo                 # offline fixture, no network
python llm_narrative.py --entity "NVIDIA"      # live HN fetch + Groq
python llm_narrative.py --entity "OpenAI" --provider claude   # needs ANTHROPIC_API_KEY
GROQ_MODEL=llama-3.1-8b-instant python llm_narrative.py --demo   # fast fallback model
```
No new dependencies — it uses `requests` + `python-dotenv`, already in `requirements.txt`.

## 6. n8n workflow integration — **steps for you to apply and verify**

> Why this is your step, not mine: n8n's Python (Pyodide) code nodes have **no network
> access**, so the LLM call is an **HTTP Request** node that authenticates with a **Groq
> credential stored in n8n's vault** — which only exists in your running n8n, and can only
> be verified by a live run against your Postgres/SMTP. The Python module above is the
> tested reference; the n8n nodes below mirror it exactly.

**Step A — create the Groq credential (once):**
1. In n8n → **Credentials → New → "Header Auth"**.
2. Name: `Groq API`. Header **Name** = `Authorization`, **Value** = `Bearer <your GROQ_API_KEY>`.

**Step B — add three nodes** between **`Build Run Row`** and its current consumers
(`Code in Python`, `If`, `Save Snapshot`). New flow:
`Build Run Row → Explode Entities → LLM Narrative (Groq) → Attach Narratives → {Code in Python, If, Save Snapshot}`.

1. **`Explode Entities`** (Code, Python) — one item per entity, each carrying a pre-built Groq
   request body. Paste:
   ```python
   THEMES = ["launch","outage","funding","research","controversy","hiring"]
   TONES  = ["bullish","bearish","neutral"]
   def build(_items):
       row = _items[0]["json"]; lb = row.get("leaderboard", [])
       out = []
       for e in lb:
           # Use the top-N stories for richer grounding; fall back to the single topStory.
           tops = e.get("topStories") or ([e["topStory"]] if e.get("topStory") else [])
           lines = []
           for i, s in enumerate(tops[:5], 1):
               t = (s.get("title") or "")[:200]
               lines.append(f"{i}. [{s.get('points', 0)} pts] {t}")
           stories = "\n".join(lines) if lines else "(no stories this window)"
           system = ("You are a technical-community analyst for an AI-sector attention "
               "tracker. Buzz measures ATTENTION, not price direction. Ground every "
               "statement in the provided titles; never invent facts. Reply with one JSON object only.")
           user = (f"Entity: {e.get('entity')} (ticker {e.get('ticker')})\n"
               f"Top Hacker News stories this window:\n{stories}\n\n"
               f'Return JSON with keys: "narrative" (<=70 words, grounded), '
               f'"theme" (one of {THEMES}), "tone" (one of {TONES}).')
           body = {"model":"llama-3.3-70b-versatile","temperature":0.3,
               "response_format":{"type":"json_object"},
               "messages":[{"role":"system","content":system},{"role":"user","content":user}]}
           out.append({"json": {"entity": e.get("entity"), "row": row, "groqBody": body}})
       return out
   return build(_items)
   ```
2. **`LLM Narrative (Groq)`** (HTTP Request): **POST** `https://api.groq.com/openai/v1/chat/completions`;
   Authentication = **Generic → Header Auth → `Groq API`**. Body config (IMPORTANT — get this exact):
   - **Send Body** = On, **Body Content Type** = **JSON**
   - **Specify Body** = **"Using JSON"**  ← NOT "Using fields below" (a blank-named field yields
     malformed JSON → `{"error":"invalid syntax"}`)
   - In the **JSON** field, expression mode: `{{ $json.groqBody }}`
   - Turn on **Retry On Fail** and **"Continue On Fail"** so one bad entity degrades instead of
     stopping the run.
3. **`Merge Narratives`** (Merge node) — recombine the input (`entity`/`row`) with the Groq
   response into one item, WITHOUT relying on any HTTP passthrough or `_('...')` (unavailable in
   some n8n Python builds). Config: **Mode = Combine**, **Combine By = Combine by Position**.
   Wire **two** inputs:
   - Input 1 ← `Explode Entities`  (carries `entity`, `row`, `groqBody`)
   - Input 2 ← `LLM Narrative (Groq)`  (carries `choices`)
   Position-combine pairs item *i* of each side, so each merged item has `entity` + `row` +
   `choices` together. (The field sets don't overlap, so nothing clashes.)

   > **Known risk — silent misalignment.** Combine-by-position is the fragile kind of merge: it
   > pairs by order/index, not by a shared key. It is used here **only because the failure it
   > works around destroyed the shared key** — the HTTP node overwrites the item with the raw API
   > response, so the company name no longer exists on the response side to join on. Position is
   > the only correspondence left. The consequence: if any step ever silently **reorders or drops**
   > an item without leaving a placeholder in its slot, company A's row would be stapled to company
   > B's narrative and **nothing would flag it** — the run would look successful and store wrong
   > data. Two things keep it safe today: both inputs originate from `Explode Entities` in the same
   > order, and **Continue On Fail** must stay ON so a failed call still emits an item in its slot
   > (turning it off collapses the list and shifts every downstream pairing). If this ever needs to
   > be hardened, the robust fix is to restore a key: have the model echo the entity name back as a
   > JSON field and have `Attach Narratives` assert it matches the position-paired `entity`,
   > degrading that entry instead of trusting the pairing blindly.
4. **`Attach Narratives`** (Code, Python) — now reads everything from its single merged input:
   ```python
   import json
   THEMES = ["launch","outage","funding","research","controversy","hiring"]
   TONES  = ["bullish","bearish","neutral"]
   def merge(_items):
       row = _items[0]["json"]["row"]
       narr = {}
       for it in _items:
           j = it["json"]; ent = j.get("entity")
           try:
               content = j["choices"][0]["message"]["content"]
               o = json.loads(content)
               theme = o.get("theme") if o.get("theme") in THEMES else "research"
               tone  = o.get("tone")  if o.get("tone")  in TONES  else "neutral"
               narr[ent] = {"narrative": (o.get("narrative") or "").strip(), "theme": theme, "tone": tone}
           except Exception as ex:
               narr[ent] = {"narrative": None, "theme": None, "tone": None, "degraded": True, "reason": str(ex)}
       for e in row.get("leaderboard", []):
           e["narrative"] = narr.get(e.get("entity"))
       row["narratives"] = narr
       return [{"json": row}]
   return merge(_items)
   ```
5. **Rewire** the full branch:
   `Build Run Row → Explode Entities`; `Explode Entities →` **both** `LLM Narrative (Groq)`
   **and** `Merge Narratives` (Input 1); `LLM Narrative (Groq) → Merge Narratives` (Input 2);
   `Merge Narratives → Attach Narratives`; `Attach Narratives →` the three original consumers
   (`Code in Python`, `If`, `Save Snapshot`).
6. **Persist it**: in **`Save Snapshot`**, add `narratives` to the INSERT
   (`INSERT INTO hn_buzz_runs (run_date, window_hours, watchlist_version, leaderboard,
   narratives, raw_metrics, complete) VALUES ($1,$2,$3,$4::jsonb,$5::jsonb,$6::jsonb,$7)`) and
   add `{{ JSON.stringify($json.narratives) }}` in the matching position of `queryReplacement`.
   The `narratives` column already exists in the schema (`DATABASE_SETUP.md`).

**Step C — verify (Phase-1-style):**
- Run the workflow manually on the full watchlist; confirm each entity row gains a
  `narrative`/`theme`/`tone`, and a row lands in `hn_buzz_runs` with a non-null `narratives`.
- Temporarily point the credential at a bad key → confirm the run still completes with
  degraded (null) narratives, not a hard failure (plan.md's "missing LLM key" edge case).
