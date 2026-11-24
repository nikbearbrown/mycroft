# G1 — Chat context leaks across turns: the vectorstore's "fresh" rebuild never clears the stale collection

**Date:** 2026-11-24 · **Component:** `Regulatory_QA/backend/app/rag.py` (`RegulatoryRAG.build_vectorstore()`) ·
**DB:** local `mycroft_intelligence` @ `localhost:5431` (not DB-rooted — this is an in-process state bug)

## The bug

`rag.py`'s `RegulatoryRAG` is a module-level singleton (`_rag_engine`), re-used across every
`POST /api/chat` request (`routers/chat.py`'s `ask_question()`). Each call re-invokes
`build_vectorstore(feeds)`, which rebuilds the Chroma store from only the currently-selected feeds:

```python
self.vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=self.embeddings,
    collection_name="regulatory_feeds",
    persist_directory=None,
)
```

The comment and `persist_directory=None` strongly imply each call gets an isolated, in-memory
store. It doesn't. `langchain_community.vectorstores.Chroma.__init__` builds a
`chromadb.Client(chromadb.config.Settings())` with no client passed in; chromadb's
`SharedSystemClient` caches the underlying ephemeral system by a settings-derived key, so every
"fresh" client constructed in the same process resolves to the *same* underlying in-memory store.
`get_or_create_collection("regulatory_feeds")` therefore returns the *same* collection every call.
New documents are added with fresh random UUIDs (no `ids=` passed) — never replacing anything — so
every prior call's documents stay in the collection, indefinitely, for the life of the backend
process.

## Why this matters

A completely ordinary multi-turn session triggers it: select feeds A, ask a question, then
deselect A, select unrelated feeds B, ask a second question. B's `similarity_search` call now
searches a collection containing both A's and B's documents — a user can get an answer "about"
their newly-selected feeds that's actually quoting content from feeds they explicitly deselected
in a prior, unrelated turn. The longer the backend runs, the more every turn's feeds accumulate
into every later turn's retrieved context: unbounded in-process memory growth, and a slow,
silent degradation of answer relevance with zero error raised anywhere. Unlike D1/F1 (a stats
display disagreeing with itself), this corrupts the actual chat answers users receive.

## The fix

`rag.py`, `build_vectorstore()` — delete the stale collection before rebuilding:

```diff
     def build_vectorstore(self, feeds: List[Feed]):
         """Build vector store from selected feeds with full content"""
         print(f"\n🔨 Building vector store for {len(feeds)} feeds...")
         documents = self.create_documents(feeds)
         
+        if self.vectorstore is not None:
+            self.vectorstore._client.delete_collection("regulatory_feeds")
+        
         self.vectorstore = Chroma.from_documents(
             documents=documents,
             embedding=self.embeddings,
             collection_name="regulatory_feeds",
             persist_directory=None
         )
         print("✅ Vector store built successfully!\n")
```

## Verification

chromadb isn't installed in this environment's default interpreter, so verification used an
isolated venv (scratchpad, not the repo) with the real `chromadb` + `langchain-community` /
`langchain-core` packages — the same classes `rag.py` imports. Reproduced `build_vectorstore()`'s
exact patched logic (a small stub class calling the same two statements in the same order) and
simulated two chat turns with disjoint feed sets (Feed A, then Feed B only):

- Pre-fix behavior (confirmed during investigation, before this fix was written): turn 2's
  collection count came back 2 (not reset to 1), and a Feed-A-specific `similarity_search` query
  run during the Feed-B-only turn returned Feed A's document — the leak, reproduced concretely.
- Post-fix (this patch): turn 2's collection count correctly returns to 1, and the same
  Feed-A-specific query during the Feed-B-only turn returns only Feed B's document — no leak.

`python3 -m py_compile` on the patched `rag.py` — clean.

Ruled out before settling on this bug: `/api/feeds/recent`'s 7-day window (dead endpoint — no
frontend component calls `feedsAPI.getRecent`, unlike F1's now-fixed `get_stats()` which the
`Stats.jsx` component does call); `source_distribution`'s 30-day window (same staleness pattern
as F1, but already explicitly scoped out as a separate, lower-priority open issue in
F1-VERIFICATION.md, and weaker in impact than a correctness-corrupting leak); `published IS NULL`
rows in the live DB (0 of 411 rows — not an issue).

## What's NOT touched

`create_documents()`, chunking, embeddings, and the `query()` method's prompt construction and
Ollama call are untouched. The chat endpoint's 10-feed cap (E1) and the dashboard's severity
queries (D1, F1) are untouched. This fix only clears stale collection state between calls — it
does not change what's retrieved for a *correctly isolated* turn, only removes contamination from
prior turns' now-deselected feeds.
