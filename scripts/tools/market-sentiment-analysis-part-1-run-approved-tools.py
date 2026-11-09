"""Purpose: Score verified records with a faithful port of the source workflow's sentiment arithmetic, flagging every substitution it makes, and prepare approval-required live calls as handoffs.
Input: step-4 output under data/verified/market-sentiment-analysis-part-1/runs/<run_id>-<fixture_set>/quality-checked/.
Output: sentiment scores plus per-score trace chains under logs/market-sentiment-analysis-part-1/runs/<run_id>-<fixture_set>/, and a summary on stdout carrying tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
Side effects: writes into logs/ only, and nothing at all under --no-write. Makes no network calls and no model calls.
Idempotent: Yes; scoring is deterministic and every timestamp comes from the run's frozen clock.
Recipe: recipes/market-sentiment-analysis-part-1.md

Layer contract (docs/architecture.md 5.2): a tool script may read data/verified/ ONLY, must
write to logs/ or reports/generated/, must not read data/raw/, and must not make network
requests. Record data reaches this step only from data/verified/, and raw provenance only as
metadata copied forward by steps 2-4 -- no source record is ever re-read here.

    Documented exception, narrow and stated: to resolve which run to score, this script reads
    `data/raw/market-sentiment-analysis-part-1/run-envelope.json` for two scalars, run_id and
    fixture_set. That file is a hand-authored run CONTROL file, not source data -- it lives
    under data/raw/ because gate 2's test names that path. No record is read from it, and no
    file under sample/ or runs/ is opened. `--input-dir` bypasses the read completely. The
    emitted `raw_layer_access` field states this rather than claiming "none", because a false
    provenance claim is a worse defect than the access it conceals (P3).

FAITHFUL PORT, LOUD SUBSTITUTIONS:
    scoring_params v1.0.0 reproduces the arithmetic of the `Aggregate & Calculate Sentiment`
    code node in the named source workflow, unchanged, so a reviewer can reconstruct any
    score the original produced. The original is not defensive: `parseFloat(x) || 0` turns a
    missing or non-numeric price into a silent 0, and a source with no records yields 50,
    which reads as "neutral" but is a default. Rather than fix these -- which would change
    what the number means and embed judgments no human has cleared -- every substitution
    emits a named flag, so a score built on one cannot be quoted without it.

    The flags this step can raise are enumerated in FLAG_CATALOGUE below, each with the
    behaviour in the original that causes it.

THE TRACE CHAIN (what makes this auditable):
    Every emitted score carries `contributions`: for each row that moved it, the verified
    file, the row's ORIGINAL raw locator, the raw source path and its SHA-256, and the
    fetched_at. A reviewer can walk any number back to a byte range in a named file and
    confirm the file is the one cited. Scores also record `rows_carrying_quality_flags` --
    rows step 4 flagged as stale or wrongly typed that nonetheless fed the score.

MODEL AND NOTIFICATION CALLS ARE NOT MADE:
    The source workflow's `AI Analysis & Synthesis` (Anthropic), Slack, and email nodes are
    emitted as handoff specifications with approved_for_live_action=false and
    live_call_performed=false. Their prompts and payloads are rendered so a human can read
    exactly what would be sent, and gate 5 plus a named approver is required before any of
    them runs. Model output, when it is eventually produced, is a judgment and must be
    labelled as one (P8), and belongs in a report's inferred-findings section, never its
    verified findings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKFLOW_NAME = 'Market Sentiment Analysis - Part 1'
WORKFLOW_SLUG = 'market-sentiment-analysis-part-1'
NODE_NAME = 'Run approved tools'
NODE_TYPE = 'recipe-step'
CLASSIFICATION = 'tool'

RAW_ROOT = f'data/raw/{WORKFLOW_SLUG}'
VERIFIED_ROOT = f'data/verified/{WORKFLOW_SLUG}'
LOGS_ROOT = f'logs/{WORKFLOW_SLUG}'
ENVELOPE_PATH = f'{RAW_ROOT}/run-envelope.json'

SOURCE_WORKFLOW = (
    'data/mycroft-main/n8n-workflows/originals/n8n_Workflows/'
    'Market_Monitoring_Agent/market_sentiment.json'
)

# ---------------------------------------------------------------------------
# scoring_params v1.0.0 -- lifted verbatim from the source workflow's code node.
#
# [TODO: DEFINE] Every constant below is unattributed. The weights, the label
# thresholds, and both keyword lists appear in the source workflow with no stated
# derivation, no backtest, and no author. For an audit reviewer these are the crux:
# they are analytic judgments wearing the costume of configuration. They are
# reproduced here unchanged and versioned so a historical score can be recomputed,
# NOT because they are endorsed. Promoting them requires a named human.
# ---------------------------------------------------------------------------
SCORING_PARAMS: dict[str, Any] = {
    'version': '1.0.0',
    'ported_from': SOURCE_WORKFLOW,
    'ported_from_node': 'Aggregate & Calculate Sentiment',
    'attribution': None,
    'attribution_note': (
        'No derivation, backtest, or author is recorded in the source workflow for any '
        'constant in this block. [TODO: DEFINE] - needs a named human.'
    ),
    'weights': {'price': 0.4, 'news': 0.3, 'social': 0.3},
    'label_thresholds': {
        'BULLISH': 65,
        'SLIGHTLY BULLISH': 55,
        'SLIGHTLY BEARISH': 45,
        'BEARISH': 35,
    },
    'price_score_map': {
        'change_gt_3': 75,
        'change_gt_0': 60,
        'change_lt_-3': 25,
        'otherwise': 40,
    },
    'news_positive_words': ['surge', 'gain', 'bull', 'upgrade', 'beat', 'strong', 'growth', 'profit', 'rise'],
    'news_negative_words': ['drop', 'fall', 'bear', 'downgrade', 'miss', 'weak', 'loss', 'decline', 'crash'],
    'reddit_bullish_terms': ['calls', 'moon', 'rocket', 'bullish', 'buy', 'long', '\U0001f680', 'to the moon'],
    'reddit_bearish_terms': ['puts', 'crash', 'bearish', 'sell', 'short', 'dump'],
    'news_scan_limit': 20,
    'no_data_score': 50,
}

FLAG_CATALOGUE = {
    'coerced_missing_field_to_zero': "original does parseFloat(undefined) || 0, so an absent field becomes 0",
    'coerced_non_numeric_to_zero': "original does parseFloat('N/A') || 0, so NaN becomes 0",
    'score_is_no_data_default': 'a stream with zero rows scores 50, which reads as neutral but is a default',
    'denominator_exceeds_scored_rows': 'news denominator is the full row count while only news_scan_limit rows are scored',
    'multi_quote_first_wins': 'original reads a single Global Quote; additional verified quotes are ignored',
    'js_undefined_concatenated': "original concatenates a missing summary/selftext, putting the literal 'undefined' into the scored text",
    'scored_row_carries_quality_flag': 'a row step 4 flagged as stale or wrongly typed still fed this score',
    'ticker_not_derived_from_question': 'no question-parsing step exists in this recipe, so the ticker comes from the price rows',
    'untested_threshold_path': 'a branch in the original that this corpus cannot exercise',
    'scoring_params_unattributed': 'the weights, thresholds and keyword lists have no recorded author',
}


def _rel(path: Path, root: Path) -> str:
    """Return a repo-relative POSIX path string."""
    return path.relative_to(root).as_posix()


def _js_parse_float(value: Any) -> float | None:
    """Mirror JavaScript parseFloat: parse a leading numeric run, else NaN (returned as None)."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    match = re.match(r'\s*[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?', value)
    return float(match.group(0)) if match else None


