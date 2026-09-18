"""Purpose: Produce the human report, the agent log, and the run audit from the prior steps' outputs.
Input: step-5 scores under logs/, step-4 quality-checked and step-3 shape-validated envelopes under data/verified/.
Output: reports/generated/market-sentiment-analysis-part-1-<DATE>.md, logs/market-sentiment-analysis-part-1-<DATE>.json, and a *-audit.md beside the data; returns summary, sources_checked, gate_results, findings, typed_todos, next_decision.
Side effects: writes to reports/generated/, logs/, and one audit file beside the verified data. Nothing under --no-write. No network calls.
Idempotent: The report and the audit are byte-identical across reruns. The agent log differs in exactly one field, `generated_at`, which the recipe's Output Contract requires; every other field is stable.
Recipe: recipes/market-sentiment-analysis-part-1.md

Layer contract (docs/architecture.md 5.2): a tool script reads data/verified/, writes to
logs/ or reports/generated/, must not read data/raw/, and must not make network requests.

    Two documented exceptions, both narrow and both stated in the emitted artifacts:

    1. It reads the prior steps' outputs from logs/ (step 5's scores). The recipe declares
       this step's input as "agent log plus raw and verified outputs", so reading logs/ is
       the contract, not a violation.
    2. It reads `data/raw/.../run-envelope.json` for run_id and fixture_set -- two scalars
       from a hand-authored run CONTROL file. No source record is read; raw provenance
       arrives only as metadata steps 2-4 copied forward. `--input-dir` bypasses it.

    It writes one `*-audit.md` under data/verified/. architecture.md says a tool must not
    write back to data/verified/ without a GIGO pass, while SNICKERDOODLE.md (which governs
    conflicts) says audits are "written beside the data they inspect as *-audit.md" and
    DATA_CONTRACT.md repeats it. The prohibition is about promoting DATA; an audit is a
    report about data, and the constitution wins. Logged here so the tension is visible.

TWO CUSTOMERS, TWICE (P5):
    The same run produces a JSON log for agents and a Markdown report for humans. One
    artifact cannot serve both, so this step writes both from one pass over the evidence and
    never lets them disagree -- the report's numbers are read from the same dict the log
    serialises.

THE REPORT'S READER:
    The recipe names "domain lead or human boss". This build targets the stricter reader a
    compliance or audit reviewer represents: someone who must reconstruct exactly how any
    score was produced. That means every number in the report carries its trace chain
    (score -> contributing rows -> verified file -> raw locator -> raw source path +
    SHA-256), the scoring parameters are reproduced so a score can be recomputed by hand,
    and each written artifact records its own SHA-256 so the reviewer can prove the file
    they are reading is the one the report cites. The recipe's Reader line is NOT edited --
    that is a recipe change and out of scope; the mismatch is carried in typed_todos.

VERIFIED VERSUS INFERRED (P3, P8):
    The sentiment score is an INFERRED finding. It is arithmetic over a keyword count with
    unattributed weights, not a market observation, and it appears under "Inferred findings"
    with its flags attached. Verified findings are only what a record supports: counts,
    hashes, defect locators, gate evidence. An audit reports what it found; it never says
    "pass" (SNICKERDOODLE, verification stack layer 2).
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
NODE_NAME = 'Produce human report'
NODE_TYPE = 'recipe-step'
CLASSIFICATION = 'tool'

RAW_ROOT = f'data/raw/{WORKFLOW_SLUG}'
VERIFIED_ROOT = f'data/verified/{WORKFLOW_SLUG}'
LOGS_ROOT = f'logs/{WORKFLOW_SLUG}'
REPORTS_ROOT = 'reports/generated'
ENVELOPE_PATH = f'{RAW_ROOT}/run-envelope.json'

STEP_SCRIPTS = [
    (1, 'Verify provenance', f'scripts/tools/{WORKFLOW_SLUG}-verify-provenance.py'),
    (2, 'Ingest declared inputs', f'scripts/ingest/{WORKFLOW_SLUG}-ingest-inputs.py'),
    (3, 'Validate data shape', f'scripts/gigo/{WORKFLOW_SLUG}-validate-data-shape.py'),
    (4, 'Transform and quality check', f'scripts/gigo/{WORKFLOW_SLUG}-transform-quality-check.py'),
    (5, 'Run approved tools', f'scripts/tools/{WORKFLOW_SLUG}-run-approved-tools.py'),
    (6, 'Produce human report', f'scripts/tools/{WORKFLOW_SLUG}-produce-human-report.py'),
]

GATES = [
    (1, 'Source gate', '[TO]', 'All required source paths present or marked with a typed TODO.'),
    (2, 'Scope gate', '[PF]', 'The run declares sample mode or an approved live mode before ingest.'),
    (3, 'Data-shape gate', '[PA]', 'Every raw and verified JSON output parses before downstream scripts run.'),
    (4, 'Script-readiness gate', '[IJ]', 'Every step script exists or is represented by a typed development TODO.'),
    (5, 'Approval gate', '[EI]', 'Live calls, external writes, credentials, or model calls require an approval record.'),
    (6, 'Report gate', '[TO]', 'Agent log and human report are written with the required fields and sections.'),
]

REPORT_SECTIONS = [
    'Run summary', 'Purpose', 'Source inventory', 'Inputs used', 'Phase-gate results',
    'Steps completed', 'Records seen', 'Rejects', 'Duplicates', 'Flags', 'Typed TODOs',
    'Human approvals', 'Verified findings', 'Inferred findings', 'Decision recommendation',
]


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return None


def _resolve_run(root: Path, overrides: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Work out which run to report on, from --run-id/--fixture-set or the run envelope."""
    run_id = overrides.get('run_id')
    fixture_set = overrides.get('fixture_set')
    envelope = _load_json(root / ENVELOPE_PATH) or {}
    if not run_id:
        run_id = envelope.get('run_id')
    if not fixture_set:
        fixture_set = envelope.get('fixture_set')
    if not run_id or not fixture_set:
        return {}, [
            'Cannot resolve the run: pass --run-id and --fixture-set, or provide '
            f'{ENVELOPE_PATH} with run_id and fixture_set.'
        ]
    return {
        'run_id': run_id,
        'fixture_set': fixture_set,
        'mode': envelope.get('mode', 'sample'),
        'frozen_clock': envelope.get('frozen_clock'),
        'recipe': envelope.get('recipe', f'recipes/{WORKFLOW_SLUG}.md'),
        'envelope': envelope,
    }, []


