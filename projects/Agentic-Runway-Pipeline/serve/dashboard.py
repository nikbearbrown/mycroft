"""
serve/dashboard.py  —  Sprint 7b: Streamlit dashboard (company comparison + trend charts).

A visual view of the stored runs (Sprint 6): compare companies side by side, and see a
company's risk signals over time. Read-only; it shows what's stored, never decides.

Requires: pip install streamlit duckdb pandas

Run (from the project root):
    streamlit run serve/dashboard.py
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

DB_PATH = "data/runs.duckdb"
DISTRESS = ("layoff", "security_issue", "executive_change")


def load():
    import duckdb
    if not Path(DB_PATH).exists():
        return None
    con = duckdb.connect(DB_PATH, read_only=True)
    df = con.execute("SELECT * FROM runs").df()
    con.close()
    return df


st.set_page_config(page_title="Runway-Risk Dashboard", layout="wide")
st.title("Runway-Risk Pipeline \u2014 Dashboard")
st.caption("Serves stored runs. It shows the data; a human still decides. HALT-AWAITING-HUMAN.")

df = load()
if df is None or df.empty:
    st.warning("No runs stored yet. Run:  python -m storage.store_runs data/deduped/signals.json --store")
    st.stop()

# --- company comparison (latest run) ---
st.header("Company comparison (latest run)")
latest = df[df["run_id"] == df["run_id"].max()]
comp = latest.groupby("company_id").agg(
    signals=("signal_id", "count"),
    validated=("validated", "sum"),
).reset_index()
distress_counts = (latest[latest["signal_type"].isin(DISTRESS)]
                   .groupby("company_id")["signal_id"].count())
comp["distress"] = comp["company_id"].map(distress_counts).fillna(0).astype(int)
st.dataframe(comp, use_container_width=True)
st.bar_chart(comp.set_index("company_id")[["signals", "distress"]])

# --- per-company trend over time ---
st.header("Risk trend over time")
company = st.selectbox("Company", sorted(df["company_id"].dropna().unique()))
cdf = df[df["company_id"] == company]
trend = cdf.groupby("run_id").agg(
    signals=("signal_id", "count"),
    validated=("validated", "sum"),
).reset_index()
tdistress = (cdf[cdf["signal_type"].isin(DISTRESS)]
             .groupby("run_id")["signal_id"].count())
trend["distress"] = trend["run_id"].map(tdistress).fillna(0).astype(int)
st.line_chart(trend.set_index("run_id")[["signals", "validated", "distress"]])
st.caption("Rising distress or falling validation is the story \u2014 for a human to judge.")
