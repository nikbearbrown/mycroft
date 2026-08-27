"""Purpose: Verify that every declared source for this recipe exists, parses, and hashes, before any ingest or scoring step runs.
Input: Optional JSON overrides (--input) naming extra paths or a different fixture set; otherwise the recipe's declared paths.
Output: JSON provenance record with workflow, source_paths, exists, parsed_ok, approval_state, checked_at; canonical destination logs/market-sentiment-analysis-part-1-verify-provenance-[DATE].json.
Side effects: Reads declared paths; writes only when --output is supplied. No network calls.
Idempotent: Yes; findings_digest is stable across runs for unchanged files (checked_at and generated_at are excluded from it).
Recipe: recipes/market-sentiment-analysis-part-1.md

Layer note (deliberate, documented exception to docs/architecture.md 5.2):
    This is a tool-layer script, and the tool layer must not read data/raw/. This script
    touches paths under data/raw/ for existence, byte hash, and parseability ONLY. It reads
    bytes to hash them and calls json.loads solely to learn whether parsing raises; the
    parsed object is discarded immediately and never inspected, returned, or scored. No
    record content crosses out of this module. Promoting record content out of data/raw/
    remains the GIGO layer's job.

Constitution notes:
    P3 - every finding is a fact about a named path (existence, size, sha256, parse result).
         Nothing here is inferred and nothing is invented.
    P4 - a missing REQUIRED source is a hard stop with a nonzero exit, not a warning.
    P8 - approval_state reports whether an approval record exists. It never concludes that
         anything was approved, and it never authorises a live call.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKFLOW_NAME = 'Market Sentiment Analysis - Part 1'
WORKFLOW_SLUG = 'market-sentiment-analysis-part-1'
NODE_NAME = 'Verify provenance'
NODE_TYPE = 'recipe-step'
CLASSIFICATION = 'tool'

RECIPE_PATH = f'recipes/{WORKFLOW_SLUG}.md'
SAMPLE_DIR = f'data/raw/{WORKFLOW_SLUG}/sample'
APPROVAL_RECORD = f'logs/gate-decisions/{WORKFLOW_SLUG}-approval.json'

# Every path this recipe declares, with why it matters and how strictly it is required.
#   required=True   -> absence or an unexpected parse failure stops the run (P4)
#   expected_parse_failure=True -> the file is SUPPOSED to be unparseable (fixture D18);
#                      a successful parse is the defect, not a failure to parse
DECLARED_SOURCES: tuple[dict[str, Any], ...] = (
    {'path': RECIPE_PATH, 'role': 'recipe under test - authoritative for intent (P6)', 'required': True},
    {'path': f'conductor/{WORKFLOW_SLUG}.md', 'role': 'conductor flow for this recipe', 'required': True},
    {
        'path': 'data/mycroft-main/n8n-workflows/originals/n8n_Workflows/Market_Monitoring_Agent/market_sentiment.json',
        'role': 'named provenance source - the original n8n workflow (quarantined Tier 3; provenance only)',
        'required': True,
    },
    {'path': f'{SAMPLE_DIR}/fixture-manifest.json', 'role': 'frozen fixture manifest - the schema and defect catalogue this run is graded against', 'required': True},
    {'path': f'{SAMPLE_DIR}/FIXTURE_MANIFEST.md', 'role': 'human view of the fixture manifest (P5)', 'required': True},
    {'path': f'{SAMPLE_DIR}/clean/price-alpha-vantage.json', 'role': 'clean fixture - price stream (Alpha Vantage GLOBAL_QUOTE)', 'required': True},
    {'path': f'{SAMPLE_DIR}/clean/news-finnhub.json', 'role': 'clean fixture - news stream (Finnhub company-news)', 'required': True},
    {'path': f'{SAMPLE_DIR}/clean/reddit-wallstreetbets.json', 'role': 'clean fixture - social stream (Reddit search.json)', 'required': True},
    {'path': f'{SAMPLE_DIR}/defective/price-alpha-vantage.json', 'role': 'defective fixture - price stream (D01-D04)', 'required': True},
    {'path': f'{SAMPLE_DIR}/defective/news-finnhub.json', 'role': 'defective fixture - news stream (D05-D12)', 'required': True},
    {'path': f'{SAMPLE_DIR}/defective/reddit-wallstreetbets.json', 'role': 'defective fixture - social stream (D13-D17)', 'required': True},
    {
        'path': f'{SAMPLE_DIR}/defective/news-finnhub-unparseable.json.broken',
        'role': 'defective fixture - truncated file (D18); exercises the parse_errors path',
        'required': True,
        'expected_parse_failure': True,
    },
    {
        'path': f'data/raw/{WORKFLOW_SLUG}/run-envelope.json',
        'role': 'run envelope - declares sample|live mode and the frozen clock; gate 2 reads this',
        'required': False,
    },
    {'path': APPROVAL_RECORD, 'role': 'gate-5 approval record for live or sensitive actions', 'required': False},
)

PARSE_CHECKED_SUFFIXES = frozenset({'.json', '.broken'})


def _sha256(path: Path) -> str:
    """Return the SHA-256 of a file's bytes, read in chunks so file size does not matter."""
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(65536), b''):
            digest.update(block)
    return digest.hexdigest()