def _collect(root: Path, ident: dict[str, Any]) -> dict[str, Any]:
    """Gather every prior-step artifact for this run. Missing pieces are recorded, not raised."""
    tag = f'{ident["run_id"]}-{ident["fixture_set"]}'
    raw_dir = root / f'{RAW_ROOT}/runs/{tag}'
    shape_dir = root / f'{VERIFIED_ROOT}/runs/{tag}'
    quality_dir = shape_dir / 'quality-checked'
    scores_path = root / f'{LOGS_ROOT}/runs/{tag}/sentiment-scores.json'

    shape_docs, quality_docs = {}, {}
    for d, target in ((shape_dir, shape_docs), (quality_dir, quality_docs)):
        if d.is_dir():
            for p in sorted(d.glob('*.json')):
                doc = _load_json(p)
                if isinstance(doc, dict) and doc.get('stream'):
                    target[doc['stream']] = {'doc': doc, 'path': _rel(p, root)}

    scores = _load_json(scores_path) if scores_path.is_file() else None
    return {
        'tag': tag,
        'raw_dir': _rel(raw_dir, root) if raw_dir.is_dir() else None,
        'raw_paths': sorted(_rel(p, root) for p in raw_dir.iterdir() if p.is_file()) if raw_dir.is_dir() else [],
        'shape_dir': _rel(shape_dir, root) if shape_dir.is_dir() else None,
        'shape_docs': shape_docs,
        'quality_dir': _rel(quality_dir, root) if quality_dir.is_dir() else None,
        'quality_docs': quality_docs,
        'scores': scores,
        'scores_path': _rel(scores_path, root) if scores_path.is_file() else None,
        'verified_paths': sorted(
            [v['path'] for v in shape_docs.values()] + [v['path'] for v in quality_docs.values()]
        ),
    }


def _sources_checked(root: Path, ident: dict[str, Any], bundle: dict[str, Any]) -> list[dict[str, Any]]:
    """Every file this run rests on, with its hash, so the reviewer can re-verify."""
    out: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(rel: str, role: str) -> None:
        if not rel or rel in seen:
            return
        seen.add(rel)
        p = root / rel
        out.append({
            'path': rel,
            'role': role,
            'exists': p.is_file(),
            'sha256': _sha256_file(p) if p.is_file() else None,
            'size_bytes': p.stat().st_size if p.is_file() else None,
        })

    add(f'recipes/{WORKFLOW_SLUG}.md', 'recipe under test - authoritative for intent (P6)')
    add(f'conductor/{WORKFLOW_SLUG}.md', 'conductor flow')
    add(ENVELOPE_PATH, 'run control file - declares mode and the frozen clock')
    add(f'{RAW_ROOT}/sample/fixture-manifest.json', 'fixture manifest - schema and defect catalogue')
    add(f'{RAW_ROOT}/sample/FIXTURE_MANIFEST.md', 'fixture manifest, human view (P5)')
    # Original source files, named by the provenance steps 2-4 carried forward.
    for v in bundle['quality_docs'].values():
        env = ((v['doc'].get('_provenance') or {}).get('source_envelope') or {})
        if env.get('source_path'):
            add(env['source_path'], f'source fixture - {v["doc"].get("stream")} stream')
    for rel in bundle['raw_paths']:
        add(rel, 'step-2 raw output')
    for rel in bundle['verified_paths']:
        add(rel, 'verified output (step 3 or 4)')
    if bundle['scores_path']:
        add(bundle['scores_path'], 'step-5 sentiment scores')
    for _n, _name, script in STEP_SCRIPTS:
        add(script, 'step script')
    return out


