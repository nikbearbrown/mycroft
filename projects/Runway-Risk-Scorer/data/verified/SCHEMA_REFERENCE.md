# Signal schema — reference only

This recipe consumes signals conforming to the `ai_company_signals` schema
defined in the upstream Mycroft repository. That schema is **not reproduced
here**: the upstream repo is all-rights-reserved, so this repo references it
rather than redistributing it.

Fields this recipe relies on (names must match the upstream schema):

| field           | type    | notes                                             |
|-----------------|---------|---------------------------------------------------|
| signal_id       | uuid    | unique per signal                                 |
| company_id      | string  | stable company slug                               |
| signal_type     | enum    | funding_round, funding_stage, layoff, executive_change, security_issue, product_launch, news_mention, ... |
| signal_title    | string  | human-readable label                              |
| signal_value    | string  | e.g. "$45M", "Series B", "negative"               |
| score           | int     | 0–100 confidence                                  |
| source_type     | enum    | News, EDGAR, GitHub, ArXiv                         |
| source_url      | string  | provenance (P3)                                   |
| occurred_date   | date    | when the event happened                           |
| ingested_at     | datetime|                                                   |
| validated_by    | string  | null until a human validates (P2)                 |
| validation_note | string  |                                                   |
| validation_date | date    |                                                   |
| used_in_brief   | bool    |                                                   |

> If you contribute this recipe upstream via fork + PR, it runs against the
> real schema in that repo and this file is unnecessary. It exists only so the
> recipe is self-describing in a standalone/private working copy.
