"""Purpose: Deduplicate shape-clean records, flag stale and wrong-typed values, and produce the final verified record set.
Input: step-3 output under data/verified/market-sentiment-analysis-part-1/runs/<run_id>-<fixture_set>/, plus the identity keys and freshness windows in sample/fixture-manifest.json.
Output: one quality-checked envelope per stream under runs/<run_id>-<fixture_set>/quality-checked/, and a summary on stdout carrying verified_records, record_count, duplicates, rejects, flags, quality_notes.
Side effects: writes into data/verified/ only. No network calls.
Idempotent: Yes; freshness is measured from the run's frozen clock, never from now(), so reruns are byte-identical.
Recipe: recipes/market-sentiment-analysis-part-1.md

Layer contract (docs/architecture.md 5.2): GIGO may read data/raw/, must validate against a
declared schema, must write only data/verified/, and must not make network requests.

SCOPE -- what this step is responsible for catching:
    Step 3 owns shape. This step owns everything else, and against the frozen corpus it must
    surface the remaining 10 of the 18 catalogued defects, in the fields the manifest names:
      duplicates    : D04 (price, same symbol+day), D06 (news, same id),
                      D05 (news, SAME HEADLINE but different id and url), D13 (reddit, same id)
      flags         : D02, D11, D17 (type violations) and D03, D10, D16 (stale timestamps)
    It also carries forward, rather than re-deriving, what step 3 found:
      rejects       : the rows step 3 withheld (D01, D07, D08, D09, D14, D15) -- this is the
                      'also_expected' step-4 outcome for D01/D09/D15: rejected, never defaulted
      quality_notes : D12, the envelope count mismatch step 3 recorded

FLAG, DO NOT DROP; FLAG, DO NOT COERCE:
    A stale row is flagged and kept, never silently dropped -- dropping it would hide the fact
    that the source returned out-of-window data. A wrong-typed value is flagged and left
    exactly as found, never coerced. The source workflow's parseFloat(...) || 0 turns "N/A"
    into a silent 0 that reaches a sentiment score; the whole point of flagging here is that
    step 5 cannot make that substitution without it appearing in the record.

DUPLICATE COUNTING:
    Every occurrence of an identity key beyond the first. Three rows sharing one key count as
    2 duplicates, not 3 and not 1. The first occurrence is kept; later ones are removed from
    verified_records and listed under duplicates with both locators.

    News gets two passes, because one is not enough: an identity-key pass on `id`, and a
    separate near-duplicate pass on the whitespace-normalised, case-folded headline. D05 is a
    syndicated copy of the same story from a second outlet -- different `id`, different `url`,
    identical headline. An id-only dedupe counts it as two independent stories and
    double-weights the sentiment.

Constitution notes:
    P2 - only rows that survive dedup reach verified_records; nothing is quietly repaired.
    P3 - every duplicate, reject and flag carries the ORIGINAL raw locator from step 3's
         promoted_locators, so a score traces back to a byte range in a named source file.
    P4 - findings are reported in full first; the run then halts on a nonzero exit if any
         reject or flag was raised, so one early finding cannot hide the rest.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

WORKFLOW_NAME = 'Market Sentiment Analysis - Part 1'
WORKFLOW_SLUG = 'market-sentiment-analysis-part-1'
NODE_NAME = 'Transform and quality check'
NODE_TYPE = 'recipe-step'
CLASSIFICATION = 'gigo'

RAW_ROOT = f'data/raw/{WORKFLOW_SLUG}'
VERIFIED_ROOT = f'data/verified/{WORKFLOW_SLUG}'
ENVELOPE_PATH = f'{RAW_ROOT}/run-envelope.json'
MANIFEST_PATH = f'{RAW_ROOT}/sample/fixture-manifest.json'

# Identity keys per stream, from fixture-manifest.json identity_keys.
IDENTITY_KEYS = {
    'price': ('01. symbol', '07. latest trading day'),
    'news': ('id',),
    'reddit': ('id',),
}

# Which field carries the row's timestamp, and how to read it.
TIMESTAMP_FIELDS = {
    'price': ('07. latest trading day', 'date'),
    'news': ('datetime', 'epoch'),
    'reddit': ('created_utc', 'epoch'),
}

# Expected value types. The manifest declares required fields and freshness windows but NO
# type contract, so this table is the closure for that gap. It is scoped to this step and is
# not a promoted schema -- see quality_notes in the emitted result.
#   numeric_string : a string parseable as a float (Alpha Vantage returns numbers as strings)
#   percent_string : a numeric string optionally suffixed with '%'
#   epoch_int      : an integer (or integral float) Unix timestamp
#   int_like       : an integer, or a string of digits
TYPE_CONTRACT = {
    'price': {
        '05. price': 'numeric_string',
        '06. volume': 'int_like',
        '08. previous close': 'numeric_string',
        '10. change percent': 'percent_string',
    },
    'news': {'datetime': 'epoch_int'},
    'reddit': {'created_utc': 'epoch_int', 'score': 'int_like'},
}

FRESHNESS_DAYS = {'price': 5, 'news': 2, 'reddit': 1}


def _rel(path: Path, root: Path) -> str:
    """Return a repo-relative POSIX path string."""
    return path.relative_to(root).as_posix()


def _load_manifest_rules(root: Path) -> tuple[dict[str, Any], list[str]]:
    """Load identity keys, the duplicate-counting rule, and freshness windows from the manifest."""
    path = root / MANIFEST_PATH
    if not path.is_file():
        return {}, [f'Quality rules are missing: {MANIFEST_PATH}.']
    try:
        manifest = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as error:
        return {}, [f'Quality rules do not parse: {MANIFEST_PATH} ({error}).']
    return {
        'schema_version': manifest.get('manifest_version'),
        'schema_source': MANIFEST_PATH,
        'identity_keys': manifest.get('identity_keys', {}),
        'duplicate_counting_rule': manifest.get('duplicate_counting_rule'),
        'freshness_policy': manifest.get('freshness_policy', {}),
    }, []


def _resolve_run(root: Path, overrides: dict[str, Any]) -> tuple[Path | None, dict[str, Any], list[str]]:
    """Work out which step-3 verified directory to quality-check."""
    if overrides.get('verified_dir'):
        d = root / overrides['verified_dir']
        if not d.is_dir():
            return None, {}, [f'Verified directory does not exist: {overrides["verified_dir"]}.']
        run_id, _, fixture_set = d.name.rpartition('-')
        return d, {'run_id': run_id, 'fixture_set': fixture_set}, []

    env_path = root / ENVELOPE_PATH
    if not env_path.is_file():
        return None, {}, [f'Run envelope is missing: {ENVELOPE_PATH}, and no --verified-dir was given.']
    try:
        envelope = json.loads(env_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as error:
        return None, {}, [f'Run envelope does not parse: {ENVELOPE_PATH} ({error}).']

    fixture_set = overrides.get('fixture_set') or envelope.get('fixture_set')
    run_id = envelope.get('run_id')
    if not run_id or not fixture_set:
        return None, {}, ['Run envelope is missing run_id or fixture_set.']
    d = root / f'{VERIFIED_ROOT}/runs/{run_id}-{fixture_set}'
    if not d.is_dir():
        return None, {}, [
            f'Verified directory does not exist: {_rel(d, root)}. Run step 3 '
            '(validate-data-shape) first.'
        ]
    return d, {'run_id': run_id, 'fixture_set': fixture_set}, []


def _parse_clock(value: Any) -> datetime | None:
    """Parse the run's frozen clock into an aware datetime."""
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _type_ok(value: Any, kind: str) -> bool:
    """Check one value against the declared type. Returns False for a violation."""
    if kind == 'numeric_string':
        if isinstance(value, bool):
            return False
        if isinstance(value, (int, float)):
            return True
        if not isinstance(value, str):
            return False
        try:
            float(value.strip())
            return True
        except ValueError:
            return False
    if kind == 'percent_string':
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return True
        if not isinstance(value, str):
            return False
        try:
            float(value.strip().rstrip('%'))
            return True
        except ValueError:
            return False
    if kind == 'epoch_int':
        if isinstance(value, bool):
            return False
        if isinstance(value, int):
            return True
        if isinstance(value, float):
            return value.is_integer()
        return False
    if kind == 'int_like':
        if isinstance(value, bool):
            return False
        if isinstance(value, int):
            return True
        if isinstance(value, float):
            return value.is_integer()
        if isinstance(value, str):
            return bool(re.fullmatch(r'-?\d+', value.strip()))
        return False
    return True