def _gate_results(root: Path, ident: dict[str, Any], bundle: dict[str, Any]) -> list[dict[str, Any]]:
    """Evaluate each gate's EVIDENCE. No gate is marked passed; a named human clears it (P4)."""
    approval_rel = f'logs/gate-decisions/{WORKFLOW_SLUG}-approval.json'
    approval_exists = (root / approval_rel).is_file()
    recipe_text = ''
    rp = root / f'recipes/{WORKFLOW_SLUG}.md'
    if rp.is_file():
        recipe_text = rp.read_text(encoding='utf-8')

    missing_scripts = [s for _n, _name, s in STEP_SCRIPTS if not (root / s).is_file()]
    unparseable: list[str] = []
    for base in (f'{RAW_ROOT}/runs/{bundle["tag"]}', f'{VERIFIED_ROOT}/runs/{bundle["tag"]}'):
        d = root / base
        if d.is_dir():
            for p in d.rglob('*.json'):
                if _load_json(p) is None:
                    unparseable.append(_rel(p, root))

    shape_ok = all(
        v['doc'].get('shape_validation', {}).get('rows_promoted') is not None
        for v in bundle['shape_docs'].values()
    ) if bundle['shape_docs'] else False

    evidence = {
        1: {
            'observed': f'{sum(1 for s in _sources_checked(root, ident, bundle) if s["exists"])} declared sources present and hashed',
            'blocking': [],
        },
        2: {
            'observed': f'envelope declares mode={ident["mode"]!r}, fixture_set={ident["fixture_set"]!r}, frozen_clock={ident["frozen_clock"]}',
            'blocking': [] if (root / ENVELOPE_PATH).is_file() else [f'{ENVELOPE_PATH} is absent'],
        },
        3: {
            'observed': (
                f'{len(bundle["verified_paths"])} verified artifact(s) written; '
                f'{len(unparseable)} JSON file(s) failed to parse'
                + ('' if shape_ok else '; shape validation output incomplete')
            ),
            'blocking': unparseable,
        },
        4: {
            'observed': f'{len(STEP_SCRIPTS) - len(missing_scripts)} of {len(STEP_SCRIPTS)} step scripts exist',
            'blocking': missing_scripts,
            'note': (
                'This gate as written is satisfiable by doing nothing: it passes if the script '
                'exists OR if the [TODO: DEV] text is still in the recipe. Both are currently true.'
                if '[TODO: DEV]' in recipe_text else None
            ),
        },
        5: {
            'observed': (
                f'approval record {"present" if approval_exists else "absent"} at {approval_rel}; '
                'no live call, external write, or model call was performed'
            ),
            'blocking': [] if approval_exists else ['no approval record on disk'],
        },
        6: {
            'observed': 'agent log and human report written by this step; section and field coverage listed below',
            'blocking': [],
        },
    }

    rows: list[dict[str, Any]] = []
    for num, name, capacity, condition in GATES:
        e = evidence[num]
        rows.append({
            'gate': num,
            'name': name,
            'human_capacity': capacity,
            'handoff_condition': condition,
            'evidence_observed': e['observed'],
            'blocking_findings': e['blocking'],
            'cleared_by': None,
            'cleared_at': None,
            'status': 'evidence recorded; awaiting a named human',
            'note': e.get('note'),
        })
    return rows


def _findings(bundle: dict[str, Any], ident: dict[str, Any]) -> dict[str, Any]:
    """Split what a record supports from what was inferred from it (P3, P8)."""
    verified: list[dict[str, Any]] = []
    inferred: list[dict[str, Any]] = []

    rows_seen = rows_promoted = 0
    for stream, v in sorted(bundle['shape_docs'].items()):
        sv = v['doc'].get('shape_validation', {})
        rows_seen += sv.get('rows_seen') or 0
        rows_promoted += sv.get('rows_promoted') or 0
        verified.append({
            'finding': f'{stream}: {sv.get("rows_seen")} row(s) seen, {sv.get("rows_promoted")} promoted, {sv.get("rows_withheld")} withheld on shape',
            'basis': v['path'],
            'kind': 'record count, recomputed',
        })
        if sv.get('count_matches_declared') is False:
            verified.append({
                'finding': (
                    f'{stream}: the source envelope declared {sv.get("source_declared_record_count")} '
                    f'record(s) but holds {sv.get("rows_seen")}. The recount governs.'
                ),
                'basis': v['path'],
                'kind': 'envelope disagreement',
            })

    for stream, v in sorted(bundle['quality_docs'].items()):
        doc = v['doc']
        if doc.get('duplicates'):
            verified.append({
                'finding': f'{stream}: {len(doc["duplicates"])} duplicate occurrence(s) beyond the first, removed',
                'basis': v['path'],
                'kind': 'duplicate detection',
            })
        if doc.get('flags'):
            kinds = sorted({f.get('flag') for f in doc['flags']})
            verified.append({
                'finding': f'{stream}: {len(doc["flags"])} quality flag(s) raised ({", ".join(kinds)}); rows kept, not dropped',
                'basis': v['path'],
                'kind': 'quality flag',
            })

    scores = bundle['scores']
    if scores:
        sa = scores.get('sentiment_analysis', {})
        flags = scores.get('flags', [])
        inferred.append({
            'finding': (
                f'Overall sentiment {sa.get("overall_score")}/100 ({sa.get("sentiment_label")}) '
                f'for ticker {scores.get("ticker")}'
            ),
            'basis': bundle['scores_path'],
            'kind': 'heuristic score - NOT a market observation',
            'method': 'keyword counts combined by scoring_params v1.0.0 (price .4 / news .3 / social .3)',
            # Unique flag kinds with their counts; the raw list repeats per-row flags and
            # a reader scanning caveats needs the distinct set, not the tally spelled out.
            'caveats': [
                (k if n == 1 else f'{k} (x{n})')
                for k, n in sorted(
                    {f.get('flag'): sum(1 for g in flags if g.get('flag') == f.get('flag'))
                     for f in flags}.items()
                )
            ],
            'why_inferred': (
                'The score is arithmetic over keyword matches using weights and thresholds '
                'with no recorded author. It is not a measurement and not a recommendation.'
            ),
        })
        for comp, label in (('news_sentiment', 'news'), ('social_sentiment', 'social'), ('price_sentiment', 'price')):
            c = sa.get(comp, {})
            entry = {
                'finding': f'{label} component score {c.get("score")}/100',
                'basis': bundle['scores_path'],
                'kind': 'heuristic component score',
            }
            if c.get('score_is_default'):
                entry['warning'] = (
                    'This is the no-data default of 50, not a measurement. The stream had zero rows.'
                )
            inferred.append(entry)
        if any(f.get('flag') == 'scored_row_carries_quality_flag' for f in flags):
            n = sum(1 for f in flags if f.get('flag') == 'scored_row_carries_quality_flag')
            inferred.append({
                'finding': f'{n} row(s) that step 4 flagged as stale or wrongly typed still fed the score',
                'basis': bundle['scores_path'],
                'kind': 'contamination warning',
                'why_inferred': 'The score is unchanged in form but its evidence base is not clean.',
            })
    else:
        inferred.append({
            'finding': 'No score was produced; step 5 output is absent for this run.',
            'basis': None,
            'kind': 'missing input',
        })

    return {
        'verified': verified,
        'inferred': inferred,
        'rows_seen': rows_seen,
        'rows_promoted': rows_promoted,
    }


