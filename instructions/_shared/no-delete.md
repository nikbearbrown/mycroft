## Never delete — archive instead

Never delete source, data, recipes, logs, or any hand-made file. Move superseded or scratch files to an archive (or out of the working tree into the full-copy archive). The only safe removals are generated/rebuildable artifacts — `**/.build/`, `__pycache__/`, `*.pyc`, `*.bak` — because they regenerate from source. When in doubt, archive and ask.
