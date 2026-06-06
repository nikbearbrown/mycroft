# Labor Separation

Mycroft uses a simple operating principle: AI does AI things, and humans do human things. AI systems can gather sources, run scripts, compare artifacts, summarize evidence, and prepare bounded drafts. Humans set goals, approve scope, judge risk, clear phase gates, accept or reject interpretations, and decide what may leave the repository.

Recipes, scripts, logs, reports, and conductor flows should preserve that separation. If a workflow asks an AI system to make a human judgment, the workflow should stop, name the required human decision, and wait for clearance.
