import streamlit as st
import requests
import pandas as pd
import base64
import json
from io import BytesIO
from PIL import Image

st.set_page_config(
    page_title="Regime Performance — Portfolio Stress Testing",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        font-size: 3rem; font-weight: bold; color: #1f77b4;
        text-align: center; margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem; color: #555;
        text-align: center; margin-bottom: 2rem;
    }
    .risk-flag {
        display: inline-block; background-color: #3a0f0f; color: #ff6b6b;
        padding: 0.25rem 0.7rem; border-radius: 999px;
        margin: 0.2rem; font-size: 0.78rem; font-weight: 600;
        letter-spacing: 0.03em; border: 1px solid #7a2020;
    }
    .success-flag {
        display: inline-block; background-color: #0f3a1a; color: #51cf66;
        padding: 0.25rem 0.7rem; border-radius: 999px;
        margin: 0.2rem; font-size: 0.78rem; font-weight: 600;
        letter-spacing: 0.03em; border: 1px solid #1a6b2a;
    }
    .flags-row { display: flex; flex-wrap: wrap; gap: 0.3rem; margin-top: 0.4rem; }
    .regime-card {
        padding: 0.9rem 1.1rem; border-radius: 0.4rem;
        margin-bottom: 0.6rem; color: #1a1a1a;
    }
    .regime-low    { background-color: #f0fff0; border-left: 4px solid #2ca02c; }
    .regime-medium { background-color: #f0f4ff; border-left: 4px solid #1f77b4; }
    .regime-high   { background-color: #fff0f0; border-left: 4px solid #d62728; }
    </style>
""", unsafe_allow_html=True)

API_BASE_URL = "http://localhost:8001/api/v1"

REGIME_EMOJI = {"low": "🟢", "medium": "🔵", "high": "🔴"}
REGIME_LABEL = {"low": "Low VIX  (<15)", "medium": "Med VIX  (15–25)", "high": "High VIX  (>25)"}

for key, default in [("regime_result", None), ("regime_portfolio", [])]:
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown('<div class="main-header">📈 Portfolio Stress Testing System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Layer 4: Regime-Specific Performance Analysis</div>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📁 Portfolio Configuration")
    st.markdown("---")
    st.subheader("Add Holdings")

    input_method = st.radio("Input Method",
                            ["Manual Entry", "CSV Upload", "Example Portfolio"])

    if input_method == "Manual Entry":
        with st.form("add_holding_form"):
            c1, c2 = st.columns(2)
            with c1:
                ticker = st.text_input("Ticker", placeholder="AAPL").upper()
            with c2:
                shares = st.number_input("Shares", min_value=1, value=100, step=1)
            weight = st.number_input("Weight (%)", min_value=0.0, max_value=100.0,
                                     value=20.0, step=0.1)
            if st.form_submit_button("➕ Add Holding") and ticker:
                st.session_state.regime_portfolio.append({
                    "ticker": ticker,
                    "shares": int(shares),
                    "weight": round(float(weight) / 100, 4)
                })
                st.success(f"Added {ticker}")

    elif input_method == "CSV Upload":
        st.info("CSV columns: ticker, shares, weight")
        f = st.file_uploader("Choose CSV", type=["csv"])
        if f:
            df = pd.read_csv(f)
            st.session_state.regime_portfolio = df.to_dict("records")
            st.success(f"Loaded {len(df)} holdings")

    else:
        if st.button("Load Example Portfolio"):
            st.session_state.regime_portfolio = [
                {"ticker": "MSFT",  "shares": 40, "weight": 0.10},
                {"ticker": "JPM",   "shares": 50, "weight": 0.10},
                {"ticker": "JNJ",   "shares": 45, "weight": 0.09},
                {"ticker": "XOM",   "shares": 60, "weight": 0.09},
                {"ticker": "AMZN",  "shares": 15, "weight": 0.09},
                {"ticker": "UNH",   "shares": 20, "weight": 0.08},
                {"ticker": "LMT",   "shares": 18, "weight": 0.08},
                {"ticker": "NEE",   "shares": 80, "weight": 0.08},
                {"ticker": "PG",    "shares": 55, "weight": 0.08},
                {"ticker": "GLD",   "shares": 35, "weight": 0.08},
                {"ticker": "BRK-B", "shares": 25, "weight": 0.07},
                {"ticker": "TLT",   "shares": 70, "weight": 0.06},
            ]
            st.success("Loaded example portfolio")

    st.markdown("---")
    st.subheader("📋 Current Portfolio")

    if st.session_state.regime_portfolio:
        pdf = pd.DataFrame(st.session_state.regime_portfolio)
        pdf["weight (%)"] = pdf["weight"] * 100
        st.dataframe(pdf[["ticker", "shares", "weight (%)"]],
                     hide_index=True, use_container_width=True)
        total_w = sum(h["weight"] for h in st.session_state.regime_portfolio)
        if abs(total_w - 1.0) > 0.01:
            st.error(f"⚠️ Weights sum to {total_w*100:.1f}% (need 100%)")
        else:
            st.success(f"✓ Total weight: {total_w*100:.1f}%")
        if st.button("🗑️ Clear Portfolio", use_container_width=True):
            st.session_state.regime_portfolio = []
            st.rerun()
    else:
        st.info("No holdings added yet")

    st.markdown("---")
    st.subheader("⚙️ Parameters")

    with st.expander("Advanced Settings", expanded=False):
        lookback_days   = st.slider("Lookback Period (days)", 252, 2520, 756, 126)
        vix_low         = st.slider("VIX Low Threshold", 10.0, 20.0, 15.0, 0.5)
        vix_high        = st.slider("VIX High Threshold", 20.0, 40.0, 25.0, 0.5)
        min_regime_days = st.slider("Min Regime Days", 5, 60, 20, 5)
        use_5day_vix    = st.checkbox("Use 5-day VIX Average", value=True)

    st.markdown("---")

    if st.button("🚀 Run Regime Analysis", type="primary", use_container_width=True):
        portfolio = st.session_state.regime_portfolio
        if not portfolio:
            st.error("Add holdings first")
        elif abs(sum(h["weight"] for h in portfolio) - 1.0) > 0.01:
            st.error("Weights must sum to 100%")
        else:
            payload = {
                "portfolio": portfolio,
                "params": {
                    "lookback_days":      lookback_days,
                    "vix_low_threshold":  vix_low,
                    "vix_high_threshold": vix_high,
                    "min_regime_days":    min_regime_days,
                    "use_5day_vix":       use_5day_vix,
                    "transition_windows": [5, 20],
                }
            }
            with st.spinner("Analysing regime-specific performance… (20–40 s)"):
                try:
                    resp = requests.post(
                        f"{API_BASE_URL}/regime-performance",
                        json=payload, timeout=180
                    )
                    if resp.status_code == 200:
                        st.session_state.regime_result = resp.json()
                        st.success("✅ Analysis complete!")
                        st.rerun()
                    else:
                        st.error(f"API Error {resp.status_code}: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API on port 8001")
                except Exception as e:
                    st.error(f"Error: {e}")

# ── Main content ──────────────────────────────────────────────────────────────
if st.session_state.regime_result is None:
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 📈 What This Does")
        st.write("""
        Measures portfolio performance separately for each VIX regime —
        revealing whether returns, risk, and Sharpe ratios are consistent
        across market conditions or regime-dependent.
        """)
    with c2:
        st.markdown("### 🎯 Key Insights")
        st.write("""
        - Annualised return, volatility, and Sharpe per regime
        - Max drawdown and win rate per regime
        - Forward returns after regime transitions
        - Equity curve coloured by active VIX regime
        """)
    with c3:
        st.markdown("### 🔗 Completes the Loop")
        st.write("""
        Layer 1 showed correlation structure.
        Layer 2 showed crash damage.
        Layer 3 showed factor mechanics.
        Layer 4 shows the performance consequence of all three.
        """)
    st.markdown("---")
    st.info("👈 Configure your portfolio in the sidebar and click Run Regime Analysis")

else:
    result = st.session_state.regime_result
    stats  = result["regime_stats"]

    # ── Summary metrics ───────────────────────────────────────────────────
    st.markdown("## 📊 Summary")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Holdings", result["portfolio_summary"]["num_holdings"])
    with c2:
        st.metric("Regime Transitions",
                  result["portfolio_summary"]["total_transitions"])
    with c3:
        st.metric("Risk Flags", len(result["risk_flags"]))
    with c4:
        # Sharpe spread: low vs high VIX
        low_s  = next((s["sharpe_ratio"] for s in stats if s["regime"] == "low"),  None)
        high_s = next((s["sharpe_ratio"] for s in stats if s["regime"] == "high"), None)
        if low_s is not None and high_s is not None:
            st.metric("Sharpe: Low vs High VIX",
                      f"{low_s:.2f} vs {high_s:.2f}")
        else:
            st.metric("Lookback", f"{result['portfolio_summary']['lookback_days']}d")

    st.markdown("---")

    # ── Per-regime stat cards ─────────────────────────────────────────────
    st.markdown("## 🌡️ Performance by Regime")

    for s in stats:
        regime = s["regime"]
        if s["observations"] < 5:
            continue
        card_class = f"regime-card regime-{regime}"
        st.markdown(
            f'<div class="{card_class}">'
            f'<strong>{REGIME_EMOJI[regime]} {REGIME_LABEL[regime]}</strong>'
            f' &nbsp;|&nbsp; {s["observations"]} trading days'
            f'</div>',
            unsafe_allow_html=True
        )
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        with m1:
            st.metric("Ann. Return",    f"{s['ann_return']*100:+.1f}%")
        with m2:
            st.metric("Ann. Volatility", f"{s['ann_volatility']*100:.1f}%")
        with m3:
            st.metric("Sharpe Ratio",   f"{s['sharpe_ratio']:.2f}")
        with m4:
            st.metric("Max Drawdown",   f"{s['max_drawdown']*100:.1f}%")
        with m5:
            st.metric("Win Rate",       f"{s['win_rate']*100:.0f}%")
        with m6:
            st.metric("Cumulative Ret", f"{s['cumulative_return']*100:+.1f}%")

    st.markdown("---")

    # ── Transition summary table ──────────────────────────────────────────
    st.markdown("## 🔀 Regime Transition Forward Returns")
    st.caption(
        "Average portfolio return in the 5 and 20 trading days "
        "following each type of regime transition."
    )

    if result["transition_summaries"]:
        trans_rows = []
        for ts in result["transition_summaries"]:
            trans_rows.append({
                "Transition":      ts["label"],
                "# Events":        ts["n_events"],
                "Avg 5d Return":   f"{ts['avg_fwd_5d']*100:+.2f}%"  if ts["avg_fwd_5d"]  is not None else "N/A",
                "Avg 20d Return":  f"{ts['avg_fwd_20d']*100:+.2f}%" if ts["avg_fwd_20d"] is not None else "N/A",
                "% Neg 5d":        f"{ts['pct_negative_5d']*100:.0f}%"  if ts["pct_negative_5d"]  is not None else "N/A",
                "% Neg 20d":       f"{ts['pct_negative_20d']*100:.0f}%" if ts["pct_negative_20d"] is not None else "N/A",
            })
        st.dataframe(pd.DataFrame(trans_rows), hide_index=True, use_container_width=True)
    else:
        st.info("No regime transitions found in the lookback window.")

    st.markdown("---")

    # ── Visualizations ────────────────────────────────────────────────────
    st.markdown("## 📊 Visualizations")
    viz = result.get("visualizations", {})

    def show_b64(key: str, width: int = 900):
        try:
            img = Image.open(BytesIO(base64.b64decode(viz[key])))
            st.image(img, width=width)
        except Exception as e:
            st.error(f"Could not render chart: {e}")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Regime Stats",
        "🎯 Win Rate & Extremes",
        "🔀 Transition Heatmap",
        "📈 Equity Curve"
    ])

    with tab1:
        st.markdown("### Return, Volatility, Sharpe & Drawdown by Regime")
        show_b64("regime_stats_bar", width=950)

    with tab2:
        st.markdown("### Win Rate, Best Day & Worst Day by Regime")
        show_b64("win_rate_chart", width=900)

    with tab3:
        st.markdown("### Average Forward Returns After Regime Transitions")
        st.caption(
            "Green = positive average forward return after transition. "
            "Red = negative. Diagonal cells (same regime) are not applicable."
        )
        show_b64("transition_heatmap", width=800)

    with tab4:
        st.markdown("### Portfolio Equity Curve — Coloured by VIX Regime")
        st.caption(
            "🟢 Green segments = Low VIX  "
            "🔵 Blue segments = Med VIX  "
            "🔴 Red segments = High VIX"
        )
        show_b64("cumulative_chart", width=950)

    st.markdown("---")

    # ── Risk flags + recommendations ──────────────────────────────────────
    col_flags, col_recs = st.columns(2)

    with col_flags:
        st.markdown("## 🚨 Risk Flags")
        if result["risk_flags"]:
            pills = "".join(
                f'<span class="risk-flag">⚠ {f.replace("_", " ")}</span>'
                for f in result["risk_flags"]
            )
            st.markdown(f'<div class="flags-row">{pills}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="flags-row">'
                '<span class="success-flag">✓ No major regime performance flags</span>'
                '</div>',
                unsafe_allow_html=True
            )

    with col_recs:
        st.markdown("## 💡 Recommendations")
        for i, rec in enumerate(result["recommendations"], 1):
            st.markdown(f"**{i}.** {rec}")

    st.markdown("---")

    # ── Export ────────────────────────────────────────────────────────────
    st.markdown("## 💾 Export Results")
    ec1, ec2, ec3 = st.columns(3)

    with ec1:
        st.download_button(
            "📄 Download JSON",
            data=json.dumps(result, indent=2),
            file_name=f"regime_performance_{result['performance_id']}.json",
            mime="application/json",
            use_container_width=True
        )

    with ec2:
        rows = [{
            "Regime":        s["regime"],
            "Observations":  s["observations"],
            "Ann Return (%)":    round(s["ann_return"] * 100, 2),
            "Ann Vol (%)":       round(s["ann_volatility"] * 100, 2),
            "Sharpe":            round(s["sharpe_ratio"], 3),
            "Max DD (%)":        round(s["max_drawdown"] * 100, 2),
            "Win Rate (%)":      round(s["win_rate"] * 100, 1),
            "Cumulative Ret (%)":round(s["cumulative_return"] * 100, 2),
        } for s in stats]
        st.download_button(
            "📊 Download CSV",
            data=pd.DataFrame(rows).to_csv(index=False),
            file_name=f"regime_stats_{result['performance_id']}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with ec3:
        if st.button("🔄 Run New Analysis", use_container_width=True):
            st.session_state.regime_result = None
            st.rerun()

    st.markdown("---")
    with st.expander("🔍 View Raw Response"):
        st.json(result)