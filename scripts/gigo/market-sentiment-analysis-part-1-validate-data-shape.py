"""Purpose: Validate the shape of ingested records and promote only shape-clean rows into the verified layer.
Input: a step-2 run directory under data/raw/market-sentiment-analysis-part-1/runs/, plus the required-field schema in sample/fixture-manifest.json.
Output: one verified envelope per stream under data/verified/market-sentiment-analysis-part-1/runs/<run_id>-<fixture_set>/, and a summary on stdout carrying record_count, required_fields_present, missing_fields, parse_errors, schema_version.
Side effects: writes into data/verified/ only. No network calls.
Idempotent: Yes; reruns over an unchanged run directory produce byte-identical outputs (timestamps come from the source envelopes, never now()).
Recipe: recipes/market-sentiment-analysis-part-1.md

Layer contract (docs/architecture.md 5.2): GIGO may read data/raw/, must validate against a
declared schema, must write only data/verified/, and must not make network requests. Nothing
enters the verified layer without passing this step (P2).

SCOPE -- what this step is responsible for catching:
    This step owns shape only. Against the frozen corpus it must surface exactly 8 of the 18
    catalogued defects, in the fields fixture-manifest.json names:
      missing_fields : D01 (key absent), D07 (key absent), D08 (present but null), D14
      parse_errors   : D09 (row is an array), D15 (row is a string), D18 (file will not parse)
      record_count   : D12 (envelope under-reports its own payload by one row)
    The other 10 -- duplicates, stale timestamps, type violations -- belong to step 4 and are
    deliberately NOT detected here. Catching them early would make step 4 untestable.

    A wrong-typed value is none of this step's five declared output fields; the recipe's
    contract has no type_errors field. Rather than smuggle type checks into missing_fields,
    this step leaves them alone and records the gap in types_deferred_to_step_4. The
    contract defect is logged, not silently worked around (P6).

Constitution notes:
    P2 - only rows that pass shape validation are written to data/verified/. Failing rows are
         recorded with their locators and excluded, never quietly repaired.
    P3 - record_count is always recomputed and reported beside the count the source declared;
         a count no record produced is not evidence.
    P4 - an unparseable file or a malformed row is a hard stop with a nonzero exit. The step
         reports every finding first, then halts, so one early rejection cannot hide the rest.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKFLOW_NAME = 'Market Sentiment Analysis - Part 1'
WORKFLOW_SLUG = 'market-sentiment-analysis-part-1'
NODE_NAME = 'Validate data shape'
NODE_TYPE = 'recipe-step'
CLASSIFICATION = 'gigo'

RAW_ROOT = f'data/raw/{WORKFLOW_SLUG}'
VERIFIED_ROOT = f'data/verified/{WORKFLOW_SLUG}'
ENVELOPE_PATH = f'{RAW_ROOT}/run-envelope.json'
MANIFEST_PATH = f'{RAW_ROOT}/sample/fixture-manifest.json'

# Where each stream's rows live inside its envelope, and what one row must look like.
STREAM_SHAPES = {
    'price': {
        'rows_at': 'records[]',
        'row_container': 'Global Quote',
        'schema_key': 'price_global_quote',
    },
    'news': {
        'rows_at': 'records[]',
        'row_container': None,
        'schema_key': 'news_article',
    },
    'reddit': {
        'rows_at': 'records[0].data.children[].data',
        'row_container': None,
        'schema_key': 'reddit_t3_data',
    },
}


def _rel(path: Path, root: Path) -> str:
    """Return a repo-relative POSIX path string."""
    return path.relative_to(root).as_posix()


def _load_schema(root: Path) -> tuple[dict[str, Any], list[str]]:
    """Load the required-field schema from the fixture manifest.

    DATA_CONTRACT.md carries no entry for this recipe, so the manifest is the only declared
    schema that exists. Reading it here rather than restating it keeps the validator and the
    corpus from drifting apart.
    """
    path = root / MANIFEST_PATH
    if not path.is_file():
        return {}, [f'Required-field schema is missing: {MANIFEST_PATH}.']
    try:
        manifest = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as error:
        return {}, [f'Required-field schema does not parse: {MANIFEST_PATH} ({error}).']
    required = manifest.get('required_fields', {})
    if not required:
        return {}, [f'{MANIFEST_PATH} declares no required_fields.']
    return {
        'schema_version': manifest.get('manifest_version'),
        'schema_source': MANIFEST_PATH,
        'required_fields': required,
        'null_rule': required.get('null_rule'),
    }, []


def _resolve_run_dir(root: Path, overrides: dict[str, Any]) -> tuple[Path | None, dict[str, Any], list[str]]:
    """Work out which step-2 run directory to validate."""
    if overrides.get('run_dir'):
        run_dir = root / overrides['run_dir']
        if not run_dir.is_dir():
            return None, {}, [f'Run directory does not exist: {overrides["run_dir"]}.']
        name = run_dir.name
        run_id, _, fixture_set = name.rpartition('-')
        return run_dir, {'run_id': run_id, 'fixture_set': fixture_set}, []

    env_path = root / ENVELOPE_PATH
    if not env_path.is_file():
        return None, {}, [f'Run envelope is missing: {ENVELOPE_PATH}, and no --run-dir was given.']
    try:
        envelope = json.loads(env_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as error:
        return None, {}, [f'Run envelope does not parse: {ENVELOPE_PATH} ({error}).']

    fixture_set = overrides.get('fixture_set') or envelope.get('fixture_set')
    run_id = envelope.get('run_id')
    if not run_id or not fixture_set:
        return None, {}, ['Run envelope is missing run_id or fixture_set.']
    run_dir = root / f'{RAW_ROOT}/runs/{run_id}-{fixture_set}'
    if not run_dir.is_dir():
        return None, {}, [
            f'Run directory does not exist: {_rel(run_dir, root)}. Run step 2 '
            '(ingest-inputs) first.'
        ]
    return run_dir, {'run_id': run_id, 'fixture_set': fixture_set}, []


def _stream_for(file_name: str) -> str | None:
    """Infer the stream from an ingested file name."""
    if 'price' in file_name:
        return 'price'
    if 'news' in file_name:
        return 'news'
    if 'reddit' in file_name:
        return 'reddit'
    return None


def _extract_rows(stream: str, records: Any) -> tuple[list[tuple[str, Any]], list[dict[str, Any]]]:
    """Pull out (locator, row) pairs for a stream. Malformed containers are reported, never raised.

    Returns (rows, malformed) where malformed entries describe rows that are not objects --
    D09 (an array where an object is required) and D15 (a string where an object is required).
    """
    rows: list[tuple[str, Any]] = []
    malformed: list[dict[str, Any]] = []

    if stream == 'reddit':
        # records[0].data.children[].data
        if not isinstance(records, list) or not records:
            malformed.append({'locator': 'records', 'detail': f'expected a non-empty list, got {type(records).__name__}'})
            return rows, malformed
        container = records[0]
        if not isinstance(container, dict):
            malformed.append({'locator': 'records[0]', 'detail': f'expected an object, got {type(container).__name__}'})
            return rows, malformed
        children = (container.get('data') or {}).get('children') if isinstance(container.get('data'), dict) else None
        if not isinstance(children, list):
            malformed.append({'locator': 'records[0].data.children', 'detail': 'expected a list of t3 entries'})
            return rows, malformed
        for i, child in enumerate(children):
            loc = f'records[0].data.children[{i}].data'
            if not isinstance(child, dict):
                malformed.append({'locator': f'records[0].data.children[{i}]', 'detail': f'expected an object, got {type(child).__name__}'})
                continue
            data = child.get('data')
            if not isinstance(data, dict):
                # D15: data is a string. It cannot be field-checked, so it is malformed.
                malformed.append({'locator': loc, 'detail': f'expected an object, got {type(data).__name__}'})
                continue
            rows.append((loc, data))
        return rows, malformed

    if not isinstance(records, list):
        malformed.append({'locator': 'records', 'detail': f'expected a list, got {type(records).__name__}'})
        return rows, malformed

    for i, row in enumerate(records):
        loc = f'records[{i}]'
        if not isinstance(row, dict):
            # D09: the row is a JSON array. Valid JSON, invalid record.
            malformed.append({'locator': loc, 'detail': f'expected an object, got {type(row).__name__}'})
            continue
        if stream == 'price':
            quote = row.get('Global Quote')
            if not isinstance(quote, dict):
                malformed.append({'locator': f'{loc}."Global Quote"', 'detail': f'expected an object, got {type(quote).__name__}'})
                continue
            rows.append((f'{loc}."Global Quote"', quote))
        else:
            rows.append((loc, row))
    return rows, malformed


def _check_required(rows: list[tuple[str, Any]], required: list[str]) -> tuple[list[dict[str, Any]], list[int]]:
    """Check required fields on each row. A field present with value null counts as missing."""
    missing: list[dict[str, Any]] = []
    failing: list[int] = []
    for index, (locator, row) in enumerate(rows):
        absent = [f for f in required if f not in row]
        nulls = [f for f in required if f in row and row[f] is None]
        if absent or nulls:
            failing.append(index)
            for field in absent:
                missing.append({'locator': locator, 'field': field, 'reason': 'key_absent'})
            for field in nulls:
                missing.append({'locator': locator, 'field': field, 'reason': 'present_but_null'})
    return missing, failing


def _validate_file(path: Path, root: Path, schema: dict[str, Any]) -> dict[str, Any]:
    """Validate one ingested file. Never raises on bad content."""
    rel = _rel(path, root)
    stream = _stream_for(path.name)
    finding: dict[str, Any] = {
        'file': rel,
        'stream': stream,
        'parse_error': None,
        'record_count': None,
        'source_declared_record_count': None,
        'count_matches_declared': None,
        'required_fields': [],
        'required_fields_present': None,
        'missing_fields': [],
        'malformed_rows': [],
        'rows_promoted': 0,
        'promoted_records': None,
        'source_envelope': None,
    }
    if stream is None:
        finding['parse_error'] = {'file': rel, 'detail': 'cannot infer stream from file name'}
        return finding

    try:
        envelope = json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        # D18. Reported, not raised; the run halts at the end, after everything is collected.
        finding['parse_error'] = {
            'file': rel,
            'detail': f'{type(error).__name__}: {error}',
            'note': 'File will not parse, so no row in it can be validated or promoted.',
        }
        return finding

    finding['source_envelope'] = {
        'source_name': envelope.get('source_name'),
        'source_type': envelope.get('source_type'),
        'fetched_at': envelope.get('fetched_at'),
        'sample_mode': envelope.get('sample_mode'),
        'source_path': (envelope.get('_provenance') or {}).get('source_path'),
        'source_sha256': (envelope.get('_provenance') or {}).get('source_sha256'),
    }

    rows, malformed = _extract_rows(stream, envelope.get('records'))
    schema_key = STREAM_SHAPES[stream]['schema_key']
    required = list(schema['required_fields'].get(schema_key, []))
    finding['required_fields'] = required

    missing, failing_idx = _check_required(rows, required)

    # record_count is always recomputed. The declared value is reported beside it, never
    # substituted for it -- that comparison is what surfaces D12.
    declared = envelope.get('source_declared_record_count')
    recount = len(rows) + len(malformed)
    finding.update({
        'record_count': recount,
        'record_count_basis': STREAM_SHAPES[stream]['rows_at'] + ' (malformed rows included in the count)',
        'source_declared_record_count': declared,
        'count_matches_declared': (declared == recount) if declared is not None else None,
        'missing_fields': missing,
        'malformed_rows': malformed,
        'required_fields_present': not missing,
    })

    # Only rows that pass shape validation are promoted (P2).
    promoted = [row for i, (_loc, row) in enumerate(rows) if i not in set(failing_idx)]
    finding['rows_promoted'] = len(promoted)
    finding['promoted_records'] = promoted
    return finding


def validate_data_shape(payload: Any = None, root: Path | None = None) -> dict[str, Any]:
    """Validate ingested record shape and promote shape-clean rows to the verified layer.

    Purpose: enforce the required-field contract before any scoring step sees the data.
    Input: optional dict with 'run_dir' or 'fixture_set'.
    Output: dict with record_count, required_fields_present, missing_fields, parse_errors, schema_version.
    Side effects: writes one file per stream into data/verified/.../runs/<run_id>-<fixture_set>/.
    Idempotent: yes; no wall-clock value enters the written artifacts.
    Recipe: recipes/market-sentiment-analysis-part-1.md
    """
    root = root or Path(__file__).resolve().parents[2]
    overrides = payload if isinstance(payload, dict) else {}

    schema, schema_stops = _load_schema(root)
    if schema_stops:
        return _stopped(schema_stops, {}, schema)

    run_dir, ident, stops = _resolve_run_dir(root, overrides)
    if stops or run_dir is None:
        return _stopped(stops, ident, schema)

    files = sorted(p for p in run_dir.iterdir() if p.is_file())
    if not files:
        return _stopped([f'Run directory is empty: {_rel(run_dir, root)}.'], ident, schema)

    findings = [_validate_file(p, root, schema) for p in files]

    out_dir_rel = f'{VERIFIED_ROOT}/runs/{ident["run_id"]}-{ident["fixture_set"]}'
    out_dir = root / out_dir_rel
    out_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    for f in findings:
        if f['parse_error'] or f['promoted_records'] is None:
            continue
        verified = {
            'workflow': WORKFLOW_NAME,
            'node': NODE_NAME,
            'classification': CLASSIFICATION,
            'stream': f['stream'],
            'schema_version': schema['schema_version'],
            'schema_source': schema['schema_source'],
            'required_fields': f['required_fields'],
            'record_count': f['rows_promoted'],
            'record_count_basis': 'rows that passed shape validation and were promoted',
            'records': f['promoted_records'],
            'shape_validation': {
                'rows_seen': f['record_count'],
                'rows_promoted': f['rows_promoted'],
                'rows_withheld': f['record_count'] - f['rows_promoted'],
                'missing_fields': f['missing_fields'],
                'malformed_rows': f['malformed_rows'],
                'source_declared_record_count': f['source_declared_record_count'],
                'count_matches_declared': f['count_matches_declared'],
            },
            'types_deferred_to_step_4': (
                'Type violations are not checked here. This step has no declared field for '
                'them, so per fixture-manifest.json they surface in step 4 flags.'
            ),
            'duplicates_deferred_to_step_4': True,
            'freshness_deferred_to_step_4': True,
            '_provenance': {
                'run_id': ident['run_id'],
                'fixture_set': ident['fixture_set'],
                'validated_by': f'scripts/gigo/{WORKFLOW_SLUG}-validate-data-shape.py',
                'raw_input': f['file'],
                'source_envelope': f['source_envelope'],
            },
        }
        dest = out_dir / Path(f['file']).name
        # newline='\n' is required: on Windows write_text would translate to CRLF, which
        # changes every artifact's SHA-256 by platform and breaks the provenance trace.
        dest.write_text(
            json.dumps(verified, indent=2, sort_keys=True, default=str) + '\n',
            encoding='utf-8',
            newline='\n',
        )
        written.append(_rel(dest, root))
        f['verified_output'] = _rel(dest, root)

    parse_errors = [f['parse_error'] for f in findings if f['parse_error']]
    # Malformed rows are parse-level failures per the manifest: D09 and D15 map to parse_errors.
    for f in findings:
        for m in f['malformed_rows']:
            parse_errors.append({
                'file': f['file'],
                'locator': m['locator'],
                'detail': m['detail'],
                'note': 'Row is valid JSON but not a valid record; it was withheld from the verified layer.',
            })

    all_missing = [dict(m, file=f['file']) for f in findings for m in f['missing_fields']]
    count_mismatches = [
        {
            'file': f['file'],
            'declared': f['source_declared_record_count'],
            'recounted': f['record_count'],
            'note': 'Envelope disagrees with its own payload; the recount governs.',
        }
        for f in findings
        if f['count_matches_declared'] is False
    ]

    stop_conditions: list[str] = []
    for pe in parse_errors:
        where = pe.get('locator') or pe['file']
        stop_conditions.append(
            f'Shape validation failed at {where}: {pe["detail"]}. Recipe stop condition: '
            'generated outputs must not omit provenance or make unsupported claims, so the '
            'affected rows are withheld rather than promoted.'
        )

    return {
        'workflow': WORKFLOW_NAME,
        'workflow_slug': WORKFLOW_SLUG,
        'node': NODE_NAME,
        'node_type': NODE_TYPE,
        'classification': CLASSIFICATION,
        'recipe': f'recipes/{WORKFLOW_SLUG}.md',
        'step': 3,
        'step_name': NODE_NAME,
        'run_id': ident['run_id'],
        'fixture_set': ident['fixture_set'],
        'raw_input_dir': _rel(run_dir, root),
        # --- the five fields the recipe declares for this step ---
        'record_count': {f['stream']: f['record_count'] for f in findings if f['stream'] and f['record_count'] is not None},
        'required_fields_present': all(f['required_fields_present'] for f in findings if f['required_fields_present'] is not None),
        'missing_fields': all_missing,
        'parse_errors': parse_errors,
        'schema_version': schema['schema_version'],
        # ---
        'schema_source': schema['schema_source'],
        'null_rule': schema['null_rule'],
        'count_mismatches': count_mismatches,
        'per_file': [
            {
                'file': f['file'],
                'stream': f['stream'],
                'record_count': f['record_count'],
                'source_declared_record_count': f['source_declared_record_count'],
                'count_matches_declared': f['count_matches_declared'],
                'missing_field_entries': len(f['missing_fields']),
                'malformed_rows': len(f['malformed_rows']),
                'rows_promoted': f['rows_promoted'],
                'verified_output': f.get('verified_output'),
                'parse_error': bool(f['parse_error']),
            }
            for f in findings
        ],
        'summary': {
            'files_seen': len(findings),
            'files_promoted': len(written),
            'files_unparseable': sum(1 for f in findings if f['parse_error']),
            'rows_seen': sum(f['record_count'] or 0 for f in findings),
            'rows_promoted': sum(f['rows_promoted'] for f in findings),
            'missing_field_entries': len(all_missing),
            'malformed_rows': sum(len(f['malformed_rows']) for f in findings),
            'count_mismatches': len(count_mismatches),
        },
        'verified_output_dir': out_dir_rel,
        'verified_output_paths': sorted(written),
        'types_deferred_to_step_4': (
            'This step has no declared field for a type violation. Per fixture-manifest.json, '
            'D02/D11/D17 surface in step 4 flags. Logged as a P6 contract defect, not worked around.'
        ),
        'deferred_to_step_4': ['duplicates', 'stale timestamps', 'type violations'],
        'network_access': 'none',
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'status': 'stop' if stop_conditions else 'ok',
        'stop_conditions': stop_conditions,
        'next_step': (
            f'Findings reported and the run halts. Shape-clean rows were still promoted to '
            f'{out_dir_rel} so step 4 can run against them once a human accepts the withholdings.'
            if stop_conditions else
            f'Step 4 (transform-quality-check) may run against {out_dir_rel}'
        ),
        'human_gate': {
            'gate': 'Gate 3 - Data-shape gate',
            'capacity': '[PA]',
            'cleared_by': None,
            'note': 'An audit reports what it found; it does not say pass. Adequacy is the human gate (P1).',
        },
    }


def _stopped(stops: list[str], ident: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    """Build a stop result that still satisfies the step's declared output fields."""
    return {
        'workflow': WORKFLOW_NAME,
        'workflow_slug': WORKFLOW_SLUG,
        'node': NODE_NAME,
        'node_type': NODE_TYPE,
        'classification': CLASSIFICATION,
        'step': 3,
        'step_name': NODE_NAME,
        'run_id': ident.get('run_id'),
        'fixture_set': ident.get('fixture_set'),
        'record_count': {},
        'required_fields_present': None,
        'missing_fields': [],
        'parse_errors': [],
        'schema_version': schema.get('schema_version'),
        'verified_output_paths': [],
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'status': 'stop',
        'stop_conditions': stops,
        'next_step': 'Blocked. Resolve the stop conditions above before running step 4.',
    }


def load_input(sample: Any | None = None) -> dict[str, Any]:
    """Load overrides from --input, --run-dir, or --fixture-set, plus the optional --output path."""
    parser = argparse.ArgumentParser(description=f'Validate ingested record shape for {WORKFLOW_NAME}.')
    parser.add_argument('--input', help='JSON string or path to a JSON file with overrides (run_dir, fixture_set).')
    parser.add_argument('--output', help='Optional path to write the summary JSON.')
    parser.add_argument('--run-dir', help='Step-2 run directory to validate, repo-relative.')
    parser.add_argument('--fixture-set', choices=('clean', 'defective'), help='Override the envelope fixture_set.')
    args = parser.parse_args()
    if args.input:
        candidate = Path(args.input)
        text = candidate.read_text(encoding='utf-8') if candidate.exists() else args.input
        data = json.loads(text)
    else:
        data = dict(sample) if isinstance(sample, dict) else {}
    if args.run_dir:
        data['run_dir'] = args.run_dir
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
    result = validate_data_shape(payload['data'])
    emit(result, payload['output'])
    # Report everything found, then halt (P4).
    raise SystemExit(1 if result['status'] == 'stop' else 0)
