"""
langgraph_pipeline.py — Multi-agent signal pipeline using LangGraph

Graph:
  conformance_node
      ↓ (pass) / → END (fail)
  cluster_node
      ↓
  scorer_node
      ↓ STRONG signals exist?
  research_node (LLM — Claude generates thesis note per STRONG signal)
      ↓
  report_node  (writes logs/ + reports/)

Usage:
    python langgraph_pipeline.py
    python langgraph_pipeline.py --no-llm   # skip LLM node, use rule-based notes
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import TypedDict, Annotated
import operator

import pandas as pd
from langgraph.graph import StateGraph, END

ROOT  = Path(__file__).parent
DATA  = ROOT / "data"
VERIFIED = DATA / "verified"   # Mycroft P2: TOOL scripts read verified layer
LOGS  = ROOT / "logs";    LOGS.mkdir(exist_ok=True)
RPTS  = ROOT / "reports"; RPTS.mkdir(exist_ok=True)

def _default_csv() -> Path:
    """Prefer verified layer; fall back to legacy data/ during migration."""
    v = VERIFIED / "enriched_trades.csv"
    return v if v.exists() else DATA / "enriched_trades.csv"

SECTOR_MAP: dict[str, str] = {
    "NVDA":"semiconductor","AMD":"semiconductor","INTC":"semiconductor",
    "MU":"semiconductor","MRVL":"semiconductor","AVGO":"semiconductor",
    "QCOM":"semiconductor","SNDK":"semiconductor","TXN":"semiconductor",
    "CRWD":"cybersecurity","FTNT":"cybersecurity","PANW":"cybersecurity",
    "DDOG":"cybersecurity","ZS":"cybersecurity","NET":"cybersecurity",
    "MSFT":"ai_cloud","GOOGL":"ai_cloud","AMZN":"ai_cloud","META":"ai_cloud",
    "HUM":"healthcare","UNH":"healthcare","CVS":"healthcare","LLY":"healthcare",
    "LMT":"defense","RTX":"defense","NOC":"defense","GD":"defense","BA":"defense",
    "XOM":"energy","CVX":"energy","COP":"energy",
    "JPM":"financials","BAC":"financials","GS":"financials",
    "LULU":"consumer","DECK":"consumer","COST":"consumer","WMT":"consumer",
}


# ── Shared state ──────────────────────────────────────────────────────────────

class PipelineState(TypedDict):
    # raw inputs
    enriched_csv:    str
    use_llm:         bool
    # gate
    gate_passed:     bool
    gate_failures:   list[str]
    total_trades:    int
    priced_trades:   int
    # clusters
    clusters:        list[dict]
    # signals
    signals:         list[dict]       # STRONG signals only
    strong_count:    int
    watch_count:     int
    skip_count:      int
    # research
    research_notes:  dict[str, str]   # ticker → note
    # provenance log
    run_log:         Annotated[list[str], operator.add]


# ── Node 1: Conformance gate ──────────────────────────────────────────────────

def conformance_node(state: PipelineState) -> PipelineState:
    log = [f"[conformance] starting — {datetime.now().isoformat()}"]
    csv_path = Path(state["enriched_csv"])

    if not csv_path.exists():
        return {**state,
                "gate_passed": False,
                "gate_failures": [f"File not found: {csv_path}"],
                "run_log": log + ["[conformance] GATE FAILED — file missing"]}

    df = pd.read_csv(csv_path, dtype=str)
    failures = []

    required = ["politician", "ticker", "trade_type", "disclosure_date", "transaction_date"]
    for col in required:
        if col not in df.columns:
            failures.append(f"Missing required column: {col}")

    blank_tickers  = (df["ticker"].isna() | (df["ticker"].str.strip() == "")).sum() if "ticker" in df.columns else 0
    blank_disclos  = (df["disclosure_date"].isna() | (df["disclosure_date"].str.strip() == "")).sum() if "disclosure_date" in df.columns else 0
    blank_pol      = (df["politician"].isna() | (df["politician"].str.strip() == "")).sum() if "politician" in df.columns else 0

    total  = len(df)
    priced = df["pct_change_post_disclosure"].notna().sum() if "pct_change_post_disclosure" in df.columns else 0
    coverage = round(priced / total * 100, 1) if total else 0

    skip_rate = round((blank_tickers + blank_disclos) / total * 100, 1) if total else 0
    log += [
        f"[conformance] rows={total}  priced={priced} ({coverage}%)  blank_tickers={blank_tickers}  blank_disclos={blank_disclos}  blank_pol={blank_pol}",
        f"[conformance] gate_skip_rate={skip_rate}%  failures={len(failures)}",
    ]

    passed = len(failures) == 0
    log.append(f"[conformance] {'GATE PASSED' if passed else 'GATE FAILED'}")
    return {**state,
            "gate_passed":   passed,
            "gate_failures": failures,
            "total_trades":  total,
            "priced_trades": priced,
            "run_log":       log}


def gate_router(state: PipelineState) -> str:
    return "cluster_node" if state["gate_passed"] else END


# ── Node 2: Cluster detection ─────────────────────────────────────────────────

def cluster_node(state: PipelineState) -> PipelineState:
    log = [f"[cluster] detecting clusters — window=30d  min_pols=2"]
    df  = pd.read_csv(state["enriched_csv"], dtype=str)

    for col in ["pct_change_post_disclosure", "spy_return_30d", "abnormal_return"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    def valid(t):
        t = str(t).strip()
        return bool(t) and t.replace("/","").replace("-","").isalpha() and 1 <= len(t) <= 6

    buys = df[df["trade_type"].str.upper() == "BUY"].copy()
    buys = buys[buys["ticker"].apply(valid)]
    buys["disc_dt"]  = pd.to_datetime(buys["disclosure_date"], errors="coerce")
    buys["ticker_u"] = buys["ticker"].str.upper()
    buys = buys.dropna(subset=["disc_dt"])

    seen: set[str] = set()
    clusters: list[dict] = []

    for ticker, grp in buys.groupby("ticker_u"):
        grp = grp.sort_values("disc_dt")
        for anchor in grp["disc_dt"]:
            key = f"{ticker}|{anchor.date()}"
            if key in seen:
                continue
            window = grp[(grp["disc_dt"] >= anchor) & (grp["disc_dt"] <= anchor + timedelta(days=30))]
            pols = window["politician"].unique().tolist()
            if len(pols) < 2:
                continue
            seen.add(key)
            ab = window["abnormal_return"].dropna()
            bcrs = []
            for pol in pols:
                pol_df   = df[df["politician"] == pol]
                pol_buys = (pol_df["trade_type"].str.upper() == "BUY").sum()
                pol_all  = len(pol_df)
                bcrs.append(round(pol_buys / pol_all, 3) if pol_all else 0.5)

            clusters.append({
                "ticker":       ticker,
                "sector":       SECTOR_MAP.get(ticker, "general"),
                "cluster_size": len(pols),
                "politicians":  sorted(pols),
                "max_bcr":      round(max(bcrs), 3),
                "anchor_date":  str(anchor.date()),
                "avg_alpha":    round(float(ab.mean()), 4) if len(ab) else None,
                "win_rate":     round(float((ab > 0).mean() * 100), 1) if len(ab) else None,
                "n":            int(len(ab)),
                "signal_score": round(len(pols) * max(bcrs), 3),
                "source":       f"capitoltrades.com — {len(pols)} disclosures from {anchor.date()} window",
            })

    clusters.sort(key=lambda c: c["signal_score"], reverse=True)
    log.append(f"[cluster] found {len(clusters)} clusters  top={clusters[0]['ticker'] if clusters else 'none'}")
    return {**state, "clusters": clusters, "run_log": log}


# ── Node 3: Signal scorer ─────────────────────────────────────────────────────

def scorer_node(state: PipelineState) -> PipelineState:
    log = ["[scorer] applying phase gates: score≥2 → STRONG, score≥1 → WATCH, else SKIP"]
    strong, watch, skip = [], [], []

    for c in state["clusters"]:
        score = c["signal_score"]
        alpha = c["avg_alpha"] or 0

        # Phase gate 1: exhausted signal (already ran up 15%+ before disclosure)
        if alpha > 50:
            c["signal_state"] = "WATCH"   # extraordinary — flag for human review
            watch.append(c)
            continue

        if score >= 2.0 and alpha > 0:
            c["signal_state"] = "STRONG"
            strong.append(c)
        elif score >= 1.0:
            c["signal_state"] = "WATCH"
            watch.append(c)
        else:
            c["signal_state"] = "SKIP"
            skip.append(c)

    log.append(f"[scorer] STRONG={len(strong)}  WATCH={len(watch)}  SKIP={len(skip)}")
    return {**state,
            "signals":      strong,
            "strong_count": len(strong),
            "watch_count":  len(watch),
            "skip_count":   len(skip),
            "run_log":      log}


def signal_router(state: PipelineState) -> str:
    return "research_node" if state["strong_count"] > 0 else "report_node"


# ── Node 4: LLM research agent ────────────────────────────────────────────────

def research_node(state: PipelineState) -> PipelineState:
    log = [f"[research] generating notes for {state['strong_count']} STRONG signals"]
    notes: dict[str, str] = {}

    if not state["use_llm"]:
        # Rule-based fallback — no API key needed
        for sig in state["signals"]:
            sector_context = {
                "semiconductor": "active CHIPS Act 2.0 drafting and AI National Security Commission work",
                "cybersecurity":  "NDAA cybersecurity provisions and federal zero-trust mandates",
                "healthcare":     "drug pricing legislation and Medicare negotiation timelines",
                "defense":        "defense appropriations and contract award cycles",
                "ai_cloud":       "AI executive orders and federal AI procurement policy",
            }.get(sig["sector"], "general legislative activity")

            notes[sig["ticker"]] = (
                f"STRONG signal — {sig['ticker']} ({sig['sector']}). "
                f"{sig['cluster_size']} politicians bought within 30 days "
                f"(max BCR {sig['max_bcr']:.2f}, signal score {sig['signal_score']:.2f}). "
                f"Historical avg alpha: {sig['avg_alpha']:+.2f}% above SPY "
                f"({sig['win_rate']}% win rate, n={sig['n']}). "
                f"Sector context: {sector_context}. "
                f"Politicians: {', '.join(sig['politicians'][:3])}{'...' if len(sig['politicians']) > 3 else ''}. "
                f"Source: {sig['source']}."
            )
        log.append("[research] rule-based notes generated (--no-llm mode)")
        return {**state, "research_notes": notes, "run_log": log}

    # LLM mode — Claude via langchain-anthropic
    try:
        from langchain_anthropic import ChatAnthropic
        from langchain_core.messages import HumanMessage

        llm = ChatAnthropic(model="claude-haiku-4-5-20251001", max_tokens=300)

        for sig in state["signals"][:5]:   # cap at 5 to save tokens
            prompt = (
                f"You are a financial research assistant analyzing congressional trade signals.\n\n"
                f"Signal: {sig['cluster_size']} U.S. politicians bought {sig['ticker']} "
                f"({sig['sector']} sector) within a 30-day window.\n"
                f"Politicians: {', '.join(sig['politicians'])}\n"
                f"Signal score: {sig['signal_score']:.2f} (cluster size × max BCR)\n"
                f"Historical alpha: {sig['avg_alpha']:+.2f}% above SPY ({sig['win_rate']}% win rate, n={sig['n']})\n\n"
                f"Write a 2-sentence research note explaining: (1) why this cluster signal may be "
                f"meaningful given the sector and congressional oversight context, "
                f"(2) what a retail investor should watch for before acting. "
                f"Be specific, cite the sector. Do not give financial advice."
            )
            resp = llm.invoke([HumanMessage(content=prompt)])
            notes[sig["ticker"]] = resp.content
            log.append(f"[research] note generated for {sig['ticker']}")

    except Exception as e:
        log.append(f"[research] LLM error: {e} — falling back to rule-based")
        for sig in state["signals"]:
            notes[sig["ticker"]] = f"STRONG signal — {sig['ticker']} | score={sig['signal_score']:.2f} | alpha={sig['avg_alpha']:+.2f}% | politicians={len(sig['politicians'])}"

    return {**state, "research_notes": notes, "run_log": log}


# ── Node 5: Report writer ─────────────────────────────────────────────────────

def report_node(state: PipelineState) -> PipelineState:
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    log = [f"[report] writing artifacts — {ts}"]

    # Agent log — full structured JSON
    log_artifact = {
        "run_at":        datetime.now().isoformat(),
        "source_csv":    state["enriched_csv"],
        "gate_passed":   state["gate_passed"],
        "gate_failures": state["gate_failures"],
        "total_trades":  state["total_trades"],
        "priced_trades": state["priced_trades"],
        "clusters_found":len(state["clusters"]),
        "strong":        state["strong_count"],
        "watch":         state["watch_count"],
        "skip":          state["skip_count"],
        "strong_signals":state["signals"],
        "research_notes":state["research_notes"],
        "run_log":       state["run_log"] + log,
    }
    log_path = LOGS / f"run_{ts}.json"
    with open(log_path, "w") as f:
        json.dump(log_artifact, f, indent=2, default=str)

    # Human report — readable markdown
    lines = [
        f"# Congressional Signal Report — {datetime.now().strftime('%B %d, %Y')}",
        f"",
        f"**Source:** `{Path(state['enriched_csv']).name}`  |  "
        f"**Trades:** {state['total_trades']:,}  |  "
        f"**Priced:** {state['priced_trades']:,}  |  "
        f"**Gate:** {'PASSED' if state['gate_passed'] else 'FAILED'}",
        f"",
        f"## Signal Summary",
        f"| Tier | Count |",
        f"|---|---|",
        f"| STRONG | {state['strong_count']} |",
        f"| WATCH  | {state['watch_count']} |",
        f"| SKIP   | {state['skip_count']} |",
        f"",
    ]

    if state["signals"]:
        lines += ["## Strong Signals", ""]
        for sig in state["signals"]:
            note = state["research_notes"].get(sig["ticker"], "")
            lines += [
                f"### {sig['ticker']} — {sig['sector'].upper()}",
                f"- **Politicians:** {', '.join(sig['politicians'])}",
                f"- **Signal score:** {sig['signal_score']:.2f}  |  "
                f"**Alpha:** {sig['avg_alpha']:+.2f}%  |  "
                f"**Win rate:** {sig['win_rate']}%  |  n={sig['n']}",
                f"- **Source:** {sig['source']}",
                f"- **Signal state:** DRAFT (window may still be open)",
                f"",
                f"> {note}",
                f"",
            ]
    else:
        lines += ["## No STRONG signals in current dataset.", ""]

    lines += [
        "---",
        f"*Generated by langgraph_pipeline.py · Log: `logs/run_{ts}.json` · "
        "Provenance: every signal traces to Capitol Trades filing + yfinance price data*"
    ]

    report_path = RPTS / f"signal_report_{ts}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    log.append(f"[report] log  → {log_path}")
    log.append(f"[report] report → {report_path}")
    print(f"\n  Log    -> {log_path}")
    print(f"  Report -> {report_path}\n")

    return {**state, "run_log": log}


# ── Build graph ───────────────────────────────────────────────────────────────

def build_graph():
    g = StateGraph(PipelineState)

    g.add_node("conformance_node", conformance_node)
    g.add_node("cluster_node",     cluster_node)
    g.add_node("scorer_node",      scorer_node)
    g.add_node("research_node",    research_node)
    g.add_node("report_node",      report_node)

    g.set_entry_point("conformance_node")
    g.add_conditional_edges("conformance_node", gate_router,
                             {"cluster_node": "cluster_node", END: END})
    g.add_edge("cluster_node",  "scorer_node")
    g.add_conditional_edges("scorer_node", signal_router,
                             {"research_node": "research_node", "report_node": "report_node"})
    g.add_edge("research_node", "report_node")
    g.add_edge("report_node",   END)

    return g.compile()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv",    default=str(_default_csv()))
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM node, use rule-based notes")
    args = parser.parse_args()

    use_llm = not args.no_llm and bool(os.environ.get("ANTHROPIC_API_KEY"))

    print(f"\n{'='*55}")
    print(f"  Congressional Signal Pipeline  (LangGraph)")
    print(f"  CSV    : {args.csv}")
    print(f"  LLM    : {'Claude Haiku' if use_llm else 'rule-based (--no-llm or no API key)'}")
    print(f"{'='*55}\n")

    graph = build_graph()

    initial_state: PipelineState = {
        "enriched_csv":   args.csv,
        "use_llm":        use_llm,
        "gate_passed":    False,
        "gate_failures":  [],
        "total_trades":   0,
        "priced_trades":  0,
        "clusters":       [],
        "signals":        [],
        "strong_count":   0,
        "watch_count":    0,
        "skip_count":     0,
        "research_notes": {},
        "run_log":        [],
    }

    final = graph.invoke(initial_state)

    print(f"  Gate   : {'PASSED' if final['gate_passed'] else 'FAILED'}")
    print(f"  Trades : {final['total_trades']:,}  priced={final['priced_trades']:,}")
    print(f"  Clusters: {len(final['clusters'])}")
    print(f"  STRONG : {final['strong_count']}")
    print(f"  WATCH  : {final['watch_count']}")
    print(f"  SKIP   : {final['skip_count']}")
    if final["strong_count"]:
        print(f"\n  Top STRONG signals:")
        for s in final["signals"][:5]:
            print(f"    {s['ticker']:<6} [{s['sector']:<14}] score={s['signal_score']:.2f}  alpha={s['avg_alpha']:+.2f}%")
