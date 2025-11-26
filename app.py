import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AI Sales Dashboard", layout="wide")

# Dummy data
np.random.seed(7)
df = pd.DataFrame({
    "Account": [f"Account {i}" for i in range(1, 51)],
    "Region": np.random.choice(["India", "US", "EMEA", "APJC"], 50),
    "Stage": np.random.choice(["Pipeline", "Proposal", "Commit", "Won"], 50),
    "Deal ($M)": np.random.uniform(1, 15, 50).round(1),
})

# KPIs
target = 120
forecast = df[df["Stage"].isin(["Commit", "Won"])]["Deal ($M)"].sum()
gap = target - forecast

st.title("🤖 AI Sales & Forecast Dashboard")
st.caption("SPO / Leadership View")

c1, c2, c3 = st.columns(3)
c1.metric("Quarter Target ($M)", target)
c2.metric("Forecast ($M)", round(forecast, 1))
c3.metric("Gap ($M)", round(gap, 1))

st.subheader("📊 Pipeline")
st.dataframe(df, use_container_width=True)

st.subheader("🧠 AI Insights")
st.warning(" High dependency on late-quarter commits")
st.success("✅ 6 large deals can close with exec focus")
