import streamlit as st
import pandas as pd
import plotly.express as px

# PAGE CONFIG

st.set_page_config(
    page_title="Churn Analytics",
    page_icon="📊",
    layout="wide"
)

# LOAD DATA

@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/churn_dashboard.csv")
    return df


df = load_data()

df.columns = df.columns.str.strip().str.lower()

if "churn" not in df.columns:
    st.error("The churn column was not found in the dashboard dataset.")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

# TITLE

st.title("📊 Customer Churn Analytics Dashboard")
st.write("Explore customer behavior, churn patterns, and key business insights.")
st.divider()

# SIDEBAR — LIVE FILTERS

with st.sidebar:

    st.header("🎛️ Filters")

    filtered_df = df.copy()

    if "contract" in df.columns:
        contract_choices = st.multiselect(
            "Contract",
            sorted(df["contract"].dropna().astype(str).unique().tolist()),
            default=sorted(df["contract"].dropna().astype(str).unique().tolist())
        )
        filtered_df = filtered_df[filtered_df["contract"].astype(str).isin(contract_choices)]

    if "internetservice" in df.columns:
        internet_choices = st.multiselect(
            "Internet Service",
            sorted(df["internetservice"].dropna().astype(str).unique().tolist()),
            default=sorted(df["internetservice"].dropna().astype(str).unique().tolist())
        )
        filtered_df = filtered_df[filtered_df["internetservice"].astype(str).isin(internet_choices)]

    if "paymentmethod" in df.columns:
        payment_choices = st.multiselect(
            "Payment Method",
            sorted(df["paymentmethod"].dropna().astype(str).unique().tolist()),
            default=sorted(df["paymentmethod"].dropna().astype(str).unique().tolist())
        )
        filtered_df = filtered_df[filtered_df["paymentmethod"].astype(str).isin(payment_choices)]

    if "tenure" in df.columns:
        t_series = pd.to_numeric(df["tenure"], errors="coerce")
        t_min, t_max = int(t_series.min()), int(t_series.max())
        tenure_range = st.slider("Tenure (months)", t_min, t_max, (t_min, t_max))
        filtered_df = filtered_df[
            pd.to_numeric(filtered_df["tenure"], errors="coerce").between(*tenure_range)
        ]

    if "monthlycharges" in df.columns:
        m_series = pd.to_numeric(df["monthlycharges"], errors="coerce")
        m_min, m_max = float(m_series.min()), float(m_series.max())
        monthly_range = st.slider("Monthly Charges ($)", m_min, m_max, (m_min, m_max))
        filtered_df = filtered_df[
            pd.to_numeric(filtered_df["monthlycharges"], errors="coerce").between(*monthly_range)
        ]

    st.caption(f"Showing **{len(filtered_df):,}** of **{len(df):,}** customers")

if filtered_df.empty:
    st.warning("No customers match the current filters. Adjust the filters in the sidebar.")
    st.stop()

df = filtered_df

# KPI CALCULATIONS

total_customers = len(df)

churned_customers = (
    df["churn"].astype(str).str.lower().eq("yes").sum()
)

churn_rate = churned_customers / total_customers if total_customers > 0 else 0

avg_monthly_charges = pd.to_numeric(df["monthlycharges"], errors="coerce").mean() if "monthlycharges" in df.columns else 0
avg_tenure = pd.to_numeric(df["tenure"], errors="coerce").mean() if "tenure" in df.columns else 0

# KPI CARDS

st.subheader("📌 Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Customers", f"{total_customers:,}")
with col2:
    st.metric("Churned Customers", f"{churned_customers:,}")
with col3:
    st.metric("Churn Rate", f"{churn_rate:.1%}")
with col4:
    st.metric("Avg Monthly Charges", f"${avg_monthly_charges:,.2f}")
with col5:
    st.metric("Avg Tenure", f"{avg_tenure:.0f} mo")


st.divider()

# CHURN DISTRIBUTION

st.subheader("📉 Churn Distribution")

churn_counts = df["churn"].astype(str).value_counts().reset_index()
churn_counts.columns = ["Churn", "Customers"]

col1, col2 = st.columns([1, 1])

with col1:
    fig = px.pie(
        churn_counts, names="Churn", values="Customers", hole=0.5,
        title="Stayed vs Churned"
    )
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.bar(
        churn_counts, x="Churn", y="Customers", color="Churn", text="Customers",
        title="Customer Counts"
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# CHURN BY CONTRACT

if "contract" in df.columns:
    st.subheader("📄 Churn by Contract Type")
    contract_churn = df.groupby(["contract", "churn"]).size().reset_index(name="Customers")
    fig = px.bar(
        contract_churn, x="contract", y="Customers", color="churn",
        barmode="group", text="Customers", title="Contract Type vs Churn"
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# CHURN BY INTERNET SERVICE


if "internetservice" in df.columns:
    st.subheader("🌐 Churn by Internet Service")
    internet_churn = df.groupby(["internetservice", "churn"]).size().reset_index(name="Customers")
    fig = px.bar(
        internet_churn, x="internetservice", y="Customers", color="churn",
        barmode="group", text="Customers", title="Internet Service vs Churn"
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# CHURN BY PAYMENT METHOD

if "paymentmethod" in df.columns:
    st.subheader("💳 Churn by Payment Method")
    payment_churn = df.groupby(["paymentmethod", "churn"]).size().reset_index(name="Customers")
    fig = px.bar(
        payment_churn, x="paymentmethod", y="Customers", color="churn",
        barmode="group", text="Customers", title="Payment Method vs Churn"
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

# CHURN BY TENURE

if "tenure" in df.columns:
    st.subheader("⏳ Churn by Customer Tenure")

    df["tenure_group"] = pd.cut(
        pd.to_numeric(df["tenure"], errors="coerce"),
        bins=[-1, 12, 24, 48, 72],
        labels=["0-12 months", "13-24 months", "25-48 months", "49-72 months"]
    )

    tenure_churn = df.groupby(["tenure_group", "churn"], observed=False).size().reset_index(name="Customers")
    fig = px.bar(
        tenure_churn, x="tenure_group", y="Customers", color="churn",
        barmode="group", text="Customers", title="Tenure Group vs Churn"
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


# BUSINESS INSIGHTS

st.divider()
st.subheader("💡 Business Insights")

st.markdown("""
### Key Observations

- **Month-to-month contracts** generally represent a higher-risk customer segment.
- **Short-tenure customers** are more likely to churn than long-term customers.
- **Payment method and service type** can help identify higher-risk customer groups.
- The ML model can be used to identify individual customers who may require retention efforts.
""")

# DATA PREVIEW + EXPORT

with st.expander("🔍 View Dashboard Data"):
    st.dataframe(df.head(100), use_container_width=True)
    st.download_button(
        "⬇️ Download filtered data (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="filtered_churn_dashboard.csv",
        mime="text/csv"
    )