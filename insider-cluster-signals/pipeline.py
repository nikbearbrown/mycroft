"""Purpose: Gated 5-node pipeline — conformance -> cluster -> score -> research -> report.
Input: data/verified/trades.json + enriched_trades.json (produced by the ingest/enrich layers).
Output: logs/run_<ts>.json (agent customer) + reports/signal_report_<ts>.md (human customer) — P5.
Side effects: Local file writes; ONE optional network call (Claude API) in the research node,
              only when ANTHROPIC_API_KEY is set AND STRONG signals exist.
Idempotent: Deterministic except run timestamps and the optional LLM text (labeled as such, P2/P8).
Recipe: recipes/insider-cluster-signal-agent.md

State machine semantics (mirrors the congressional-signals sibling's LangGraph design,
implemented stdlib-only to keep this module dependency-free):
  G1 conformance  — machine-checkable gate; FAILURE HALTS THE RUN (exit 2, P4).
  N2 cluster      — cluster_analyzer.analyze on the enriched corpus.
  N3 score        — signal_scorer.score; STRONG/WATCH/SKIP from trade-time info only.
  N4 research     — runs ONLY if STRONG signals exist. Claude (claude-opus-4-8) via stdlib
                    urllib when ANTHROPIC_API_KEY is set; rule-based notes otherwise.
                    Model output is labeled a model judgment, never a verified fact (P8).
  N5 report       — dual outputs per the recipe's Output Contract.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MODULE_DIR = Path(__file__).parent

ANTHROPIC_MODEL = "claude-opus-4-8"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, MODULE_DIR / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------- G1: conformance
def node_conformance(verified_dir: Path) -> dict:
    """Machine-checkable gate. Returns findings; caller halts on failed=True (P4)."""
    findings, failed = [], False

    trades_path = verified_dir / "trades.json"
    enriched_path = verified_dir / "enriched_trades.json"
    for path in (trades_path, enriched_path):
        if not path.exists():
            findings.append(f"MISSING: {path.name}")
            failed = True
    if failed:
        return {"failed": True, "findings": findings}

    try:
        trades = json.loads(trades_path.read_text())
        enriched = json.loads(enriched_path.read_text())
    except json.JSONDecodeError as exc:
        return {"failed": True, "findings": [f"UNPARSEABLE JSON: {exc}"]}

    s = trades["summary"]
    if s["records_verified"] + s["records_rejected"] != s["records_extracted"]:
        findings.append(
            "LEDGER MISMATCH: verified + rejected != extracted "
            f"({s['records_verified']} + {s['records_rejected']} != {s['records_extracted']})"
        )
        failed = True
    if not trades["records"]:
        findings.append("EMPTY: zero verified trade records")
        failed = True
    for r in enriched["records"]:
        if r["alpha_30d"] is None and not r.get("alpha_unavailable_reason"):
            findings.append(f"SILENT NULL: {r['accession']} has no alpha and no reason")
            failed = True

    findings.append(
        f"OK: {s['records_verified']} verified trades, {enriched['summary']['enriched']} enriched "
        f"({enriched['summary']['with_alpha']} with matured alpha)"
    )
    return {"failed": failed, "findings": findings}


# ------------------------------------------------------- N4: research (STRONG only)
def rule_based_research(signal: dict) -> str:
    roles = ", ".join(f"{m['owner_name']} ({m['role']})" for m in signal["members"][:4])
    alpha = (
        f"mean 30d alpha vs SPY {signal['mean_alpha_30d']:+.2f}% over {signal['trades_with_alpha']} priced trades"
        if signal["mean_alpha_30d"] is not None
        else "alpha window not yet matured"
    )
    return (
        f"{signal['n_insiders']} insiders ({roles}) bought {signal['ticker']} "
        f"({signal['issuer_name']}) between {signal['window']['start']} and {signal['window']['end']}; "
        f"total ${signal['total_value_usd']:,.0f}; {alpha}. [rule-based note]"
    )


def claude_research(signal: dict, api_key: str) -> str:
    """One short research note via the Claude API (stdlib HTTP). Output is a model judgment."""
    prompt = (
        "You are a research assistant. In 3-4 sentences, give neutral research context for this "
        "insider cluster-buy signal. No investment advice, no price targets. Facts provided:\n"
        + json.dumps(
            {k: signal[k] for k in ("ticker", "issuer_name", "window", "n_insiders",
                                     "total_value_usd", "mean_alpha_30d", "signal_reason")},
            default=str,
        )
    )
    body = json.dumps(
        {
            "model": ANTHROPIC_MODEL,
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode()
    req = urllib.request.Request(
        ANTHROPIC_URL,
        data=body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as response:
        payload = json.loads(response.read())
    if payload.get("stop_reason") == "refusal":
        return rule_based_research(signal)
    text = " ".join(b["text"] for b in payload["content"] if b["type"] == "text").strip()
    return f"{text} [model judgment: {ANTHROPIC_MODEL}]" if text else rule_based_research(signal)


def node_research(signals: list[dict]) -> tuple[list[dict], str]:
    strong = [s for s in signals if s["signal"] == "STRONG"]
    if not strong:
        return signals, "skipped (no STRONG signals)"
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    mode = f"claude ({ANTHROPIC_MODEL})" if api_key else "rule-based fallback (no ANTHROPIC_API_KEY)"
    for s in signals:
        if s["signal"] != "STRONG":
            continue
        try:
            s["research_note"] = claude_research(s, api_key) if api_key else rule_based_research(s)
        except Exception as exc:  # LLM failure must not kill the run; fall back and record it
            s["research_note"] = rule_based_research(s) + f" [claude call failed: {type(exc).__name__}]"
    return signals, mode


# ---------------------------------------------------------------- N5: report
def write_reports(run: dict, signals: list[dict], module_dir: Path) -> tuple[Path, Path]:
    ts = run["run_id"]
    log_path = module_dir / "logs" / f"run_{ts}.json"
    log_path.write_text(json.dumps({**run, "signals": signals}, indent=2, default=str) + "\n")

    lines = [
        f"# Insider Cluster Signal Report — {run['generated_at'][:10]}",
        "",
        "Research only — no investment advice. Every row traces to SEC EDGAR filings",
        "(accession URLs below); method and gates: `recipes/insider-cluster-signal-agent.md`.",
        "",
        "## Run summary",
        "",
        f"- Run ID: `{ts}` · mode: {run['mode']} · research: {run['research_mode']}",
        f"- Conformance gate: {'PASSED' if not run['conformance']['failed'] else 'FAILED'}",
        f"- Clusters: {run['clusters_found']} -> "
        f"**{run['strong']} STRONG / {run['watch']} WATCH / {run['skip']} SKIP**",
        "",
        "## Method (one paragraph)",
        "",
        "Form 4 filings fetched from EDGAR (SHA-256 manifests) -> 6-rule validation gate ->",
        "30-day SPY-adjusted alpha per trade (nearest prior trading day, immature windows",
        "excluded with reason) -> clusters of >=2 distinct insiders per ticker per 30-day",
        "window, role-weighted (officer 1.5 > director 1.0 > 10% 0.75) -> STRONG/WATCH/SKIP",
        "from trade-time information only; alpha reported as the scoreboard, never used to",
        "classify.",
        "",
        "## Signals",
        "",
    ]
    for s in signals:
        alpha = f"{s['mean_alpha_30d']:+.2f}%" if s["mean_alpha_30d"] is not None else "not matured"
        lines += [
            f"### {s['signal']} — {s['ticker']} ({s['issuer_name']})",
            "",
            f"- Window: {s['window']['start']} .. {s['window']['end']} · "
            f"{s['n_insiders']} insiders · {s['n_trades']} trades · ${s['total_value_usd']:,.0f}",
            f"- Conviction: {s['weighted_conviction']} (rank {s['rank_score']}) · mean 30d alpha vs SPY: {alpha}",
            f"- Why this tier: {s['signal_reason']}",
        ]
        for m in s["members"]:
            title = f" — {m['officer_title']}" if m["officer_title"] else ""
            lines.append(f"  - {m['owner_name']} ({m['role']}{title}): {m['shares']:,.0f} sh, ${m['value_usd']:,.0f}")
        if s.get("research_note"):
            lines.append(f"- Research note: {s['research_note']}")
        lines.append("- Source filings: " + ", ".join(
            f"[{a}](https://www.sec.gov/cgi-srv/browse-edgar?action=getcompany&filenum={a})"
            for a in s["accessions"][:6]
        ))
        lines.append("")
    lines += [
        "## Limitations",
        "",
        "- Corpus: one complete trading day (2026-03-02) + July sample days — not a backtest.",
        "- Alpha is a 30-calendar-day window vs SPY only; no sector adjustment, no transaction costs.",
        "- Signal tiers are deterministic rules, not model predictions; research notes are the only",
        "  model-generated content and are labeled as such.",
        f"- Human signal-quality gate (recipe Gate 3) is OPEN — spot-check pending before external use.",
        "",
    ]
    report_path = module_dir / "reports" / f"signal_report_{ts}.md"
    report_path.write_text("\n".join(lines))
    return log_path, report_path


# ---------------------------------------------------------------- orchestration
def run_pipeline(mode: str) -> int:
    module_dir = MODULE_DIR
    verified_dir = module_dir / "data" / "verified"
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # G1 — conformance (halts)
    conformance = node_conformance(verified_dir)
    print(f"[G1 conformance] {'FAILED' if conformance['failed'] else 'passed'}")
    for f in conformance["findings"]:
        print(f"    {f}")
    if conformance["failed"]:
        print("[HALT] conformance gate failed — no downstream node runs (P4)")
        return 2

    # N2 — cluster
    cluster_analyzer = _load("cluster_analyzer")
    cluster_summary = cluster_analyzer.analyze(verified_dir / "enriched_trades.json", verified_dir)
    print(f"[N2 cluster] {cluster_summary['clusters_found']} clusters from {cluster_summary['purchases_in']} purchases")

    # N3 — score
    signal_scorer = _load("signal_scorer")
    score_summary = signal_scorer.score(verified_dir / "cluster_signals.json", verified_dir)
    print(f"[N3 score] {score_summary['strong']} STRONG / {score_summary['watch']} WATCH / {score_summary['skip']} SKIP")

    # N4 — research (STRONG only)
    signals = json.loads((verified_dir / "scored_signals.json").read_text())["signals"]
    signals, research_mode = node_research(signals)
    print(f"[N4 research] {research_mode}")

    # N5 — report (both customers, P5)
    run = {
        "run_id": ts,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "conformance": conformance,
        "clusters_found": score_summary["clusters_in"],
        "strong": score_summary["strong"],
        "watch": score_summary["watch"],
        "skip": score_summary["skip"],
        "research_mode": research_mode,
        "source_manifests": sorted(
            p.name for p in (module_dir / "data" / "raw").glob("*manifest*.json")
        ),
    }
    log_path, report_path = write_reports(run, signals, module_dir)
    print(f"[N5 report] agent log: {log_path.name} · human report: {report_path.name}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the gated insider-cluster-signals pipeline.")
    parser.add_argument("--mode", default="dialogic", choices=["dialogic"])
    args = parser.parse_args()
    sys.exit(run_pipeline(args.mode))


if __name__ == "__main__":
    main()
