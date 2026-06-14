## Default to Markdown for humans

AI-native formats (JSON, YAML) are the source of truth for the machine. When showing an artifact to a person, render the Markdown view (`scripts/to-markdown.mjs` / the `review` skill) by default. Show raw JSON/YAML only when asked.
