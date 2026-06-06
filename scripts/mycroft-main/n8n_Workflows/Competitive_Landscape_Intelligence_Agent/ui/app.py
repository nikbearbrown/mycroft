import json
import subprocess
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "data" / "outputs"
SCRIPTS = ROOT / "scripts"

FILES = {
    "profiles": OUTPUTS / "clean_company_profiles.json",
    "scorecard": OUTPUTS / "company_scorecard.csv",
    "winner": OUTPUTS / "winner_report.md",
    "summary": OUTPUTS / "clean_summary.md",
}

st.set_page_config(page_title="Mycroft — Competitive Change UI", layout="wide")

st.title("Competitive Change Agent — UI (Mycroft)")
st.caption("Loads existing outputs + provides a Q/A interface on top.")

# ---------- Helpers ----------
def read_text(p: Path) -> str:
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")

def read_json(p: Path):
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8", errors="ignore"))

def load_scorecard(p: Path):
    if not p.exists():
        return None
    return pd.read_csv(p)

def outputs_status():
    rows = []
    for k, p in FILES.items():
        rows.append({
            "artifact": k,
            "path": str(p.relative_to(ROOT)),
            "exists": p.exists(),
            "size_kb": round(p.stat().st_size / 1024, 1) if p.exists() else None,
        })
    return pd.DataFrame(rows)

def run_qa(question: str) -> str:
    qa_script = SCRIPTS / "04_qa_layer.py"
    if not qa_script.exists():
        return "❌ scripts/04_qa_layer.py not found."
    cmd = ["python", str(qa_script), question]
    try:
        out = subprocess.check_output(cmd, cwd=str(ROOT), stderr=subprocess.STDOUT, text=True)
        return out
    except subprocess.CalledProcessError as e:
        return f"❌ Q/A error:\n\n{e.output}"

# ---------- Sidebar ----------
st.sidebar.header("Artifacts")
st.sidebar.dataframe(outputs_status(), use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.header("Quick actions")
if st.sidebar.button("Refresh"):
    st.rerun()

# ---------- Tabs ----------
tab1, tab2 = st.tabs(["📊 Dashboard", "💬 Q/A"])

with tab1:
    colA, colB = st.columns([1, 1])

    with colA:
        st.subheader("Scorecard (CSV)")
        df = load_scorecard(FILES["scorecard"])
        if df is None:
            st.warning("company_scorecard.csv not found in data/outputs/")
        else:
            st.dataframe(df, use_container_width=True)

            st.download_button(
                "Download scorecard CSV",
                data=FILES["scorecard"].read_bytes(),
                file_name="company_scorecard.csv",
                mime="text/csv",
            )

    with colB:
        st.subheader("Winner report (MD)")
        winner_md = read_text(FILES["winner"])
        if not winner_md:
            st.warning("winner_report.md not found in data/outputs/")
        else:
            st.markdown(winner_md)
            st.download_button(
                "Download winner report (MD)",
                data=winner_md.encode("utf-8"),
                file_name="winner_report.md",
                mime="text/markdown",
            )

    st.markdown("---")
    st.subheader("Clean summary (MD)")
    summary_md = read_text(FILES["summary"])
    if not summary_md:
        st.warning("clean_summary.md not found in data/outputs/")
    else:
        st.markdown(summary_md)
        st.download_button(
            "Download clean summary (MD)",
            data=summary_md.encode("utf-8"),
            file_name="clean_summary.md",
            mime="text/markdown",
        )

    st.markdown("---")
    st.subheader("Company profiles (JSON)")
    profiles = read_json(FILES["profiles"])
    if profiles is None:
        st.warning("clean_company_profiles.json not found in data/outputs/")
    else:
        # Controls
        companies = [p.get("company", "") for p in profiles if p.get("company")]
        selected = st.multiselect("Select companies", options=companies, default=companies)

        for p in profiles:
            c = p.get("company", "")
            if c not in selected:
                continue
            with st.expander(f"{c.upper()} — profile details", expanded=False):
                st.write("Sources used:", ", ".join(p.get("sources_used", [])))
                st.write("Top terms:", ", ".join(p.get("top_terms", [])))

                st.markdown("**Pricing highlights**")
                for x in p.get("pricing_highlights", [])[:10]:
                    st.write(f"- {x}")

                st.markdown("**Recent links**")
                for link in p.get("recent_links", [])[:10]:
                    title = link.get("title", "(no title)")
                    url = link.get("url", "")
                    if url:
                        st.markdown(f"- [{title}]({url})")
                    else:
                        st.write(f"- {title}")

        st.download_button(
            "Download company profiles (JSON)",
            data=json.dumps(profiles, indent=2).encode("utf-8"),
            file_name="clean_company_profiles.json",
            mime="application/json",
        )

with tab2:
    st.subheader("Ask a question (runs 04_qa_layer.py)")
    st.caption("Examples: which company is doing better? | compare pricing | recent news | positioning | openai snapshot")

    preset = st.selectbox(
        "Pick a preset question",
        [
            "which company is doing better?",
            "compare pricing",
            "recent news",
            "positioning",
            "openai snapshot",
        ],
        index=0,
    )

    q = st.text_input("Or type your own question", value=preset)

    if st.button("Ask"):
        with st.spinner("Running Q/A..."):
            answer = run_qa(q)
        st.code(answer, language="markdown")