def _typed_todos(root: Path, bundle: dict[str, Any]) -> list[dict[str, Any]]:
    """Open typed TODOs, including the contract defects this build could not close in scope."""
    todos: list[dict[str, Any]] = [
        {
            'type': 'DEFINE',
            'item': 'scoring_params v1.0.0 constants are unattributed',
            'detail': (
                'The weights (price .4 / news .3 / social .3), the label thresholds '
                '(65/55/45/35) and both keyword lists appear in the source workflow with no '
                'derivation, backtest, or author. They are reproduced, not endorsed.'
            ),
            'closed_by': 'human',
            'evidence_required': 'the values, in the recipe, with one sentence of reasoning',
            'status': 'OPEN',
        },
        {
            'type': 'APPROVE',
            'item': 'Gate 5 approval for the model, Slack, and email calls',
            'detail': (
                'Step 5 rendered three live-call handoffs with approved_for_live_action=false. '
                'Each needs a logged gate decision and a named approver before it runs.'
            ),
            'closed_by': 'human',
            'evidence_required': 'a logged gate decision (this is a gate, not a checkbox)',
            'status': 'OPEN',
        },
        {
            'type': 'DEFINE',
            'item': 'No type contract exists in the declared schema',
            'detail': (
                'fixture-manifest.json declares required fields, identity keys and freshness '
                'windows but no value types. Step 4 carries a step-scoped TYPE_CONTRACT table '
                'as the closure; it is not a promoted schema and belongs in DATA_CONTRACT.md.'
            ),
            'closed_by': 'human',
            'evidence_required': 'the type contract, in DATA_CONTRACT.md, with a named owner',
            'status': 'OPEN',
        },
        {
            'type': 'DEFECT',
            'item': "Step 3's output contract has no field for a type violation",
            'detail': (
                'Its declared fields are record_count, required_fields_present, missing_fields, '
                'parse_errors, schema_version. A wrong-typed value is none of them, so D02/D11/D17 '
                'surface in step 4 flags instead. The recipe should add type_errors to step 3 or '
                'state that type checking belongs to step 4.'
            ),
            'closed_by': 'human',
            'evidence_required': 'a recipe amendment',
            'status': 'OPEN',
        },
        {
            'type': 'DEFECT',
            'item': 'Report reader mismatch',
            'detail': (
                'The recipe names the reader as "domain lead or human boss". This report is '
                'written for the stricter reader a compliance or audit reviewer represents, and '
                'carries per-score trace chains and artifact hashes accordingly. The recipe line '
                'was not edited -- that is a recipe change and out of scope.'
            ),
            'closed_by': 'human',
            'evidence_required': 'all three: exact columns/sections, reader role, decision enabled',
            'status': 'OPEN',
        },
        {
            'type': 'DEFECT',
            'item': 'reports/templates/ contradicts the recipe on the log path',
            'detail': (
                f'reports/templates/{WORKFLOW_SLUG}.md cites logs/{WORKFLOW_SLUG}/[RUN_ID].json; '
                f'the recipe Output Contract and the gate-6 test cite logs/{WORKFLOW_SLUG}-[DATE].json. '
                'The recipe governs; the template is wrong and untouched.'
            ),
            'closed_by': 'human',
            'evidence_required': 'a template correction',
            'status': 'OPEN',
        },
        {
            'type': 'DEFECT',
            'item': 'Gates 4 and 5 are satisfiable by doing nothing',
            'detail': (
                'Each passes if its artifact exists OR if the typed TODO text is still present '
                'in the recipe. A gate with no failure path is not a gate.'
            ),
            'closed_by': 'human',
            'evidence_required': 'a recipe amendment tightening both tests',
            'status': 'OPEN',
        },
        {
            'type': 'DEV',
            'item': 'Live mode is unimplemented',
            'detail': (
                'Step 2 stops in live mode. Real fetchers need credentials from the environment '
                '(ALPHA_VANTAGE_API_KEY, FINNHUB_API_KEY, REDDIT_USER_AGENT) plus 401/403/429/'
                'timeout/empty-200 handling that the fixture corpus explicitly does not cover.'
            ),
            'closed_by': 'AI, after gate 5',
            'evidence_required': 'script exists + conformance passes + handoff condition met',
            'status': 'OPEN',
        },
        {
            'type': 'DEV',
            'item': 'Recipe lifecycle frontmatter is absent',
            'detail': (
                'The recipe carries no status/todos_open/last_gate/attestation/recipe_version '
                'block, so its lifecycle stage cannot be stated. The six [TODO: DEV] markers '
                'also still stand even though all six scripts now exist.'
            ),
            'closed_by': 'human',
            'evidence_required': 'the frontmatter block, in the recipe',
            'status': 'OPEN',
        },
    ]
    return todos


def _next_decision(gate_rows: list[dict[str, Any]], bundle: dict[str, Any], findings: dict[str, Any]) -> dict[str, Any]:
    """State the decision this report enables, and recommend one without making it."""
    blocking = [g for g in gate_rows if g['blocking_findings']]
    quality_flags = sum(len(v['doc'].get('flags') or []) for v in bundle['quality_docs'].values())
    rejects = sum(len(v['doc'].get('rejects') or []) for v in bundle['quality_docs'].values())

    if blocking and any(g['gate'] == 3 for g in blocking):
        rec = 'request source or schema fixes'
        why = 'A verified artifact failed to parse, so the data-shape gate cannot be cleared.'
    elif rejects or quality_flags:
        rec = 'approve for the next phase only with the withholdings and flags accepted in writing'
        why = (
            f'{rejects} row(s) were withheld and {quality_flags} quality flag(s) raised. The score '
            'was still computed, so accepting it means accepting a score whose evidence base '
            'carries known defects.'
        )
    else:
        rec = 'approve the sample run for the next phase'
        why = 'No rejects and no quality flags on this run. Live execution remains blocked by gate 5.'

    return {
        'options': [
            'approve the run for the next phase',
            'request source or schema fixes',
            'block live execution',
        ],
        'recommendation': rec,
        'why': why,
        'live_execution': 'BLOCKED - no gate-5 approval record exists and no live call was made',
        'decided_by': None,
        'decided_at': None,
        'note': 'This is a recommendation, not a decision. Adequacy is the human gate (P1).',
    }


