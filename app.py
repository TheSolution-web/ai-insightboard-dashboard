import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import zscore

st.set_page_config(page_title="InsightBoard", layout="wide")

st.title("📊 InsightBoard AI Dashboard")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.dataframe(df)

    date_col = st.selectbox("Select Date Column", df.columns)
    metric_col = st.selectbox("Select Metric Column", df.columns)
    segment_col = st.selectbox("Select Segment Column", df.columns)

    df[date_col] = pd.to_datetime(df[date_col])
    df[metric_col] = pd.to_numeric(df[metric_col], errors="coerce")

    col1, col2 = st.columns(2)
    col1.metric("Total", df[metric_col].sum())
    col2.metric("Average", df[metric_col].mean())

    trend = df.groupby(date_col)[metric_col].sum().reset_index()
    fig = px.line(trend, x=date_col, y=metric_col)
    st.plotly_chart(fig)

    breakdown = df.groupby(segment_col)[metric_col].sum().reset_index()
    fig2 = px.bar(breakdown, x=segment_col, y=metric_col)
    st.plotly_chart(fig2)

    df["z"] = zscore(df[metric_col].fillna(0))
    st.write("### Anomalies")
    st.dataframe(df[df["z"].abs() > 3])