def _parse_check(path: Path) -> tuple[bool | None, str | None]:
    """Report whether a file parses as JSON. The parsed object is discarded, never inspected.

    Returns (parsed_ok, parse_error). parsed_ok is None for formats this step does not
    parse (Markdown, for instance) - unknown is reported as unknown, never as True.
    """
    if path.suffix not in PARSE_CHECKED_SUFFIXES:
        return None, None
    try:
        json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as error:
        return False, f'JSONDecodeError: {error}'
    except UnicodeDecodeError as error:
        return False, f'UnicodeDecodeError: {error}'
    return True, None


def _check_source(source: dict[str, Any], root: Path) -> dict[str, Any]:
    """Check one declared source path: existence, size, hash, and parseability."""
    relative = source['path']
    path = root / relative
    expected_failure = bool(source.get('expected_parse_failure'))
    finding: dict[str, Any] = {
        'path': relative,
        'role': source['role'],
        'required': bool(source['required']),
        'expected_parse_failure': expected_failure,
        'exists': path.is_file(),
        'size_bytes': None,
        'sha256': None,
        'parsed_ok': None,
        'parse_error': None,
        'verdict': 'MISSING',
    }
    if not finding['exists']:
        finding['verdict'] = 'MISSING'
        return finding

    finding['size_bytes'] = path.stat().st_size
    finding['sha256'] = _sha256(path)
    parsed_ok, parse_error = _parse_check(path)
    finding['parsed_ok'] = parsed_ok
    finding['parse_error'] = parse_error

    if expected_failure:
        # The file is supposed to be unparseable. Parsing successfully means the fixture
        # was repaired or replaced, which invalidates the defect catalogue.
        finding['verdict'] = 'OK_UNPARSEABLE_AS_EXPECTED' if parsed_ok is False else 'UNEXPECTEDLY_PARSED'
    elif parsed_ok is False:
        finding['verdict'] = 'PARSE_FAILED'
    elif parsed_ok is None:
        finding['verdict'] = 'PRESENT_NOT_PARSE_CHECKED'
    else:
        finding['verdict'] = 'OK'
    return finding


def _approval_state(findings: list[dict[str, Any]]) -> dict[str, Any]:
    """Report whether a gate-5 approval record exists. Never concludes that anything is approved (P8)."""
    record = next((f for f in findings if f['path'] == APPROVAL_RECORD), None)
    present = bool(record and record['exists'])
    return {
        'state': 'approval-record-present' if present else 'no-approval-record',
        'record_path': APPROVAL_RECORD,
        'record_sha256': record['sha256'] if present else None,
        'approved_for_live_action': False,
        'note': (
            'An approval record exists on disk. Its adequacy is a human judgment and is not '
            'assessed here (P1); this step does not authorise a live call.'
            if present else
            'No approval record on disk. Live network calls, external writes, credentialed '
            'services, notifications, and model calls remain blocked pending gate 5.'
        ),
    }