def _js_parse_int(value: Any) -> int | None:
    """Mirror JavaScript parseInt: parse a leading integer run, else NaN (returned as None)."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if not isinstance(value, str):
        return None
    match = re.match(r'\s*[+-]?\d+', value)
    return int(match.group(0)) if match else None


def _coerce_or_zero(
    value: Any, field: str, locator: str, flags: list[dict[str, Any]], as_int: bool = False
) -> float:
    """Apply the original's `parseFloat(x) || 0`, recording a flag whenever it substitutes."""
    present = value is not None
    parsed = _js_parse_int(value) if as_int else _js_parse_float(value)
    if parsed is None or parsed == 0:
        if not present:
            flags.append({
                'flag': 'coerced_missing_field_to_zero',
                'locator': locator,
                'field': field,
                'value': None,
                'substituted': 0,
                'why': FLAG_CATALOGUE['coerced_missing_field_to_zero'],
            })
            return 0.0
        if parsed is None:
            flags.append({
                'flag': 'coerced_non_numeric_to_zero',
                'locator': locator,
                'field': field,
                'value': value,
                'substituted': 0,
                'why': FLAG_CATALOGUE['coerced_non_numeric_to_zero'],
            })
            return 0.0
    return float(parsed)


def _keyword_verdict(text: str, positive: list[str], negative: list[str]) -> tuple[str, int, int]:
    """Count matching keywords the way the original does and return its verdict."""
    lowered = text.lower()
    pos = sum(1 for w in positive if w in lowered)
    neg = sum(1 for w in negative if w in lowered)
    if pos > neg:
        return 'positive', pos, neg
    if neg > pos:
        return 'negative', pos, neg
    return 'neutral', pos, neg


