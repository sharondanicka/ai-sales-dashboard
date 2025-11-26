import streamlit as st
import pandas as pd
import numpy as np

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="AI Sales & Forecast Dashboard",
    layout="wide"
)

st.title("🤖 AI Sales & Forecast Dashboard")
st.caption("Upload latest report → map columns → pick analysis → view insights")

# -------------------------
# 1. FILE UPLOAD
# -------------------------
st.sidebar.header("1️⃣ Upload data")

uploaded_file = st.sidebar.file_uploader(
    "Upload sales report (CSV or Excel)",
    type=["csv", "xlsx", "xls"]
)

if uploaded_file is not None:
    file_name = uploaded_file.name.lower()

    try:
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif file_name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        else:
            st.error("❌ Unsupported file format. Use CSV or Excel.")
            st.stop()

        st.success("✅ File uploaded successfully")

    except Exception as e:
        st.error(f"❌ Could not read file: {e}")
        st.stop()

else:
    # Fallback: sample data
    st.info("ℹ️ No file uploaded. Using sample dummy data for now.")
    np.random.seed(42)
    df = pd.DataFrame({
        "Account": [f"Account {i}" for i in range(1, 51)],
        "Region": np.random.choice(["India", "US", "EMEA", "APJC"], 50),
        "Stage": np.random.choice(["Pipeline", "Proposal", "Commit", "Won"], 50),
        "Deal Value": np.random.uniform(1, 15, 50).round(1),
        "Close Week": np.random.randint(1, 14, 50)
    })

# -------------------------
# 2. DATA PREVIEW
# -------------------------
st.subheader("📄 Data preview")

with st.expander("Show first 10 rows"):
    st.dataframe(df.head(10), use_container_width=True)
    st.write("Columns detected:", list(df.columns))

# -------------------------
# 3. COLUMN MAPPING
# -------------------------
st.sidebar.header("2️⃣ Map columns")

# Basic defensive check
if len(df.columns) < 2:
    st.error("❌ Not enough columns in the file. Please upload a richer dataset.")
    st.stop()

stage_col = st.sidebar.selectbox(
    "Stage column",
    options=df.columns,
    index=0
)

value_col = st.sidebar.selectbox(
    "Deal value column",
    options=df.columns,
    index=1 if len(df.columns) > 1 else 0
)

close_week_option = st.sidebar.selectbox(
    "Close week column (optional)",
    options=["(None)"] + list(df.columns)
)
close_week_col = None if close_week_option == "(None)" else close_week_option

# Ensure numeric value column
df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

# -------------------------
# 4. FORECAST SETTINGS
# -------------------------
st.sidebar.header("3️⃣ Forecast settings")

stage_values = sorted(df[stage_col].astype(str).unique())

# Try to guess commit/won-like stages
default_commit_stages = [
    s for s in stage_values
    if "commit" in s.lower() or "won" in s.lower()
]
if not default_commit_stages and stage_values:
    default_commit_stages = [stage_values[0]]

commit_stages = st.sidebar.multiselect(
    "Stages that count towards Forecast",
    options=stage_values,
    default=default_commit_stages
)

target = st.sidebar.number_input(
    "Quarter target (same unit as value column)",
    value=120.0,
    step=10.0
)

large_deal_threshold = st.sidebar.number_input(
    "Large deal threshold",
    value=float(df[value_col].quantile(0.75) if df[value_col].notna().any() else 10.0),
    step=1.0
)

# -------------------------
# 5. KPI CALCULATIONS
# -------------------------
if commit_stages:
    commit_mask = df[stage_col].astype(str).isin(commit_stages)
    forecast = df.loc[commit_mask, value_col].sum()
else:
    forecast = 0.0

gap = target - forecast
coverage = (forecast / target) * 100 if target > 0 else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Quarter Target", f"{target:,.1f}")
k2.metric("Forecast", f"{forecast:,.1f}")
k3.metric("Gap", f"{gap:,.1f}")
k4.metric("Coverage", f"{coverage:.0f}%")

# -------------------------
# 6. ANALYSIS SELECTION
# -------------------------
st.subheader("📊 Analysis")

analysis_option = st.selectbox(
    "Choose analysis",
    [
        "Pipeline by Stage",
        "Forecast Risk (Late Deals)",
        "Large Deal Upside",
        "Raw Data View"
    ]
)

# -------------------------
# 7. ANALYSIS LOGIC
# -------------------------
if analysis_option == "Pipeline by Stage":
    st.markdown("### Pipeline by Stage")
    stage_summary = (
        df.groupby(stage_col)[value_col]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(stage_summary)
    st.dataframe(
        df[[stage_col, value_col]].sort_values(by=value_col, ascending=False),
        use_container_width=True
    )

elif analysis_option == "Forecast Risk (Late Deals)":
    st.markdown("### Forecast Risk – Late Quarter Deals")

    if close_week_col is None:
        st.info("ℹ️ To see late-quarter risk, select a Close Week column in the sidebar.")
    else:
        # Assume higher week number = later in quarter
        late_cutoff = st.slider(
            "Weeks considered 'late quarter'",
            min_value=int(df[close_week_col].min()),
            max_value=int(df[close_week_col].max()),
            value=int(df[close_week_col].max()) - 2
        )

        risky_deals = df[
            (df[close_week_col] >= late_cutoff)
            & (~df[stage_col].astype(str).isin(commit_stages))
        ]

        st.write(f"🔎 Late-quarter non-commit deals: **{len(risky_deals)}**")
        st.dataframe(risky_deals, use_container_width=True)

elif analysis_option == "Large Deal Upside":
    st.markdown("### Large Deal Upside")

    big_deals = df[df[value_col] >= large_deal_threshold]

    st.write(
        f"💰 Deals above threshold ({large_deal_threshold}): "
        f"**{len(big_deals)}**"
    )
    st.dataframe(big_deals, use_container_width=True)

else:  # Raw Data View
    st.markdown("### Full Data View")
    st.dataframe(df, use_container_width=True)

# -------------------------
# 8. SIMPLE TEXT INSIGHTS
# -------------------------
st.subheader("🧠 Summary (Rule-based)")

insights = []

if gap > 0:
    insights.append(f"• There is a remaining gap of **{gap:,.1f}** to target.")
else:
    insights.append("• Target appears covered based on selected commit stages.")

if coverage < 80:
    insights.append("• Forecast coverage is below 80%. Funnel may be thin.")
elif coverage >= 100:
    insights.append("• Forecast exceeds target. Check deal quality and risk.")

if close_week_col is not None:
    try:
        late_cut = df[close_week_col].max() - 1
        late_deals = df[df[close_week_col] >= late_cut]
        if len(late_deals) > 0:
            insights.append(
                f"• {len(late_deals)} deals are concentrated in the last weeks of the quarter."
            )
    except Exception:
        pass

if len(insights) == 0:
    st.write("No major observations based on current settings.")
else:
    for line in insights:
        st.write(line)

