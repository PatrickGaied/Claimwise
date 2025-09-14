# streamlit_app.py
import streamlit as st
import requests
import os
from pathlib import Path

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Claims Adjuster – Demo", layout="wide")
st.title("AI Claims Adjuster — MVP Demo")

uploaded = st.file_uploader("Upload claim file (PDF or TXT)", type=["pdf", "txt"])

if uploaded:
    st.info("Uploading and processing...")
    files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
    r = requests.post(API_URL + "/process-claim", files=files, timeout=60)
    if r.status_code != 200:
        st.error(f"Error: {r.text}")
    else:
        j = r.json()
        st.subheader("Raw Extracted / Parsed Claim (JSON)")
        st.json(j["claim"])
        st.subheader("Judge Result")
        st.json(j["judge"])
        st.subheader("Generated Report (Markdown)")
        st.markdown(j["report_markdown"])
        st.download_button("Download Report (MD)", j["report_markdown"], file_name=f"claim_report_{j['claim']['claim_id']}.md")
