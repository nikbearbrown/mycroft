"""Purpose: Ingest the declared sources for this recipe into the raw layer, transporting them without repair.
Input: data/raw/market-sentiment-analysis-part-1/run-envelope.json plus the fixture set it names; optional JSON overrides via --input.
Output: one raw envelope per source file under data/raw/market-sentiment-analysis-part-1/runs/<run_id>-<fixture_set>/, plus a run summary on stdout carrying records, source_name, source_type, fetched_at, sample_mode, rejects.
Side effects: writes into data/raw/ only. No network calls in sample mode; live mode is unimplemented and stops.
Idempotent: Yes; the same envelope and fixture set produce byte-identical outputs, because fetched_at comes from frozen_clock and never from now().
Recipe: recipes/market-sentiment-analysis-part-1.md

Layer contract (docs/architecture.md 5.2): ingest may touch the network and must write only
to data/raw/. It must not write data/verified/ and must not be called by a tool script.

TRANSPORT, DO NOT REPAIR -- the load-bearing rule of this step:
    This script carries source payloads into the raw layer verbatim. It does NOT recount
    records, drop malformed rows, fill missing fields, coerce types, or dedupe. Those are
    the GIGO layer's job (steps 3 and 4), and the fixture corpus exists to prove they do
    it. Two catalogued defects make the point concretely:
      - D12: the defective news envelope declares record_count 7 while holding 8 rows. This
        step preserves the declared 7 verbatim under source_declared_record_count. Were
        ingest to "helpfully" recount, step 3's record_count check would have nothing left
        to catch.
      - D18: news-finnhub-unparseable.json.broken does not parse. This step neither raises
        nor silently skips it; it copies the bytes through unchanged and records a reject,
        so step 3 can attempt the parse itself and report parse_errors.
    An ingest script that cleans data destroys the evidence that cleaning was needed.

Constitution notes:
    P2 - only ingest scripts touch sources, and nothing here enters the verified layer.
    P3 - every output carries _provenance: the source path, its SHA-256, and the run that
         produced it, so a later score can be walked back to a named file.
    P4 - a missing envelope, an unreadable fixture manifest, or live mode without approval
         is a hard stop with a nonzero exit, not a warning.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKFLOW_NAME = 'Market Sentiment Analysis - Part 1'
WORKFLOW_SLUG = 'market-sentiment-analysis-part-1'
NODE_NAME = 'Ingest declared inputs'
NODE_TYPE = 'recipe-step'
CLASSIFICATION = 'ingest'

RAW_ROOT = f'data/raw/{WORKFLOW_SLUG}'
ENVELOPE_PATH = f'{RAW_ROOT}/run-envelope.json'

# Human-readable source identity per stream, matching the fixture envelopes.
SOURCE_NAMES = {
    'price': 'Alpha Vantage GLOBAL_QUOTE',
    'news': 'Finnhub company-news',
    'reddit': 'Reddit search.json (r/wallstreetbets)',
}

REQUIRED_ENVELOPE_FIELDS = ('run_id', 'mode', 'fixture_set', 'frozen_clock')


def _sha256_bytes(data: bytes) -> str:
    """Return the SHA-256 of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def _rel(path: Path, root: Path) -> str:
    """Return a repo-relative POSIX path string."""
    return path.relative_to(root).as_posix()


