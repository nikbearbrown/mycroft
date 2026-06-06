# ============================================================================
# FILE: streamlit_app.py
# ============================================================================

import streamlit as st
import requests
import pandas as pd
import base64
from io import BytesIO
from PIL import Image
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Portfolio Stress Testing",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .risk-flag {
        background-color: #ffebee;
        color: #c62828;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.3rem 0;
        font-weight: bold;
    }
    .success-flag {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.3rem 0;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8001/api/v1"

# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'portfolio_data' not in st.session_state:
    st.session_state.portfolio_data = []

# Header
st.markdown('<div class="main-header">📊 Portfolio Stress Testing System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Layer 1: Regime-Dependent Diversification Analysis</div>', unsafe_allow_html=True)

# Sidebar - Portfolio Input
with st.sidebar:
    st.header("📁 Portfolio Configuration")
    
    st.markdown("---")
    st.subheader("Add Holdings")
    
    # Portfolio input method
    input_method = st.radio(
        "Input Method",
        ["Manual Entry", "CSV Upload", "Example Portfolio"],
        horizontal=False
    )
    
    if input_method == "Manual Entry":
        with st.form("add_holding_form"):
            col1, col2 = st.columns(2)
            with col1:
                ticker = st.text_input("Ticker", placeholder="AAPL").upper()
            with col2:
                shares = st.number_input("Shares", min_value=1, value=100, step=1)
            
            weight = st.number_input("Weight (%)", min_value=0.0, max_value=100.0, value=20.0, step=0.1)
            
            submitted = st.form_submit_button("➕ Add Holding")
            
            if submitted and ticker:
                st.session_state.portfolio_data.append({
                    "ticker": ticker,
                    "shares": int(shares),
                    "weight": float(weight) / 100
                })
                st.success(f"Added {ticker}")
    
    elif input_method == "CSV Upload":
        st.info("Upload CSV with columns: ticker, shares, weight")
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.session_state.portfolio_data = df.to_dict('records')
            st.success(f"Loaded {len(df)} holdings")
    
    else:  # Example Portfolio
        if st.button("Load Example Portfolio"):
            st.session_state.portfolio_data = [
                {"ticker": "AAPL", "shares": 100, "weight": 0.25},
                {"ticker": "MSFT", "shares": 75, "weight": 0.25},
                {"ticker": "GOOGL", "shares": 50, "weight": 0.20},
                {"ticker": "TSLA", "shares": 30, "weight": 0.15},
                {"ticker": "NVDA", "shares": 20, "weight": 0.15}
            ]
            st.success("Loaded example portfolio")
    
    st.markdown("---")
    st.subheader("📋 Current Portfolio")
    
    if st.session_state.portfolio_data:
        portfolio_df = pd.DataFrame(st.session_state.portfolio_data)
        portfolio_df['weight_pct'] = portfolio_df['weight'] * 100
        st.dataframe(
            portfolio_df[['ticker', 'shares', 'weight_pct']].rename(columns={'weight_pct': 'weight (%)'}),
            hide_index=True,
            use_container_width=True
        )
        
        total_weight = sum([h['weight'] for h in st.session_state.portfolio_data])
        if abs(total_weight - 1.0) > 0.01:
            st.error(f"⚠️ Weights must sum to 100% (currently {total_weight*100:.1f}%)")
        else:
            st.success(f"✓ Total weight: {total_weight*100:.1f}%")
        
        if st.button("🗑️ Clear Portfolio", use_container_width=True):
            st.session_state.portfolio_data = []
            st.rerun()
    else:
        st.info("No holdings added yet")
    
    st.markdown("---")
    st.subheader("⚙️ Analysis Parameters")
    
    with st.expander("Advanced Settings", expanded=False):
        lookback_days = st.slider("Lookback Period (days)", 252, 2520, 756, 126)
        rolling_window = st.slider("Rolling Window (days)", 20, 504, 252, 20)
        vix_low = st.slider("VIX Low Threshold", 10.0, 20.0, 15.0, 0.5)
        vix_high = st.slider("VIX High Threshold", 20.0, 40.0, 25.0, 0.5)
        min_regime_days = st.slider("Min Regime Days", 5, 60, 20, 5)
        use_5day_vix = st.checkbox("Use 5-day VIX Average", value=True)
    
    st.markdown("---")
    
    # Run Analysis Button
    if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
        if not st.session_state.portfolio_data:
            st.error("Please add holdings first")
        elif abs(sum([h['weight'] for h in st.session_state.portfolio_data]) - 1.0) > 0.01:
            st.error("Portfolio weights must sum to 100%")
        else:
            with st.spinner("Running analysis... This may take 30-60 seconds"):
                try:
                    payload = {
                        "portfolio": st.session_state.portfolio_data,
                        "params": {
                            "lookback_days": lookback_days,
                            "rolling_window": rolling_window,
                            "vix_low_threshold": vix_low,
                            "vix_high_threshold": vix_high,
                            "min_regime_days": min_regime_days,
                            "use_5day_vix": use_5day_vix
                        }
                    }
                    
                    response = requests.post(f"{API_BASE_URL}/analyze", json=payload, timeout=120)
                    
                    if response.status_code == 200:
                        st.session_state.analysis_result = response.json()
                        st.success("✅ Analysis completed!")
                        st.rerun()
                    else:
                        st.error(f"API Error: {response.status_code} - {response.text}")
                
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure the FastAPI service is running on port 8001")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Main Content Area
if st.session_state.analysis_result is None:
    # Landing page
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📈 What This Does")
        st.write("""
        Analyzes how your portfolio's diversification changes across different market volatility regimes:
        - **Low VIX (<15)**: Calm markets
        - **Medium VIX (15-25)**: Normal volatility
        - **High VIX (>25)**: Stress periods
        """)
    
    with col2:
        st.markdown("### 🎯 Key Insights")
        st.write("""
        Reveals hidden risks that emerge during market stress:
        - Correlation spikes between holdings
        - Diversification degradation
        - Effective portfolio concentration
        - Risk flags and recommendations
        """)
    
    with col3:
        st.markdown("### 🚀 Get Started")
        st.write("""
        1. Add your portfolio holdings in the sidebar
        2. Adjust analysis parameters (optional)
        3. Click "Run Analysis"
        4. Review results and visualizations
        """)
    
    st.markdown("---")
    st.info("👈 Add your portfolio holdings in the sidebar to begin analysis")

else:
    # Display Results
    result = st.session_state.analysis_result
    
    # Summary Metrics
    st.markdown("## 📊 Analysis Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Portfolio Holdings",
            result['portfolio_summary']['num_holdings']
        )
    
    with col2:
        st.metric(
            "Analysis Period",
            f"{result['portfolio_summary']['lookback_days']} days"
        )
    
    with col3:
        risk_severity = "🔴 HIGH" if len(result['risk_flags']) > 2 else "🟡 MEDIUM" if len(result['risk_flags']) > 0 else "🟢 LOW"
        st.metric(
            "Risk Level",
            risk_severity
        )
    
    with col4:
        st.metric(
            "Risk Flags",
            len(result['risk_flags'])
        )
    
    st.markdown("---")
    
    # Correlation Metrics Comparison
    st.markdown("## 🔄 Correlation Metrics by Regime")
    
    # Create comparison table
    metrics_data = {
        "Metric": [
            "Avg Pairwise Correlation",
            "Max Correlation",
            "Min Correlation",
            "Effective # of Assets"
        ],
        "Low VIX": [
            f"{result['regime_metrics']['low_vix']['avg_pairwise_correlation']:.3f}",
            f"{result['regime_metrics']['low_vix']['max_correlation']:.3f}",
            f"{result['regime_metrics']['low_vix']['min_correlation']:.3f}",
            f"{result['regime_metrics']['low_vix']['effective_n_assets']:.2f}"
        ],
        "Medium VIX": [
            f"{result['regime_metrics']['medium_vix']['avg_pairwise_correlation']:.3f}",
            f"{result['regime_metrics']['medium_vix']['max_correlation']:.3f}",
            f"{result['regime_metrics']['medium_vix']['min_correlation']:.3f}",
            f"{result['regime_metrics']['medium_vix']['effective_n_assets']:.2f}"
        ],
        "High VIX": [
            f"{result['regime_metrics']['high_vix']['avg_pairwise_correlation']:.3f}",
            f"{result['regime_metrics']['high_vix']['max_correlation']:.3f}",
            f"{result['regime_metrics']['high_vix']['min_correlation']:.3f}",
            f"{result['regime_metrics']['high_vix']['effective_n_assets']:.2f}"
        ]
    }
    
    metrics_df = pd.DataFrame(metrics_data)
    st.dataframe(metrics_df, hide_index=True, use_container_width=True)
    
    # Degradation Analysis
    st.markdown("## 📉 Diversification Degradation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Correlation Increase (Low → High VIX)",
            f"{result['degradation_analysis']['avg_corr_pct_increase']:.1f}%",
            delta=f"{result['degradation_analysis']['avg_corr_increase']:.3f}",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "Effective Assets Decrease",
            f"{result['degradation_analysis']['eff_assets_pct_decrease']:.1f}%",
            delta=f"-{result['degradation_analysis']['eff_assets_decrease']:.2f}",
            delta_color="inverse"
        )
    
    st.markdown("---")
    
    # Visualizations
    st.markdown("## 📊 Correlation Heatmaps")
    
    try:
        # Decode and display correlation heatmaps
        heatmap_base64 = result['visualizations']['correlation_heatmaps']
        heatmap_image = Image.open(BytesIO(base64.b64decode(heatmap_base64)))
        st.image(heatmap_image, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying heatmap: {str(e)}")
    
    st.markdown("---")
    
    st.markdown("## 📈 Degradation Analysis")
    
    try:
        # Decode and display degradation chart
        degradation_base64 = result['visualizations']['degradation_chart']
        degradation_image = Image.open(BytesIO(base64.b64decode(degradation_base64)))
        st.image(degradation_image, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying degradation chart: {str(e)}")
    
    st.markdown("---")
    
    # Risk Flags and Recommendations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("## 🚨 Risk Flags")
        
        if result['risk_flags']:
            for flag in result['risk_flags']:
                st.markdown(f'<div class="risk-flag">⚠️ {flag.replace("_", " ")}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-flag">✅ No major risk flags detected</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("## 💡 Recommendations")
        
        for i, rec in enumerate(result['recommendations'], 1):
            st.markdown(f"**{i}.** {rec}")
    
    st.markdown("---")
    
    # Export Options
    st.markdown("## 💾 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export JSON
        json_str = json.dumps(result, indent=2)
        st.download_button(
            label="📄 Download JSON",
            data=json_str,
            file_name=f"analysis_{result['analysis_id']}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Export CSV of metrics
        export_data = {
            "Analysis ID": [result['analysis_id']],
            "Timestamp": [result['timestamp']],
            "Holdings": [result['portfolio_summary']['num_holdings']],
            "Low VIX Avg Corr": [result['regime_metrics']['low_vix']['avg_pairwise_correlation']],
            "High VIX Avg Corr": [result['regime_metrics']['high_vix']['avg_pairwise_correlation']],
            "Correlation Increase %": [result['degradation_analysis']['avg_corr_pct_increase']],
            "Risk Flags": [len(result['risk_flags'])]
        }
        export_df = pd.DataFrame(export_data)
        
        st.download_button(
            label="📊 Download CSV",
            data=export_df.to_csv(index=False),
            file_name=f"metrics_{result['analysis_id']}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        if st.button("🔄 Run New Analysis", use_container_width=True):
            st.session_state.analysis_result = None
            st.rerun()
    
    st.markdown("---")
    
    # Analysis Details
    with st.expander("🔍 View Raw Analysis Data"):
        st.json(result)