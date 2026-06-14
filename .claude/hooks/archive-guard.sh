#!/usr/bin/env bash
# archive-guard.sh — PreToolUse(Bash) hook.
# Enforces Madison's no-delete rule (instructions/_shared/no-delete.md):
# block `rm` of anything that isn't a rebuildable artifact. Safe removals are
# only files that regenerate from source: .build  __pycache__  *.pyc  *.bak
# Everything else (source, data, recipes, logs) must be archived, not deleted.
CMD=$(python3 -c 'import sys,json; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' 2>/dev/null)
# Not an rm command -> no opinion.
if ! printf '%s' "$CMD" | grep -qE '(^|[;&|[:space:]])rm([[:space:]]|$)'; then exit 0; fi
# rm referencing ONLY rebuildable artifacts -> allow.
if printf '%s' "$CMD" | grep -qE '\.build|__pycache__|\.pyc|\.bak'; then exit 0; fi
# Otherwise deny + explain.
python3 - <<'PY'
import json
print(json.dumps({"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Madison no-delete rule: never delete source, data, recipes, or logs — archive them instead (or your full-copy archive). Safe rm targets are rebuildables only: .build, __pycache__, *.pyc, *.bak."}}))
PY
