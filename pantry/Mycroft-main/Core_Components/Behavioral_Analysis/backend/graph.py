import os
import json
from datetime import datetime
from typing import TypedDict, Annotated
import operator
import pandas as pd
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from groq import Groq

from models import AgentFindings, EdgeReport, TradeStats
from agents import (
    behavior_agent,
    timing_agent,
    regime_agent,
    sector_agent,
    hold_duration_agent,
    luck_vs_skill_agent,
)

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ── Graph state ──────────────────────────────────────────────────────────────

class AnalysisState(TypedDict):
    df: pd.DataFrame
    trade_stats: dict
    findings: Annotated[list[AgentFindings], operator.add]
    narrative: str
    edge_profile: dict
    error: str | None


# ── Node: compute trade stats ────────────────────────────────────────────────

def compute_stats_node(state: AnalysisState) -> dict:
    df = state["df"]
    sells = df[(df["action"] == "SELL") & df["pnl"].notna()]

    stats = TradeStats(
        total_trades=len(df),
        total_buys=len(df[df["action"] == "BUY"]),
        total_sells=len(df[df["action"] == "SELL"]),
        unique_tickers=df["ticker"].nunique(),
        date_range_start=df["date"].min(),
        date_range_end=df["date"].max(),
        total_realized_pnl=round(sells["pnl"].sum(), 2),
        win_rate=round(sells["is_winner"].sum() / max(len(sells), 1) * 100, 1),
        avg_hold_days=round(sells["days_held"].dropna().mean(), 1) if len(sells) > 0 else 0.0,
    )
    return {"trade_stats": stats.model_dump()}


# ── Agent nodes (each returns a single AgentFindings wrapped in a list) ──────

def behavior_node(state: AnalysisState) -> dict:
    return {"findings": [behavior_agent(state["df"])]}

def timing_node(state: AnalysisState) -> dict:
    return {"findings": [timing_agent(state["df"])]}

def regime_node(state: AnalysisState) -> dict:
    return {"findings": [regime_agent(state["df"])]}

def sector_node(state: AnalysisState) -> dict:
    return {"findings": [sector_agent(state["df"])]}

def hold_duration_node(state: AnalysisState) -> dict:
    return {"findings": [hold_duration_agent(state["df"])]}

def luck_vs_skill_node(state: AnalysisState) -> dict:
    return {"findings": [luck_vs_skill_agent(state["df"])]}


# ── Node: Claude narrative synthesis ────────────────────────────────────────

NARRATIVE_SYSTEM = """You are a quantitative investment analyst specializing in behavioral finance.
You receive structured analysis of a personal investor's trading history.
Your job is to write a brutally honest, insightful edge report — about 400-500 words.

Structure your response as:
1. **Overall Edge Verdict** (2-3 sentences): Does this investor have a genuine, repeatable edge?
2. **Where Your Edge Lives** (bullet points): Specific conditions where they consistently outperform.
3. **Where You're Losing Alpha** (bullet points): Behavioral patterns and conditions that cost them money.
4. **The One Thing To Fix**: The single highest-impact change they could make.
5. **Bottom Line**: A direct, honest summary score — e.g. "Developing edge, not yet systematic."

Be specific with numbers. Reference actual metrics from the data. Don't be generic.
Do not hedge everything. Be direct."""


def synthesize_node(state: AnalysisState) -> dict:
    findings = state["findings"]
    stats    = state["trade_stats"]

    # Build structured summary for Claude
    findings_text = "\n\n".join([
        f"### {f.agent_name.upper()} AGENT\n"
        f"Insights:\n" + "\n".join(f"- {i}" for i in f.insights) + "\n"
        f"Key metrics: {json.dumps(f.metrics, default=str, indent=2)}"
        for f in findings
    ])

    prompt = f"""Here is a complete behavioral analysis of a personal investor's trading history.

## Trade Summary
{json.dumps(stats, default=str, indent=2)}

## Agent Findings
{findings_text}

Write the edge report now."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": NARRATIVE_SYSTEM},
            {"role": "user",   "content": prompt},
        ]
    )
    narrative = response.choices[0].message.content

    # Build structured edge profile
    edge_scores = {f.agent_name: f.edge_score for f in findings if f.edge_score is not None}
    all_insights = [i for f in findings for i in f.insights]

    edge_profile = {
        "edge_scores_by_dimension": edge_scores,
        "overall_edge_score": round(sum(edge_scores.values()) / max(len(edge_scores), 1), 3),
        "total_realized_pnl": stats.get("total_realized_pnl"),
        "overall_win_rate": stats.get("win_rate"),
        "key_insights": all_insights,
    }

    return {"narrative": narrative, "edge_profile": edge_profile}


# ── Build the graph ──────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    g = StateGraph(AnalysisState)

    g.add_node("compute_stats",   compute_stats_node)
    g.add_node("behavior",        behavior_node)
    g.add_node("timing",          timing_node)
    g.add_node("regime",          regime_node)
    g.add_node("sector",          sector_node)
    g.add_node("hold_duration",   hold_duration_node)
    g.add_node("luck_vs_skill",   luck_vs_skill_node)
    g.add_node("synthesize",      synthesize_node)

    # Stats runs first, then all 6 agents in parallel
    g.set_entry_point("compute_stats")
    for agent in ["behavior", "timing", "regime", "sector", "hold_duration", "luck_vs_skill"]:
        g.add_edge("compute_stats", agent)
        g.add_edge(agent, "synthesize")

    g.add_edge("synthesize", END)
    return g.compile()


# ── Public entry point ───────────────────────────────────────────────────────

def run_analysis(enriched_df: pd.DataFrame) -> EdgeReport:
    graph = build_graph()
    result = graph.invoke({
        "df":          enriched_df,
        "trade_stats": {},
        "findings":    [],
        "narrative":   "",
        "edge_profile":{},
        "error":       None,
    })

    findings_list = result["findings"]
    # Deduplicate (LangGraph fan-in can occasionally duplicate)
    seen = set()
    unique_findings = []
    for f in findings_list:
        if f.agent_name not in seen:
            seen.add(f.agent_name)
            unique_findings.append(f)

    stats = TradeStats(**result["trade_stats"])

    return EdgeReport(
        trade_stats=stats,
        agent_findings=unique_findings,
        narrative=result["narrative"],
        edge_profile=result["edge_profile"],
        generated_at=datetime.utcnow().isoformat(),
    )