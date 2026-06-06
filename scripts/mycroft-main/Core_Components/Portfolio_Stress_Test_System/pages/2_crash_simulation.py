import streamlit as st
import requests
import pandas as pd
import base64
import json
from io import BytesIO
from PIL import Image
from datetime import datetime, date

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crash Simulation — Portfolio Stress Testing",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Shared CSS (matches Layer 1) ──────────────────────────────────────────────
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
    .metric-card {
        background-color: #f0f2f6; padding: 1rem;
        border-radius: 0.5rem; margin: 0.5rem 0;
    }
    .risk-flag {
        display: inline-block;
        background-color: #3a0f0f;
        color: #ff6b6b;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        margin: 0.2rem 0.2rem 0.2rem 0;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        border: 1px solid #7a2020;
    }
    .success-flag {
        display: inline-block;
        background-color: #0f3a1a;
        color: #51cf66;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        margin: 0.2rem 0.2rem 0.2rem 0;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        border: 1px solid #1a6b2a;
    }
    .flags-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.3rem;
        margin-top: 0.4rem;
    }
    .crash-card {
        background-color: #fff8f8; border-left: 4px solid #d62728;
        padding: 1rem; border-radius: 0.4rem; margin-bottom: 1rem;
        color: #1a1a1a;
    }
    .crash-card-ok {
        background-color: #f8fff8; border-left: 4px solid #2ca02c;
        padding: 1rem; border-radius: 0.4rem; margin-bottom: 1rem;
        color: #1a1a1a;
    }
    </style>
