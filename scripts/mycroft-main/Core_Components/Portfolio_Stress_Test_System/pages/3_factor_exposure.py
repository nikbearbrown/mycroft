import streamlit as st
import requests
import pandas as pd
import base64
import json
from io import BytesIO
from PIL import Image

st.set_page_config(
    page_title="Factor Exposure — Portfolio Stress Testing",
    page_icon="🔬",
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
    .factor-card {
        background-color: #f0f4ff; border-left: 4px solid #1f77b4;
        padding: 0.8rem 1rem; border-radius: 0.4rem; margin-bottom: 0.5rem;
        color: #1a1a1a;
    }
    </style>
""", unsafe_allow_html=True)

API_BASE_URL = "http://localhost:8001/api/v1"

FACTOR_DESCRIPTIONS = {
    "MKT": "Market Beta — sensitivity to broad market moves",
    "SMB": "Size — small-cap vs large-cap tilt",
    "HML": "Value — high book-to-market vs growth tilt",
    "RMW": "Profitability — high vs low operating profitability",
    "CMA": "Investment — conservative vs aggressive reinvestment",
    "UMD": "Momentum — recent winners vs recent losers",
}

for key, default in [("factor_result", None), ("factor_portfolio", [])]:
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown('<div class="main-header">🔬 Portfolio Stress Testing System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Layer 3: Factor Exposure Decomposition</div>', unsafe_allow_html=True)

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
                st.session_state.factor_portfolio.append({
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
            st.session_state.factor_portfolio = df.to_dict("records")
            st.success(f"Loaded {len(df)} holdings")

    else:
        if st.button("Load Example Portfolio"):
            st.session_state.factor_portfolio = [
                {"ticker": "AAPL",  "shares": 100, "weight": 0.25},
                {"ticker": "MSFT",  "shares": 75,  "weight": 0.25},
                {"ticker": "GOOGL", "shares": 50,  "weight": 0.20},
                {"ticker": "TSLA",  "shares": 30,  "weight": 0.15},
                {"ticker": "NVDA",  "shares": 20,  "weight": 0.15},
            ]
            st.success("Loaded example portfolio")

    st.markdown("---")
    st.subheader("📋 Current Portfolio")

    if st.session_state.factor_portfolio:
        pdf = pd.DataFrame(st.session_state.factor_portfolio)
        pdf["weight (%)"] = pdf["weight"] * 100
        st.dataframe(pdf[["ticker", "shares", "weight (%)"]],
                     hide_index=True, use_container_width=True)
        total_w = sum(h["weight"] for h in st.session_state.factor_portfolio)
        if abs(total_w - 1.0) > 0.01:
            st.error(f"⚠️ Weights sum to {total_w*100:.1f}% (need 100%)")
        else:
            st.success(f"✓ Total weight: {total_w*100:.1f}%")
        if st.button("🗑️ Clear Portfolio", use_container_width=True):
            st.session_state.factor_portfolio = []
            st.rerun()
    else:
        st.info("No holdings added yet")

    st.markdown("---")
    st.subheader("⚙️ Parameters")

    with st.expander("Advanced Settings", expanded=False):
        lookback_days   = st.slider("Lookback Period (days)", 252, 2520, 756, 126)
        rolling_window  = st.slider("Rolling Window (days)", 60, 504, 252, 20)
        vix_low         = st.slider("VIX Low Threshold", 10.0, 20.0, 15.0, 0.5)
        vix_high        = st.slider("VIX High Threshold", 20.0, 40.0, 25.0, 0.5)
        min_regime_days = st.slider("Min Regime Days", 5, 60, 20, 5)
        use_5day_vix    = st.checkbox("Use 5-day VIX Average", value=True)
        sig_level       = st.select_slider(
            "Significance Level (α)", options=[0.01, 0.05, 0.10], value=0.05
        )

    st.markdown("---")

    if st.button("🚀 Run Factor Analysis", type="primary", use_container_width=True):
        portfolio = st.session_state.factor_portfolio
        if not portfolio:
            st.error("Add holdings first")
        elif abs(sum(h["weight"] for h in portfolio) - 1.0) > 0.01:
            st.error("Weights must sum to 100%")
        else:
            payload = {
                "portfolio": portfolio,
                "params": {
                    "lookback_days":   lookback_days,
                    "rolling_window":  rolling_window,
                    "vix_low_threshold":  vix_low,
                    "vix_high_threshold": vix_high,
                    "min_regime_days": min_regime_days,
                    "use_5day_vix":    use_5day_vix,
                    "significance_level": sig_level,
                }
            }
            with st.spinner("Running factor decomposition… (30–60 s)"):
                try:
                    resp = requests.post(
                        f"{API_BASE_URL}/factor-exposure",
                        json=payload, timeout=180
                    )
                    if resp.status_code == 200:
                        st.session_state.factor_result = resp.json()
                        st.success("✅ Analysis complete!")
                        st.rerun()
                    else:
                        st.error(f"API Error {resp.status_code}: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API on port 8001")
                except Exception as e:
                    st.error(f"Error: {e}")

# ── Main content ──────────────────────────────────────────────────────────────
if st.session_state.factor_result is None:
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🔬 What This Does")
        st.write("""
        Reveals the hidden factor bets driving your portfolio returns using the
        Fama-French 5-factor + momentum model.
        """)
    with c2:
        st.markdown("### 🎯 Key Insights")
        st.write("""
        - Which factors explain your returns (and how much)
        - Whether factor exposures are drifting over time
        - How factor loadings shift across VIX regimes
        - Unexplained alpha or idiosyncratic risk
        """)
    with c3:
        st.markdown("### 📐 The Six Factors")
        for f, desc in FACTOR_DESCRIPTIONS.items():
            st.markdown(f"**{f}** — {desc.split('—')[1].strip()}")
    st.markdown("---")
    st.info("👈 Configure your portfolio in the sidebar and click Run Factor Analysis")

else:
    result = st.session_state.factor_result
    static = result["static_regression"]

    # ── Summary metrics ───────────────────────────────────────────────────
    st.markdown("## 📊 Regression Summary")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("R²", f"{static['r_squared']:.3f}")
    with c2:
        st.metric("Unexplained Variance",
                  f"{static['unexplained_variance_pct']:.1f}%")
    with c3:
        alpha_pct = static['alpha'] * 100
        st.metric("Annual Alpha",
                  f"{alpha_pct:+.2f}%",
                  delta=f"{'sig.' if static['alpha_p_value'] < 0.05 else 'insig.'}")
    with c4:
        st.metric("Dominant Factor", static["dominant_factor"])

    st.markdown("---")

    # ── Factor loadings table ─────────────────────────────────────────────
    st.markdown("## 📐 Factor Loadings")

    rows = []
    for l in static["factor_loadings"]:
        rows.append({
            "Factor":       l["factor"],
            "Description":  FACTOR_DESCRIPTIONS.get(l["factor"], ""),
            "Beta (β)":     f"{l['beta']:+.4f}",
            "t-stat":       f"{l['t_stat']:+.3f}",
            "p-value":      f"{l['p_value']:.4f}",
            "Significant":  "✓" if l["significant"] else "—",
            "Variance %":   f"{l['contribution_to_variance']*100:.1f}%",
        })

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True
    )

    st.markdown("---")

    # ── Regime table ──────────────────────────────────────────────────────
    st.markdown("## 🌡️ Factor Loadings by VIX Regime")

    regime_rows = []
    for regime in result["regime_regressions"]:
        row = {
            "Regime":  regime["regime"].capitalize() + " VIX",
            "Obs":     regime["observations"],
            "R²":      f"{regime['r_squared']:.3f}",
            "Alpha/yr":f"{regime['alpha']*100:+.2f}%",
        }
        for l in regime["factor_loadings"]:
            row[l["factor"]] = f"{l['beta']:+.3f}{'*' if l['significant'] else ''}"
        regime_rows.append(row)

    st.dataframe(
        pd.DataFrame(regime_rows),
        hide_index=True,
        use_container_width=True
    )
    st.caption("* = statistically significant at chosen α level")

    st.markdown("---")

    # ── Visualizations ────────────────────────────────────────────────────
    st.markdown("## 📊 Visualizations")
    viz = result.get("visualizations", {})

    def show_b64(key: str, width: int = 850):
        try:
            img = Image.open(BytesIO(base64.b64decode(viz[key])))
            st.image(img, width=width)
        except Exception as e:
            st.error(f"Could not render chart: {e}")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Factor Betas",
        "🥧 Variance Decomposition",
        "📈 Rolling Betas",
        "🗺️ Regime Heatmap"
    ])

    with tab1:
        st.markdown("### Factor Beta Coefficients")
        st.caption("Solid = statistically significant. Grey = insignificant. "
                   "* p<0.05  ** p<0.01")
        show_b64("factor_betas", width=750)

    with tab2:
        st.markdown("### Variance Decomposition")
        st.caption("How much of your portfolio's variance each factor explains.")
        show_b64("variance_decomposition", width=600)

    with tab3:
        st.markdown("### Rolling Factor Loadings (252-day window)")
        st.caption("⚠ = drift flag triggered (beta range > 0.4 over the window)")
        show_b64("rolling_betas", width=950)

    with tab4:
        st.markdown("### Factor Loadings by VIX Regime")
        st.caption("How factor exposures shift between calm and stress markets. "
                   "* = statistically significant.")
        show_b64("regime_heatmap", width=650)

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
                '<span class="success-flag">✓ No major factor risk flags</span>'
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
            file_name=f"factor_exposure_{result['exposure_id']}.json",
            mime="application/json",
            use_container_width=True
        )

    with ec2:
        rows = [{"Factor": l["factor"],
                 "Beta": l["beta"],
                 "t-stat": l["t_stat"],
                 "p-value": l["p_value"],
                 "Significant": l["significant"],
                 "Variance %": round(l["contribution_to_variance"] * 100, 2)}
                for l in static["factor_loadings"]]
        st.download_button(
            "📊 Download CSV",
            data=pd.DataFrame(rows).to_csv(index=False),
            file_name=f"factor_loadings_{result['exposure_id']}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with ec3:
        if st.button("🔄 Run New Analysis", use_container_width=True):
            st.session_state.factor_result = None
            st.rerun()

    st.markdown("---")
    with st.expander("🔍 View Raw Response"):
        st.json(result)