def _row_timestamp(stream: str, row: dict[str, Any]) -> tuple[datetime | None, Any]:
    """Read a row's timestamp. Returns (datetime or None, raw value)."""
    field, kind = TIMESTAMP_FIELDS[stream]
    raw = row.get(field)
    if kind == 'epoch':
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            return None, raw
        try:
            return datetime.fromtimestamp(float(raw), timezone.utc), raw
        except (OverflowError, OSError, ValueError):
            return None, raw
    if isinstance(raw, str):
        try:
            return datetime.fromisoformat(raw.strip()).replace(tzinfo=timezone.utc), raw
        except ValueError:
            return None, raw
    return None, raw


def _identity(stream: str, row: dict[str, Any]) -> tuple[Any, ...]:
    """Build a row's identity tuple from its declared key fields."""
    return tuple(row.get(k) for k in IDENTITY_KEYS[stream])


def _normalise_headline(value: Any) -> str | None:
    """Whitespace-normalise and case-fold a headline for the news near-duplicate pass."""
    if not isinstance(value, str):
        return None
    collapsed = re.sub(r'\s+', ' ', value).strip().casefold()
    return collapsed or None


def _check_stream(
    stream: str, records: list[Any], locators: list[str], clock: datetime | None
) -> dict[str, Any]:
    """Run dedup, freshness and type checks over one stream's shape-clean rows."""
    duplicates: list[dict[str, Any]] = []
    flags: list[dict[str, Any]] = []
    window = timedelta(days=FRESHNESS_DAYS[stream])

    def loc_of(i: int) -> str:
        return locators[i] if i < len(locators) else f'records[{i}]'

    # Rows step 3 should already have withheld. Recorded, never raised.
    bad_rows = {i for i, row in enumerate(records) if not isinstance(row, dict)}
    for i in sorted(bad_rows):
        flags.append({
            'flag': 'unexpected_row_type',
            'locator': loc_of(i),
            'detail': f'expected an object, got {type(records[i]).__name__}',
        })

    # --- dedup: independent passes, so a row can be a duplicate under more than one basis ---
    # The manifest counts news_by_id and news_by_headline separately. A byte-identical repeat
    # is a duplicate on BOTH bases, and short-circuiting after the first would under-report
    # the headline pass -- which is the pass that catches syndicated copies.
    duplicate_idx: set[int] = set()

    def dedup_pass(basis: str, key_fields: list[str], key_of, note: str | None = None) -> None:
        seen: dict[Any, int] = {}
        for i, row in enumerate(records):
            if i in bad_rows:
                continue
            key = key_of(row)
            if key is None:
                continue
            if key in seen:
                entry = {
                    'basis': basis,
                    'key_fields': key_fields,
                    'key_value': list(key) if isinstance(key, tuple) else [key],
                    'locator': loc_of(i),
                    'first_seen_locator': loc_of(seen[key]),
                    'action': 'removed from verified_records; first occurrence kept',
                }
                if note:
                    entry['note'] = note
                duplicates.append(entry)
                duplicate_idx.add(i)
            else:
                seen[key] = i

    dedup_pass('identity_key', list(IDENTITY_KEYS[stream]), lambda r: _identity(stream, r))
    if stream == 'news':
        dedup_pass(
            'headline_near_duplicate',
            ['headline (whitespace-normalised, case-folded)'],
            lambda r: _normalise_headline(r.get('headline')),
            note=(
                'Same headline. When id and url differ this is a syndicated copy of one '
                'story; an id-only dedupe would count it as independent and double-weight it.'
            ),
        )

    # --- per-row quality checks on the rows that survive dedup ---
    kept_idx: list[int] = []
    for i, row in enumerate(records):
        if i in bad_rows or i in duplicate_idx:
            continue
        loc = loc_of(i)

        # type violations: flagged, never coerced
        type_flagged: set[str] = set()
        for field, kind in TYPE_CONTRACT.get(stream, {}).items():
            if field in row and row[field] is not None and not _type_ok(row[field], kind):
                type_flagged.add(field)
                flags.append({
                    'flag': 'type_violation',
                    'locator': loc,
                    'field': field,
                    'value': row[field],
                    'expected': kind,
                    'action': 'flagged and left as found; must not be coerced downstream',
                })

        # freshness: flagged, never dropped
        ts_field = TIMESTAMP_FIELDS[stream][0]
        ts, raw_ts = _row_timestamp(stream, row)
        if ts is None:
            # Only report unreadability when the type check has not already said so, or the
            # same bad value would be counted twice under two different flag names.
            if raw_ts is not None and ts_field not in type_flagged:
                flags.append({
                    'flag': 'timestamp_unreadable',
                    'locator': loc,
                    'field': ts_field,
                    'value': raw_ts,
                    'action': 'flagged; row cannot be placed in or out of the freshness window',
                })
        elif clock is not None and (clock - ts) > window:
            flags.append({
                'flag': 'stale_timestamp',
                'locator': loc,
                'field': ts_field,
                'value': raw_ts,
                'observed_at': ts.isoformat(),
                'window_days': FRESHNESS_DAYS[stream],
                'age_days': (clock - ts).days,
                'measured_from': clock.isoformat(),
                'action': 'flagged and kept; stale data must not be silently dropped',
            })

        kept_idx.append(i)

    return {
        'verified_records': [records[i] for i in kept_idx],
        'verified_locators': [locators[i] if i < len(locators) else f'records[{i}]' for i in kept_idx],
        'duplicates': duplicates,
        'flags': flags,
        'rows_in': len(records),
        'rows_out': len(kept_idx),
    }


