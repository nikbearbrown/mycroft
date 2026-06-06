# Shared Recipe Contract

## Executive Summary

This file defines the rules all recipes must follow.

## Rules

1. Check verified local data first.
2. Check vetted stored scripts in `scripts/` first.
3. Do not create or reference `SCRIPTS/`.
4. Use external lookup only after local evidence is insufficient.
5. Create ad hoc scripts only when no stored script fits.
6. Run explicit tests before scaling automation.
7. Log meaningful runs in `logs/RUN_LOG.md`.

## Phase Gates

1. Problem gate
2. Local evidence gate
3. Stored script gate
4. Small-run gate
5. Verification gate
6. Logging gate
