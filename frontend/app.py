import os
from typing import Any, Dict, Optional

import pandas as pd
import requests
import streamlit as st

# Environment configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AI Match Quality Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=30)
def fetch_json(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """Helper to query backend API endpoints with query parameters."""
    try:
        response = requests.get(
            f"{BACKEND_API_URL}{endpoint}", params=params, timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as err:
        st.error(f"Failed to fetch {endpoint}: {err}")
        return None


st.title("🎯 AI Match Quality & Alignment Dashboard")
st.caption(
    "Evaluation of Rule-based Scorer vs. LLM Scorer performance against recruiter ground truth."
)

# ------------------------------------------------------------------------------
# TAB DEFINITIONS
# ------------------------------------------------------------------------------
tab_overview, tab_drilldown, tab_behavior = st.tabs(
    ["📊 Executive Overview", "🔍 Segment Drill-Down", "👁️ Recruiter Behavior"]
)

# ==============================================================================
# TAB 1: EXECUTIVE OVERVIEW
# ==============================================================================
with tab_overview:
    st.header("Executive Summary")

    kpis = fetch_json("/api/overview/kpis") or {}

    m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
    m1.metric("Evaluated Apps", kpis.get("total_applications", 0))
    m2.metric(
        "Positive Outcome Rate",
        f"{round(kpis.get('positive_outcome_rate', 0.0) * 100, 1)}%",
    )
    m3.metric(
        "Classification Disagreement",
        f"{round(kpis.get('classification_disagreement_rate', 0.0) * 100, 1)}%",
        help="Share of evaluated applications where one score is at least 0.5 and the other is below 0.5.",
    )
    m4.metric("Avg Rule Score", kpis.get("avg_rule_score", 0.0))
    m5.metric(
        "Rule Accuracy",
        f"{round(kpis.get('rule_accuracy', 0.0) * 100, 1)}%",
        help="Percentage of predictions (>= 0.5) matching actual recruiter decisions.",
    )
    m6.metric("Avg LLM Score (Norm)", kpis.get("avg_llm_score", 0.0))
    m7.metric(
        "LLM Accuracy",
        f"{round(kpis.get('llm_accuracy', 0.0) * 100, 1)}%",
        help="Percentage of predictions (>= 0.5) matching actual recruiter decisions.",
    )

    st.caption(
        f"Large score-gap rate (>0.4): {round(kpis.get('large_score_gap_rate', 0.0) * 100, 1)}%. "
        "All evaluation metrics exclude pending applications."
    )

    metric_rows = []
    for name, key in [("Rule-based", "rule_metrics"), ("LLM-based", "llm_metrics")]:
        metrics = kpis.get(key, {})
        metric_rows.append(
            {
                "System": name,
                "Balanced accuracy": metrics.get("balanced_accuracy", 0.0),
                "MCC": metrics.get("mcc", 0.0),
                "Accuracy 95% CI": (
                    f"{metrics.get('accuracy_ci_low', 0.0) * 100:.1f}% - "
                    f"{metrics.get('accuracy_ci_high', 0.0) * 100:.1f}%"
                ),
            }
        )
    st.dataframe(pd.DataFrame(metric_rows), use_container_width=True, hide_index=True)

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Score Distribution by Recruiter Decision")
        st.caption("Do higher scores correlate with hired/interviewed decisions?")

        dist_data = fetch_json("/api/overview/distributions")
        if dist_data:
            df_dist = pd.DataFrame(dist_data)
            df_dist = df_dist.rename(
                columns={
                    "avg_rule_score": "Rule Score",
                    "avg_llm_score_norm": "LLM Score",
                }
            )
            st.bar_chart(
                df_dist.set_index("recruiter_decision")[
                    ["Rule Score", "LLM Score"]
                ]
            )
        else:
            st.info("No distribution data returned.")

    with col_right:
        st.subheader("Model-Version Comparison")
        st.caption(
            "Version-level differences are observational and may reflect different application mixes."
        )

        version_data = fetch_json("/api/overview/model-versions")
        if version_data:
            df_version = pd.DataFrame(version_data)
            st.dataframe(df_version, use_container_width=True, hide_index=True)
            st.bar_chart(
                df_version.set_index("llm_model_version")[
                    ["rule_accuracy", "llm_accuracy"]
                ]
            )
        else:
            st.info("No model version comparison available.")


# ==============================================================================
# TAB 2: SEGMENT DRILL-DOWN (SYSTEMATIC FLAW FINDER)
# ==============================================================================
with tab_drilldown:
    st.header("Segment Failure Analysis")
    st.caption(
        "Isolate systematic failures across job families, countries, and profile completeness levels."
    )

    # Global Filters for Drill-Down
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    job_family = f_col1.selectbox(
        "Job Family",
        [
            "All",
            "IT",
            "Logistics",
            "Manufacturing",
            "Healthcare",
            "Office & Admin",
        ],
    )
    country = f_col2.selectbox("Country", ["All", "DE", "AT"])
    model_version = f_col3.selectbox("LLM Model Version", ["All", "v1", "v2"])
    min_completeness = f_col4.slider(
        "Min Profile Completeness", 0.0, 1.0, 0.0, 0.1
    )

    # Build query parameters dictionary
    query_params = {}
    if job_family != "All":
        query_params["job_family"] = job_family
    if country != "All":
        query_params["country"] = country
    if model_version != "All":
        query_params["model_version"] = model_version
    if min_completeness > 0.0:
        query_params["min_profile_completeness"] = min_completeness

    st.divider()

    st.subheader("Aggregated Performance by Selected Segment")
    segment_data = fetch_json("/api/segments/analytics", params=query_params)

    if segment_data:
        df_seg = pd.DataFrame(segment_data)
        st.dataframe(df_seg, use_container_width=True, hide_index=True)
    else:
        st.warning("No data found matching the selected segment filters.")

    st.divider()

    st.subheader("Disagreement Case Inspector")
    st.caption(
        "Individual applications with a score gap greater than 0.4; this is separate from binary classification disagreement."
    )

    disagree_data = fetch_json(
        "/api/segments/disagreements", params=query_params
    )

    if disagree_data:
        df_disagree = pd.DataFrame(disagree_data)
        st.dataframe(df_disagree, use_container_width=True, hide_index=True)
    else:
        st.info("No extreme disagreement records found for this segment.")


# ==============================================================================
# TAB 3: RECRUITER BEHAVIOR & INTERACTION ANALYSIS
# ==============================================================================
with tab_behavior:
    st.header("Recruiter Interaction Analytics")
    st.caption(
        "How recruiters interact with AI scores and whether score exposure affects hiring choices."
    )

    behavior_data = fetch_json("/api/recruiter/behavior")

    if behavior_data:
        df_beh = pd.DataFrame(behavior_data)

        b_col1, b_col2 = st.columns([1, 2])

        with b_col1:
            st.write("Event Type Breakdown")
            st.dataframe(df_beh, use_container_width=True, hide_index=True)

        with b_col2:
            st.write("Recruiter Funnel (Unique Applications Affected)")
            st.bar_chart(
                df_beh.set_index("event_type")["unique_applications_affected"]
            )
    else:
        st.info("No recruiter behavior event data available.")