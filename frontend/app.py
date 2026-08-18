import os
from typing import Any

import pandas as pd
import requests
import streamlit as st

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

st.set_page_config(page_title="Recruitment Analyzer Dashboard", layout="wide")


@st.cache_data(ttl=60)
def fetch_json(endpoint: str) -> Any:
    response = requests.get(f"{BACKEND_API_URL}{endpoint}", timeout=10)
    response.raise_for_status()
    return response.json()


st.title("Recruitment Tool Effectiveness Dashboard")

summary = fetch_json("/api/summary")
performance = fetch_json("/api/tool-performance")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total applications", summary.get("total_applications", 0))
col2.metric("Hired", summary.get("hired", 0))
col3.metric("Interviewed", summary.get("interviewed", 0))
col4.metric("Rejected", summary.get("rejected", 0))

st.subheader("Average scores")
col1, col2 = st.columns(2)
col1.metric("Rule tool average", round(summary.get("average_rule_score", 0.0), 3))
col2.metric("LLM tool average", round(summary.get("average_llm_score", 0.0), 3))

if performance:
    df = pd.DataFrame(performance)
    st.subheader("Model vs rule comparison")
    st.dataframe(df, use_container_width=True)

    chart_df = df.rename(columns={
        "avg_llm_score": "LLM average",
        "avg_rule_score": "Rule average",
    })
    st.bar_chart(chart_df[["LLM average", "Rule average"]])
else:
    st.info("No comparison data available yet.")
