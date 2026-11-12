# E1 — "Select All" has no cap matching the chat endpoint's 10-feed limit: verification & fix

**Date:** 2026-11-12 · **Component:** `Regulatory_QA/frontend/src/{App.jsx, components/ChatInterface.jsx}`

## The bug

The chat endpoint (`POST /api/chat`) hard-caps context to 10 feeds — enforced by Pydantic on
`FeedQuery.feed_ids` (`models.py`, `max_items=10`) and documented as an intentional RAG context
size limit (`config.py`'s `max_context_feeds: int = 10`).

Nothing on the frontend respects that limit. `App.jsx` loads up to 100 feeds
(`feedsAPI.listFeeds({ limit: 100 })`), and `FeedList.jsx`'s prominent, unguarded "Select All"
button calls `handleSelectAll()`, which did:

```js
const handleSelectAll = () => {
  setSelected(new Set(feeds.map(f => f.id)));
};
```

— selecting every loaded feed, no cap. On the live `mycroft_intelligence` DB (411 rows), clicking
it selects close to 100 feeds. Any question asked afterward is guaranteed to fail backend
validation with HTTP 422.

Compounding it, `ChatInterface.jsx`'s error handler only ever showed axios's generic
`error.message`:

```js
content: 'Failed to get response: ' + error.message,
```

For a non-2xx response, axios's own `error.message` is just `"Request failed with status code
422"` — it never reads `error.response.data.detail`, where FastAPI actually puts the real
validation reason. So the user saw a meaningless, network-sounding error with zero indication the
real problem was "you selected too many feeds."

## Why this matters

"Select All" is the single most discoverable, inviting action in the feed panel (top-right, no
disabled state, no tooltip). It's the natural first move before asking a broad question —
including the app's own suggested prompt, "Summarize the key regulatory changes." Clicking it
deterministically breaks the chat feature, the app's core value proposition, on every subsequent
question, with an error that looks like a server/network failure rather than a validation rule a
user could fix by deselecting feeds. This is a full, repeatable feature outage reachable from the
most obvious UI action, not an edge case.

## The fix

`App.jsx` — cap both selection paths (`handleSelectAll` and individual `handleToggle`) at the same
limit the backend enforces:

```diff
+// Must match the backend's FeedQuery.feed_ids max_items / config.max_context_feeds
+// (Regulatory_QA/backend/app/models.py, app/config.py) - the RAG context size limit.
+const MAX_SELECTABLE_FEEDS = 10;
+
 function App() {
   ...
   const handleToggle = (id) => {
     setSelected(prev => {
       const newSet = new Set(prev);
       if (newSet.has(id)) {
         newSet.delete(id);
-      } else {
+      } else if (newSet.size < MAX_SELECTABLE_FEEDS) {
         newSet.add(id);
       }
       return newSet;
     });
   };

   const handleSelectAll = () => {
-    setSelected(new Set(feeds.map(f => f.id)));
+    setSelected(new Set(feeds.slice(0, MAX_SELECTABLE_FEEDS).map(f => f.id)));
   };
```

`handleToggle` is capped too, not just `handleSelectAll` — otherwise a user could reach the exact
same outage by clicking 11 individual feeds instead of using the button, leaving the bug reachable
through a second path.

`ChatInterface.jsx` — surface the real backend validation reason instead of axios's generic
message, as defense-in-depth for any other validation error the backend might return:

```diff
     } catch (error) {
+      // FastAPI validation errors (422) arrive as error.response.data.detail, either a
+      // plain string or a list of {msg, ...} objects - axios's own error.message is just
+      // "Request failed with status code 422", which tells the user nothing.
+      const detail = error.response?.data?.detail;
+      const reason = Array.isArray(detail)
+        ? detail.map(d => d.msg || JSON.stringify(d)).join('; ')
+        : detail || error.message;
       const errorMessage = {
         role: 'error',
-        content: 'Failed to get response: ' + error.message,
+        content: 'Failed to get response: ' + reason,
         timestamp: new Date(),
       };
```

## Verification

Extracted the patched `handleToggle`/`handleSelectAll` logic and the patched error-reason
extraction verbatim into a live Node.js harness (`verification/verify_feed_cap.js` in this week's
video project folder) and ran it:

| Test | Result |
|---|---|
| `handleSelectAll` against a 411-feed list (matching the real live DB size) | selects exactly 10 — PASS |
| 15 individual `handleToggle` calls in sequence | stops adding at 10, later toggles are no-ops — PASS |
| Untoggling at the cap, then adding a new feed | frees a slot correctly, new feed added, still capped at 10 — PASS |
| Error-reason extraction against the real 422 body a live FastAPI `TestClient` returned for 15 `feed_ids` (captured directly from `app.models.FeedQuery`, not reconstructed) | old behavior: `"Request failed with status code 422"`; new behavior: `"List should have at most 10 items after validation, not 15"` — PASS |
| Error-reason extraction with no `response.data.detail` (e.g. a real network failure) | falls back to `error.message` unchanged — PASS |

All 7 assertions pass. The 422 response body used in the harness is the real one a live,
unmodified `app.models.FeedQuery` returns for an oversized `feed_ids` list (confirmed via FastAPI's
`TestClient` against the actual Pydantic model during investigation), not a guessed shape.

Did not run a full `vite build`/browser end-to-end check — `node_modules` isn't installed in this
environment and installing it was out of scope for a two-line logic fix. The IDE's own static
diagnostics ran against both edited files post-change and reported zero new errors (only
pre-existing, unrelated warnings already present before this fix).

## What's NOT touched

The backend's `max_items=10` limit and `max_context_feeds` setting are untouched — this fix makes
the frontend respect the backend's existing, intentional limit, not loosen it. `FeedList.jsx`
itself is untouched (no visual indicator that selection is capped was added — a `MAX_SELECTABLE_FEEDS`
constant comment is as far as this fix goes; a disabled-state/tooltip on "Select All" past the cap
would be a reasonable follow-up but is a UI polish item, not required to close the actual bug).
`Stats.jsx`, `Header.jsx`, and every other component are untouched.
