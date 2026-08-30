"""ECIS Streamlit Dashboard."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ecis.dashboard.data import (
    get_agent_actions,
    get_pending_approvals,
    get_reader_weights,
    get_signals,
    get_signals_with_outcomes,
    get_summary_stats,
    get_ticker_registry,
    get_tickers,
)

_COLORS = {
    "bg": "#0f1419",
    "surface": "#1a222c",
    "surface2": "#243040",
    "ink": "#e8eef4",
    "muted": "#8b9aab",
    "accent": "#3d9b8f",
    "accent2": "#c4a35a",
    "raised": "#3d9b8f",
    "lowered": "#c45c5c",
    "maintained": "#7a8fa3",
    "grid": "#2a3544",
}

_PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color=_COLORS["ink"], size=13),
    margin=dict(l=40, r=20, t=48, b=40),
    xaxis=dict(gridcolor=_COLORS["grid"], zeroline=False),
    yaxis=dict(gridcolor=_COLORS["grid"], zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)


def _inject_styles() -> None:
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap');

:root {{
  --bg: {_COLORS["bg"]};
  --surface: {_COLORS["surface"]};
  --surface2: {_COLORS["surface2"]};
  --ink: {_COLORS["ink"]};
  --muted: {_COLORS["muted"]};
  --accent: {_COLORS["accent"]};
  --accent2: {_COLORS["accent2"]};
}}

html, body, [data-testid="stAppViewContainer"] {{
  background: var(--bg) !important;
  color: var(--ink);
  font-family: "DM Sans", system-ui, sans-serif;
}}

[data-testid="stAppViewContainer"]::before {{
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    radial-gradient(ellipse 80% 50% at 10% -10%, rgba(61, 155, 143, 0.18), transparent 55%),
    radial-gradient(ellipse 60% 40% at 90% 0%, rgba(196, 163, 90, 0.10), transparent 50%),
    linear-gradient(180deg, #121820 0%, var(--bg) 40%);
  animation: ambientShift 18s ease-in-out infinite alternate;
}}

@keyframes ambientShift {{
  from {{ filter: hue-rotate(0deg) brightness(1); }}
  to   {{ filter: hue-rotate(12deg) brightness(1.05); }}
}}

@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(14px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes countPulse {{
  0%, 100% {{ transform: scale(1); }}
  50% {{ transform: scale(1.02); }}
}}

.block-container {{
  padding-top: 1.5rem !important;
  max-width: 1200px;
  position: relative;
  z-index: 1;
}}

h1, h2, h3, .ecis-brand {{
  font-family: "Fraunces", Georgia, serif !important;
  letter-spacing: -0.02em;
  color: var(--ink) !important;
}}

.ecis-hero {{
  animation: fadeUp 0.7s ease-out both;
  margin-bottom: 1.75rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid {_COLORS["grid"]};
}}

.ecis-brand {{
  font-size: 2.35rem;
  font-weight: 600;
  margin: 0 0 0.35rem 0;
  background: linear-gradient(120deg, var(--ink) 0%, var(--accent) 55%, var(--accent2) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent !important;
}}

.ecis-tagline {{
  color: var(--muted);
  font-size: 1.05rem;
  margin: 0;
  max-width: 36rem;
  animation: fadeUp 0.85s ease-out 0.12s both;
}}

.metric-grid {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin: 1.25rem 0 1.75rem;
}}

.metric-card {{
  background: linear-gradient(160deg, var(--surface) 0%, var(--surface2) 100%);
  border: 1px solid {_COLORS["grid"]};
  border-radius: 12px;
  padding: 1.15rem 1.25rem;
  animation: fadeUp 0.6s ease-out both;
  transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
}}

.metric-card:nth-child(1) {{ animation-delay: 0.08s; }}
.metric-card:nth-child(2) {{ animation-delay: 0.16s; }}
.metric-card:nth-child(3) {{ animation-delay: 0.24s; }}

.metric-card:hover {{
  border-color: rgba(61, 155, 143, 0.45);
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.28);
}}

.metric-label {{
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  margin-bottom: 0.4rem;
}}

.metric-value {{
  font-family: "Fraunces", Georgia, serif;
  font-size: 2rem;
  font-weight: 600;
  color: var(--ink);
  animation: countPulse 2.8s ease-in-out infinite;
  animation-delay: 1s;
}}

.section-enter {{
  animation: fadeUp 0.55s ease-out both;
}}

div[data-testid="stTabs"] {{
  animation: fadeUp 0.65s ease-out 0.2s both;
}}

div[data-testid="stTabs"] button {{
  font-family: "DM Sans", sans-serif;
  color: var(--muted) !important;
}}

div[data-testid="stTabs"] button[aria-selected="true"] {{
  color: var(--accent) !important;
  border-bottom-color: var(--accent) !important;
}}

[data-testid="stMetric"],
[data-testid="stSidebar"] {{
  display: none;
}}

div[data-testid="stDataFrame"] {{
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid {_COLORS["grid"]};
  animation: fadeUp 0.5s ease-out both;
}}

.stSelectbox label, .stMultiSelect label, .stTextArea label, .stSlider label {{
  color: var(--muted) !important;
}}

div[data-baseweb="select"] > div {{
  background-color: var(--surface) !important;
  border-color: {_COLORS["grid"]} !important;
}}

.stButton > button {{
  background: var(--accent) !important;
  color: #0a1210 !important;
  border: none !important;
  font-weight: 600 !important;
  border-radius: 8px !important;
  transition: transform 0.2s ease, filter 0.2s ease !important;
}}

.stButton > button:hover {{
  filter: brightness(1.08);
  transform: translateY(-1px);
}}

@media (max-width: 768px) {{
  .metric-grid {{ grid-template-columns: 1fr; }}
  .ecis-brand {{ font-size: 1.75rem; }}
}}
</style>
        """,
        unsafe_allow_html=True,
    )