""", unsafe_allow_html=True)

API_BASE_URL = "http://localhost:8001/api/v1"

PREDEFINED_CRASHES = {
    "covid_2020":       ("COVID Crash",       "2020-02-19", "2020-03-23", "SPY"),
    "tech_selloff_2022":("Tech Selloff 2022", "2022-01-03", "2022-10-12", "QQQ"),
    "q4_selloff_2018":  ("Q4 Selloff 2018",   "2018-09-20", "2018-12-24", "SPY"),
    "flash_crash_2015": ("Flash Crash 2015",  "2015-08-01", "2015-08-24", "SPY"),
}

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("crash_result", None),
    ("crash_portfolio", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">📉 Portfolio Stress Testing System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Layer 2: Historical Crash Simulation</div>', unsafe_allow_html=True)

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
                st.session_state.crash_portfolio.append({
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
            st.session_state.crash_portfolio = df.to_dict("records")
            st.success(f"Loaded {len(df)} holdings")

    else:
        if st.button("Load Example Portfolio"):
            st.session_state.crash_portfolio = [
                {"ticker": "AAPL",  "shares": 100, "weight": 0.25},
                {"ticker": "MSFT",  "shares": 75,  "weight": 0.25},
                {"ticker": "GOOGL", "shares": 50,  "weight": 0.20},
                {"ticker": "TSLA",  "shares": 30,  "weight": 0.15},
                {"ticker": "NVDA",  "shares": 20,  "weight": 0.15},
            ]
            st.success("Loaded example portfolio")

    st.markdown("---")
    st.subheader("📋 Current Portfolio")

    if st.session_state.crash_portfolio:
        pdf = pd.DataFrame(st.session_state.crash_portfolio)
        pdf["weight (%)"] = pdf["weight"] * 100
        st.dataframe(pdf[["ticker", "shares", "weight (%)"]],
                     hide_index=True, use_container_width=True)
        total_w = sum(h["weight"] for h in st.session_state.crash_portfolio)
        if abs(total_w - 1.0) > 0.01:
            st.error(f"⚠️ Weights sum to {total_w*100:.1f}% (need 100%)")
        else:
            st.success(f"✓ Total weight: {total_w*100:.1f}%")
        if st.button("🗑️ Clear Portfolio", use_container_width=True):
            st.session_state.crash_portfolio = []
            st.rerun()
    else:
        st.info("No holdings added yet")

    st.markdown("---")

    # ── Crash period selection ─────────────────────────────────────────────
    st.subheader("💥 Crash Periods")

    selected_keys = []
    for key, (name, start, end, bench) in PREDEFINED_CRASHES.items():
        if st.checkbox(f"{name}  ({start} → {end})", value=True, key=f"cb_{key}"):
            selected_keys.append(key)

    st.markdown("---")
    st.subheader("📅 Custom Crash Window (optional)")
    use_custom = st.checkbox("Add custom period")
    custom_payload = None

    if use_custom:
        with st.form("custom_crash_form"):
            custom_name  = st.text_input("Label", value="My Custom Period")
            custom_key   = st.text_input("Key (no spaces)", value="custom_1")
            col_s, col_e = st.columns(2)
            with col_s:
                custom_start = st.date_input("Start", value=date(2023, 3, 1))
            with col_e:
                custom_end   = st.date_input("End",   value=date(2023, 5, 4))
            custom_bench = st.selectbox("Benchmark", ["SPY", "QQQ", "DIA", "IWM"])
            custom_desc  = st.text_area("Description (optional)", height=60)
            if st.form_submit_button("✅ Set Custom Period"):
                if custom_start >= custom_end:
                    st.error("End date must be after start date")
                else:
                    custom_payload = {
                        "key":              custom_key.strip().replace(" ", "_"),
                        "name":             custom_name,
                        "start":            str(custom_start),
                        "end":              str(custom_end),
                        "benchmark_ticker": custom_bench,
                        "description":      custom_desc or None,
                    }
                    st.success(f"Custom period set: {custom_name}")

    st.markdown("---")

    # ── Run button ─────────────────────────────────────────────────────────
    if st.button("🚀 Run Crash Simulation", type="primary", use_container_width=True):
        portfolio = st.session_state.crash_portfolio

        if not portfolio:
            st.error("Add holdings first")
        elif abs(sum(h["weight"] for h in portfolio) - 1.0) > 0.01:
            st.error("Weights must sum to 100%")
        elif not selected_keys and not custom_payload:
            st.error("Select at least one crash period")
        else:
            payload: dict = {
                "portfolio":       portfolio,
                "selected_crashes": selected_keys if selected_keys else None,
            }
            if custom_payload:
                payload["custom_crash"] = custom_payload

            with st.spinner("Fetching historical data and simulating crashes… (30–90 s)"):
                try:
                    resp = requests.post(
                        f"{API_BASE_URL}/crash-simulation",
                        json=payload,
                        timeout=180
                    )
                    if resp.status_code == 200:
                        st.session_state.crash_result = resp.json()
                        st.success("✅ Simulation completed!")
                        st.rerun()
                    else:
                        st.error(f"API Error {resp.status_code}: {resp.text}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API on port 8001")
                except Exception as e:
                    st.error(f"Error: {e}")

# ── Main content ──────────────────────────────────────────────────────────────
if st.session_state.crash_result is None:
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 📉 What This Does")
        st.write("""
        Time-travels your current holdings through past market crashes to reveal
        structural vulnerabilities before they appear in live performance.
        """)
    with c2:
        st.markdown("### 🎯 Key Insights")
        st.write("""
        - Portfolio vs benchmark drawdown paths
        - Which holdings drove the most loss
        - How long recovery took after each crash
        - Concentrated loss drivers across events
        """)
    with c3:
        st.markdown("### 🚀 Get Started")
        st.write("""
        1. Add portfolio holdings in the sidebar
        2. Select crash periods to simulate
        3. Optionally add a custom window
        4. Click "Run Crash Simulation"
        """)
    st.markdown("---")
    st.info("👈 Configure your portfolio and crash periods in the sidebar")

else:
    result = st.session_state.crash_result

    # ── Top-level summary metrics ─────────────────────────────────────────
    st.markdown("## 📊 Simulation Summary")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Holdings", result["portfolio_summary"]["num_holdings"])
    with col2:
        st.metric("Crashes Simulated", result["portfolio_summary"]["crashes_run"])
    with col3:
        st.metric("Avg Max Drawdown",
                  f"{result['avg_max_drawdown']*100:.1f}%",
                  delta=None)
    with col4:
        rel = result["avg_relative_performance"]
        st.metric("Avg vs Benchmark",
                  f"{rel*100:+.1f}%",
                  delta=f"{rel*100:+.1f}%",
                  delta_color="normal")

    st.markdown("---")

    # ── Per-crash results ─────────────────────────────────────────────────
    st.markdown("## 💥 Results by Crash Period")

    for crash in result["crash_results"]:
        is_worst = (crash["key"] == result["worst_crash"])
        card_class = "crash-card" if crash["max_drawdown"] < -0.10 else "crash-card-ok"

        st.markdown(
            f'<div class="{card_class}"><strong>{"🔴 " if is_worst else ""}  {crash["name"]}</strong>'
            f'  &nbsp;|&nbsp;  {crash["start"]} → {crash["end"]}'
            f'  &nbsp;|&nbsp;  {crash["trading_days"]} trading days'
            f'  &nbsp;|&nbsp;  Benchmark: {crash["benchmark_ticker"]}'
            f'<br><small>{crash["description"]}</small></div>',
            unsafe_allow_html=True
        )

        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric("Portfolio Return",
                      f"{crash['portfolio_total_return']*100:+.1f}%")
        with m2:
            st.metric("Benchmark Return",
                      f"{crash['benchmark_total_return']*100:+.1f}%")
        with m3:
            rel = crash["relative_performance"]
            st.metric("vs Benchmark",
                      f"{rel*100:+.1f}%",
                      delta=f"{rel*100:+.1f}%",
                      delta_color="normal")
        with m4:
            st.metric("Max Drawdown",
                      f"{crash['max_drawdown']*100:.1f}%")
        with m5:
            rec = crash["recovery_days"]
            st.metric("Recovery",
                      f"{rec} days" if rec else "Not recovered")

        # Loss drivers table
        with st.expander(f"📊 Loss Attribution — {crash['name']}"):
            drivers_df = pd.DataFrame([{
                "Ticker":             d["ticker"],
                "Weight (%)":         f"{d['weight']*100:.1f}",
                "Period Return (%)":  f"{d['period_return']*100:+.2f}",
                "Contribution (%)":   f"{d['contribution_to_loss']*100:+.2f}",
                "Share of Loss (%)":  f"{d['contribution_pct']*100:+.1f}",
            } for d in crash["loss_drivers"]])
            st.dataframe(drivers_df, hide_index=True, use_container_width=True)

        # Risk flags for this crash
        if crash["risk_flags"]:
            pills = ""
            for flag in crash["risk_flags"]:
                display = (flag
                    .replace("_", " ")
                    .replace("CONCENTRATED LOSS DRIVER:", "⚡ ")
                )
                pills += f'<span class="risk-flag">⚠ {display}</span>'
            st.markdown(f'<div class="flags-row">{pills}</div>', unsafe_allow_html=True)

        st.markdown("---")

    # ── Visualizations ────────────────────────────────────────────────────
    viz = result.get("visualizations", {})

    tab1, tab2, tab3 = st.tabs(["📉 Drawdown Paths", "📊 Loss Attribution", "🗺️ Summary Heatmap"])

    def show_b64(key: str, width: int = 900):
        try:
            img = Image.open(BytesIO(base64.b64decode(viz[key])))
            st.image(img, width=width)
        except Exception as e:
            st.error(f"Could not render chart: {e}")

    with tab1:
        st.markdown("### Portfolio vs Benchmark Drawdown Paths")
        show_b64("drawdown_chart")

    with tab2:
        st.markdown("### Loss Attribution by Holding")
        show_b64("loss_driver_chart")

    with tab3:
        st.markdown("### Holding Returns Across All Crashes")
        show_b64("summary_heatmap")

    st.markdown("---")

    # ── Overall risk flags + recommendations ─────────────────────────────
    col_flags, col_recs = st.columns(2)

    with col_flags:
        st.markdown("## 🚨 Overall Risk Flags")
        if result["overall_risk_flags"]:
            pills = ""
            for flag in result["overall_risk_flags"]:
                pills += f'<span class="risk-flag">⚠ {flag.replace("_", " ")}</span>'
            st.markdown(f'<div class="flags-row">{pills}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="flags-row"><span class="success-flag">✓ No major cross-crash risk flags</span></div>',
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
            label="📄 Download JSON",
            data=json.dumps(result, indent=2),
            file_name=f"crash_simulation_{result['simulation_id']}.json",
            mime="application/json",
            use_container_width=True
        )

    with ec2:
        rows = []
        for c in result["crash_results"]:
            rows.append({
                "Crash":               c["name"],
                "Portfolio Return (%)": round(c["portfolio_total_return"] * 100, 2),
                "Benchmark Return (%)": round(c["benchmark_total_return"] * 100, 2),
                "Relative Perf (%)":   round(c["relative_performance"] * 100, 2),
                "Max Drawdown (%)":    round(c["max_drawdown"] * 100, 2),
                "Recovery (days)":     c["recovery_days"] or "N/A",
            })
        st.download_button(
            label="📊 Download CSV",
            data=pd.DataFrame(rows).to_csv(index=False),
            file_name=f"crash_metrics_{result['simulation_id']}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with ec3:
        if st.button("🔄 Run New Simulation", use_container_width=True):
            st.session_state.crash_result = None
            st.rerun()

    st.markdown("---")
    with st.expander("🔍 View Raw Response"):
        st.json(result)