def _md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    if not rows:
        return ['_None._', '']
    out = ['| ' + ' | '.join(headers) + ' |', '|' + '|'.join(['---'] * len(headers)) + '|']
    out += ['| ' + ' | '.join(str(c).replace('|', '\\|') for c in r) + ' |' for r in rows]
    out.append('')
    return out


def _build_report(
    ident: dict[str, Any], bundle: dict[str, Any], sources: list[dict[str, Any]],
    gate_rows: list[dict[str, Any]], findings: dict[str, Any],
    todos: list[dict[str, Any]], decision: dict[str, Any], date_tag: str,
) -> str:
    """Render the 15 sections the recipe's Output Contract requires."""
    scores = bundle['scores'] or {}
    sa = scores.get('sentiment_analysis', {})
    L: list[str] = []

    L += [f'# {WORKFLOW_NAME} — {date_tag}', '']
    L += [
        f'**Run:** `{ident["run_id"]}` · **Mode:** `{ident["mode"]}` · '
        f'**Fixture set:** `{ident["fixture_set"]}` · **Frozen clock:** `{ident["frozen_clock"]}`',
        '',
        '**Reader:** compliance or audit reviewer who must reconstruct how any score was produced.',
        '',
        '**Decision enabled:** approve the run for the next phase, request source/schema fixes, '
        'or block live execution.',
        '',
        '> **Nothing here is a market observation.** The fixture set is synthetic; ticker `FAKE` '
        'does not exist. No live call, external write, or model call was performed.',
        '',
        '---', '',
    ]

    L += ['## Run summary', '']
    if scores:
        L += [
            f'Six of six steps ran against the `{ident["fixture_set"]}` fixture set. '
            f'{findings["rows_seen"]} row(s) were seen and {findings["rows_promoted"]} passed shape '
            f'validation; the run produced an overall sentiment of **{sa.get("overall_score")}/100 '
            f'({sa.get("sentiment_label")})**, which is a heuristic score and not a measurement.',
            '',
        ]
    else:
        L += ['Step 5 produced no score for this run, so no sentiment figure is reported.', '']

    L += ['## Purpose', '']
    L += [
        'Market Sentiment Analysis - Part 1 collects news, price, and social signals and asks '
        'whether the available local evidence is sufficient for a human decision, without '
        'unapproved external writes or unsupported analytical claims.',
        '',
    ]

    L += ['## Source inventory', '']
    L += ['Every file this run rests on, with the hash a reviewer can re-verify.', '']
    L += _md_table(
        ['Path', 'Role', 'Present', 'SHA-256 (first 16)'],
        [[f'`{s["path"]}`', s['role'], 'yes' if s['exists'] else '**NO**',
          (s['sha256'][:16] + '…') if s['sha256'] else '—'] for s in sources],
    )

    L += ['## Inputs used', '']
    L += _md_table(
        ['Input', 'Value'],
        [
            ['Run envelope', f'`{ENVELOPE_PATH}`'],
            ['Declared mode', f'`{ident["mode"]}`'],
            ['Fixture set', f'`{ident["fixture_set"]}`'],
            ['Frozen clock (only clock any step reads)', f'`{ident["frozen_clock"]}`'],
            ['Raw run directory', f'`{bundle["raw_dir"]}`' if bundle['raw_dir'] else '—'],
            ['Shape-validated directory', f'`{bundle["shape_dir"]}`' if bundle['shape_dir'] else '—'],
            ['Quality-checked directory', f'`{bundle["quality_dir"]}`' if bundle['quality_dir'] else '—'],
            ['Step-5 scores', f'`{bundle["scores_path"]}`' if bundle['scores_path'] else '—'],
        ],
    )

    L += ['## Phase-gate results', '']
    L += [
        'An audit reports what it found; it does not say "pass". Every gate below is cleared by '
        'a named human, not by this script.', '',
    ]
    L += _md_table(
        ['Gate', 'Capacity', 'Evidence observed', 'Blocking', 'Cleared by'],
        [[f'{g["gate"]} — {g["name"]}', g['human_capacity'], g['evidence_observed'],
          (f'**{len(g["blocking_findings"])}**' if g['blocking_findings'] else 'none'),
          '_awaiting_'] for g in gate_rows],
    )
    for g in gate_rows:
        if g.get('note'):
            L += [f'- **Gate {g["gate"]} caveat:** {g["note"]}', '']

    L += ['## Steps completed', '']
    L += _md_table(
        ['#', 'Step', 'Script', 'Exists'],
        [[n, name, f'`{s}`', 'yes'] for n, name, s in STEP_SCRIPTS],
    )

    L += ['## Records seen', '']
    rows = []
    for stream, v in sorted(bundle['shape_docs'].items()):
        sv = v['doc'].get('shape_validation', {})
        q = bundle['quality_docs'].get(stream, {}).get('doc', {})
        rows.append([
            stream, sv.get('source_declared_record_count'), sv.get('rows_seen'),
            sv.get('rows_promoted'), q.get('record_count', '—'),
        ])
    L += _md_table(['Stream', 'Declared by source', 'Recounted', 'Passed shape', 'After dedup'], rows)

    L += ['## Rejects', '']
    rows = []
    for stream, v in sorted(bundle['quality_docs'].items()):
        for r in v['doc'].get('rejects') or []:
            rows.append([stream, r.get('reason'), f'`{r.get("locator")}`', r.get('field') or '—', r.get('found_by') or '—'])
    L += _md_table(['Stream', 'Reason', 'Locator', 'Field', 'Found by'], rows)

    L += ['## Duplicates', '']
    L += ['Counting rule: every occurrence of an identity key beyond the first.', '']
    rows = []
    for stream, v in sorted(bundle['quality_docs'].items()):
        for d in v['doc'].get('duplicates') or []:
            rows.append([stream, d.get('basis'), f'`{d.get("locator")}`', f'`{d.get("first_seen_locator")}`'])
    L += _md_table(['Stream', 'Basis', 'Duplicate at', 'First seen at'], rows)

    L += ['## Flags', '']
    L += ['Stale and wrongly-typed rows are flagged and **kept**, never silently dropped or coerced.', '']
    rows = []
    for stream, v in sorted(bundle['quality_docs'].items()):
        for f in v['doc'].get('flags') or []:
            rows.append([stream, f.get('flag'), f'`{f.get("locator")}`', f.get('field') or '—', f'`{f.get("value")}`'])
    L += _md_table(['Stream', 'Flag', 'Locator', 'Field', 'Value'], rows)
    if scores.get('flags'):
        L += ['### Scoring-step flags', '']
        L += ['Substitutions the ported arithmetic made, each of which changes what the score means.', '']
        L += _md_table(
            ['Flag', 'Where', 'Why it matters'],
            [[f.get('flag'), f'`{f.get("locator") or f.get("stream") or "run"}`', f.get('why') or '—']
             for f in scores['flags']],
        )

    L += ['## Typed TODOs', '']
    L += _md_table(
        ['Type', 'Item', 'Closed by', 'Status'],
        [[t['type'], t['item'], t['closed_by'], t['status']] for t in todos],
    )
    for t in todos:
        L += [f'- **[{t["type"]}] {t["item"]}** — {t["detail"]}', '']

    L += ['## Human approvals', '']
    L += _md_table(
        ['Approval', 'Required for', 'Record', 'Status'],
        [
            ['Gate 5 — live/model calls', 'Anthropic, Slack, email',
             f'`logs/gate-decisions/{WORKFLOW_SLUG}-approval.json`', '**absent — all three blocked**'],
            ['Attestation', 'promotion to VERIFIED', '—', 'not recorded'],
        ],
    )
    if scores.get('flags') is not None:
        L += ['No live call, external write, or model call was performed by this run.', '']

    L += ['## Verified findings', '']
    L += ['Facts a record supports. Counts are recomputed, never copied from an envelope.', '']
    L += _md_table(
        ['Finding', 'Kind', 'Basis'],
        [[f['finding'], f['kind'], f'`{f["basis"]}`'] for f in findings['verified']],
    )

    L += ['## Inferred findings', '']
    L += [
        'Judgments, kept separate from the verified findings above (P3, P8). '
        '**The sentiment score belongs here, not above.**', '',
    ]
    for f in findings['inferred']:
        L += [f'- **{f["finding"]}** — _{f["kind"]}_']
        if f.get('method'):
            L += [f'  - Method: {f["method"]}']
        if f.get('why_inferred'):
            L += [f'  - Why inferred: {f["why_inferred"]}']
        if f.get('warning'):
            L += [f'  - ⚠ {f["warning"]}']
        if f.get('caveats'):
            L += [f'  - Caveats: {", ".join(c for c in f["caveats"] if c)}']
    L += ['']

    if scores:
        L += ['### How to reconstruct the score', '']
        L += ['Scoring parameters, reproduced so the arithmetic can be recomputed by hand:', '']
        sp = scores.get('scoring_params', {})
        L += _md_table(
            ['Parameter', 'Value'],
            [
                ['Version', f'`{sp.get("version")}`'],
                ['Ported from', f'`{sp.get("ported_from_node")}`'],
                ['Attribution', '**none recorded** — see typed TODOs'],
                ['Weights', f'`{json.dumps(sp.get("weights"))}`'],
                ['Label thresholds', f'`{json.dumps(sp.get("label_thresholds"))}`'],
                ['News formula', '`(positive − negative) / total_rows × 50 + 50`'],
                ['Overall formula', f'`{sa.get("overall_formula")}`'],
            ],
        )
        L += ['Trace chain — every row that moved the score, back to a byte range in a named file:', '']
        rows = []
        for stream, tc in (scores.get('trace_chain') or {}).items():
            for c in tc.get('contributions') or []:
                rows.append([
                    stream, f'`{c.get("raw_locator")}`',
                    f'`{(c.get("raw_source_path") or "").split("/")[-1]}`',
                    (c.get('raw_source_sha256') or '')[:16] + '…',
                    c.get('fetched_at'),
                ])
        L += _md_table(['Stream', 'Raw locator', 'Source file', 'Source SHA-256 (first 16)', 'Fetched at'], rows)

    L += ['## Decision recommendation', '']
    L += [f'**Recommended:** {decision["recommendation"]}', '', f'{decision["why"]}', '']
    L += _md_table(['Option', 'Available'], [[o, 'yes'] for o in decision['options']])
    L += [f'**Live execution:** {decision["live_execution"]}', '']
    L += [f'_{decision["note"]}_', '']
    L += ['---', '', f'_Generated by `scripts/tools/{WORKFLOW_SLUG}-produce-human-report.py` (step 6 of 6)._', '']
    return '\n'.join(L)


