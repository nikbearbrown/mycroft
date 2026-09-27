"""dashboard — the human report surface + the review gate UI.

Reads query-api's REST endpoint. The only way to move a signal to `actionable` is
`ClearGate`, and that always writes a gate_decisions row with a named reviewer.
"""

import os

import requests
import streamlit as st

API = os.getenv("QUERY_API", "http://query-api:8080")

st.set_page_config(page_title="finance-event-signals", layout="wide")
st.title("Material-event review queue")
st.caption("A monitoring queue for an analyst. Nothing here decides or places a trade.")

col_a, col_b = st.columns([1, 3])
status = col_a.selectbox(
    "status", ["pending_review", "withheld", "actionable", "rejected", "(all)"], index=0
)
q_status = "" if status == "(all)" else status

try:
    r = requests.get(f"{API}/v1/signals", params={"status": q_status, "limit": 200}, timeout=10)
    r.raise_for_status()
    signals = r.json().get("signals") or []
except Exception as e:
    st.error(f"query-api unreachable: {e}")
    st.stop()

col_b.write(f"**{len(signals)}** signals · api `{API}`")

for s in signals:
    with st.container(border=True):
        c = st.columns([4, 1, 1, 1])
        c[0].markdown(
            f"**{s.get('company') or '?'}**  ·  {s.get('ticker') or '—'}  ·  "
            f"`{s.get('event_type') or ''}`"
        )
        c[0].write(s.get("title") or "")
        c[0].caption(
            f"{s.get('event_key')} · {s.get('published_at') or ''} · "
            f"[filing]({s.get('url') or ''})"
        )
        c[1].metric("direction", s.get("direction") or "—")
        c[2].metric("confidence", f"{float(s.get('confidence') or 0):.2f}")
        c[3].write(f"**{s.get('status')}**")

        if s.get("withheld_reason"):
            st.warning(f"withheld — {s['withheld_reason']}")
        elif s.get("rationale"):
            st.write(s["rationale"])
        if s.get("reviewer"):
            st.info(f"decided: **{s.get('verdict')}** by {s['reviewer']} — {s.get('note') or ''}")

        if s.get("status") in ("pending_review", "withheld"):
            with st.form(key=f"form_{s['signal_id']}"):
                reviewer = st.text_input("reviewer (required)", key=f"rv_{s['signal_id']}")
                note = st.text_input("note", key=f"nt_{s['signal_id']}")
                b1, b2 = st.columns(2)
                act = b1.form_submit_button("Clear → actionable", type="primary")
                rej = b2.form_submit_button("Reject")
                if act or rej:
                    if not reviewer.strip():
                        st.error("reviewer required — the gate needs a named human")
                    else:
                        verdict = "actionable" if act else "reject"
                        resp = requests.post(
                            f"{API}/v1/signals/{s['signal_id']}/clear",
                            json={"reviewer": reviewer.strip(), "verdict": verdict, "note": note},
                            timeout=10,
                        )
                        if resp.ok:
                            st.success(f"{verdict} by {reviewer}")
                            st.rerun()
                        else:
                            st.error(resp.text)
