# streamlit_dashboard.py
import streamlit as st
from pathlib import Path
import pandas as pd
import io
from data_cleaner import clean_and_standardize, merge_dataframes
from data_loader import read_file
from data_analyzer import generate_statistics
import plotly.express as px

st.set_page_config(page_title="Chemical Data Dashboard", layout="wide")

st.title(" Chemical Industry Data Dashboard ")

with st.sidebar:
    st.header("Uploads & Settings")
    uploaded = st.file_uploader("Upload CSV / Excel files (multiple)", accept_multiple_files=True, type=['csv', 'xlsx', 'xls'])
    preview_rows = st.number_input("Preview rows", min_value=5, max_value=1000, value=10)
    use_example = st.button("Load example dataset")

dfs = []
if uploaded:
    for f in uploaded:
        try:
            # streamlit UploadedFile behaves like a file-like object
            df = pd.read_csv(f) if f.name.lower().endswith(".csv") else pd.read_excel(f)
            dfs.append(df)
        except Exception as e:
            st.error(f"Failed to read {f.name}: {e}")

if use_example and not dfs:
    # small synthetic example
    import numpy as np
    df = pd.DataFrame({
        "timestamp": pd.date_range(end=pd.Timestamp.now(), periods=30, freq="D"),
        "product_code": [f"P{i%4}" for i in range(30)],
        "temperature": (20 + np.random.rand(30) * 10).round(2),
        "ph": (6 + np.random.rand(30) * 2).round(2),
        "quantity_kg": (np.random.rand(30) * 100).round(2),
        "cost_usd": (50 + np.random.rand(30) * 200).round(2),
        "purity_pct": (90 + np.random.rand(30) * 10).round(2)
    })
    dfs.append(df)

if not dfs:
    st.info("Upload files or use the example dataset to start.")
    st.stop()

# Clean each dataframe
cleaned = [clean_and_standardize(df) for df in dfs]
merged = merge_dataframes(cleaned)

st.subheader("Data preview")
st.dataframe(merged.head(int(preview_rows)))

st.subheader("Summary statistics")
st.dataframe(generate_statistics(merged).head(200))

st.subheader("Interactive charts")
numeric_cols = merged.select_dtypes(include=['number']).columns.tolist()
time_col = next((c for c in merged.columns if 'timestamp' in c or 'date' in c), None)

chart_type = st.selectbox("Chart", ["Time series (line)", "Scatter", "Bar (category)"])
if chart_type == "Time series (line)":
    if not time_col or not numeric_cols:
        st.warning("Need a timestamp/date column and at least one numeric column for time series.")
    else:
        y = st.selectbox("Y axis", numeric_cols)
        df_ts = merged.dropna(subset=[time_col, y]).copy()
        df_ts[time_col] = pd.to_datetime(df_ts[time_col])
        df_plot = df_ts.set_index(time_col).resample('D').mean().reset_index()
        fig = px.line(df_plot, x=time_col, y=y, title=f"{y} over time")
        st.plotly_chart(fig, use_container_width=True)

elif chart_type == "Scatter":
    if len(numeric_cols) < 2:
        st.warning("Need at least two numeric columns for scatter.")
    else:
        x = st.selectbox("X", numeric_cols, index=0)
        y = st.selectbox("Y", numeric_cols, index=1)
        fig = px.scatter(merged, x=x, y=y, hover_data=merged.columns)
        st.plotly_chart(fig, use_container_width=True)

else:  # Bar by category
    cat_cols = merged.select_dtypes(include=['object', 'category']).columns.tolist()
    if not cat_cols or not numeric_cols:
        st.warning("Need a categorical and numeric column for a bar chart.")
    else:
        cat = st.selectbox("Category (x)", cat_cols)
        val = st.selectbox("Value (y)", numeric_cols)
        agg = st.selectbox("Aggregation", ["mean", "sum", "median"])
        df_bar = merged.groupby(cat)[val].agg(agg).reset_index().sort_values(val, ascending=False)
        fig = px.bar(df_bar, x=cat, y=val, title=f"{agg.title()} {val} by {cat}")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.download_button("Download cleaned CSV", data=merged.to_csv(index=False).encode('utf-8'), file_name="cleaned_merged.csv", mime="text/csv")
st.caption("Code By Vansh, Vibhansu, Himanshu, Manya, Kushi")