def _load_envelope(root: Path, overrides: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Load and check the run envelope. Returns (envelope, stop_conditions)."""
    path = root / ENVELOPE_PATH
    if not path.is_file():
        return {}, [
            f'Run envelope is missing: {ENVELOPE_PATH}. Gate 2 (scope gate) cannot clear, '
            'so no run may begin.'
        ]
    try:
        envelope = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as error:
        return {}, [f'Run envelope does not parse: {ENVELOPE_PATH} ({error}).']

    stops: list[str] = []
    for field in REQUIRED_ENVELOPE_FIELDS:
        if not envelope.get(field):
            stops.append(f'Run envelope is missing required field {field!r}.')

    # Overrides are applied after the file is read, so the envelope stays authoritative
    # and the override is visible in the emitted result.
    if overrides.get('fixture_set'):
        envelope['fixture_set'] = overrides['fixture_set']
        envelope['fixture_set_overridden'] = True

    if envelope.get('fixture_set') not in ('clean', 'defective'):
        stops.append(
            f'fixture_set must be "clean" or "defective", got {envelope.get("fixture_set")!r}.'
        )

    mode = envelope.get('mode')
    if mode not in ('sample', 'live'):
        stops.append(f'mode must be "sample" or "live", got {mode!r}.')
    elif mode == 'live':
        creds = envelope.get('live_mode_requirements', {}).get('credentials', [])
        stops.append(
            'Live mode is not implemented and is not approved. Recipe stop condition: live '
            'external calls require explicit human approval (gate 5). Implementing it needs '
            'real HTTP fetchers, credentials read from the environment '
            f'({", ".join(creds) or "unspecified"}), and 401/403/429/timeout/empty-200 '
            'handling that the current fixture corpus explicitly does not cover.'
        )
    return envelope, stops


def _sources_from_manifest(root: Path, envelope: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    """Select the manifest-declared files belonging to the requested fixture set.

    Manifest-driven on purpose: fixture-manifest.json is the declared inventory of the
    sample corpus, so a file added or renamed there is picked up without editing this
    script, and the two cannot drift apart silently.
    """
    manifest_rel = envelope.get('fixture_manifest') or f'{RAW_ROOT}/sample/fixture-manifest.json'
    path = root / manifest_rel
    if not path.is_file():
        return [], [f'Fixture manifest is missing: {manifest_rel}.']
    try:
        manifest = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as error:
        return [], [f'Fixture manifest does not parse: {manifest_rel} ({error}).']

    fixture_root = envelope.get('fixture_root') or f'{RAW_ROOT}/sample'
    wanted = envelope['fixture_set'] + '/'
    selected = [
        {
            'stream': entry['source'],
            'rel_path': f'{fixture_root}/{entry["path"]}',
            'file_name': Path(entry['path']).name,
            'manifest_rows': entry.get('rows'),
            'manifest_rows_basis': entry.get('rows_basis'),
            'manifest_defects': entry.get('defects', []),
        }
        for entry in manifest.get('files', [])
        if str(entry.get('path', '')).startswith(wanted)
    ]
    if not selected:
        return [], [f'Fixture manifest lists no files under {wanted!r}.']
    return selected, []


def _ingest_one(
    source: dict[str, Any], root: Path, out_dir: Path, envelope: dict[str, Any]
) -> dict[str, Any]:
    """Transport one source file into the run directory. Never repairs, never raises on bad content."""
    src = root / source['rel_path']
    stream = source['stream']
    result: dict[str, Any] = {
        'stream': stream,
        'source_name': SOURCE_NAMES.get(stream, stream),
        'source_path': source['rel_path'],
        'manifest_defects': source['manifest_defects'],
        'source_sha256': None,
        'source_size_bytes': None,
        'written_to': None,
        'parsed': None,
        'declared_record_count': None,
        'reject': None,
    }
    if not src.is_file():
        result['reject'] = {
            'reason': 'source_missing',
            'path': source['rel_path'],
            'detail': 'file not found',
        }
        return result

    raw = src.read_bytes()
    result['source_sha256'] = _sha256_bytes(raw)
    result['source_size_bytes'] = len(raw)

    provenance = {
        'run_id': envelope['run_id'],
        'recipe': envelope.get('recipe'),
        'ingested_by': f'scripts/ingest/{WORKFLOW_SLUG}-ingest-inputs.py',
        'source_path': source['rel_path'],
        'source_sha256': result['source_sha256'],
        'fixture_set': envelope['fixture_set'],
        'manifest_declared_rows': source['manifest_rows'],
        'manifest_declared_rows_basis': source['manifest_rows_basis'],
        'transport_only': 'Records are verbatim. This step does not recount, dedupe, drop, or coerce.',
    }

    try:
        payload = json.loads(raw.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        # D18 path. Copy the bytes through unchanged, preserving the .broken suffix so the
        # file stays invisible to the *.json globs in gate 3 and conformance.mjs, and record
        # a reject. Step 3 attempts the parse itself and reports parse_errors.
        dest = out_dir / source['file_name']
        shutil.copyfile(src, dest)
        result.update({
            'parsed': False,
            'written_to': _rel(dest, root),
            'reject': {
                'reason': 'unparseable_source',
                'path': source['rel_path'],
                'detail': f'{type(error).__name__}: {error}',
                'copied_to': _rel(dest, root),
                'note': (
                    'Bytes copied through unchanged. Step 3 must report this in parse_errors '
                    'and halt, rather than raising an unhandled exception.'
                ),
            },
        })
        return result

    is_dict = isinstance(payload, dict)
    # Preserve the source's own declared count verbatim; never substitute a recount (D12).
    declared = payload.get('record_count') if is_dict else None
    records = payload.get('records') if is_dict else payload

    out = {
        'workflow': WORKFLOW_NAME,
        'node': NODE_NAME,
        'classification': CLASSIFICATION,
        'stream': stream,
        # --- the six fields the recipe declares for this step ---
        'records': records,
        'source_name': (payload.get('source_name') if is_dict else None) or SOURCE_NAMES.get(stream, stream),
        'source_type': (payload.get('source_type') if is_dict else None) or 'http_json',
        'fetched_at': envelope['frozen_clock'],
        'sample_mode': envelope['mode'] == 'sample',
        'rejects': [],
        # --- carried through unmodified, for the GIGO layer to check against ---
        'source_declared_record_count': declared,
        'source_declared_record_count_basis': payload.get('record_count_basis') if is_dict else None,
        'source_url_or_path': payload.get('source_url_or_path') if is_dict else None,
        'source_errors': payload.get('errors') if is_dict else None,
        'source_fixture_block': payload.get('_fixture') if is_dict else None,
        'live_call_performed': False,
        'recount_performed': False,
        'recount_note': (
            'Deliberately absent. Recounting and comparing against '
            'source_declared_record_count is step 3 (validate-data-shape).'
        ),
        '_provenance': provenance,
    }
    dest = out_dir / source['file_name']
    # newline='\n' is required: on Windows write_text would translate to CRLF, which changes
    # every artifact's SHA-256 by platform and breaks the provenance trace.
    dest.write_text(
        json.dumps(out, indent=2, sort_keys=True, default=str) + '\n',
        encoding='utf-8',
        newline='\n',
    )
    result.update({
        'parsed': True,
        'written_to': _rel(dest, root),
        'declared_record_count': declared,
    })
    return result


def _stopped(stops: list[str], envelope: dict[str, Any]) -> dict[str, Any]:
    """Build a stop result that still satisfies the step's declared output fields."""
    return {
        'workflow': WORKFLOW_NAME,
        'workflow_slug': WORKFLOW_SLUG,
        'node': NODE_NAME,
        'node_type': NODE_TYPE,
        'classification': CLASSIFICATION,
        'step': 2,
        'step_name': NODE_NAME,
        'records': {},
        'source_name': [],
        'source_type': None,
        'fetched_at': envelope.get('frozen_clock'),
        'sample_mode': envelope.get('mode') == 'sample',
        'rejects': [],
        'run_id': envelope.get('run_id'),
        'mode': envelope.get('mode'),
        'fixture_set': envelope.get('fixture_set'),
        'raw_output_dir': None,
        'raw_output_paths': [],
        'live_call_performed': False,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'status': 'stop',
        'stop_conditions': stops,
        'next_step': 'Blocked. Resolve the stop conditions above before running step 3.',
    }


def ingest_inputs(payload: Any = None, root: Path | None = None) -> dict[str, Any]:
    """Ingest the declared sources into the raw layer, verbatim.

    Purpose: transport source payloads into data/raw/ for the GIGO layer to validate.
    Input: optional dict with 'fixture_set' ('clean' or 'defective') overriding the envelope.
    Output: dict with records, source_name, source_type, fetched_at, sample_mode, rejects.
    Side effects: writes one file per source into data/raw/.../runs/<run_id>-<fixture_set>/.
    Idempotent: yes; fetched_at comes from frozen_clock, so reruns are byte-identical.
    Recipe: recipes/market-sentiment-analysis-part-1.md
    """
    root = root or Path(__file__).resolve().parents[2]
    overrides = payload if isinstance(payload, dict) else {}

    envelope, stops = _load_envelope(root, overrides)
    if stops:
        return _stopped(stops, envelope)

    sources, manifest_stops = _sources_from_manifest(root, envelope)
    if manifest_stops:
        return _stopped(manifest_stops, envelope)

    run_dir_rel = f'{RAW_ROOT}/runs/{envelope["run_id"]}-{envelope["fixture_set"]}'
    out_dir = root / run_dir_rel
    out_dir.mkdir(parents=True, exist_ok=True)

    results = [_ingest_one(s, root, out_dir, envelope) for s in sources]
    rejects = [r['reject'] for r in results if r['reject']]
    written = [r['written_to'] for r in results if r['written_to']]

    by_stream: dict[str, list[dict[str, Any]]] = {}
    for r in results:
        by_stream.setdefault(r['stream'], []).append({
            'source_path': r['source_path'],
            'written_to': r['written_to'],
            'parsed': r['parsed'],
            'declared_record_count': r['declared_record_count'],
            'source_sha256': r['source_sha256'],
            'manifest_defects': r['manifest_defects'],
        })

    missing = [r for r in results if r['reject'] and r['reject']['reason'] == 'source_missing']
    stop_conditions = [
        f'Declared source is missing: {r["source_path"]}. Recipe stop condition: required '
        'local source data is missing and no approved live-call path is available.'
        for r in missing
    ]

    return {
        'workflow': WORKFLOW_NAME,
        'workflow_slug': WORKFLOW_SLUG,
        'node': NODE_NAME,
        'node_type': NODE_TYPE,
        'classification': CLASSIFICATION,
        'recipe': envelope.get('recipe'),
        'step': 2,
        'step_name': NODE_NAME,
        'run_id': envelope['run_id'],
        'mode': envelope['mode'],
        'fixture_set': envelope['fixture_set'],
        'fixture_set_overridden': bool(envelope.get('fixture_set_overridden')),
        # --- the six fields the recipe declares for this step ---
        'records': by_stream,
        'source_name': [SOURCE_NAMES.get(s, s) for s in sorted({r['stream'] for r in results})],
        'source_type': 'http_json',
        'fetched_at': envelope['frozen_clock'],
        'sample_mode': envelope['mode'] == 'sample',
        'rejects': rejects,
        # ---
        'summary': {
            'sources_declared': len(sources),
            'files_written': len(written),
            'parsed_ok': sum(1 for r in results if r['parsed'] is True),
            'unparseable': sum(1 for r in results if r['parsed'] is False),
            'missing': len(missing),
            'defects_carried': sorted({d for r in results for d in r['manifest_defects']}),
        },
        'raw_output_dir': run_dir_rel,
        'raw_output_paths': sorted(written),
        'live_call_performed': False,
        'network_access': 'none - sample mode reads local fixtures only',
        'transport_only': True,
        'transport_only_note': (
            'No recount, dedupe, drop, or coercion was performed. Record-level validation '
            'belongs to steps 3 and 4.'
        ),
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'status': 'stop' if stop_conditions else 'ok',
        'stop_conditions': stop_conditions,
        'next_step': (
            'Blocked. Resolve the stop conditions above before running step 3.'
            if stop_conditions else
            f'Step 3 (validate-data-shape) may run against {run_dir_rel}'
        ),
        'human_gate': {
            'gate': 'Gate 2 - Scope gate',
            'capacity': '[PF]',
            'cleared_by': None,
            'note': 'The declared mode is evidence for the gate, not the gate decision (P1).',
        },
    }


def load_input(sample: Any | None = None) -> dict[str, Any]:
    """Load overrides from --input or the --fixture-set shorthand, plus the optional --output path."""
    parser = argparse.ArgumentParser(description=f'Ingest declared inputs for {WORKFLOW_NAME}.')
    parser.add_argument('--input', help='JSON string or path to a JSON file with overrides (fixture_set).')
    parser.add_argument('--output', help='Optional path to write the run summary JSON.')
    parser.add_argument(
        '--fixture-set',
        choices=('clean', 'defective'),
        help='Override the envelope fixture_set for one run.',
    )
    args = parser.parse_args()
    if args.input:
        candidate = Path(args.input)
        text = candidate.read_text(encoding='utf-8') if candidate.exists() else args.input
        data = json.loads(text)
    else:
        data = dict(sample) if isinstance(sample, dict) else {}
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
    result = ingest_inputs(payload['data'])
    emit(result, payload['output'])
    # A missing declared source is a hard stop, not a warning (P4).
    raise SystemExit(1 if result['status'] == 'stop' else 0)