def transform_quality_check(payload: Any = None, root: Path | None = None) -> dict[str, Any]:
    """Deduplicate, flag, and produce the final verified record set.

    Purpose: finish the GIGO pass so tool scripts read data whose defects are all recorded.
    Input: optional dict with 'verified_dir' or 'fixture_set'.
    Output: dict with verified_records, record_count, duplicates, rejects, flags, quality_notes.
    Side effects: writes one file per stream into runs/<run_id>-<fixture_set>/quality-checked/.
    Idempotent: yes; freshness is measured from the run's frozen clock.
    Recipe: recipes/market-sentiment-analysis-part-1.md
    """
    root = root or Path(__file__).resolve().parents[2]
    overrides = payload if isinstance(payload, dict) else {}

    rules, rule_stops = _load_manifest_rules(root)
    if rule_stops:
        return _stopped(rule_stops, {}, rules)

    src_dir, ident, stops = _resolve_run(root, overrides)
    if stops or src_dir is None:
        return _stopped(stops, ident, rules)

    files = sorted(p for p in src_dir.iterdir() if p.is_file() and p.suffix == '.json')
    if not files:
        return _stopped([f'No step-3 output in {_rel(src_dir, root)}.'], ident, rules)

    out_dir = src_dir / 'quality-checked'
    out_dir.mkdir(parents=True, exist_ok=True)

    per_stream: list[dict[str, Any]] = []
    all_duplicates: list[dict[str, Any]] = []
    all_flags: list[dict[str, Any]] = []
    all_rejects: list[dict[str, Any]] = []
    quality_notes: list[dict[str, Any]] = []
    written: list[str] = []

    for path in files:
        try:
            doc = json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as error:
            all_rejects.append({
                'reason': 'step3_output_unparseable',
                'file': _rel(path, root),
                'detail': f'{type(error).__name__}: {error}',
            })
            continue

        stream = doc.get('stream')
        if stream not in IDENTITY_KEYS:
            all_rejects.append({
                'reason': 'unknown_stream',
                'file': _rel(path, root),
                'detail': f'stream={stream!r}',
            })
            continue

        records = doc.get('records') or []
        locators = doc.get('promoted_locators') or []
        prov = doc.get('_provenance') or {}
        clock = _parse_clock((prov.get('source_envelope') or {}).get('fetched_at'))

        result = _check_stream(stream, records, locators, clock)

        # Carry forward, rather than re-derive, what step 3 already found.
        shape = doc.get('shape_validation') or {}
        for m in shape.get('missing_fields', []):
            all_rejects.append({
                'reason': 'missing_required_field',
                'stream': stream,
                'file': _rel(path, root),
                'locator': m.get('locator'),
                'field': m.get('field'),
                'detail': m.get('reason'),
                'found_by': 'step 3 (validate-data-shape)',
                'action': 'row withheld from the verified layer; never defaulted',
            })
        for m in shape.get('malformed_rows', []):
            all_rejects.append({
                'reason': 'malformed_row',
                'stream': stream,
                'file': _rel(path, root),
                'locator': m.get('locator'),
                'detail': m.get('detail'),
                'found_by': 'step 3 (validate-data-shape)',
                'action': 'row withheld from the verified layer',
            })
        if shape.get('count_matches_declared') is False:
            quality_notes.append({
                'note': 'envelope_count_mismatch',
                'stream': stream,
                'file': _rel(path, root),
                'declared': shape.get('source_declared_record_count'),
                'recounted': shape.get('rows_seen'),
                'detail': (
                    'The source envelope under-reported its own payload. The recount governs; '
                    'the declared value is retained for provenance.'
                ),
                'found_by': 'step 3 (validate-data-shape)',
            })

        for d in result['duplicates']:
            all_duplicates.append(dict(d, stream=stream, file=_rel(path, root)))
        for f in result['flags']:
            all_flags.append(dict(f, stream=stream, file=_rel(path, root)))

        out = {
            'workflow': WORKFLOW_NAME,
            'node': NODE_NAME,
            'classification': CLASSIFICATION,
            'stream': stream,
            'schema_version': rules['schema_version'],
            'schema_source': rules['schema_source'],
            # --- the six fields the recipe declares for this step ---
            'verified_records': result['verified_records'],
            'record_count': result['rows_out'],
            'duplicates': result['duplicates'],
            'rejects': [r for r in all_rejects if r.get('file') == _rel(path, root)],
            'flags': result['flags'],
            'quality_notes': [q for q in quality_notes if q.get('file') == _rel(path, root)],
            # ---
            'record_count_basis': 'rows surviving dedup; flagged rows are kept, not dropped',
            'verified_locators': result['verified_locators'],
            'rows_in': result['rows_in'],
            'rows_removed_as_duplicates': len(result['duplicates']),
            'identity_keys': list(IDENTITY_KEYS[stream]),
            'duplicate_counting_rule': rules['duplicate_counting_rule'],
            'freshness_window_days': FRESHNESS_DAYS[stream],
            'freshness_measured_from': clock.isoformat() if clock else None,
            'type_contract': TYPE_CONTRACT.get(stream, {}),
            '_provenance': {
                'run_id': ident['run_id'],
                'fixture_set': ident['fixture_set'],
                'quality_checked_by': f'scripts/gigo/{WORKFLOW_SLUG}-transform-quality-check.py',
                'step3_input': _rel(path, root),
                'source_envelope': prov.get('source_envelope'),
            },
        }
        dest = out_dir / path.name
        dest.write_text(
            json.dumps(out, indent=2, sort_keys=True, default=str) + '\n',
            encoding='utf-8',
            newline='\n',
        )
        written.append(_rel(dest, root))
        per_stream.append({
            'stream': stream,
            'file': _rel(path, root),
            'output': _rel(dest, root),
            'rows_in': result['rows_in'],
            'record_count': result['rows_out'],
            'duplicates': len(result['duplicates']),
            'flags': len(result['flags']),
        })

    # The manifest declares required fields, identity keys and freshness windows but no type
    # contract. TYPE_CONTRACT in this script is the closure, and it is step-scoped, not promoted.
    quality_notes.append({
        'note': 'type_contract_is_step_scoped',
        'detail': (
            'fixture-manifest.json declares required fields, identity keys and freshness '
            'windows but no value types. The TYPE_CONTRACT table in this script is that '
            'closure. It is not a promoted schema; if accepted it belongs in DATA_CONTRACT.md '
            'and needs a named human.'
        ),
    })

    stop_conditions: list[str] = []
    if all_rejects:
        stop_conditions.append(
            f'{len(all_rejects)} row(s) were rejected and withheld from the verified layer. '
            'A human must accept the withholdings before the run continues.'
        )
    if all_flags:
        stop_conditions.append(
            f'{len(all_flags)} quality flag(s) were raised (stale timestamps and/or type '
            'violations). Recipe stop condition: outputs must not make unsupported analytical '
            'claims, so a score built on flagged rows needs human acceptance first.'
        )

    counts_by_stream = {p['stream']: p['record_count'] for p in per_stream}
    return {
        'workflow': WORKFLOW_NAME,
        'workflow_slug': WORKFLOW_SLUG,
        'node': NODE_NAME,
        'node_type': NODE_TYPE,
        'classification': CLASSIFICATION,
        'recipe': f'recipes/{WORKFLOW_SLUG}.md',
        'step': 4,
        'step_name': NODE_NAME,
        'run_id': ident['run_id'],
        'fixture_set': ident['fixture_set'],
        'step3_input_dir': _rel(src_dir, root),
        # --- the six fields the recipe declares for this step ---
        'verified_records': counts_by_stream,
        'record_count': sum(counts_by_stream.values()),
        'duplicates': all_duplicates,
        'rejects': all_rejects,
        'flags': all_flags,
        'quality_notes': quality_notes,
        # ---
        'verified_records_note': (
            'Counts per stream. The records themselves are in the per-stream files under '
            'verified_output_paths, so this summary stays readable.'
        ),
        'duplicate_counting_rule': rules['duplicate_counting_rule'],
        'identity_keys': rules['identity_keys'],
        'freshness_policy': rules['freshness_policy'],
        'per_stream': per_stream,
        'summary': {
            'streams': len(per_stream),
            'rows_in': sum(p['rows_in'] for p in per_stream),
            'rows_out': sum(p['record_count'] for p in per_stream),
            'duplicates': len(all_duplicates),
            'duplicates_by_basis': {
                b: sum(1 for d in all_duplicates if d['basis'] == b)
                for b in sorted({d['basis'] for d in all_duplicates})
            },
            'rejects': len(all_rejects),
            'flags': len(all_flags),
            'flags_by_kind': {
                k: sum(1 for f in all_flags if f['flag'] == k)
                for k in sorted({f['flag'] for f in all_flags})
            },
            'quality_notes': len(quality_notes),
        },
        'verified_output_dir': _rel(out_dir, root),
        'verified_output_paths': sorted(written),
        'network_access': 'none',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'status': 'stop' if stop_conditions else 'ok',
        'stop_conditions': stop_conditions,
        'next_step': (
            'Findings reported and the run halts. Deduped rows were still written so step 5 '
            'can run once a human accepts the rejects and flags.'
            if stop_conditions else
            f'Step 5 (run-approved-tools) may run against {_rel(out_dir, root)}'
        ),
        'human_gate': {
            'gate': 'Gate 3 - Data-shape gate (quality half)',
            'capacity': '[PA]',
            'cleared_by': None,
            'note': 'An audit reports what it found; it does not say pass (P1).',
        },
    }


