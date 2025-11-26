import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AI Sales Dashboard", layout="wide")

st.title("🤖 AI Sales & Forecast Dashboard")
st.caption("Upload latest data → choose analysis → get instant insights")

# ----------------------------------
# FILE UPLOAD
# ----------------------------------
st.sidebar.header("📤 Upload Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload sales report (CSV or Excel)",
    type=["csv", "xlsx"]
)

# ----------------------------------
# LOAD DATA
# ----------------------------------
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("✅ File uploaded successfully")

else:
    # fallback dummy data
    np.random.seed(7)
    df = pd.DataFrame({
        "Account": [f"Account {i}" for i in range(1, 51)],
        "Region": np.random.choice(["India", "US", "EMEA", "APJC"], 50),
        "Stage": np.random.choice(
            ["Pipeline", "Proposal", "Commit", "Won"], 50
        ),
        "Deal_Size": np.random.uniform(1, 15, 50).round(1),
        "Close_Week": np.random.randint(1, 14, 50)
    })

    st.info("ℹ️ Using sample data (upload file to replace)")

# ----------------------------------
# KPI SECTION
# ----------------------------------
target = 120
forecast = df[df["Stage"].isin(["Commit", "Won"])]["Deal_Size"].sum()
gap = target - forecast

c1, c2, c3 = st.columns(3)
c1.metric("Quarter Target ($M)", target)
c2.metric("Forecast ($M)", round(forecast, 1))
c3.metric("Gap ($M)", round(gap, 1))

# ----------------------------------
# ANALYSIS DROPDOWN
# ----------------------------------
st.subheader("📊 Select Analysis")

analysis_option = st.selectbox(
    "Choose analysis type",
    [
        "Pipeline Overview",
        "Forecast Risk Analysis",
        "Late Quarter Deals",
        "Large Deal Upside",
    ],
)

# ----------------------------------
# ANALYSIS OUTPUT
# ----------------------------------
if analysis_option == "Pipeline Overview":
    st.markdown("### Pipeline by Stage")
    stage_summary = df.groupby("Stage")["Deal_Size"].sum()
    st.bar_chart(stage_summary)
    st.dataframe(df)

elif analysis_option == "Forecast Risk Analysis":
    st.markdown("### Deals at Risk of Slippage")
    risky = df[
        (df["Stage"] == "Proposal") & (df["Close_Week"] >= 11)
    ]

    if risky.empty:
        st.success("✅ No major risk deals detected")
    else:
        st.warning(f" {len(risky)} deals may slip")
        st.dataframe(risky)

elif analysis_option == "Late Quarter Deals":
    st.markdown("### Deals Closing Late in Quarter")
    late = df[df["Close_Week"] >= 11]
    st.dataframe(late)

elif analysis_option == "Large Deal Upside":
    st.markdown("### Large Deals with Upside")
    big_deals = df[df["Deal_Size"] >= 10]
    st.success(f"✅ {len(big_deals)} large deals identified")
    st.dataframe(big_deals)