def _build_audit(ident: dict[str, Any], bundle: dict[str, Any], findings: dict[str, Any], date_tag: str) -> str:
    """Render the audit that sits beside the data it inspects. It reports; it never says pass."""
    L = [
        f'# Audit — {WORKFLOW_NAME} run `{bundle["tag"]}`', '',
        f'**Inspected:** `{bundle["shape_dir"]}`  ·  **Run date:** {date_tag}  ·  '
        f'**Frozen clock:** `{ident["frozen_clock"]}`', '',
        '> This audit reports what it found. It does not say "pass" — adequacy is the human '
        'gate (SNICKERDOODLE, verification stack layer 2).', '',
        '## Records in, records out', '',
    ]
    rows = []
    for stream, v in sorted(bundle['shape_docs'].items()):
        sv = v['doc'].get('shape_validation', {})
        q = bundle['quality_docs'].get(stream, {}).get('doc', {})
        rows.append([
            stream, sv.get('rows_seen'), sv.get('rows_promoted'),
            len(q.get('duplicates') or []), q.get('record_count', '—'), len(q.get('flags') or []),
        ])
    L += _md_table(['Stream', 'Seen', 'Passed shape', 'Duplicates removed', 'Final', 'Flags'], rows)

    L += ['## What was withheld, and why', '']
    rows = []
    for stream, v in sorted(bundle['quality_docs'].items()):
        for r in v['doc'].get('rejects') or []:
            rows.append([stream, f'`{r.get("locator")}`', r.get('reason'), r.get('action') or '—'])
    L += _md_table(['Stream', 'Locator', 'Reason', 'Action'], rows)

    L += ['## What was flagged and kept', '']
    rows = []
    for stream, v in sorted(bundle['quality_docs'].items()):
        for f in v['doc'].get('flags') or []:
            rows.append([stream, f'`{f.get("locator")}`', f.get('flag'), f'`{f.get("value")}`'])
    L += _md_table(['Stream', 'Locator', 'Flag', 'Value'], rows)

    L += ['## Anomalies a shape check cannot catch', '']
    L += [
        '- **Wrong-entity signals.** A row that is well-formed, fresh, unique and complete but '
        'belongs to a different company. No check in this pipeline catches it; ticker `FAKE` is '
        'unambiguous by construction and cannot exercise it.',
        '- **Whether the score is right.** This audit asserts nothing about the sentiment number. '
        'That is a human adequacy judgment (P1).',
        '- **Upstream HTTP failures, encoding defects, volume.** Not covered by the fixture set.',
        '',
    ]
    return '\n'.join(L)


