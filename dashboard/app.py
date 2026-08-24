import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path


st.set_page_config(
    page_title="ChurnIQ | Customer Churn Analytics & Prediction",
    page_icon="\U0001F52E",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PATHS

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent

DATA_PATHS = [
    PROJECT_DIR / "data" / "processed" / "churn_dashboard.csv",
    PROJECT_DIR / "data" / "churn_dashboard.csv",
    APP_DIR / "churn_dashboard.csv",
    APP_DIR / "data" / "processed" / "churn_dashboard.csv",
]

MODEL_PATHS = [
    PROJECT_DIR / "models",
    APP_DIR.parent / "models",
    APP_DIR / "models",
]

# SESSION STATE DEFAULTS

PAGES = [
    "\U0001F3E0 Home",
    "\U0001F4CA Dashboard",
    "\U0001F50E Churn Analysis",
    "\U0001F3AF Predict Churn",
    "\U0001F916 Model Performance",
    "\U0001F4A1 Business Insights",
]

if "nav_radio" not in st.session_state:
    st.session_state["nav_radio"] = "\U0001F3E0 Home"


def go_to(page_name: str):
    st.session_state["nav_radio"] = page_name



# THEME 

BLUE_PALETTE = ["#275391", "#4783E9", "#70A2FF", "#76A1F8", "#98B4EC", "#173F8A"]


def theme_vars():
    return dict(
        bg="#FBFAFF",
        bg_secondary="#F1EEFF",
        card_bg="#FFFFFF",
        card_bg_alt="#F7F5FF",
        text="#2E2B45",
        text_muted="#6E6889",
        border="#E7E2FA",
        accent1="#8EA7FF",
        accent2="#FF9FCB",
        accent3="#7FE0B4",
        accent4="#FFC98B",
        shadow="rgba(140,130,210,0.18)",
        plotly_template="plotly_white",
        palette=BLUE_PALETTE,
        success_bg="#E6FAF0", success_text="#1C7A50", success_border="#BEEED9",
        warn_bg="#FFF7E0", warn_text="#8A6A16", warn_border="#F5E3AE",
        danger_bg="#FFEAF1", danger_text="#60F585", danger_border="#F7CBDD",
    )


def inject_css():
    v = theme_vars()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {v['bg']};
            color: {v['text']};
        }}
        section[data-testid="stSidebar"] {{
            background: {v['bg_secondary']};
            border-right: 1px solid {v['border']};
        }}
        section[data-testid="stSidebar"] * {{
            color: {v['text']} !important;
        }}
        h1, h2, h3, h4, h5, p, span, label, div {{
            color: {v['text']};
        }}
        .stCaption, .st-emotion-cache-1629p8f, .subtitle-muted {{
            color: {v['text_muted']} !important;
        }}

        /* Hero */
        .hero {{
            background: linear-gradient(120deg, {v['accent1']}33, {v['accent2']}33 45%, {v['accent3']}33);
            border: 1px solid {v['border']};
            border-radius: 22px;
            padding: 38px 42px;
            margin-bottom: 28px;
        }}
        .hero-title {{
            font-size: 44px;
            font-weight: 800;
            margin-bottom: 4px;
            letter-spacing: -0.5px;
        }}
        .hero-badge {{
            display:inline-block;
            background: {v['accent1']}30;
            color: {v['text']};
            border: 1px solid {v['accent1']}80;
            border-radius: 999px;
            padding: 4px 14px;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 14px;
        }}
        .hero-subtitle {{
            font-size: 17px;
            color: {v['text_muted']};
            max-width: 720px;
            margin-bottom: 0;
        }}

        /* Generic card */
        .ciq-card {{
            background: {v['card_bg']};
            border: 1px solid {v['border']};
            border-radius: 16px;
            padding: 20px 22px;
            box-shadow: 0 4px 14px {v['shadow']};
            height: 100%;
        }}

        /* KPI strip */
        .kpi-card {{
            background: {v['card_bg']};
            border: 1px solid {v['border']};
            border-radius: 14px;
            padding: 16px 18px;
            text-align: center;
            box-shadow: 0 3px 10px {v['shadow']};
        }}
        .kpi-value {{
            font-size: 26px;
            font-weight: 800;
        }}
        .kpi-label {{
            color: {v['text_muted']};
            font-size: 13px;
            margin-top: 2px;
        }}

        /* Feature buttons (Dashboard / Predict) act like big clickable cards */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 18px !important;
        }}
        .feature-wrap div[data-testid="stButton"] > button {{
            width: 100%;
            min-height: 84px;
            border-radius: 16px;
            border: 1px solid {v['border']};
            background: linear-gradient(135deg, {v['accent1']}2A, {v['accent2']}2A);
            color: {v['text']};
            font-size: 17px;
            font-weight: 700;
            transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
            box-shadow: 0 4px 14px {v['shadow']};
        }}
        .feature-wrap div[data-testid="stButton"] > button:hover {{
            transform: translateY(-4px);
            box-shadow: 0 10px 24px {v['shadow']};
            background: linear-gradient(135deg, {v['accent1']}45, {v['accent2']}45);
            border-color: {v['accent1']};
        }}
        .feature-wrap.predict div[data-testid="stButton"] > button {{
            background: linear-gradient(135deg, {v['accent3']}2A, {v['accent4']}2A);
        }}
        .feature-wrap.predict div[data-testid="stButton"] > button:hover {{
            background: linear-gradient(135deg, {v['accent3']}45, {v['accent4']}45);
            border-color: {v['accent3']};
        }}

        /* Secondary nav pills */
        .pill-wrap div[data-testid="stButton"] > button {{
            width: 100%;
            border-radius: 12px;
            border: 1px solid {v['border']};
            background: {v['card_bg_alt']};
            color: {v['text']};
            font-weight: 600;
            font-size: 14px;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }}
        .pill-wrap div[data-testid="stButton"] > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 14px {v['shadow']};
        }}

        /* Risk banners */
        .risk-high {{
            background-color: {v['danger_bg']};
            color: {v['danger_text']};
            border: 1px solid {v['danger_border']};
            padding: 18px; border-radius: 12px; font-weight: 700;
        }}
        .risk-medium {{
            background-color: {v['warn_bg']};
            color: {v['warn_text']};
            border: 1px solid {v['warn_border']};
            padding: 18px; border-radius: 12px; font-weight: 700;
        }}
        .risk-low {{
            background-color: {v['success_bg']};
            color: {v['success_text']};
            border: 1px solid {v['success_border']};
            padding: 18px; border-radius: 12px; font-weight: 700;
        }}

        [data-testid="stMetricValue"] {{
            color: {v['text']};
        }}
        [data-testid="stMetric"] {{
            background: {v['card_bg']};
            border: 1px solid {v['border']};
            border-radius: 14px;
            padding: 10px 6px;
            box-shadow: 0 3px 10px {v['shadow']};
        }}

        hr {{
            border-color: {v['border']};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


V = theme_vars()
inject_css()

# DATA LOADING

@st.cache_data
def load_dashboard_data():
    for path in DATA_PATHS:
        if path.exists():
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
            return df, str(path)
    return None, None


df, data_location = load_dashboard_data()


def normalize_churn(value):
    if pd.isna(value):
        return 0
    value = str(value).strip().lower()
    if value in ["yes", "1", "true", "churn"]:
        return 1
    return 0


def get_column(dframe, possible_names):
    for name in possible_names:
        if name in dframe.columns:
            return name
    return None


def find_model(filename):
    for folder in MODEL_PATHS:
        path = folder / filename
        if path.exists():
            return path
    return None


@st.cache_resource
def load_models():
    preprocessor_path = find_model("preprocessor.pkl")
    rf_path = find_model("random_forest.pkl")
    preprocessor = joblib.load(preprocessor_path) if preprocessor_path else None
    random_forest = joblib.load(rf_path) if rf_path else None
    return preprocessor, random_forest


preprocessor, random_forest = load_models()


def percentage(value):
    return f"{value * 100:.1f}%"


def hex_to_rgba(hex_color: str, alpha: float = 0.35) -> str:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def plotly_style(fig):
    fig.update_layout(
        template=V["plotly_template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=V["text"]),
        legend_title_text="",
        margin=dict(t=50, l=10, r=10, b=10),
    )
    return fig


# SIDEBAR

with st.sidebar:
    st.markdown("## \U0001F52E ChurnIQ")
    st.caption("Customer Churn Analytics & Prediction Platform")
    st.markdown("---")

    page = st.radio("Navigation", PAGES, key="nav_radio")

    st.markdown("---")
    st.caption("Python • Pandas • Scikit-learn • Random Forest • Plotly • Streamlit")


# DATA GUARDS


if df is None:
    st.error(
        "Unable to find `churn_dashboard.csv`.\n\n"
        "Expected location: `data/processed/churn_dashboard.csv`"
    )
    st.stop()

churn_col = get_column(df, ["churn", "customer_churn", "churn_status"])
if churn_col is None:
    st.error("The dataset does not contain a churn column.")
    st.stop()

df["churn_numeric"] = df[churn_col].apply(normalize_churn)

contract_col = get_column(df, ["contract", "contract_type"])
internet_col = get_column(df, ["internetservice", "internet_service"])
payment_col = get_column(df, ["paymentmethod", "payment_method"])
tenure_col = get_column(df, ["tenure", "tenure_months"])
monthly_col = get_column(df, ["monthlycharges", "monthly_charges"])

total_customers = len(df)
churned_customers = int(df["churn_numeric"].sum())
churn_rate = churned_customers / total_customers if total_customers else 0
avg_monthly = pd.to_numeric(df[monthly_col], errors="coerce").mean() if monthly_col else 0
avg_tenure = pd.to_numeric(df[tenure_col], errors="coerce").mean() if tenure_col else 0

# HOME
if page == "\U0001F3E0 Home":

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-badge">\U0001F52E ChurnIQ</div>
            <div class="hero-title">Customer Churn Analytics & Prediction Platform</div>
            <div class="hero-subtitle">
                Explore live churn patterns, understand what drives customers to leave,
                and score any individual customer's churn risk in seconds — all in one place.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Quick KPI strip
    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        (k1, "Total Customers", f"{total_customers:,}"),
        (k2, "Churned Customers", f"{churned_customers:,}"),
        (k3, "Churn Rate", percentage(churn_rate)),
        (k4, "Avg Monthly Charges", f"${avg_monthly:,.2f}"),
    ]
    for col, label, value in kpis:
        with col:
            st.markdown(
                f"""<div class="kpi-card">
                        <div class="kpi-value">{value}</div>
                        <div class="kpi-label">{label}</div>
                    </div>""",
                unsafe_allow_html=True
            )

    st.write("")
    st.write("")

    # Primary actions: Dashboard & Predict Churn
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="feature-wrap">', unsafe_allow_html=True)
        st.markdown("#### \U0001F4CA Explore the Dashboard")
        st.caption("Interactive charts on churn by contract, tenure, payment method & more.")
        st.button(
            "\U0001F4CA  Open Dashboard  →", key="home_dashboard_btn", width='stretch',
            on_click=go_to, args=("\U0001F4CA Dashboard",)
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="feature-wrap predict">', unsafe_allow_html=True)
        st.markdown("#### \U0001F3AF Predict Churn")
        st.caption("Enter a customer's details and get an instant churn risk score.")
        st.button(
            "\U0001F3AF  Predict Churn  →", key="home_predict_btn", width='stretch',
            on_click=go_to, args=("\U0001F3AF Predict Churn",)
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("##### More in ChurnIQ")

    p1, p2, p3 = st.columns(3)
    pill_targets = [
        (p1, "\U0001F50E Churn Analysis"),
        (p2, "\U0001F916 Model Performance"),
        (p3, "\U0001F4A1 Business Insights"),
    ]
    for col, target in pill_targets:
        with col:
            st.markdown('<div class="pill-wrap">', unsafe_allow_html=True)
            st.button(
                target, key=f"home_pill_{target}", width='stretch',
                on_click=go_to, args=(target,)
            )
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Snapshot chart on home page
    if contract_col:
        st.markdown("##### Snapshot: Churn by Contract Type")
        snap = pd.crosstab(df[contract_col], df[churn_col]).reset_index()
        snap_melt = snap.melt(id_vars=contract_col, var_name="Churn", value_name="Customers")
        fig = px.bar(
            snap_melt, x=contract_col, y="Customers", color="Churn",
            barmode="group", color_discrete_sequence=V["palette"], text="Customers"
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(plotly_style(fig), width='stretch')


# DASHBOARD

elif page == "\U0001F4CA Dashboard":

    st.markdown(
        '<div class="hero"><div class="hero-title" style="font-size:32px;">\U0001F4CA Churn Analytics Dashboard</div>'
        '<div class="hero-subtitle">Live filters, live insights.</div></div>',
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.markdown("### \U0001F39B\uFE0F Dashboard Filters")
        filtered_df = df.copy()

        if contract_col:
            opts = sorted(df[contract_col].dropna().astype(str).unique().tolist())
            sel = st.multiselect("Contract", opts, default=opts, key="f_contract")
            filtered_df = filtered_df[filtered_df[contract_col].astype(str).isin(sel)]

        if internet_col:
            opts = sorted(df[internet_col].dropna().astype(str).unique().tolist())
            sel = st.multiselect("Internet Service", opts, default=opts, key="f_internet")
            filtered_df = filtered_df[filtered_df[internet_col].astype(str).isin(sel)]

        if payment_col:
            opts = sorted(df[payment_col].dropna().astype(str).unique().tolist())
            sel = st.multiselect("Payment Method", opts, default=opts, key="f_payment")
            filtered_df = filtered_df[filtered_df[payment_col].astype(str).isin(sel)]

        if tenure_col:
            t_series = pd.to_numeric(df[tenure_col], errors="coerce")
            t_min, t_max = int(t_series.min()), int(t_series.max())
            rng = st.slider("Tenure (months)", t_min, t_max, (t_min, t_max), key="f_tenure")
            filtered_df = filtered_df[
                pd.to_numeric(filtered_df[tenure_col], errors="coerce").between(*rng)
            ]

        if monthly_col:
            m_series = pd.to_numeric(df[monthly_col], errors="coerce")
            m_min, m_max = float(m_series.min()), float(m_series.max())
            rng = st.slider("Monthly Charges ($)", m_min, m_max, (m_min, m_max), key="f_monthly")
            filtered_df = filtered_df[
                pd.to_numeric(filtered_df[monthly_col], errors="coerce").between(*rng)
            ]

        st.caption(f"Showing **{len(filtered_df):,}** of **{len(df):,}** customers")

    if filtered_df.empty:
        st.warning("No customers match the current filters. Adjust the filters in the sidebar.")
        st.stop()

    d = filtered_df

    d_churned = (d[churn_col].astype(str).str.lower().isin(["yes", "1", "true", "churn"])).sum()
    d_total = len(d)
    d_rate = d_churned / d_total if d_total else 0
    d_avg_monthly = pd.to_numeric(d[monthly_col], errors="coerce").mean() if monthly_col else 0
    d_avg_tenure = pd.to_numeric(d[tenure_col], errors="coerce").mean() if tenure_col else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Total Customers", f"{d_total:,}")
    with c2: st.metric("Churned Customers", f"{d_churned:,}")
    with c3: st.metric("Churn Rate", f"{d_rate:.1%}")
    with c4: st.metric("Avg Monthly Charges", f"${d_avg_monthly:,.2f}")
    with c5: st.metric("Avg Tenure", f"{d_avg_tenure:.0f} mo")

    st.markdown("---")
    st.subheader( "\U0001F4C9 Churn Distribution")

    churn_counts = d[churn_col].astype(str).value_counts().reset_index()
    churn_counts.columns = ["Churn", "Customers"]

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(churn_counts, names="Churn", values="Customers", hole=0.55,
                      color_discrete_sequence=V["palette"], title="Stayed vs Churned")
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(plotly_style(fig), width='stretch')
    with col2:
        fig = px.bar(churn_counts, x="Churn", y="Customers", color="Churn", text="Customers",
                      color_discrete_sequence=V["palette"], title="Customer Counts")
        fig.update_traces(textposition="outside")
        st.plotly_chart(plotly_style(fig), width='stretch')

    if contract_col:
        st.subheader("\U0001F4C4 Churn by Contract Type")
        t = d.groupby([contract_col, churn_col]).size().reset_index(name="Customers")
        fig = px.bar(t, x=contract_col, y="Customers", color=churn_col, barmode="group",
                      text="Customers", color_discrete_sequence=V["palette"])
        fig.update_traces(textposition="outside")
        st.plotly_chart(plotly_style(fig), width='stretch')

    if internet_col:
        st.subheader("\U0001F310 Churn by Internet Service")
        t = d.groupby([internet_col, churn_col]).size().reset_index(name="Customers")
        fig = px.bar(t, x=internet_col, y="Customers", color=churn_col, barmode="group",
                      text="Customers", color_discrete_sequence=V["palette"])
        fig.update_traces(textposition="outside")
        st.plotly_chart(plotly_style(fig), width='stretch')

    if payment_col:
        st.subheader("\U0001F4B3 Churn by Payment Method")
        t = d.groupby([payment_col, churn_col]).size().reset_index(name="Customers")
        fig = px.bar(t, x=payment_col, y="Customers", color=churn_col, barmode="group",
                      text="Customers", color_discrete_sequence=V["palette"])
        fig.update_traces(textposition="outside")
        st.plotly_chart(plotly_style(fig), width='stretch')

    if tenure_col:
        st.subheader("\U000023F3 Churn by Customer Tenure")
        temp = d.copy()
        temp["tenure_group"] = pd.cut(
            pd.to_numeric(temp[tenure_col], errors="coerce"),
            bins=[-1, 12, 24, 48, 72],
            labels=["0-12 months", "13-24 months", "25-48 months", "49-72 months"]
        )
        t = temp.groupby(["tenure_group", churn_col], observed=False).size().reset_index(name="Customers")
        fig = px.bar(t, x="tenure_group", y="Customers", color=churn_col, barmode="group",
                      text="Customers", color_discrete_sequence=V["palette"])
        fig.update_traces(textposition="outside")
        st.plotly_chart(plotly_style(fig), width='stretch')

    st.markdown("---")
    with st.expander("\U0001F50D View Dashboard Data"):
        st.dataframe(d.head(100), width='stretch')
        st.download_button(
            "\U00002B07\U0000FE0F Download filtered data (CSV)",
            data=d.to_csv(index=False).encode("utf-8"),
            file_name="filtered_churn_dashboard.csv",
            mime="text/csv"
        )


# CHURN ANALYSIS

elif page == "🔎 Churn Analysis":

    st.markdown(
        '<div class="hero"><div class="hero-title" style="font-size:32px;">🔎 Churn Analysis</div>'
        '<div class="hero-subtitle">Explore which customer groups are more likely to churn.</div></div>',
        unsafe_allow_html=True
    )

    selected_churn = st.selectbox("View customers", ["All", "Churned", "Stayed"])

    analysis_df = df.copy()
    if selected_churn == "Churned":
        analysis_df = df[df["churn_numeric"] == 1]
    elif selected_churn == "Stayed":
        analysis_df = df[df["churn_numeric"] == 0]

    st.write(f"Customers in selection: **{len(analysis_df):,}**")
    st.markdown("---")

    if contract_col:
        st.subheader("📄 Contract Type")
        t = pd.crosstab(analysis_df[contract_col], analysis_df[churn_col]).reset_index().melt(
            id_vars=contract_col, var_name="Churn", value_name="Customers")
        fig = px.bar(t, x=contract_col, y="Customers", color="Churn", barmode="group",
                      text="Customers", color_discrete_sequence=V["palette"])
        fig.update_traces(textposition="outside")
        st.plotly_chart(plotly_style(fig), width='stretch')

    if tenure_col:
        st.subheader("⏳ Customer Tenure")
        temp = analysis_df.copy()
        temp["tenure_group"] = pd.cut(
            pd.to_numeric(temp[tenure_col], errors="coerce"),
            bins=[-1, 6, 12, 24, 48, 1000],
            labels=["0–6 months", "7–12 months", "13–24 months", "25–48 months", "49+ months"]
        )
        t = temp.groupby(["tenure_group", churn_col], observed=False).size().reset_index(name="Customers")
        fig = px.bar(t, x="tenure_group", y="Customers", color=churn_col, barmode="group",
                      text="Customers", color_discrete_sequence=V["palette"])
        fig.update_traces(textposition="outside")
        st.plotly_chart(plotly_style(fig), width='stretch')

    if payment_col:
        st.subheader("💳 Payment Method")
        t = analysis_df.groupby([payment_col, churn_col]).size().reset_index(name="Customers")
        fig = px.bar(t, x=payment_col, y="Customers", color=churn_col, barmode="group",
                      text="Customers", color_discrete_sequence=V["palette"])
        fig.update_traces(textposition="outside")
        st.plotly_chart(plotly_style(fig), width='stretch')

    if monthly_col:
        st.subheader("💰 Monthly Charges")
        temp = analysis_df.copy()
        temp[monthly_col] = pd.to_numeric(temp[monthly_col], errors="coerce")
        temp["charge_group"] = pd.cut(
            temp[monthly_col], bins=[0, 30, 60, 90, 150],
            labels=["Low: <$30", "Medium: $30–60", "High: $60–90", "Very High: $90+"]
        )
        t = temp.groupby(["charge_group", churn_col], observed=False).size().reset_index(name="Customers")
        fig = px.bar(t, x="charge_group", y="Customers", color=churn_col, barmode="group",
                      text="Customers", color_discrete_sequence=V["palette"])
        fig.update_traces(textposition="outside")
        st.plotly_chart(plotly_style(fig), width='stretch')

# PREDICT CHURN

elif page == "\U0001F3AF Predict Churn":

    st.markdown(
        '<div class="hero"><div class="hero-title" style="font-size:32px;"> Customer Churn Prediction</div>'
        '<div class="hero-subtitle">Enter customer information to estimate the probability that the customer will churn.</div></div>',
        unsafe_allow_html=True
    )

    if preprocessor is None or random_forest is None:
        st.error(
            "Model files could not be loaded. "
            "Make sure `models/preprocessor.pkl` and `models/random_forest.pkl` exist."
        )
        st.stop()

    st.subheader("\U0001F464 Customer Information")
    col1, col2, col3 = st.columns(3)

    gender_col = get_column(df, ["gender"])
    if gender_col:
        gender = col1.selectbox("Gender", df[gender_col].dropna().astype(str).unique().tolist())
    else:
        gender = "Female"

    senior_col = get_column(df, ["seniorcitizen", "senior_citizen"])
    if senior_col:
        senior = col1.selectbox("Senior Citizen", df[senior_col].dropna().unique().tolist())
    else:
        senior = 0

    partner_col = get_column(df, ["partner"])
    if partner_col:
        partner = col1.selectbox("Partner", df[partner_col].dropna().astype(str).unique().tolist())
    else:
        partner = "No"

    dependent_col = get_column(df, ["dependents"])
    if dependent_col:
        dependents = col2.selectbox("Dependents", df[dependent_col].dropna().astype(str).unique().tolist())
    else:
        dependents = "No"

    if tenure_col:
        tenure = col2.number_input("Tenure (months)", min_value=0, max_value=100, value=12)
    else:
        tenure = 12

    phone_col = get_column(df, ["phoneservice", "phone_service"])
    if phone_col:
        phone_service = col2.selectbox("Phone Service", df[phone_col].dropna().astype(str).unique().tolist())
    else:
        phone_service = "Yes"

    if contract_col:
        contract = col3.selectbox("Contract", df[contract_col].dropna().astype(str).unique().tolist())
    else:
        contract = "Month-to-month"

    if monthly_col:
        monthly_charges = col3.number_input("Monthly Charges", min_value=0.0, value=70.0, step=1.0)
    else:
        monthly_charges = 70.0

    total_col = get_column(df, ["totalcharges", "total_charges"])
    if total_col:
        total_charges = col3.number_input("Total Charges", min_value=0.0, value=840.0, step=10.0)
    else:
        total_charges = 840.0

    st.subheader("\U0001F6E0 Services")
    service_cols = [
        ("internetservice", "Internet Service"),
        ("onlinesecurity", "Online Security"),
        ("onlinebackup", "Online Backup"),
        ("deviceprotection", "Device Protection"),
        ("techsupport", "Tech Support"),
        ("streamingtv", "Streaming TV"),
        ("streamingmovies", "Streaming Movies"),
        ("multiplelines", "Multiple Lines"),
        ("paperlessbilling", "Paperless Billing"),
        ("paymentmethod", "Payment Method"),
    ]

    selected_values = {}
    cols = st.columns(3)
    for i, (column_name, label) in enumerate(service_cols):
        actual_col = get_column(df, [column_name, column_name.replace("_", "")])
        if actual_col:
            options = df[actual_col].dropna().astype(str).unique().tolist()
            selected_values[column_name] = cols[i % 3].selectbox(
                label, options, key=f"predict_{column_name}"
            )

    st.markdown("---")

    if st.button("\U0001F464 Predict Churn", type="primary", width='stretch'):
        try:
            input_data = {
                "gender": gender,
                "seniorcitizen": senior,
                "partner": partner,
                "dependents": dependents,
                "tenure": tenure,
                "phoneservice": phone_service,
                "contract": contract,
                "monthlycharges": monthly_charges,
                "totalcharges": total_charges,
            }
            input_data.update(selected_values)

            if hasattr(preprocessor, "feature_names_in_"):
                required_columns = list(preprocessor.feature_names_in_)
            else:
                required_columns = list(input_data.keys())

            row = {}
            for column in required_columns:
                if column in input_data:
                    row[column] = input_data[column]
                elif column in df.columns:
                    row[column] = df[column].dropna().mode()[0]
                else:
                    row[column] = 0

            input_df = pd.DataFrame([row])
            X_processed = preprocessor.transform(input_df)
            if hasattr(X_processed, "toarray"):
                X_processed = X_processed.toarray()

            probability = float(random_forest.predict_proba(X_processed)[0][1])
            prediction = int(probability >= 0.5)

            st.subheader("\U0001F3AF Prediction Result")
            r1, r2 = st.columns([2, 1])

            with r1:
                if prediction == 1:
                    st.error("\U000026A0\U0000FE0F Customer is likely to CHURN")
                else:
                    st.success("\U00002705 Customer is likely to STAY")

            with r2:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=probability * 100,
                    number={"suffix": "%"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": V["accent1"]},
                        "steps": [
                            {"range": [0, 40], "color": hex_to_rgba(BLUE_PALETTE[0], 0.6)},
                            {"range": [40, 70], "color": hex_to_rgba(BLUE_PALETTE[2], 0.5)},
                            {"range": [70, 100], "color": hex_to_rgba(BLUE_PALETTE[4], 0.5)},
                        ],
                    },
                    title={"text": "Churn Probability"},
                ))
                fig.update_layout(height=220, margin=dict(t=30, b=10, l=10, r=10))
                st.plotly_chart(plotly_style(fig), width='stretch')

            if probability >= 0.70:
                st.markdown('<div class="risk-high">\U0001F534 HIGH RISK — Immediate retention action recommended.</div>', unsafe_allow_html=True)
                recommendation = ("Contact the customer immediately. Consider a retention offer, "
                                   "discount, contract upgrade, or personalized support.")
            elif probability >= 0.40:
                st.markdown('<div class="risk-medium">\U0001F7E1 MEDIUM RISK — Customer should be monitored.</div>', unsafe_allow_html=True)
                recommendation = ("Monitor the customer closely and consider targeted engagement "
                                   "or service improvements.")
            else:
                st.markdown('<div class="risk-low">\U0001F7E2 LOW RISK — Customer is likely to stay.</div>', unsafe_allow_html=True)
                recommendation = "Maintain good service quality and continue regular customer engagement."

            st.subheader("\U0001F4A1 Retention Recommendation")
            st.info(recommendation)

        except Exception as e:
            st.error(f"Prediction failed: {str(e)}")
            st.info(
                "This usually happens when the prediction input columns do not exactly "
                "match the columns used during model training."
            )



# MODEL PERFORMANCE

elif page == "\U0001F916 Model Performance":

    st.markdown(
        '<div class="hero"><div class="hero-title" style="font-size:32px;">\U0001F916 Model Performance</div>'
        '<div class="hero-subtitle">Evaluate the machine learning models used for customer churn prediction.</div></div>',
        unsafe_allow_html=True
    )

    metrics = pd.DataFrame({
        "Metric": ["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"],
        "Logistic Regression": [0.805, 0.660, 0.560, 0.605, 0.842],
        "Random Forest": [0.7573, 0.5295, 0.7674, 0.6266, 0.8393],
    })

    st.subheader("\U0001F4CA Model Comparison")
    st.dataframe(
        metrics.style.format({"Logistic Regression": "{:.3f}", "Random Forest": "{:.3f}"}),
        width='stretch', hide_index=True
    )

    st.markdown("---")
    rf_values = [0.7573, 0.5295, 0.7674, 0.6266, 0.8393]
    labels = ["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]
    cols = st.columns(5)
    for col, label, value in zip(cols, labels, rf_values):
        with col:
            st.metric(label, f"{value:.3f}")

    st.markdown("---")
    st.subheader("\U0001F4C8 Performance Comparison")
    chart_df = metrics.melt(id_vars="Metric", var_name="Model", value_name="Score")
    fig = px.bar(chart_df, x="Metric", y="Score", color="Model", barmode="group",
                  color_discrete_sequence=V["palette"], text="Score")
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    st.plotly_chart(plotly_style(fig), width='stretch')

    st.markdown("---")
    st.subheader("\U0001F522 Random Forest Confusion Matrix")

    cm_values = [[780, 255], [87, 287]]
    cm_labels_y = ["Actual: No Churn", "Actual: Churn"]
    cm_labels_x = ["Predicted: No Churn", "Predicted: Churn"]

    fig = px.imshow(
        cm_values, x=cm_labels_x, y=cm_labels_y, text_auto=True,
        color_continuous_scale=[BLUE_PALETTE[0], BLUE_PALETTE[4]],
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(plotly_style(fig), width='stretch')

    st.info(
        "The model correctly identifies a large proportion of customers who are actually "
        "going to churn. Recall is particularly important for retention because missing a "
        "customer who is about to churn can result in lost revenue."
    )

    st.markdown("---")
    st.subheader("\U0001F9E0 Which Model Should We Use?")
    st.write(
        """
        **Random Forest** provides strong churn detection, with a recall of approximately
        **76.7%** and ROC-AUC of approximately **0.839**.

        **Logistic Regression** has slightly better overall accuracy and ROC-AUC in our comparison.

        For a business retention system, Random Forest can be useful when the priority is
        identifying as many potentially churning customers as possible.
        """
    )

# BUSINESS INSIGHTS

elif page == "\U0001F4A1 Business Insights":

    st.markdown(
        '<div class="hero"><div class="hero-title" style="font-size:32px;">\U0001F4A1 Business Insights</div>'
        '<div class="hero-subtitle">Turn churn analysis into practical customer retention actions.</div></div>',
        unsafe_allow_html=True
    )

    st.subheader("\U0001F4CC Overall Situation")
    st.metric("Current Churn Rate", f"{churn_rate * 100:.1f}%")

    if churn_rate > 0.25:
        st.warning("The business has a relatively high churn rate. Customer retention should be a priority.")
    else:
        st.success("The overall churn rate is manageable, but high-risk customer segments should still be targeted.")

    if contract_col:
        st.subheader("\U0001F4C4 Contract Strategy")
        contract_rate = df.groupby(contract_col)["churn_numeric"].mean().sort_values(ascending=False).reset_index()
        contract_rate.columns = [contract_col, "Churn Rate"]
        fig = px.bar(contract_rate, x=contract_col, y="Churn Rate", color=contract_col,
                      color_discrete_sequence=V["palette"], text="Churn Rate")
        fig.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(plotly_style(fig), width='stretch')

        highest_contract = contract_rate.iloc[0][contract_col]
        st.info(
            f"**{highest_contract}** currently has the highest observed churn rate. "
            "Consider incentives that encourage customers to move toward longer-term contracts."
        )

    if tenure_col:
        st.subheader("\U000023F3 Tenure Strategy")
        temp = df.copy()
        temp["tenure_group"] = pd.cut(
            pd.to_numeric(temp[tenure_col], errors="coerce"),
            bins=[-1, 6, 12, 24, 48, 1000],
            labels=["0–6 months", "7–12 months", "13–24 months", "25–48 months", "49+ months"]
        )
        tenure_rate = temp.groupby("tenure_group", observed=False)["churn_numeric"].mean().reset_index()
        tenure_rate.columns = ["Tenure Group", "Churn Rate"]
        fig = px.bar(tenure_rate, x="Tenure Group", y="Churn Rate", color="Tenure Group",
                      color_discrete_sequence=V["palette"], text="Churn Rate")
        fig.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(plotly_style(fig), width='stretch')
        st.info("New customers should receive additional onboarding and engagement during their first few months.")

    if payment_col:
        st.subheader("\U0001F4B3 Payment Method Strategy")
        payment_rate = df.groupby(payment_col)["churn_numeric"].mean().sort_values(ascending=False).reset_index()
        payment_rate.columns = [payment_col, "Churn Rate"]
        fig = px.bar(payment_rate, x=payment_col, y="Churn Rate", color=payment_col,
                      color_discrete_sequence=V["palette"], text="Churn Rate")
        fig.update_traces(texttemplate="%{text:.1%}", textposition="outside")
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(plotly_style(fig), width='stretch')

    st.markdown("---")
    st.subheader("\U0001F3AF Recommended Retention Strategy")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="ciq-card">', unsafe_allow_html=True)
        st.markdown("### \U0001F534 High Risk")
        st.write("• Immediate customer contact\n\n• Personalized offers\n\n• Contract incentives\n\n• Dedicated support")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="ciq-card">', unsafe_allow_html=True)
        st.markdown("### \U0001F7E1 Medium Risk")
        st.write("• Monitor behavior\n\n• Targeted promotions\n\n• Service recommendations\n\n• Engagement campaigns")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="ciq-card">', unsafe_allow_html=True)
        st.markdown("### \U0001F7E2 Low Risk")
        st.write("• Maintain service quality\n\n• Loyalty programs\n\n• Regular engagement\n\n• Upselling opportunities")
        st.markdown('</div>', unsafe_allow_html=True)

# FOOTER

st.markdown("---")
st.caption("\U0001F52E ChurnIQ — Customer Churn Analytics & Prediction Platform | Python • Pandas • Scikit-learn • Random Forest • Plotly • Streamlit")