def _stopped(stops: list[str], ident: dict[str, Any], rules: dict[str, Any]) -> dict[str, Any]:
    """Build a stop result that still satisfies the step's declared output fields."""
    return {
        'workflow': WORKFLOW_NAME,
        'workflow_slug': WORKFLOW_SLUG,
        'node': NODE_NAME,
        'node_type': NODE_TYPE,
        'classification': CLASSIFICATION,
        'step': 4,
        'step_name': NODE_NAME,
        'run_id': ident.get('run_id'),
        'fixture_set': ident.get('fixture_set'),
        'verified_records': {},
        'record_count': 0,
        'duplicates': [],
        'rejects': [],
        'flags': [],
        'quality_notes': [],
        'verified_output_paths': [],
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'status': 'stop',
        'stop_conditions': stops,
        'next_step': 'Blocked. Resolve the stop conditions above before running step 5.',
    }


def _require_sample_mode() -> None:
    """Enforce --sample: the run envelope must declare sample mode, or this stops.

    The flag is an assertion, not decoration. Without this check `--sample` would be a
    comfortable no-op that someone could pass at a live envelope and feel safe.
    """
    envelope = Path(__file__).resolve().parents[2] / f'data/raw/{WORKFLOW_SLUG}/run-envelope.json'
    if not envelope.is_file():
        return  # nothing declares a mode here; the step's own stop conditions still apply
    try:
        mode = json.loads(envelope.read_text(encoding='utf-8')).get('mode')
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return
    if mode != 'sample':
        raise SystemExit(
            f"--sample was given, but the run envelope declares mode={mode!r}. "
            'Refusing to run: the flag asserts a sample run and this is not one.'
        )


