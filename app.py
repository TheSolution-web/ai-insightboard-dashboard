import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import zscore

# Page config
st.set_page_config(page_title="InsightBoard", layout="wide")

st.title("📊 InsightBoard AI Dashboard")

# Upload file
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # ✅ Clean column names
    df.columns = df.columns.str.strip()

    # -------------------------------
    # COLUMN SELECTION
    # -------------------------------
    st.subheader("⚙️ Configuration")

    col1, col2, col3 = st.columns(3)
    with col1:
        date_col = st.selectbox("Select Date Column", df.columns)
    with col2:
        metric_col = st.selectbox("Select Metric Column", df.columns)
    with col3:
        segment_col = st.selectbox("Select Segment Column", df.columns)

    # -------------------------------
    # DATA CLEANING ✅
    # -------------------------------
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df[metric_col] = pd.to_numeric(df[metric_col], errors="coerce")

    # Remove invalid dates
    df = df.dropna(subset=[date_col])

    # -------------------------------
    # SIDEBAR FILTERS ✅
    # -------------------------------
    st.sidebar.header("🔍 Filters")

    min_date = df[date_col].min().date()
    max_date = df[date_col].max().date()

    date_range = st.sidebar.date_input(
        "📅 Select Date Range",
        value=(min_date, max_date)
    )

    segments = df[segment_col].dropna().unique()

    selected_segments = st.sidebar.multiselect(
        "📊 Select Segment",
        options=segments,
        default=segments
    )

    # -------------------------------
    # SAFE FILTERING ✅
    # -------------------------------
    if date_range and isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range

        filtered_df = df[
            (df[date_col] >= pd.to_datetime(start_date)) &
            (df[date_col] <= pd.to_datetime(end_date)) &
            (df[segment_col].isin(selected_segments))
        ]
    else:
        filtered_df = df.copy()

    # -------------------------------
    # KPI SECTION ✅
    # -------------------------------
    st.subheader("📌 Key Metrics")

    if metric_col in filtered_df.columns and len(filtered_df) > 0:
        col1, col2 = st.columns(2)
        col1.metric("Total", f"{filtered_df[metric_col].sum():,.0f}")
        col2.metric("Average", f"{filtered_df[metric_col].mean():,.0f}")
    else:
        st.warning("No data available for KPIs")

    # -------------------------------
    # CHARTS ✅
    # -------------------------------
    st.subheader("📈 Trend Analysis")

    if len(filtered_df) > 0:
        trend = filtered_df.groupby(date_col)[metric_col].sum().reset_index()
        fig = px.line(trend, x=date_col, y=metric_col, title="Trend Over Time")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 Segment Breakdown")

        breakdown = filtered_df.groupby(segment_col)[metric_col].sum().reset_index()
        fig2 = px.bar(breakdown, x=segment_col, y=metric_col, title="By Segment")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No data available after filtering")

    # -------------------------------
    # ANOMALY DETECTION ✅
    # -------------------------------
    st.subheader("⚠️ Anomalies")

    if len(filtered_df) > 0:
        filtered_df["z_score"] = zscore(filtered_df[metric_col].fillna(0))
        anomalies = filtered_df[filtered_df["z_score"].abs() > 3]
        st.dataframe(anomalies)
    else:
        st.write("No anomalies detected")