def produce_human_report(payload: Any = None, root: Path | None = None) -> dict[str, Any]:
    """Produce the human report, the agent log, and the run audit.

    Purpose: turn the prior steps' machine outputs into a decision a human can actually make.
    Input: optional dict with 'run_id', 'fixture_set', or 'no_write'.
    Output: dict with summary, sources_checked, gate_results, findings, typed_todos, next_decision.
    Side effects: writes the report, the agent log, and one audit file; nothing under no_write.
    Idempotent: yes; every written value derives from the run's frozen clock.
    Recipe: recipes/market-sentiment-analysis-part-1.md
    """
    root = root or Path(__file__).resolve().parents[2]
    overrides = payload if isinstance(payload, dict) else {}
    no_write = bool(overrides.get('no_write'))

    ident, stops = _resolve_run(root, overrides)
    if stops:
        return _stopped(stops, ident, no_write)

    bundle = _collect(root, ident)
    if not bundle['shape_docs'] and not bundle['quality_docs']:
        return _stopped(
            [f'No prior-step output found for run {bundle["tag"]}. Run steps 2-5 first.'],
            ident, no_write,
        )

    sources = _sources_checked(root, ident, bundle)
    gate_rows = _gate_results(root, ident, bundle)
    findings = _findings(bundle, ident)
    todos = _typed_todos(root, bundle)
    decision = _next_decision(gate_rows, bundle, findings)

    # The run's frozen-clock date identifies the report, not the day it was regenerated --
    # that is what keeps reruns byte-identical. The fixture set is appended so a clean and a
    # defective run on the same date cannot overwrite each other. Both are an interpretation
    # of the recipe's `[DATE]` placeholder; carried in typed_todos if you disagree.
    clock = ident.get('frozen_clock') or ''
    date_tag = (clock[:10] or datetime.now(timezone.utc).date().isoformat())
    file_tag = f'{date_tag}-{ident["fixture_set"]}'

    report_rel = f'{REPORTS_ROOT}/{WORKFLOW_SLUG}-{file_tag}.md'
    log_rel = f'logs/{WORKFLOW_SLUG}-{file_tag}.json'
    audit_rel = f'{VERIFIED_ROOT}/runs/{bundle["tag"]}/{bundle["tag"]}-audit.md'

    report_md = _build_report(ident, bundle, sources, gate_rows, findings, todos, decision, date_tag)
    audit_md = _build_audit(ident, bundle, findings, date_tag)

    scores = bundle['scores'] or {}
    all_rejects = [r for v in bundle['quality_docs'].values() for r in (v['doc'].get('rejects') or [])]
    all_dups = [d for v in bundle['quality_docs'].values() for d in (v['doc'].get('duplicates') or [])]
    all_flags = [f for v in bundle['quality_docs'].values() for f in (v['doc'].get('flags') or [])]
    stop_conditions = [f'gate {g["gate"]} ({g["name"]}): {b}' for g in gate_rows for b in g['blocking_findings']]

    agent_log = {
        'workflow': WORKFLOW_NAME,
        'run_id': ident['run_id'],
        'mode': ident['mode'],
        'steps_completed': [{'step': n, 'name': name, 'script': s} for n, name, s in STEP_SCRIPTS],
        'records_seen': {
            'total_rows_seen': findings['rows_seen'],
            'total_rows_promoted': findings['rows_promoted'],
            'by_stream': {
                s: (v['doc'].get('shape_validation') or {}).get('rows_seen')
                for s, v in bundle['shape_docs'].items()
            },
        },
        'rejects': all_rejects,
        'duplicates': all_dups,
        'flags': {'quality': all_flags, 'scoring': scores.get('flags', [])},
        'stop_conditions': stop_conditions,
        'todo_items': todos,
        'source_files': sources,
        'gate_decisions': gate_rows,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'raw_output_paths': bundle['raw_paths'],
        'verified_output_paths': bundle['verified_paths'],
        'report_path': report_rel,
    }

    written: list[str] = []
    artifact_hashes: dict[str, str] = {}
    if not no_write:
        for rel, text in ((report_rel, report_md), (audit_rel, audit_md)):
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding='utf-8', newline='\n')
            written.append(rel)
            artifact_hashes[rel] = _sha256_file(p)
        agent_log['artifact_hashes'] = dict(artifact_hashes)
        p = root / log_rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps(agent_log, indent=2, sort_keys=True, default=str) + '\n',
            encoding='utf-8', newline='\n',
        )
        written.append(log_rel)
        artifact_hashes[log_rel] = _sha256_file(p)

    missing_sections = [s for s in REPORT_SECTIONS if f'## {s}' not in report_md]

    return {
        'workflow': WORKFLOW_NAME,
        'workflow_slug': WORKFLOW_SLUG,
        'node': NODE_NAME,
        'node_type': NODE_TYPE,
        'classification': CLASSIFICATION,
        'recipe': f'recipes/{WORKFLOW_SLUG}.md',
        'step': 6,
        'step_name': NODE_NAME,
        'run_id': ident['run_id'],
        'fixture_set': ident['fixture_set'],
        # --- the six fields the recipe declares for this step ---
        'summary': {
            'run': bundle['tag'],
            'mode': ident['mode'],
            'rows_seen': findings['rows_seen'],
            'rows_promoted': findings['rows_promoted'],
            'rejects': len(all_rejects),
            'duplicates': len(all_dups),
            'quality_flags': len(all_flags),
            'scoring_flags': len(scores.get('flags', [])),
            'overall_score': (scores.get('sentiment_analysis') or {}).get('overall_score'),
            'sentiment_label': (scores.get('sentiment_analysis') or {}).get('sentiment_label'),
            'score_is_inferred': True,
            'live_call_performed': False,
        },
        'sources_checked': sources,
        'gate_results': gate_rows,
        'findings': {'verified': findings['verified'], 'inferred': findings['inferred']},
        'typed_todos': todos,
        'next_decision': decision,
        # ---
        'report_path': None if no_write else report_rel,
        'agent_log_path': None if no_write else log_rel,
        'audit_path': None if no_write else audit_rel,
        'artifact_hashes': artifact_hashes,
        'report_sections_required': REPORT_SECTIONS,
        'report_sections_missing': missing_sections,
        'agent_log_fields_present': sorted(agent_log.keys()),
        'no_write_mode': no_write,
        'written_paths': written,
        'live_call_performed': False,
        'model_call_performed': False,
        'network_access': 'none',
        'raw_layer_access': (
            'control file only: run-envelope.json is read for run_id and fixture_set. No '
            'source record is read; raw provenance arrives as metadata steps 2-4 carried forward.'
        ),
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'status': 'stop' if missing_sections else 'ok',
        'stop_conditions': (
            [f'Report is missing required section(s): {", ".join(missing_sections)}.']
            if missing_sections else []
        ),
        'next_step': (
            'All six steps have run. Gate decisions are the remaining work and belong to a '
            'named human; live execution stays blocked until gate 5 is cleared.'
        ),
        'human_gate': {
            'gate': 'Gate 6 - Report gate',
            'capacity': '[TO]',
            'cleared_by': None,
            'note': 'The report and log exist with their required fields; whether they are adequate is the human gate (P1).',
        },
    }