def verify_provenance(payload: Any = None, root: Path | None = None) -> dict[str, Any]:
    """Verify every declared source for this recipe exists, parses, and hashes.

    Purpose: establish the provenance chain before any ingest or scoring step runs.
    Input: optional dict with 'extra_paths' (list of repo-relative paths to also check).
    Output: dict with workflow, source_paths, exists, parsed_ok, approval_state, checked_at.
    Side effects: reads the declared paths; no writes, no network.
    Idempotent: yes; findings_digest is stable for unchanged files.
    Recipe: recipes/market-sentiment-analysis-part-1.md
    """
    root = root or Path(__file__).resolve().parents[2]
    overrides = payload if isinstance(payload, dict) else {}
    sources = list(DECLARED_SOURCES)
    for extra in overrides.get('extra_paths', []) or []:
        sources.append({'path': str(extra), 'role': 'caller-supplied path (--input extra_paths)', 'required': False})

    findings = [_check_source(source, root) for source in sources]
    required = [f for f in findings if f['required']]

    missing_required = [f['path'] for f in required if not f['exists']]
    unparseable_required = [f['path'] for f in required if f['verdict'] in {'PARSE_FAILED', 'UNEXPECTEDLY_PARSED'}]

    stop_conditions: list[str] = []
    for path in missing_required:
        stop_conditions.append(f'Required source is missing: {path}. Recipe stop condition: required local source data is missing and no approved live-call path is available.')
    for path in unparseable_required:
        verdict = next(f['verdict'] for f in required if f['path'] == path)
        if verdict == 'UNEXPECTEDLY_PARSED':
            stop_conditions.append(f'Fixture expected to be unparseable now parses: {path}. The frozen defect catalogue no longer describes the file on disk (P6).')
        else:
            stop_conditions.append(f'Required source failed to parse: {path}. Data-shape gate (gate 3) cannot clear.')

    # Deterministic digest over the findings only - timestamps are deliberately excluded so
    # two runs over unchanged files produce the same digest and a reviewer can compare them.
    digest_basis = [
        {k: f[k] for k in ('path', 'exists', 'size_bytes', 'sha256', 'parsed_ok', 'verdict')}
        for f in findings
    ]
    findings_digest = hashlib.sha256(
        json.dumps(digest_basis, sort_keys=True, default=str).encode('utf-8')
    ).hexdigest()

    return {
        'workflow': WORKFLOW_NAME,
        'workflow_slug': WORKFLOW_SLUG,
        'node': NODE_NAME,
        'node_type': NODE_TYPE,
        'classification': CLASSIFICATION,
        'recipe': RECIPE_PATH,
        'step': 1,
        'step_name': NODE_NAME,
        # Recipe-declared roll-ups. Detail per path is in source_paths.
        'exists': all(f['exists'] for f in required),
        'parsed_ok': not unparseable_required,
        'source_paths': findings,
        'approval_state': _approval_state(findings),
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'summary': {
            'declared': len(findings),
            'required': len(required),
            'present': sum(1 for f in findings if f['exists']),
            'missing_required': missing_required,
            'missing_optional': [f['path'] for f in findings if not f['required'] and not f['exists']],
            'unparseable_required': unparseable_required,
            'parse_checked': sum(1 for f in findings if f['parsed_ok'] is not None),
            'not_parse_checked': [f['path'] for f in findings if f['exists'] and f['parsed_ok'] is None],
        },
        'findings_digest': findings_digest,
        'live_call_performed': False,
        'network_access': 'none - this step makes no network calls',
        'raw_layer_access': 'existence, byte hash, and parse check only; no record content read out of data/raw/',
        'status': 'stop' if stop_conditions else 'ok',
        'stop_conditions': stop_conditions,
        'next_step': (
            'Blocked. Resolve the stop conditions above before running step 2 (ingest declared inputs).'
            if stop_conditions else
            'Provenance established. Gate 1 (source gate) has its evidence; a named human clears it. '
            'Step 2 (ingest declared inputs) may run in sample mode.'
        ),
        'human_gate': {
            'gate': 'Gate 1 - Source gate',
            'capacity': '[TO]',
            'cleared_by': None,
            'note': 'Machines verify conformance; humans verify adequacy (P1). This record is evidence for the gate, not the gate decision.',
        },
    }


def load_input(sample: Any | None = None) -> dict[str, Any]:
    """Load JSON overrides from --input (JSON string or path) and the optional --output path."""
    parser = argparse.ArgumentParser(description=f'Verify declared provenance for {WORKFLOW_NAME}.')
    parser.add_argument('--input', help='JSON string or path to a JSON file with optional overrides (extra_paths).')
    parser.add_argument('--output', help=f'Optional path to write JSON output. Canonical: logs/{WORKFLOW_SLUG}-verify-provenance-[DATE].json')
    args = parser.parse_args()
    if args.input:
        candidate = Path(args.input)
        text = candidate.read_text(encoding='utf-8') if candidate.exists() else args.input
        data = json.loads(text)
    else:
        data = sample if sample is not None else {}
    return {'data': data, 'output': args.output}


def emit(data: Any, output_path: str | None = None) -> None:
    """Print JSON to stdout and, when an output path is given, write the same bytes there as UTF-8."""
    text = json.dumps(data, indent=2, sort_keys=True, default=str)
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + '\n', encoding='utf-8')
    print(text)


if __name__ == '__main__':
    payload = load_input({})
    result = verify_provenance(payload['data'])
    emit(result, payload['output'])
    # A missing or unparseable required source is a hard stop, not a warning (P4).
    raise SystemExit(1 if result['status'] == 'stop' else 0)
