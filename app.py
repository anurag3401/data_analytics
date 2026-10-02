import streamlit as st
import pandas as pd
import numpy as np
import sqlite3

from pathlib import Path
from datetime import timedelta

import plotly.express as px
import plotly.graph_objects as go

from sklearn.ensemble import IsolationForest
from scipy.stats import ttest_ind


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Pharmaceutical Commercial Analytics",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = (
    BASE_DIR
    / "database"
    / "pharma_analytics.db"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 34px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 16px;
        opacity: 0.70;
        margin-bottom: 20px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 600;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .insight-box {
        padding: 14px;
        border-radius: 8px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0


# ============================================================
# DATABASE LOADING
# ============================================================

@st.cache_data
def load_data(refresh_counter=0):

    if not DATABASE_PATH.exists():
        st.error(
            f"Database not found:\n\n{DATABASE_PATH}"
        )
        st.stop()

    conn = sqlite3.connect(
        DATABASE_PATH
    )

    # Try the expected sales table.
    query = """
        SELECT *
        FROM sales
    """

    data = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    if data.empty:
        st.error(
            "The sales table is empty."
        )
        st.stop()

    # --------------------------------------------------------
    # DATE CONVERSION
    # --------------------------------------------------------

    if "date" not in data.columns:
        st.error(
            "The database does not contain a 'date' column."
        )
        st.stop()

    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce"
    )

    data = data.dropna(
        subset=["date"]
    )

    # --------------------------------------------------------
    # NUMERIC COLUMNS
    # --------------------------------------------------------

    numeric_columns = [
        "revenue",
        "target_sales",
        "units_sold",
        "prescriptions",
        "promotion_spend"
    ]

    for column in numeric_columns:

        if column in data.columns:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            ).fillna(0)

    return data


df = load_data(
    st.session_state.refresh_counter
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">💊 Pharmaceutical Commercial Analytics</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    Interactive commercial performance, customer and revenue analytics
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Dashboard Controls")


# ------------------------------------------------------------
# REFRESH DATA
# ------------------------------------------------------------

st.sidebar.subheader("Data")

if st.sidebar.button(
    "🔄 Refresh Data",
    width="stretch"
):

    st.cache_data.clear()

    st.session_state.refresh_counter += 1

    st.rerun()


# ------------------------------------------------------------
# LAST UPDATE
# ------------------------------------------------------------

last_update = pd.Timestamp.now().strftime(
    "%d-%b-%Y %H:%M:%S"
)

st.sidebar.caption(
    f"Dashboard refreshed: {last_update}"
)


# ============================================================
# NAVIGATION
# ============================================================

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    [
        "Executive Overview",
        "Product Analytics",
        "Territory Analytics",
        "Advanced Analytics",
        "Data Explorer"
    ]
)


# ============================================================
# GLOBAL FILTERS
# ============================================================

st.sidebar.divider()

st.sidebar.subheader(
    "Filters"
)


# ------------------------------------------------------------
# DATE FILTER
# ------------------------------------------------------------

minimum_date = df["date"].min().date()
maximum_date = df["date"].max().date()

selected_dates = st.sidebar.date_input(
    "Date Range",
    value=(
        minimum_date,
        maximum_date
    ),
    min_value=minimum_date,
    max_value=maximum_date
)


if isinstance(
    selected_dates,
    tuple
) and len(selected_dates) == 2:

    start_date = pd.Timestamp(
        selected_dates[0]
    )

    end_date = pd.Timestamp(
        selected_dates[1]
    )

else:

    start_date = pd.Timestamp(
        minimum_date
    )

    end_date = pd.Timestamp(
        maximum_date
    )


# ------------------------------------------------------------
# REGION FILTER
# ------------------------------------------------------------

if "region" in df.columns:

    regions = st.sidebar.multiselect(
        "Region",
        sorted(
            df["region"]
            .dropna()
            .unique()
        ),
        default=sorted(
            df["region"]
            .dropna()
            .unique()
        )
    )

else:

    regions = []


# ------------------------------------------------------------
# PRODUCT FILTER
# ------------------------------------------------------------

if "product" in df.columns:

    products = st.sidebar.multiselect(
        "Product",
        sorted(
            df["product"]
            .dropna()
            .unique()
        ),
        default=sorted(
            df["product"]
            .dropna()
            .unique()
        )
    )

