#!/usr/bin/env bash
# conformance-check.sh — Stop hook.
# Runs Snickerdoodle conformance when Claude finishes. If it fails, surface the
# reason and exit 2 so Claude knows the work isn't done (machine half of P4).
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
if ! node scripts/conformance.mjs >/tmp/snickerdoodle-conformance.log 2>&1; then
  echo "Snickerdoodle conformance FAILED — invalid JSON/YAML/JS is not done. Fix before finishing:" >&2
  tail -25 /tmp/snickerdoodle-conformance.log >&2
  exit 2
fi
exit 0