def load_input(sample: Any | None = None) -> dict[str, Any]:
    """Load overrides from --input, --verified-dir, or --fixture-set, plus the optional --output path."""
    parser = argparse.ArgumentParser(description=f'Deduplicate and quality-check records for {WORKFLOW_NAME}.')
    parser.add_argument('--input', help='JSON string or path to a JSON file with overrides (verified_dir, fixture_set).')
    # The recipe's Step Commands table documents --sample for every step, so the step
    # accepts it. It is an assertion, not a no-op: it requires the run to be a sample
    # run and fails if the envelope declares anything else, so `--sample` cannot
    # silently ride along on a live run.
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Require sample mode; fail if the run envelope does not declare it.',
    )
    parser.add_argument('--output', help='Optional path to write the summary JSON.')
    parser.add_argument('--verified-dir', help='Step-3 verified directory to check, repo-relative.')
    parser.add_argument('--fixture-set', choices=('clean', 'defective'), help='Override the envelope fixture_set.')
    args = parser.parse_args()
    if args.sample:
        _require_sample_mode()
    if args.input:
        candidate = Path(args.input)
        text = candidate.read_text(encoding='utf-8') if candidate.exists() else args.input
        data = json.loads(text)
    else:
        data = dict(sample) if isinstance(sample, dict) else {}
    if args.verified_dir:
        data['verified_dir'] = args.verified_dir
    if args.fixture_set:
        data['fixture_set'] = args.fixture_set
    return {'data': data, 'output': args.output}


def emit(data: Any, output_path: str | None = None) -> None:
    """Print JSON to stdout and, when an output path is given, write the same bytes there as UTF-8."""
    text = json.dumps(data, indent=2, sort_keys=True, default=str)
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + '\n', encoding='utf-8', newline='\n')
    print(text)


if __name__ == '__main__':
    payload = load_input({})
    result = transform_quality_check(payload['data'])
    emit(result, payload['output'])
    # Report everything found, then halt (P4).
    raise SystemExit(1 if result['status'] == 'stop' else 0)