else:

    products = []


# ------------------------------------------------------------
# CUSTOMER SEGMENT FILTER
# ------------------------------------------------------------

if "customer_segment" in df.columns:

    segments = st.sidebar.multiselect(
        "Customer Segment",
        sorted(
            df["customer_segment"]
            .dropna()
            .unique()
        ),
        default=sorted(
            df["customer_segment"]
            .dropna()
            .unique()
        )
    )

else:

    segments = []


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    (df["date"] >= start_date)
    &
    (df["date"] <= end_date + timedelta(days=1))
].copy()


if regions:

    filtered_df = filtered_df[
        filtered_df["region"].isin(
            regions
        )
    ]


if products:

    filtered_df = filtered_df[
        filtered_df["product"].isin(
            products
        )
    ]


if segments:

    filtered_df = filtered_df[
        filtered_df["customer_segment"].isin(
            segments
        )
    ]


# ============================================================
# PREVIOUS PERIOD CALCULATION
# ============================================================

period_length = (
    end_date - start_date
).days + 1

previous_end = (
    start_date - timedelta(days=1)
)

previous_start = (
    previous_end
    - timedelta(days=period_length - 1)
)


previous_df = df[
    (df["date"] >= previous_start)
    &
    (df["date"] <= previous_end)
].copy()


if regions:

    previous_df = previous_df[
        previous_df["region"].isin(
            regions
        )
    ]


if products:

    previous_df = previous_df[
        previous_df["product"].isin(
            products
        )
    ]


if segments:

    previous_df = previous_df[
        previous_df["customer_segment"].isin(
            segments
        )
    ]


# ============================================================
# CORE KPI CALCULATIONS
# ============================================================

total_revenue = filtered_df[
    "revenue"
].sum()


previous_revenue = previous_df[
    "revenue"
].sum()


if previous_revenue != 0:

    revenue_growth = (
        (total_revenue - previous_revenue)
        /
        previous_revenue
    ) * 100

else:

    revenue_growth = 0


total_target = filtered_df[
    "target_sales"
].sum()


if total_target != 0:

    target_achievement = (
        total_revenue
        /
        total_target
    ) * 100

else:

    target_achievement = 0


target_gap = (
    total_revenue
    -
    total_target
)


units_sold = filtered_df[
    "units_sold"
].sum()


prescriptions = filtered_df[
    "prescriptions"
].sum()


customer_count = filtered_df[
    "doctor_id"
].nunique()


if customer_count > 0:

    revenue_per_customer = (
        total_revenue
        /
        customer_count
    )

else:

    revenue_per_customer = 0


if prescriptions > 0:

    revenue_per_prescription = (
        total_revenue
        /
        prescriptions
    )

else:

    revenue_per_prescription = 0


transaction_count = len(
    filtered_df
)


