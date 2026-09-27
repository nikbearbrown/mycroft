# Deadletter audit - 2026-08-30 23:43 UTC

**8** rejected events on `events.deadletter`.

## By reason class

| reason | count |
|---|---:|
| schema | 7 |
| stale | 1 |

## By source

| source | count |
|---|---:|
| ? | 5 |
| manual | 3 |

## Sample (up to 15)

| event_key | source | reject_reason |
|---|---|---|
| - | - | schema: not valid json (invalid character 'ï' looking for beginning of value) |
| - | - | schema: not valid json (invalid character 'ï' looking for beginning of value) |
| STALE-1 | manual | stale: published_at 2020-01-01 older than 7d |
|  | manual | schema: missing event_key |
| - | - | schema: not valid json (invalid character 'ï' looking for beginning of value) |
| - | - | schema: not valid json (invalid character 'ï' looking for beginning of value) |
| - | - | schema: not valid json (invalid character 'o' in literal true (expecting 'r')) |
| NORAW-1 | manual | schema: missing raw provenance |

_An audit reports what it found; it does not say pass._