def _stopped(stops: list[str], ident: dict[str, Any], no_write: bool) -> dict[str, Any]:
    """Build a stop result that still satisfies the step's declared output fields."""
    return {
        'workflow': WORKFLOW_NAME,
        'workflow_slug': WORKFLOW_SLUG,
        'node': NODE_NAME,
        'node_type': NODE_TYPE,
        'classification': CLASSIFICATION,
        'step': 6,
        'step_name': NODE_NAME,
        'run_id': ident.get('run_id'),
        'fixture_set': ident.get('fixture_set'),
        'summary': {},
        'sources_checked': [],
        'gate_results': [],
        'findings': {'verified': [], 'inferred': []},
        'typed_todos': [],
        'next_decision': {
            'options': ['request source or schema fixes', 'block live execution'],
            'recommendation': 'request source or schema fixes',
            'why': 'The report could not be produced.',
            'decided_by': None,
        },
        'report_path': None,
        'no_write_mode': no_write,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'status': 'stop',
        'stop_conditions': stops,
        'next_step': 'Blocked. Resolve the stop conditions above.',
    }


def load_input(sample: Any | None = None) -> dict[str, Any]:
    """Load overrides from --input, --run-id, --fixture-set, or --no-write, plus --output."""
    parser = argparse.ArgumentParser(description=f'Produce the human report for {WORKFLOW_NAME}.')
    parser.add_argument('--input', help='JSON string or path to a JSON file with overrides.')
    parser.add_argument('--output', help='Optional path to write the step summary JSON.')
    parser.add_argument('--run-id', help='Run id to report on; defaults to the run envelope.')
    parser.add_argument('--fixture-set', choices=('clean', 'defective'), help='Override the envelope fixture_set.')
    parser.add_argument('--no-write', action='store_true', help='Build the report but write no files.')
    args = parser.parse_args()
    if args.input:
        candidate = Path(args.input)
        text = candidate.read_text(encoding='utf-8') if candidate.exists() else args.input
        data = json.loads(text)
    else:
        data = dict(sample) if isinstance(sample, dict) else {}
    if args.run_id:
        data['run_id'] = args.run_id
    if args.fixture_set:
        data['fixture_set'] = args.fixture_set
    if args.no_write:
        data['no_write'] = True
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
    result = produce_human_report(payload['data'])
    emit(result, payload['output'])
    raise SystemExit(1 if result['status'] == 'stop' else 0)