def _metric_cards(stats: dict) -> None:
    st.markdown(
        f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-label">Total Signals</div>
    <div class="metric-value">{stats["total_signals"]:,}</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Tickers</div>
    <div class="metric-value">{stats["total_tickers"]}</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Resolved Outcomes</div>
    <div class="metric-value">{stats["total_outcomes"]:,}</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _direction_chart(by_direction: dict) -> go.Figure | None:
    if not by_direction:
        return None
    labels = list(by_direction.keys())
    values = [by_direction[k] for k in labels]
    colors = [_COLORS.get(k, _COLORS["maintained"]) for k in labels]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.58,
                marker=dict(colors=colors, line=dict(color=_COLORS["bg"], width=2)),
                textinfo="label+percent",
                textfont=dict(size=12),
            )
        ]
    )
    layout = {**_PLOTLY_LAYOUT, "margin": dict(l=10, r=10, t=40, b=10)}
    fig.update_layout(
        **layout,
        title=dict(text="Direction mix", font=dict(size=16, family="Fraunces")),
        showlegend=False,
        height=280,
    )
    return fig


st.set_page_config(
    page_title="ECIS Dashboard",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)
_inject_styles()

st.markdown(
    """
<div class="ecis-hero">
  <p class="ecis-brand">ECIS</p>
  <p class="ecis-tagline">Earnings Call Intelligence Signals — explore extractions, reader performance, and calibration.</p>
</div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Signal Explorer",
    "Reader Comparison",
    "Model Comparison",
    "Calibration",
    "Agent Activity",
    "Approvals",
    "RAG Query",
])

with tab1:
    st.markdown('<div class="section-enter">', unsafe_allow_html=True)
    stats = get_summary_stats()
    _metric_cards(stats)

    left, right = st.columns([1.2, 1])
    with left:
        fig_dir = _direction_chart(stats.get("by_direction") or {})
        if fig_dir:
            st.plotly_chart(fig_dir, use_container_width=True, config={"displayModeBar": False})
    with right:
        st.markdown("##### Filters")
        tickers = get_tickers()
        sel_ticker = st.selectbox("Ticker", ["All"] + tickers, key="sig_ticker")
        sel_direction = st.selectbox(
            "Direction", ["All", "raised", "lowered", "maintained"], key="sig_dir"
        )
        sel_method = st.selectbox(
            "Source",
            ["All", "keyword", "finbert", "llm", "triangulated"],
            key="sig_method",
        )
        sel_model = st.selectbox(
            "Model",
            ["All", "llama", "mistral", "qwen"],
            key="sig_model",
        )

    df = get_signals(
        ticker=sel_ticker if sel_ticker != "All" else None,
        direction=sel_direction if sel_direction != "All" else None,
        source_method=sel_method if sel_method != "All" else None,
        llm_model=sel_model if sel_model != "All" else None,
    )

    if not df.empty:
        display_cols = [
            "signal_id", "ticker", "direction", "confidence_raw",
            "confidence_calibrated", "source_method", "section_label",
            "speaker", "speaker_role", "transcript_date", "llm_model",
            "low_confidence", "chunk_quality", "trend", "retry_count",
            "supporting_quote",
        ]
        available = [c for c in display_cols if c in df.columns]
        st.dataframe(df[available], use_container_width=True, height=420)

        if st.checkbox("Show reasoning traces"):
            for _, row in df.head(20).iterrows():
                if row.get("reasoning_trace"):
                    with st.expander(
                        f"Signal {row['signal_id']} — {row['ticker']} {row['direction']}"
                    ):
                        st.text(row["reasoning_trace"])
    else:
        st.info("No signals found. Run extraction first.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section-enter">', unsafe_allow_html=True)
    st.subheader("Reader Comparison")
    merged = get_signals_with_outcomes()

    if not merged.empty and "correct" in merged.columns:
        scored = merged.dropna(subset=["correct"])

        if not scored.empty:
            from ecis.scoring.metrics import brier_score, expected_calibration_error

            reader_metrics = []
            for method in scored["source_method"].unique():
                subset = scored[scored["source_method"] == method]
                confs = subset["confidence_raw"].tolist()
                outs = subset["correct"].astype(int).tolist()
                bs = brier_score(confs, outs)
                ece, _ = expected_calibration_error(confs, outs)
                acc = sum(outs) / len(outs) if outs else 0
                reader_metrics.append({
                    "Reader": method,
                    "N Samples": len(outs),
                    "Accuracy": round(acc, 4),
                    "Brier Score": round(bs, 4),
                    "ECE": round(ece, 4),
                })

            metrics_df = pd.DataFrame(reader_metrics)
            st.dataframe(metrics_df, use_container_width=True)

            fig = px.bar(
                metrics_df,
                x="Reader",
                y=["Brier Score", "ECE"],
                barmode="group",
                title="Reader performance",
                color_discrete_sequence=[_COLORS["accent"], _COLORS["accent2"]],
            )
            fig.update_layout(**_PLOTLY_LAYOUT, title_font=dict(family="Fraunces", size=16))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No resolved outcomes yet. Run outcome resolution first.")
    else:
        st.info("No signals with outcomes. Run extraction and outcome resolution first.")

    st.subheader("Current reader weights")
    weights = get_reader_weights()
    if not weights.empty:
        fig_w = px.bar(
            weights,
            x="reader_name",
            y="weight",
            title="Triangulation weights",
            color_discrete_sequence=[_COLORS["accent"]],
        )
        fig_w.update_layout(**_PLOTLY_LAYOUT, title_font=dict(family="Fraunces", size=16))
        st.plotly_chart(fig_w, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="section-enter">', unsafe_allow_html=True)
    st.subheader("Llama vs Mistral vs Qwen")
    try:
        from ecis.scoring.scorer import score_by_llm_model

        model_scores = score_by_llm_model()
    except Exception as exc:
        model_scores = []
        st.warning(f"Could not compute model scores: {exc}")

    if model_scores:
        model_df = pd.DataFrame(model_scores)
        if "murphy" in model_df.columns:
            model_df["reliability"] = model_df["murphy"].apply(
                lambda m: (m or {}).get("reliability")
            )
            model_df["resolution"] = model_df["murphy"].apply(
                lambda m: (m or {}).get("resolution")
            )
            model_df = model_df.drop(columns=["murphy"])
        st.dataframe(model_df, use_container_width=True)

        chart_df = pd.DataFrame(model_scores)
        if not chart_df.empty and "brier" in chart_df.columns:
            fig_m = px.bar(
                chart_df,
                x="llm_model",
                y=["brier", "ece"],
                barmode="group",
                title="Per-model Brier and ECE",
                color_discrete_sequence=[_COLORS["accent"], _COLORS["accent2"]],
            )
            fig_m.update_layout(**_PLOTLY_LAYOUT, title_font=dict(family="Fraunces", size=16))
            st.plotly_chart(fig_m, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info(
            "No per-model scores yet. Run extraction with `--model llama`, "
            "`--model mistral`, `--model qwen`, `--model both`, or `--model all`, "
            "then resolve outcomes."
        )

    try:
        from ecis.scoring.scorer import score_by_trend

        trend_scores = score_by_trend()
    except Exception:
        trend_scores = []
    labelled = [t for t in trend_scores if t.get("n_samples") and t.get("trend") != "unlabelled"]
    if labelled:
        st.subheader("By trend")
        st.dataframe(pd.DataFrame(labelled), use_container_width=True)

    registry = get_ticker_registry()
    if not registry.empty:
        st.subheader("Ticker registry")
        st.dataframe(registry, use_container_width=True, height=280)
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section-enter">', unsafe_allow_html=True)
    st.subheader("Calibration curves")
    merged = get_signals_with_outcomes()

    if not merged.empty and "correct" in merged.columns:
        scored = merged.dropna(subset=["correct"])

        if not scored.empty:
            from ecis.scoring.metrics import expected_calibration_error

            methods = scored["source_method"].unique().tolist()
            sel_readers = st.multiselect("Select readers", methods, default=list(methods[:3]))
            overlay_models = st.checkbox("Overlay LLM models", value=True, key="cal_models")

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1], mode="lines",
                name="Perfect",
                line=dict(dash="dash", color=_COLORS["muted"], width=1.5),
            ))

            palette = [_COLORS["accent"], _COLORS["accent2"], _COLORS["lowered"], "#6b8cae"]
            for i, method in enumerate(sel_readers):
                subset = scored[scored["source_method"] == method]
                confs = subset["confidence_raw"].tolist()
                outs = subset["correct"].astype(int).tolist()
                _, bins = expected_calibration_error(confs, outs)
                non_empty = [b for b in bins if b["count"] > 0]
                if non_empty:
                    fig.add_trace(go.Scatter(
                        x=[b["avg_confidence"] for b in non_empty],
                        y=[b["avg_accuracy"] for b in non_empty],
                        mode="lines+markers",
                        name=method,
                        line=dict(color=palette[i % len(palette)], width=2.5),
                        marker=dict(size=9),
                        text=[f"n={b['count']}" for b in non_empty],
                    ))

            if overlay_models and "llm_model" in scored.columns:
                from ecis.config.settings import settings as _settings

                model_palette = {"llama": _COLORS["accent"], "mistral": _COLORS["accent2"], "qwen": "#6b8cae"}
                aliases = scored["llm_model"].dropna().map(_settings.model_alias)
                scored = scored.assign(_alias=aliases)
                for alias, color in model_palette.items():
                    subset = scored[scored["_alias"] == alias]
                    if subset.empty:
                        continue
                    confs = subset["confidence_raw"].tolist()
                    outs = subset["correct"].astype(int).tolist()
                    _, bins = expected_calibration_error(confs, outs)
                    non_empty = [b for b in bins if b["count"] > 0]
                    if non_empty:
                        fig.add_trace(go.Scatter(
                            x=[b["avg_confidence"] for b in non_empty],
                            y=[b["avg_accuracy"] for b in non_empty],
                            mode="lines+markers",
                            name=alias,
                            line=dict(color=color, width=2, dash="dot"),
                            marker=dict(size=8),
                        ))

            base = {k: v for k, v in _PLOTLY_LAYOUT.items() if k not in ("xaxis", "yaxis")}
            fig.update_layout(
                **base,
                title=dict(text="Reliability diagram", font=dict(family="Fraunces", size=16)),
                xaxis_title="Mean predicted confidence",
                yaxis_title="Fraction correct",
                xaxis=dict(range=[0, 1], gridcolor=_COLORS["grid"], zeroline=False),
                yaxis=dict(range=[0, 1], gridcolor=_COLORS["grid"], zeroline=False),
                height=420,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No resolved outcomes for calibration curves.")
    else:
        st.info("No data available for calibration curves.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="section-enter">', unsafe_allow_html=True)
    st.subheader("Agent activity")
    agent_filter = st.selectbox(
        "Filter by agent",
        [
            "All",
            "orchestration_agent",
            "learning_graph",
            "vindication_aggregation",
            "recalibrator",
            "watchdog_triangulated",
            "watchdog_llm",
        ],
        key="agent_filter",
    )
    actions = get_agent_actions(
        agent_name=agent_filter if agent_filter != "All" else None
    )
    if not actions.empty:
        st.dataframe(actions, use_container_width=True, height=420)
    else:
        st.info("No agent actions recorded yet.")
    st.markdown("</div>", unsafe_allow_html=True)

with tab6:
    st.markdown('<div class="section-enter">', unsafe_allow_html=True)
    st.subheader("Human-in-the-loop approvals")
    pending = get_pending_approvals()
    if pending.empty:
        st.info("No pending proposals. Watchdog and learning-graph HITL items appear here.")
    else:
        for _, row in pending.iterrows():
            aid = int(row["approval_id"])
            with st.expander(
                f"#{aid} — {row['agent_name']} · {row['action_type']} · {row['created_at']}",
                expanded=True,
            ):
                st.markdown("**Proposal**")
                st.json(row["proposal"] if isinstance(row["proposal"], dict) else {})
                st.markdown("**Evidence**")
                st.json(row["evidence"] if isinstance(row["evidence"], dict) else {})
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Approve", key=f"approve_{aid}", type="primary"):
                        from ecis.db.approvals import resolve_approval

                        try:
                            resolve_approval(aid, approved=True)
                            st.success(f"Approved #{aid}")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))
                with c2:
                    if st.button("Reject", key=f"reject_{aid}"):
                        from ecis.db.approvals import resolve_approval

                        try:
                            resolve_approval(aid, approved=False)
                            st.warning(f"Rejected #{aid}")
                            st.rerun()
                        except Exception as exc:
                            st.error(str(exc))
    st.markdown("</div>", unsafe_allow_html=True)

with tab7:
    st.markdown('<div class="section-enter">', unsafe_allow_html=True)
    st.subheader("Semantic search")
    query_text = st.text_area("Query earnings guidance", height=100)
    tickers = get_tickers()
    rag_cols = st.columns(3)
    with rag_cols[0]:
        rag_ticker = st.selectbox("Ticker", ["All"] + tickers, key="rag_ticker")
    with rag_cols[1]:
        rag_section = st.selectbox(
            "Section", ["All", "prepared_remarks", "qa"], key="rag_section"
        )
    with rag_cols[2]:
        n_results = st.slider("Results", 1, 20, 5)

    if st.button("Search") and query_text:
        try:
            from ecis.embedding.embedder import query_similar

            results = query_similar(
                query_text,
                n_results=n_results,
                ticker=rag_ticker if rag_ticker != "All" else None,
                section_label=rag_section if rag_section != "All" else None,
            )
            if results:
                for i, r in enumerate(results, 1):
                    meta = r["metadata"]
                    dist = r["distance"]
                    with st.expander(
                        f"Result {i} — {meta.get('ticker', '?')} "
                        f"({meta.get('transcript_date', '?')}) "
                        f"[{1 - dist:.3f}]"
                    ):
                        st.markdown(f"**Section:** {meta.get('section_label', '?')}")
                        st.markdown(f"**Speaker:** {meta.get('speaker', 'Unknown')}")
                        st.markdown(f"**Source:** `{meta.get('source_file', '?')}`")
                        st.text(r["text"])
            else:
                st.warning("No results found.")
        except Exception as e:
            st.error(f"Search failed: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