# ============================================================
# PAGE 1 — EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":

    st.header(
        "Executive Overview"
    )

    # --------------------------------------------------------
    # ACTIVE FILTER SUMMARY
    # --------------------------------------------------------

    st.info(
        f"""
        **Analysis Period:** {start_date.strftime('%d %b %Y')}
        → {end_date.strftime('%d %b %Y')}
        
        **Transactions:** {transaction_count:,}
        """
    )


    # ========================================================
    # KPI ROW 1
    # ========================================================

    c1, c2, c3, c4 = st.columns(4)


    c1.metric(
        "Total Revenue",
        f"₹{total_revenue:,.0f}"
    )


    c2.metric(
        "Revenue Growth",
        f"{revenue_growth:.2f}%",
        delta=f"{revenue_growth:.2f}%"
    )


    c3.metric(
        "Target Achievement",
        f"{target_achievement:.2f}%"
    )


    c4.metric(
        "Target Gap",
        f"₹{target_gap:,.0f}"
    )


    # ========================================================
    # KPI ROW 2
    # ========================================================

    st.write("")

    c5, c6, c7, c8 = st.columns(4)


    c5.metric(
        "Units Sold",
        f"{units_sold:,.0f}"
    )


    c6.metric(
        "Prescriptions",
        f"{prescriptions:,.0f}"
    )


    c7.metric(
        "Customers",
        f"{customer_count:,}"
    )


    c8.metric(
        "Revenue / Customer",
        f"₹{revenue_per_customer:,.0f}"
    )


    # ========================================================
    # KPI ROW 3
    # ========================================================

    st.write("")

    c9, c10 = st.columns(2)


    c9.metric(
        "Revenue / Prescription",
        f"₹{revenue_per_prescription:,.0f}"
    )


    c10.metric(
        "Transactions",
        f"{transaction_count:,}"
    )


    st.divider()


    # ========================================================
    # TARGET PERFORMANCE
    # ========================================================

    st.subheader(
        "🎯 Target Performance"
    )


    target_col1, target_col2 = st.columns(
        [2, 1]
    )


    with target_col1:

        target_chart = go.Figure()


        target_chart.add_trace(
            go.Bar(
                x=["Actual Revenue"],
                y=[total_revenue],
                name="Actual"
            )
        )


        target_chart.add_trace(
            go.Bar(
                x=["Target Revenue"],
                y=[total_target],
                name="Target"
            )
        )


        target_chart.update_layout(
            title="Actual Revenue vs Target",
            yaxis_title="Revenue",
            barmode="group"
        )


        st.plotly_chart(
            target_chart,
            width="stretch"
        )


    with target_col2:

        if target_achievement >= 100:

            st.success(
                f"""
                ### 🟢 Target Achieved

                Achievement:

                **{target_achievement:.2f}%**

                Surplus:

                **₹{target_gap:,.0f}**
                """
            )

        else:

            st.warning(
                f"""
                ### 🟠 Target Gap

                Achievement:

                **{target_achievement:.2f}%**

                Remaining:

                **₹{abs(target_gap):,.0f}**
                """
            )


    # ========================================================
    # MONTHLY REVENUE TREND
    # ========================================================

    st.subheader(
        "📈 Revenue Trend"
    )


    if not filtered_df.empty:

        monthly = (
            filtered_df
            .groupby(
                filtered_df["date"]
                .dt
                .to_period("M")
            )
            .agg(
                revenue=("revenue", "sum"),
                target=("target_sales", "sum")
            )
            .reset_index()
        )


        monthly["date"] = (
            monthly["date"]
            .astype(str)
        )


        fig = go.Figure()


        fig.add_trace(
            go.Scatter(
                x=monthly["date"],
                y=monthly["revenue"],
                mode="lines+markers",
                name="Revenue"
            )
        )


        fig.add_trace(
            go.Scatter(
                x=monthly["date"],
                y=monthly["target"],
                mode="lines",
                name="Target"
            )
        )


        fig.update_layout(
            title="Monthly Revenue vs Target",
            xaxis_title="Month",
            yaxis_title="Revenue",
            hovermode="x unified"
        )


        st.plotly_chart(
            fig,
            width="stretch"
        )


    # ========================================================
    # PRODUCT + REGION
    # ========================================================

    col1, col2 = st.columns(2)


    with col1:

        product_summary = (
            filtered_df
            .groupby("product")
            ["revenue"]
            .sum()
            .sort_values(
                ascending=False
            )
            .reset_index()
        )


        fig_product = px.bar(
            product_summary,
            x="product",
            y="revenue",
            title="Revenue by Product"
        )


        st.plotly_chart(
            fig_product,
            width="stretch"
        )


    with col2:

        region_summary = (
            filtered_df
            .groupby("region")
            ["revenue"]
            .sum()
            .sort_values(
                ascending=False
            )
            .reset_index()
        )


        fig_region = px.bar(
            region_summary,
            x="region",
            y="revenue",
            title="Revenue by Region"
        )


        st.plotly_chart(
            fig_region,
            width="stretch"
        )


    # ========================================================
    # DYNAMIC BUSINESS INSIGHTS
    # ========================================================

    st.subheader(
        "💡 Dynamic Business Insights"
    )


    insights = []


    # --------------------------------------------------------
    # Revenue growth insight
    # --------------------------------------------------------

    if revenue_growth > 0:

        insights.append(
            f"🟢 Revenue increased by "
            f"**{revenue_growth:.2f}%** compared with "
            f"the previous period."
        )

    elif revenue_growth < 0:

        insights.append(
            f"🔴 Revenue decreased by "
            f"**{abs(revenue_growth):.2f}%** compared "
            f"with the previous period."
        )

    else:

        insights.append(
            "🔵 Revenue remained approximately unchanged "
            "compared with the previous period."
        )


    # --------------------------------------------------------
    # Target insight
    # --------------------------------------------------------

    if target_achievement >= 100:

        insights.append(
            f"🟢 The selected business scope exceeded "
            f"the sales target by "
            f"**₹{target_gap:,.0f}**."
        )

    else:

        insights.append(
            f"🟠 The selected business scope is "
            f"**₹{abs(target_gap):,.0f}** below the "
            f"current sales target."
        )


    # --------------------------------------------------------
    # Product insight
    # --------------------------------------------------------

    if not product_summary.empty:

        top_product = (
            product_summary.iloc[0]["product"]
        )

        top_product_revenue = (
            product_summary.iloc[0]["revenue"]
        )


        product_share = (
            top_product_revenue
            /
            total_revenue
            *
            100
            if total_revenue != 0
            else 0
        )


        insights.append(
            f"🔵 **{top_product}** is the leading "
            f"product, contributing approximately "
            f"**{product_share:.1f}%** of selected revenue."
        )


    # --------------------------------------------------------
    # Territory insight
    # --------------------------------------------------------

    if not region_summary.empty:

        top_region = (
            region_summary.iloc[0]["region"]
        )

        top_region_revenue = (
            region_summary.iloc[0]["revenue"]
        )


        region_share = (
            top_region_revenue
            /
            total_revenue
            *
            100
            if total_revenue != 0
            else 0
        )


        insights.append(
            f"🌍 **{top_region}** generates the highest "
            f"revenue contribution at approximately "
            f"**{region_share:.1f}%**."
        )


    # --------------------------------------------------------
    # Customer value insight
    # --------------------------------------------------------

    if revenue_per_customer > 0:

        insights.append(
            f"👥 Average revenue per selected customer "
            f"is **₹{revenue_per_customer:,.0f}**."
        )


    # --------------------------------------------------------
    # Display insights
    # --------------------------------------------------------

    for insight in insights:

        st.markdown(
            f"""
            <div class="insight-box">
            {insight}
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# PAGE 2 — PRODUCT ANALYTICS
# ============================================================

elif page == "Product Analytics":

    st.header(
        "Product Analytics"
    )


    product = (
        filtered_df
        .groupby("product")
        .agg(
            revenue=("revenue", "sum"),
            units=("units_sold", "sum"),
            prescriptions=("prescriptions", "sum"),
            target=("target_sales", "sum")
        )
        .reset_index()
    )


    product["achievement"] = np.where(
        product["target"] != 0,
        (
            product["revenue"]
            /
            product["target"]
        ) * 100,
        0
    )


    product["contribution"] = np.where(
        total_revenue != 0,
        (
            product["revenue"]
            /
            total_revenue
        ) * 100,
        0
    )


    product["target_gap"] = (
        product["revenue"]
        -
        product["target"]
    )


    st.dataframe(
        product.sort_values(
            "revenue",
            ascending=False
        ),
        width="stretch"
    )


    col1, col2 = st.columns(2)


    with col1:

        fig = px.bar(
            product.sort_values(
                "revenue",
                ascending=False
            ),
            x="product",
            y="revenue",
            title="Revenue by Product"
        )


        st.plotly_chart(
            fig,
            width="stretch"
        )


    with col2:

        fig = px.bar(
            product.sort_values(
                "achievement",
                ascending=False
            ),
            x="product",
            y="achievement",
            title="Target Achievement by Product"
        )


        fig.add_hline(
            y=100,
            line_dash="dash",
            annotation_text="Target"
        )


        st.plotly_chart(
            fig,
            width="stretch"
        )


# ============================================================
# PAGE 3 — TERRITORY ANALYTICS
# ============================================================

elif page == "Territory Analytics":

    st.header(
        "Territory Analytics"
    )


    territory = (
        filtered_df
        .groupby("region")
        .agg(
            revenue=("revenue", "sum"),
            target=("target_sales", "sum"),
            customers=("doctor_id", "nunique"),
            prescriptions=("prescriptions", "sum")
        )
        .reset_index()
    )


    territory["achievement"] = np.where(
        territory["target"] != 0,
        (
            territory["revenue"]
            /
            territory["target"]
        ) * 100,
        0
    )


    territory["target_gap"] = (
        territory["revenue"]
        -
        territory["target"]
    )


    territory["revenue_per_customer"] = np.where(
        territory["customers"] != 0,
        (
            territory["revenue"]
            /
            territory["customers"]
        ),
        0
    )


    st.dataframe(
        territory.sort_values(
            "revenue",
            ascending=False
        ),
        width="stretch"
    )


    fig = px.scatter(
        territory,
        x="revenue",
        y="achievement",
        size="customers",
        color="region",
        hover_name="region",
        title="Territory Performance Matrix"
    )


    fig.add_hline(
        y=100,
        line_dash="dash",
        annotation_text="Target"
    )


    st.plotly_chart(
        fig,
        width="stretch"
    )


    st.subheader(
        "Territory Target Gaps"
    )


    gap_chart = px.bar(
        territory.sort_values(
            "target_gap"
        ),
        x="region",
        y="target_gap",
        title="Revenue Gap vs Target"
    )


    gap_chart.add_hline(
        y=0,
        line_dash="dash"
    )


    st.plotly_chart(
        gap_chart,
        width="stretch"
    )


# ============================================================
# PAGE 4 — ADVANCED ANALYTICS
# ============================================================

elif page == "Advanced Analytics":

    st.header("🚀 Advanced Analytics")

    st.markdown(
        """
        Advanced analytical tools for identifying unusual transactions,
        evaluating customer risk, and statistically testing commercial
        relationships.
        """
    )

    # ========================================================
    # TABS
    # ========================================================

    tab1, tab2, tab3 = st.tabs(
        [
            "🔴 Anomaly Detection",
            "👥 Customer Risk",
            "🧪 Statistical Testing"
        ]
    )

    # ========================================================
    # TAB 1 — ANOMALY DETECTION
    # ========================================================

    with tab1:

        st.subheader(
            "🔴 Transaction Anomaly Detection"
        )

        st.write(
            """
            Isolation Forest is used to identify transactions whose
            commercial behavior differs substantially from the rest
            of the selected dataset.
            """
        )

        anomaly_features = [
            "revenue",
            "units_sold",
            "prescriptions",
            "promotion_spend"
        ]

        available_features = [
            column
            for column in anomaly_features
            if column in filtered_df.columns
        ]

        if len(available_features) < 2:

            st.warning(
                "At least two numerical variables are required "
                "for anomaly detection."
            )

        elif len(filtered_df) < 20:

            st.warning(
                "At least 20 records are recommended for "
                "anomaly detection."
            )

        else:

            contamination = st.slider(
                "Expected anomaly proportion",
                min_value=0.01,
                max_value=0.10,
                value=0.02,
                step=0.01
            )

            anomaly_data = filtered_df[
                available_features
            ].copy()

            anomaly_data = anomaly_data.replace(
                [np.inf, -np.inf],
                np.nan
            )

            anomaly_data = anomaly_data.dropna()

            model = IsolationForest(
                contamination=contamination,
                random_state=42
            )

            predictions = model.fit_predict(
                anomaly_data
            )

            anomaly_scores = model.decision_function(
                anomaly_data
            )

            anomaly_result = anomaly_data.copy()

            anomaly_result["anomaly_prediction"] = predictions

            anomaly_result["anomaly_score"] = anomaly_scores

            anomaly_result["status"] = np.where(
                predictions == -1,
                "Anomaly",
                "Normal"
            )

            anomaly_count = (
                anomaly_result["status"]
                == "Anomaly"
            ).sum()

            normal_count = (
                anomaly_result["status"]
                == "Normal"
            ).sum()

            # ------------------------------------------------
            # KPI ROW
            # ------------------------------------------------

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Records Analysed",
                f"{len(anomaly_result):,}"
            )

            c2.metric(
                "Potential Anomalies",
                f"{anomaly_count:,}"
            )

            c3.metric(
                "Anomaly Rate",
                f"{(anomaly_count / len(anomaly_result)) * 100:.2f}%"
            )

            st.divider()

            # ------------------------------------------------
            # ANOMALY VISUALIZATION
            # ------------------------------------------------

            if (
                "revenue" in anomaly_result.columns
                and "promotion_spend" in anomaly_result.columns
            ):

                fig_anomaly = px.scatter(
                    anomaly_result,
                    x="promotion_spend",
                    y="revenue",
                    color="status",
                    hover_data=available_features,
                    title="Potential Transaction Anomalies"
                )

                st.plotly_chart(
                    fig_anomaly,
                    width="stretch"
                )

            # ------------------------------------------------
            # ANOMALY TABLE
            # ------------------------------------------------

            st.subheader(
                "Potentially Unusual Transactions"
            )

            anomalies = anomaly_result[
                anomaly_result["status"] == "Anomaly"
            ].sort_values(
                "anomaly_score"
            )

            if anomalies.empty:

                st.success(
                    "No significant anomalies were detected."
                )

            else:

                st.dataframe(
                    anomalies,
                    width="stretch"
                )

                csv_anomalies = anomalies.to_csv(
                    index=False
                )

                st.download_button(
                    "📥 Download Anomaly Report",
                    csv_anomalies,
                    "anomaly_report.csv",
                    "text/csv"
                )

            st.info(
                """
                **Interpretation:** An anomaly is a transaction with
                an unusual combination of observed commercial variables.
                It should be investigated further rather than automatically
                treated as an error or fraud.
                """
            )

    # ========================================================
    # TAB 2 — CUSTOMER RISK
    # ========================================================

    with tab2:

        st.subheader(
            "👥 Customer Risk Scoring"
        )

        st.write(
            """
            Customers are evaluated using Recency, Frequency and
            Monetary behavior. Customers with weaker recent activity
            receive higher commercial risk scores.
            """
        )

        customer_column = "doctor_id"

        if customer_column not in filtered_df.columns:

            st.warning(
                "Customer identifier 'doctor_id' is required "
                "for customer risk analysis."
            )

        elif filtered_df.empty:

            st.warning(
                "No records available for customer analysis."
            )

        else:

            analysis_date = (
                filtered_df["date"].max()
                + timedelta(days=1)
            )

            customer_rfm = (
                filtered_df
                .groupby(customer_column)
                .agg(
                    recency=(
                        "date",
                        lambda x:
                        (analysis_date - x.max()).days
                    ),
                    frequency=(
                        "transaction_id",
                        "nunique"
                    ) if "transaction_id"
                    in filtered_df.columns
                    else (
                        "date",
                        "count"
                    ),
                    monetary=(
                        "revenue",
                        "sum"
                    )
                )
                .reset_index()
            )

            # ------------------------------------------------
            # RISK COMPONENTS
            # ------------------------------------------------

            customer_rfm["recency_risk"] = (
                customer_rfm["recency"]
                .rank(
                    pct=True
                )
            )

            customer_rfm["frequency_risk"] = (
                1
                -
                customer_rfm["frequency"]
                .rank(
                    pct=True
                )
            )

            customer_rfm["monetary_risk"] = (
                1
                -
                customer_rfm["monetary"]
                .rank(
                    pct=True
                )
            )

            # ------------------------------------------------
            # FINAL RISK SCORE
            # ------------------------------------------------

            customer_rfm["risk_score"] = (
                0.40
                * customer_rfm["recency_risk"]
                +
                0.30
                * customer_rfm["frequency_risk"]
                +
                0.30
                * customer_rfm["monetary_risk"]
            ) * 100

            customer_rfm["risk_level"] = pd.cut(
                customer_rfm["risk_score"],
                bins=[
                    -np.inf,
                    33,
                    66,
                    np.inf
                ],
                labels=[
                    "Low",
                    "Medium",
                    "High"
                ]
            )

            # ------------------------------------------------
            # KPI
            # ------------------------------------------------

            high_risk = (
                customer_rfm["risk_level"]
                == "High"
            ).sum()

            medium_risk = (
                customer_rfm["risk_level"]
                == "Medium"
            ).sum()

            low_risk = (
                customer_rfm["risk_level"]
                == "Low"
            ).sum()

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Customers",
                f"{len(customer_rfm):,}"
            )

            c2.metric(
                "High Risk",
                f"{high_risk:,}"
            )

            c3.metric(
                "Medium Risk",
                f"{medium_risk:,}"
            )

            c4.metric(
                "Low Risk",
                f"{low_risk:,}"
            )

            st.divider()

            # ------------------------------------------------
            # RISK DISTRIBUTION
            # ------------------------------------------------

            risk_distribution = (
                customer_rfm
                ["risk_level"]
                .value_counts()
                .reset_index()
            )

            risk_distribution.columns = [
                "risk_level",
                "customers"
            ]

            fig_risk = px.bar(
                risk_distribution,
                x="risk_level",
                y="customers",
                title="Customer Risk Distribution",
                category_orders={
                    "risk_level": [
                        "Low",
                        "Medium",
                        "High"
                    ]
                }
            )

            st.plotly_chart(
                fig_risk,
                width="stretch"
            )

            # ------------------------------------------------
            # CUSTOMER RISK TABLE
            # ------------------------------------------------

            st.subheader(
                "Customer Risk Assessment"
            )

            risk_table = customer_rfm.sort_values(
                "risk_score",
                ascending=False
            )

            st.dataframe(
                risk_table,
                width="stretch"
            )

            csv_risk = risk_table.to_csv(
                index=False
            )

            st.download_button(
                "📥 Download Customer Risk Report",
                csv_risk,
                "customer_risk_report.csv",
                "text/csv"
            )

            # ------------------------------------------------
            # HIGH VALUE / HIGH RISK CUSTOMERS
            # ------------------------------------------------

            high_value_threshold = (
                customer_rfm["monetary"]
                .quantile(0.75)
            )

            high_value_risk = customer_rfm[
                (
                    customer_rfm["monetary"]
                    >= high_value_threshold
                )
                &
                (
                    customer_rfm["risk_level"]
                    == "High"
                )
            ]

            st.subheader(
                "⚠️ High-Value Customers Requiring Attention"
            )

            if high_value_risk.empty:

                st.success(
                    "No high-value customers currently fall "
                    "into the high-risk category."
                )

            else:

                st.warning(
                    f"{len(high_value_risk)} high-value customers "
                    "show elevated commercial risk."
                )

                st.dataframe(
                    high_value_risk.sort_values(
                        "monetary",
                        ascending=False
                    ),
                    width="stretch"
                )

    # ========================================================
    # TAB 3 — STATISTICAL TESTING
    # ========================================================

    with tab3:

        st.subheader(
            "🧪 Promotion vs Revenue Statistical Analysis"
        )

        st.write(
            """
            This analysis compares revenue during relatively
            high-promotion and low-promotion periods using Welch's
            independent two-sample t-test.
            """
        )

        required_columns = [
            "revenue",
            "promotion_spend",
            "date"
        ]

        if not all(
            column in filtered_df.columns
            for column in required_columns
        ):

            st.warning(
                "Revenue, promotion_spend and date columns "
                "are required."
            )

        else:

            # ------------------------------------------------
            # MONTHLY AGGREGATION
            # ------------------------------------------------

            monthly_promo = (
                filtered_df
                .assign(
                    month=filtered_df["date"]
                    .dt
                    .to_period("M")
                )
                .groupby("month")
                .agg(
                    revenue=("revenue", "sum"),
                    promotion_spend=(
                        "promotion_spend",
                        "sum"
                    )
                )
                .reset_index()
            )

            if len(monthly_promo) < 4:

                st.warning(
                    "At least four months of data are recommended "
                    "for this analysis."
                )

            else:

                # ------------------------------------------------
                # SPLIT AT MEDIAN
                # ------------------------------------------------

                promotion_median = (
                    monthly_promo[
                        "promotion_spend"
                    ].median()
                )

                high_promotion = monthly_promo[
                    monthly_promo[
                        "promotion_spend"
                    ]
                    >= promotion_median
                ]["revenue"]

                low_promotion = monthly_promo[
                    monthly_promo[
                        "promotion_spend"
                    ]
                    < promotion_median
                ]["revenue"]

                # ------------------------------------------------
                # T-TEST
                # ------------------------------------------------

                statistic, p_value = ttest_ind(
                    high_promotion,
                    low_promotion,
                    equal_var=False
                )

                high_mean = (
                    high_promotion.mean()
                )

                low_mean = (
                    low_promotion.mean()
                )

                revenue_difference = (
                    high_mean - low_mean
                )

                percentage_difference = (
                    revenue_difference
                    /
                    low_mean
                    *
                    100
                    if low_mean != 0
                    else 0
                )

                # ------------------------------------------------
                # RESULTS
                # ------------------------------------------------

                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "High-Promotion Revenue",
                    f"₹{high_mean:,.0f}"
                )

                c2.metric(
                    "Low-Promotion Revenue",
                    f"₹{low_mean:,.0f}"
                )

                c3.metric(
                    "Revenue Difference",
                    f"₹{revenue_difference:,.0f}"
                )

                c4.metric(
                    "p-value",
                    f"{p_value:.4f}"
                )

                st.divider()

                # ------------------------------------------------
                # HYPOTHESIS
                # ------------------------------------------------

                st.markdown(
                    """
                    ### Hypotheses

                    **H₀:** Mean revenue is the same during
                    high-promotion and low-promotion periods.

                    **H₁:** Mean revenue differs between
                    high-promotion and low-promotion periods.
                    """
                )

                if p_value < 0.05:

                    st.success(
                        f"""
                        The test produced a p-value of
                        **{p_value:.4f}**, which is below the
                        0.05 significance level.

                        The sample provides statistical evidence
                        of a difference in mean revenue between
                        the two promotion groups.
                        """
                    )

                else:

                    st.info(
                        f"""
                        The test produced a p-value of
                        **{p_value:.4f}**, which is not below the
                        0.05 significance level.

                        The sample does not provide sufficient
                        statistical evidence of a difference in
                        mean revenue between the two groups.
                        """
                    )

                # ------------------------------------------------
                # VISUALIZATION
                # ------------------------------------------------

                monthly_promo["promotion_group"] = np.where(
                    monthly_promo[
                        "promotion_spend"
                    ]
                    >= promotion_median,
                    "High Promotion",
                    "Low Promotion"
                )

                fig_promo = px.box(
                    monthly_promo,
                    x="promotion_group",
                    y="revenue",
                    points="all",
                    title="Revenue Distribution by Promotion Level"
                )

                st.plotly_chart(
                    fig_promo,
                    width="stretch"
                )

                # ------------------------------------------------
                # IMPORTANT INTERPRETATION
                # ------------------------------------------------

                st.warning(
                    """
                    **Important:** A statistical difference does
                    not by itself prove that promotion spending
                    caused the revenue difference. Other factors
                    such as seasonality, product mix, territory
                    performance and market conditions may also
                    influence revenue.
                    """
                )

                # ------------------------------------------------
                # MONTHLY DATA
                # ------------------------------------------------

                st.subheader(
                    "Monthly Promotion Analysis"
                )

                display_monthly = monthly_promo.copy()

                display_monthly["month"] = (
                    display_monthly["month"]
                    .astype(str)
                )

                st.dataframe(
                    display_monthly,
                    width="stretch"
                )
                
# ============================================================
# PAGE 4 — DATA EXPLORER
# ============================================================

elif page == "Data Explorer":

    st.header(
        "Data Explorer"
    )


    # --------------------------------------------------------
    # DATA QUALITY
    # --------------------------------------------------------

    st.subheader(
        "🔎 Data Quality Monitor"
    )


    total_rows = len(
        filtered_df
    )


    missing_values = (
        filtered_df.isna()
        .sum()
        .sum()
    )


    duplicate_rows = (
        filtered_df.duplicated()
        .sum()
    )


    invalid_revenue = 0

    if "revenue" in filtered_df.columns:

        invalid_revenue = (
            filtered_df["revenue"] < 0
        ).sum()


    quality_col1, quality_col2, quality_col3, quality_col4 = (
        st.columns(4)
    )


    quality_col1.metric(
        "Records",
        f"{total_rows:,}"
    )


    quality_col2.metric(
        "Missing Values",
        f"{missing_values:,}"
    )


    quality_col3.metric(
        "Duplicate Rows",
        f"{duplicate_rows:,}"
    )


    quality_col4.metric(
        "Negative Revenue",
        f"{invalid_revenue:,}"
    )


    st.divider()


    # --------------------------------------------------------
    # DATA TABLE
    # --------------------------------------------------------

    st.subheader(
        "Filtered Dataset"
    )


    st.write(
        f"Showing **{len(filtered_df):,}** records."
    )


    st.dataframe(
        filtered_df,
        width="stretch",
        height=600
    )


    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    csv = filtered_df.to_csv(
        index=False
    )


    st.download_button(
        label="📥 Download Filtered Data",
        data=csv,
        file_name=(
            "filtered_pharmaceutical_sales.csv"
        ),
        mime="text/csv",
        width="stretch"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Pharmaceutical Commercial Analytics | "
    "Python • SQL • Statistics • Plotly • Streamlit"
)