def _contribution(doc: dict[str, Any], locator: str, index: int, verified_file: str) -> dict[str, Any]:
    """Build one link in the trace chain: which row, in which file, from which source."""
    env = (doc.get('_provenance') or {}).get('source_envelope') or {}
    return {
        'verified_file': verified_file,
        'record_index': index,
        'raw_locator': locator,
        'raw_source_path': env.get('source_path'),
        'raw_source_sha256': env.get('source_sha256'),
        'fetched_at': env.get('fetched_at'),
    }


def _flagged_locators(doc: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Index step-4 quality flags by locator, so scored rows can declare what is wrong with them."""
    out: dict[str, list[dict[str, Any]]] = {}
    for f in doc.get('flags', []) or []:
        out.setdefault(f.get('locator'), []).append({
            'flag': f.get('flag'),
            'field': f.get('field'),
            'value': f.get('value'),
        })
    return out


def _score_price(doc: dict[str, Any], verified_file: str, flags: list[dict[str, Any]]) -> dict[str, Any]:
    """Port the original's price arithmetic. The original reads exactly one Global Quote."""
    rows = doc.get('verified_records') or []
    locs = doc.get('verified_locators') or []
    flagged = _flagged_locators(doc)
    p = SCORING_PARAMS['price_score_map']

    if not rows:
        flags.append({
            'flag': 'score_is_no_data_default',
            'stream': 'price',
            'substituted': SCORING_PARAMS['no_data_score'],
            'why': FLAG_CATALOGUE['score_is_no_data_default'],
        })
        return {
            'score': p['otherwise'],
            'basis': 'no rows; the original would parseFloat(undefined) || 0 and score change 0',
            'current_price': 0, 'change_percent': 0, 'volume': 0, 'previous_close': 0,
            'rows_scored': 0, 'contributions': [], 'rows_carrying_quality_flags': [],
        }

    if len(rows) > 1:
        flags.append({
            'flag': 'multi_quote_first_wins',
            'stream': 'price',
            'rows_available': len(rows),
            'row_used': locs[0] if locs else 'records[0]',
            'rows_ignored': locs[1:],
            'why': FLAG_CATALOGUE['multi_quote_first_wins'],
        })

    quote = rows[0]
    loc = locs[0] if locs else 'records[0]'
    current_price = _coerce_or_zero(quote.get('05. price'), '05. price', loc, flags)
    raw_change = quote.get('10. change percent')
    change_stripped = raw_change.replace('%', '') if isinstance(raw_change, str) else raw_change
    change_percent = _coerce_or_zero(change_stripped, '10. change percent', loc, flags)
    volume = _coerce_or_zero(quote.get('06. volume'), '06. volume', loc, flags, as_int=True)
    previous_close = _coerce_or_zero(quote.get('08. previous close'), '08. previous close', loc, flags)

    if change_percent > 0:
        score = p['change_gt_3'] if change_percent > 3 else p['change_gt_0']
    elif change_percent < -3:
        score = p['change_lt_-3']
    else:
        score = p['otherwise']

    carrying = [{'locator': loc, 'quality_flags': flagged[loc]}] if loc in flagged else []
    for c in carrying:
        flags.append({
            'flag': 'scored_row_carries_quality_flag',
            'stream': 'price',
            'locator': c['locator'],
            'quality_flags': c['quality_flags'],
            'why': FLAG_CATALOGUE['scored_row_carries_quality_flag'],
        })

    return {
        'score': score,
        'basis': 'change_percent thresholds from scoring_params.price_score_map',
        'current_price': current_price,
        'change_percent': change_percent,
        'volume': int(volume),
        'previous_close': previous_close,
        'rows_scored': 1,
        'contributions': [_contribution(doc, loc, 0, verified_file)],
        'rows_carrying_quality_flags': carrying,
    }


def _score_text_stream(
    stream: str,
    doc: dict[str, Any],
    verified_file: str,
    flags: list[dict[str, Any]],
    text_fields: tuple[str, str],
    positive: list[str],
    negative: list[str],
    scan_limit: int | None,
) -> dict[str, Any]:
    """Port the original's keyword scoring for news and reddit."""
    rows = doc.get('verified_records') or []
    locs = doc.get('verified_locators') or []
    flagged = _flagged_locators(doc)
    total = len(rows)

    if total == 0:
        flags.append({
            'flag': 'score_is_no_data_default',
            'stream': stream,
            'substituted': SCORING_PARAMS['no_data_score'],
            'why': FLAG_CATALOGUE['score_is_no_data_default'],
        })
        return {
            'score': SCORING_PARAMS['no_data_score'],
            'score_is_default': True,
            'positive': 0, 'negative': 0, 'neutral': 0,
            'total_rows': 0, 'rows_scored': 0,
            'contributions': [], 'rows_carrying_quality_flags': [], 'per_row': [],
        }

    scanned = rows[:scan_limit] if scan_limit else rows
    if scan_limit and total > scan_limit:
        # The original divides by the FULL row count while scoring only the first slice.
        flags.append({
            'flag': 'denominator_exceeds_scored_rows',
            'stream': stream,
            'rows_scored': len(scanned),
            'denominator_used': total,
            'why': FLAG_CATALOGUE['denominator_exceeds_scored_rows'],
        })

    pos_n = neg_n = neu_n = 0
    per_row: list[dict[str, Any]] = []
    contributions: list[dict[str, Any]] = []
    carrying: list[dict[str, Any]] = []
    primary, secondary = text_fields

    for i, row in enumerate(scanned):
        loc = locs[i] if i < len(locs) else f'records[{i}]'
        a, b = row.get(primary), row.get(secondary)
        # The original uses string concatenation, so a missing field becomes 'undefined'.
        if b is None:
            flags.append({
                'flag': 'js_undefined_concatenated',
                'stream': stream,
                'locator': loc,
                'field': secondary,
                'why': FLAG_CATALOGUE['js_undefined_concatenated'],
            })
        text = f'{a if a is not None else "undefined"} {b if b is not None else "undefined"}'
        verdict, p_hits, n_hits = _keyword_verdict(text, positive, negative)
        if verdict == 'positive':
            pos_n += 1
        elif verdict == 'negative':
            neg_n += 1
        else:
            neu_n += 1
        per_row.append({
            'locator': loc, 'verdict': verdict,
            'positive_hits': p_hits, 'negative_hits': n_hits,
        })
        contributions.append(_contribution(doc, loc, i, verified_file))
        if loc in flagged:
            carrying.append({'locator': loc, 'quality_flags': flagged[loc]})
            flags.append({
                'flag': 'scored_row_carries_quality_flag',
                'stream': stream,
                'locator': loc,
                'quality_flags': flagged[loc],
                'why': FLAG_CATALOGUE['scored_row_carries_quality_flag'],
            })

    score = (pos_n - neg_n) / total * 50 + 50
    return {
        'score': score,
        'score_is_default': False,
        'positive': pos_n, 'negative': neg_n, 'neutral': neu_n,
        'total_rows': total, 'rows_scored': len(scanned),
        'denominator': total,
        'formula': '(positive - negative) / total_rows * 50 + 50',
        'contributions': contributions,
        'rows_carrying_quality_flags': carrying,
        'per_row': per_row,
    }


def _label(score: int) -> str:
    """Apply the original's label thresholds, in the original's order."""
    t = SCORING_PARAMS['label_thresholds']
    if score >= t['BULLISH']:
        return 'BULLISH'
    if score >= t['SLIGHTLY BULLISH']:
        return 'SLIGHTLY BULLISH'
    if score <= t['BEARISH']:
        return 'BEARISH'
    if score <= t['SLIGHTLY BEARISH']:
        return 'SLIGHTLY BEARISH'
    return 'NEUTRAL'


def _handoffs(scores: dict[str, Any], ticker: str | None) -> list[dict[str, Any]]:
    """Render the live-call specifications without performing any of them."""
    sa = scores['sentiment_analysis']
    prompt = (
        'You are a financial market analyst providing sentiment analysis.\n\n'
        f'Market Data for {ticker}:\n'
        f'- Current Price: {scores["price_data"]["current_price"]}\n'
        f'- Change: {scores["price_data"]["change_percent"]}%\n'
        f'- Volume: {scores["price_data"]["volume"]}\n\n'
        'Sentiment Analysis:\n'
        f'- Overall Sentiment: {sa["sentiment_label"]} ({sa["overall_score"]}/100)\n'
        f'- News Sentiment: {sa["news_sentiment"]["positive"]} positive, '
        f'{sa["news_sentiment"]["negative"]} negative out of '
        f'{sa["news_sentiment"]["total_articles"]} articles\n'
        f'- Social Media: {sa["social_sentiment"]["positive"]} bullish, '
        f'{sa["social_sentiment"]["negative"]} bearish out of '
        f'{sa["social_sentiment"]["total_mentions"]} mentions\n'
    )
    common = {
        'approved_for_live_action': False,
        'live_call_performed': False,
        'gate': 'Gate 5 - Approval gate',
        'approval_record_required': f'logs/gate-decisions/{WORKFLOW_SLUG}-approval.json',
        'credential_policy': 'Environment variables only; never hardcoded.',
    }
    return [
        dict(common, **{
            'tool_name': 'AI Analysis & Synthesis',
            'kind': 'model_call',
            'model': 'claude-sonnet-4-20250514',
            'model_source': f'{SOURCE_WORKFLOW} (lmChatAnthropic node)',
            'credentials': ['ANTHROPIC_API_KEY'],
            'rendered_prompt': prompt,
            'output_labelling': (
                'Model output is a judgment (P8). It belongs in the report inferred-findings '
                'section, never verified findings, and must be labelled as a model judgment.'
            ),
            'caution': (
                'The source prompt asks for "actionable insights" on a financial question. '
                'Any released text needs a human owner and a suitability review.'
            ),
        }),
        dict(common, **{
            'tool_name': 'Send to Slack',
            'kind': 'notification',
            'credentials': ['SLACK_BOT_TOKEN', 'SLACK_CHANNEL_ID'],
            'payload_summary': f'{sa["sentiment_label"]} {sa["overall_score"]}/100 for {ticker}',
        }),
        dict(common, **{
            'tool_name': 'Send Email',
            'kind': 'notification',
            'credentials': ['SMTP_HOST', 'SMTP_USER', 'SMTP_PASSWORD', 'REPORT_RECIPIENT'],
            'payload_summary': f'{sa["sentiment_label"]} {sa["overall_score"]}/100 for {ticker}',
        }),
    ]


def _resolve_run(root: Path, overrides: dict[str, Any]) -> tuple[Path | None, dict[str, Any], list[str]]:
    """Work out which step-4 quality-checked directory to score."""
    if overrides.get('input_dir'):
        d = root / overrides['input_dir']
        if not d.is_dir():
            return None, {}, [f'Input directory does not exist: {overrides["input_dir"]}.']
        run_id, _, fixture_set = d.parent.name.rpartition('-')
        return d, {'run_id': run_id, 'fixture_set': fixture_set}, []

    env_path = root / ENVELOPE_PATH
    if not env_path.is_file():
        return None, {}, [f'Run envelope is missing: {ENVELOPE_PATH}, and no --input-dir was given.']
    try:
        envelope = json.loads(env_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as error:
        return None, {}, [f'Run envelope does not parse: {ENVELOPE_PATH} ({error}).']
    fixture_set = overrides.get('fixture_set') or envelope.get('fixture_set')
    run_id = envelope.get('run_id')
    if not run_id or not fixture_set:
        return None, {}, ['Run envelope is missing run_id or fixture_set.']
    d = root / f'{VERIFIED_ROOT}/runs/{run_id}-{fixture_set}/quality-checked'
    if not d.is_dir():
        return None, {}, [
            f'Quality-checked directory does not exist: {_rel(d, root)}. Run step 4 '
            '(transform-quality-check) first.'
        ]
    return d, {'run_id': run_id, 'fixture_set': fixture_set}, []


def run_approved_tools(payload: Any = None, root: Path | None = None) -> dict[str, Any]:
    """Score verified records and prepare approval-required calls as handoffs.

    Purpose: produce the sentiment scores with a complete trace chain, and perform no live action.
    Input: optional dict with 'input_dir', 'fixture_set', or 'no_write'.
    Output: dict with tool_name, input_path, output_path, action_taken, approval_id, no_write_mode.
    Side effects: writes scores into logs/, unless no_write is set.
    Idempotent: yes; scoring is deterministic.
    Recipe: recipes/market-sentiment-analysis-part-1.md
    """
    root = root or Path(__file__).resolve().parents[2]
    overrides = payload if isinstance(payload, dict) else {}
    no_write = bool(overrides.get('no_write'))

    src_dir, ident, stops = _resolve_run(root, overrides)
    if stops or src_dir is None:
        return _stopped(stops, ident, no_write)

    docs: dict[str, dict[str, Any]] = {}
    files: dict[str, str] = {}
    for path in sorted(src_dir.glob('*.json')):
        try:
            doc = json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as error:
            return _stopped([f'Step-4 output does not parse: {_rel(path, root)} ({error}).'], ident, no_write)
        stream = doc.get('stream')
        if stream:
            docs[stream] = doc
            files[stream] = _rel(path, root)
    if not docs:
        return _stopped([f'No step-4 output in {_rel(src_dir, root)}.'], ident, no_write)

    flags: list[dict[str, Any]] = [{
        'flag': 'scoring_params_unattributed',
        'scoring_params_version': SCORING_PARAMS['version'],
        'why': FLAG_CATALOGUE['scoring_params_unattributed'],
        'action': '[TODO: DEFINE] - the weights, thresholds and keyword lists need a named human.',
    }]

    empty = {'verified_records': [], 'verified_locators': [], 'flags': [], '_provenance': {}}
    price = _score_price(docs.get('price', empty), files.get('price', ''), flags)
    news = _score_text_stream(
        'news', docs.get('news', empty), files.get('news', ''), flags,
        ('headline', 'summary'),
        SCORING_PARAMS['news_positive_words'], SCORING_PARAMS['news_negative_words'],
        SCORING_PARAMS['news_scan_limit'],
    )
    reddit = _score_text_stream(
        'reddit', docs.get('reddit', empty), files.get('reddit', ''), flags,
        ('title', 'selftext'),
        SCORING_PARAMS['reddit_bullish_terms'], SCORING_PARAMS['reddit_bearish_terms'],
        None,
    )

    w = SCORING_PARAMS['weights']
    overall_raw = price['score'] * w['price'] + news['score'] * w['news'] + reddit['score'] * w['social']
    overall = round(overall_raw)
    label = _label(overall)

    # The original gates two social findings behind `redditMentions > 20`; this corpus
    # cannot reach that, so the branch is untested rather than passing.
    if reddit['total_rows'] <= 20:
        flags.append({
            'flag': 'untested_threshold_path',
            'stream': 'reddit',
            'branch': 'redditMentions > 20 (high social activity findings)',
            'rows_available': reddit['total_rows'],
            'why': FLAG_CATALOGUE['untested_threshold_path'],
        })

    price_rows = (docs.get('price') or {}).get('verified_records') or []
    ticker = price_rows[0].get('01. symbol') if price_rows else None
    flags.append({
        'flag': 'ticker_not_derived_from_question',
        'ticker_used': ticker,
        'ticker_source': "price row field '01. symbol'",
        'why': FLAG_CATALOGUE['ticker_not_derived_from_question'],
        'note': (
            "The source workflow derives the ticker from a parsed question and defaults to "
            "'SPY' when none is found, which silently turns a ticker-less question into an "
            'SPY analysis. This recipe has no question-parsing step, so that default cannot '
            'fire here -- and no question is scored either.'
        ),
    })

    scores = {
        'ticker': ticker,
        'scoring_params': SCORING_PARAMS,
        'price_data': {
            'current_price': price['current_price'],
            'change_percent': price['change_percent'],
            'volume': price['volume'],
            'previous_close': price['previous_close'],
        },
        'sentiment_analysis': {
            'overall_score': overall,
            'overall_score_unrounded': overall_raw,
            'overall_formula': 'price*0.4 + news*0.3 + social*0.3, rounded',
            'sentiment_label': label,
            'news_sentiment': {
                'score': round(news['score']), 'positive': news['positive'],
                'negative': news['negative'], 'neutral': news['neutral'],
                'total_articles': news['total_rows'], 'score_is_default': news['score_is_default'],
            },
            'social_sentiment': {
                'score': round(reddit['score']), 'positive': reddit['positive'],
                'negative': reddit['negative'], 'neutral': reddit['neutral'],
                'total_mentions': reddit['total_rows'], 'score_is_default': reddit['score_is_default'],
            },
            'price_sentiment': {'score': price['score']},
        },
        'trace_chain': {
            'price': {'contributions': price['contributions'], 'rows_carrying_quality_flags': price['rows_carrying_quality_flags']},
            'news': {'contributions': news['contributions'], 'per_row': news['per_row'], 'rows_carrying_quality_flags': news['rows_carrying_quality_flags']},
            'reddit': {'contributions': reddit['contributions'], 'per_row': reddit['per_row'], 'rows_carrying_quality_flags': reddit['rows_carrying_quality_flags']},
        },
        'flags': flags,
        'interpretation_warning': (
            'This score is arithmetic over a keyword count, not a market observation. It is '
            'not a recommendation, and every flag above changes what it means.'
        ),
    }

    out_dir_rel = f'{LOGS_ROOT}/runs/{ident["run_id"]}-{ident["fixture_set"]}'
    out_path_rel = f'{out_dir_rel}/sentiment-scores.json'
    scores_digest = hashlib.sha256(
        json.dumps(scores, sort_keys=True, default=str).encode('utf-8')
    ).hexdigest()

    action_taken = 'computed_scores_no_write' if no_write else 'computed_scores_and_wrote_log'
    if not no_write:
        out_dir = root / out_dir_rel
        out_dir.mkdir(parents=True, exist_ok=True)
        (root / out_path_rel).write_text(
            json.dumps(scores, indent=2, sort_keys=True, default=str) + '\n',
            encoding='utf-8',
            newline='\n',
        )

    handoffs = _handoffs(scores, ticker)
    tools = [{
        'tool_name': 'Aggregate & Calculate Sentiment',
        'input_path': sorted(files.values()),
        'output_path': None if no_write else out_path_rel,
        'action_taken': action_taken,
        'approval_id': None,
        'no_write_mode': no_write,
        'live_call_performed': False,
    }] + [{
        'tool_name': h['tool_name'],
        'input_path': out_path_rel if not no_write else None,
        'output_path': None,
        'action_taken': 'handoff_prepared_not_executed',
        'approval_id': None,
        'no_write_mode': no_write,
        'live_call_performed': False,
    } for h in handoffs]

    return {
        'workflow': WORKFLOW_NAME,
        'workflow_slug': WORKFLOW_SLUG,
        'node': NODE_NAME,
        'node_type': NODE_TYPE,
        'classification': CLASSIFICATION,
        'recipe': f'recipes/{WORKFLOW_SLUG}.md',
        'step': 5,
        'step_name': NODE_NAME,
        'run_id': ident['run_id'],
        'fixture_set': ident['fixture_set'],
        # --- the six fields the recipe declares for this step (primary tool) ---
        'tool_name': 'Aggregate & Calculate Sentiment',
        'input_path': sorted(files.values()),
        'output_path': None if no_write else out_path_rel,
        'action_taken': action_taken,
        'approval_id': None,
        'no_write_mode': no_write,
        # --- per-tool detail ---
        'tools': tools,
        'live_call_handoffs': handoffs,
        'scores': scores,
        'scores_digest': scores_digest,
        'scoring_params_version': SCORING_PARAMS['version'],
        'summary': {
            'overall_score': overall,
            'sentiment_label': label,
            'price_score': price['score'],
            'news_score': round(news['score']),
            'reddit_score': round(reddit['score']),
            'rows_scored': price['rows_scored'] + news['rows_scored'] + reddit['rows_scored'],
            'flags': len(flags),
            'flags_by_kind': {
                k: sum(1 for f in flags if f['flag'] == k)
                for k in sorted({f['flag'] for f in flags})
            },
            'rows_carrying_quality_flags': sum(
                len(scores['trace_chain'][s]['rows_carrying_quality_flags']) for s in ('price', 'news', 'reddit')
            ),
            'handoffs_prepared': len(handoffs),
        },
        'live_call_performed': False,
        'model_call_performed': False,
        'network_access': 'none',
        'raw_layer_access': (
            'control file only: data/raw/.../run-envelope.json is read for run_id and '
            'fixture_set. No record, and no file under data/raw/.../sample/ or runs/, is '
            'opened. Pass --input-dir to avoid the read entirely.'
        ),
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'status': 'ok',
        'stop_conditions': [],
        'next_step': f'Step 6 (produce-human-report) may run against {out_path_rel}',
        'human_gate': {
            'gate': 'Gate 5 - Approval gate',
            'capacity': '[EI]',
            'cleared_by': None,
            'note': (
                'No live or model call was made. Every handoff needs a gate-5 record and a '
                'named approver before it runs (P4, P8).'
            ),
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
        'step': 5,
        'step_name': NODE_NAME,
        'run_id': ident.get('run_id'),
        'fixture_set': ident.get('fixture_set'),
        'tool_name': 'Aggregate & Calculate Sentiment',
        'input_path': [],
        'output_path': None,
        'action_taken': 'not_run',
        'approval_id': None,
        'no_write_mode': no_write,
        'live_call_performed': False,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'status': 'stop',
        'stop_conditions': stops,
        'next_step': 'Blocked. Resolve the stop conditions above before running step 6.',
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
    """Load overrides from --input, --input-dir, --fixture-set, or --no-write, plus --output."""
    parser = argparse.ArgumentParser(description=f'Run approved tools for {WORKFLOW_NAME}.')
    parser.add_argument('--input', help='JSON string or path to a JSON file with overrides.')
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
    parser.add_argument('--input-dir', help='Step-4 quality-checked directory, repo-relative.')
    parser.add_argument('--fixture-set', choices=('clean', 'defective'), help='Override the envelope fixture_set.')
    parser.add_argument('--no-write', action='store_true', help='Compute scores but write no files.')
    args = parser.parse_args()
    if args.sample:
        _require_sample_mode()
    if args.input:
        candidate = Path(args.input)
        text = candidate.read_text(encoding='utf-8') if candidate.exists() else args.input
        data = json.loads(text)
    else:
        data = dict(sample) if isinstance(sample, dict) else {}
    if args.input_dir:
        data['input_dir'] = args.input_dir
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
    result = run_approved_tools(payload['data'])
    emit(result, payload['output'])
    raise SystemExit(1 if result['status'] == 'stop' else 0)
