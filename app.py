import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

from pathlib import Path
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


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
# PROJECT PATH
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
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 16px;
        opacity: 0.7;
        margin-bottom: 25px;
    }

    .metric-card {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(128,128,128,0.25);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    conn = sqlite3.connect(DATABASE_PATH)

    query = """
        SELECT *
        FROM sales
    """

    data = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    data["date"] = pd.to_datetime(
        data["date"]
    )

    return data


df = load_data()


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="main-title">💊 Pharmaceutical Commercial Analytics</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    Interactive sales, customer, territory, product and statistical
    analytics platform
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Analysis",
    [
        "Executive Overview",
        "Product Analytics",
        "Territory Analytics",
        "Customer Analytics",
        "What-If Simulator",
        "Statistical Analytics",
        "Forecasting",
        "Data Explorer"
    ]
)


# ============================================================
# GLOBAL FILTERS
# ============================================================

st.sidebar.divider()

st.sidebar.subheader("Global Filters")


regions = st.sidebar.multiselect(
    "Region",
    sorted(df["region"].unique()),
    default=sorted(df["region"].unique())
)

products = st.sidebar.multiselect(
    "Product",
    sorted(df["product"].unique()),
    default=sorted(df["product"].unique())
)

segments = st.sidebar.multiselect(
    "Customer Segment",
    sorted(df["customer_segment"].unique()),
    default=sorted(df["customer_segment"].unique())
)


filtered_df = df[
    df["region"].isin(regions)
    &
    df["product"].isin(products)
    &
    df["customer_segment"].isin(segments)
].copy()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_growth(data):

    monthly = (
        data
        .groupby(
            data["date"].dt.to_period("M")
        )["revenue"]
        .sum()
    )

    if len(monthly) < 2:
        return 0

    current = monthly.iloc[-1]
    previous = monthly.iloc[-2]

    if previous == 0:
        return 0

    return (
        (current - previous)
        / previous
    ) * 100


def calculate_target_achievement(data):

    target = data["target_sales"].sum()

    if target == 0:
        return 0

    return (
        data["revenue"].sum()
        /
        target
    ) * 100


# ============================================================
# PAGE 1 — EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":

    st.header("Executive Overview")

    total_revenue = filtered_df["revenue"].sum()

    total_units = filtered_df["units_sold"].sum()

    total_prescriptions = (
        filtered_df["prescriptions"].sum()
    )

    achievement = calculate_target_achievement(
        filtered_df
    )

    growth = calculate_growth(
        filtered_df
    )

    customers = filtered_df["doctor_id"].nunique()

    avg_customer_value = (
        total_revenue / customers
        if customers > 0
        else 0
    )


    # --------------------------------------------------------
    # KPI ROW
    # --------------------------------------------------------

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(
        "Revenue",
        f"₹{total_revenue:,.0f}"
    )

    c2.metric(
        "Revenue Growth",
        f"{growth:.2f}%"
    )

    c3.metric(
        "Target Achievement",
        f"{achievement:.2f}%"
    )

    c4.metric(
        "Units Sold",
        f"{total_units:,.0f}"
    )

    c5.metric(
        "Prescriptions",
        f"{total_prescriptions:,.0f}"
    )

    c6.metric(
        "Avg Customer Value",
        f"₹{avg_customer_value:,.0f}"
    )


    st.divider()


    # --------------------------------------------------------
    # MONTHLY TREND
    # --------------------------------------------------------

    monthly = (
        filtered_df
        .groupby(
            filtered_df["date"].dt.to_period("M")
        )
        .agg(
            revenue=("revenue", "sum"),
            target=("target_sales", "sum")
        )
        .reset_index()
    )

    monthly["date"] = (
        monthly["date"].astype(str)
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
        title="Revenue vs Target",
        xaxis_title="Month",
        yaxis_title="Revenue",
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


    # --------------------------------------------------------
    # PRODUCT + REGION
    # --------------------------------------------------------

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


# ============================================================
# PAGE 2 — PRODUCT ANALYTICS
# ============================================================

elif page == "Product Analytics":

    st.header("Product Analytics")

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

    product["achievement"] = (
        product["revenue"]
        /
        product["target"]
    ) * 100

    product["contribution"] = (
        product["revenue"]
        /
        product["revenue"].sum()
    ) * 100


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
            title="Product Revenue"
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

        fig.update_layout(
            yaxis_title="Achievement (%)"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )


# ============================================================
# PAGE 3 — TERRITORY ANALYTICS
# ============================================================

elif page == "Territory Analytics":

    st.header("Territory Performance")

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

    territory["achievement"] = (
        territory["revenue"]
        /
        territory["target"]
    ) * 100

    territory["revenue_per_customer"] = (
        territory["revenue"]
        /
        territory["customers"]
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


# ============================================================
# PAGE 4 — CUSTOMER ANALYTICS
# ============================================================

elif page == "Customer Analytics":

    st.header("Customer Analytics")

    customer = (
        filtered_df
        .groupby("doctor_id")
        .agg(
            last_purchase=("date", "max"),
            frequency=("transaction_id", "count"),
            monetary=("revenue", "sum"),
            prescriptions=("prescriptions", "sum")
        )
        .reset_index()
    )

    reference_date = filtered_df["date"].max()

    customer["recency"] = (
        reference_date
        -
        customer["last_purchase"]
    ).dt.days


    # --------------------------------------------------------
    # RFM SCORE
    # --------------------------------------------------------

    customer["R_score"] = pd.qcut(
        customer["recency"].rank(
            method="first"
        ),
        5,
        labels=[5, 4, 3, 2, 1]
    ).astype(int)

    customer["F_score"] = pd.qcut(
        customer["frequency"].rank(
            method="first"
        ),
        5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    customer["M_score"] = pd.qcut(
        customer["monetary"].rank(
            method="first"
        ),
        5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)


    customer["RFM_score"] = (
        customer["R_score"]
        +
        customer["F_score"]
        +
        customer["M_score"]
    )


    def segment_customer(score):

        if score >= 13:
            return "Champions"

        elif score >= 10:
            return "Loyal Customers"

        elif score >= 7:
            return "Potential Growth"

        elif score >= 5:
            return "At Risk"

        else:
            return "Low Value"


    customer["RFM_segment"] = (
        customer["RFM_score"]
        .apply(segment_customer)
    )


    # --------------------------------------------------------
    # RFM VISUAL
    # --------------------------------------------------------

    segment_summary = (
        customer
        .groupby("RFM_segment")
        .agg(
            customers=("doctor_id", "count"),
            revenue=("monetary", "sum")
        )
        .reset_index()
    )


    col1, col2 = st.columns(2)


    with col1:

        fig = px.bar(
            segment_summary,
            x="RFM_segment",
            y="customers",
            title="Customers by RFM Segment"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )


    with col2:

        fig = px.pie(
            segment_summary,
            names="RFM_segment",
            values="revenue",
            title="Revenue Contribution by RFM Segment"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )


    st.subheader("Customer Segmentation")

    st.dataframe(
        customer.sort_values(
            "monetary",
            ascending=False
        ),
        width="stretch"
    )


# ============================================================
# PAGE 5 — WHAT IF SIMULATOR
# ============================================================

elif page == "What-If Simulator":

    st.header("What-If Revenue Simulator")

    st.write(
        """
        Adjust the assumptions below to simulate potential
        revenue changes.
        """
    )


    promotion_change = st.slider(
        "Promotion Spend Change (%)",
        -50,
        100,
        10
    )


    price_change = st.slider(
        "Price Change (%)",
        -20,
        30,
        0
    )


    unit_change = st.slider(
        "Units Sold Change (%)",
        -30,
        50,
        5
    )


    base_revenue = (
        filtered_df["revenue"].sum()
    )


    # Assumption:
    # revenue changes proportionally with price and units,
    # while promotion has a smaller assumed elasticity.

    promotion_effect = (
        1 +
        (promotion_change / 100) * 0.20
    )

    price_effect = (
        1 +
        price_change / 100
    )

    unit_effect = (
        1 +
        unit_change / 100
    )


    simulated_revenue = (
        base_revenue
        *
        promotion_effect
        *
        price_effect
        *
        unit_effect
    )


    revenue_change = (
        simulated_revenue
        -
        base_revenue
    )


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "Current Revenue",
        f"₹{base_revenue:,.0f}"
    )

    col2.metric(
        "Simulated Revenue",
        f"₹{simulated_revenue:,.0f}"
    )

    col3.metric(
        "Revenue Impact",
        f"₹{revenue_change:,.0f}",
        delta=f"{revenue_change / base_revenue:.2%}"
    )


    st.info(
        """
        This is a scenario simulation, not a causal forecast.
        The promotion effect is an explicit modeling assumption.
        """
    )


# ============================================================
# PAGE 6 — STATISTICAL ANALYTICS
# ============================================================

elif page == "Statistical Analytics":

    st.header("Statistical Analytics")

    analysis_df = (
        filtered_df
        .groupby(
            filtered_df["date"].dt.to_period("M")
        )
        .agg(
            revenue=("revenue", "sum"),
            promotion_spend=("promotion_spend", "sum"),
            units=("units_sold", "sum"),
            prescriptions=("prescriptions", "sum")
        )
        .reset_index()
    )


    # --------------------------------------------------------
    # CORRELATION
    # --------------------------------------------------------

    correlation = (
        analysis_df[
            [
                "revenue",
                "promotion_spend",
                "units",
                "prescriptions"
            ]
        ]
        .corr()
    )


    st.subheader("Correlation Matrix")

    st.dataframe(
        correlation,
        width="stretch"
    )


    # --------------------------------------------------------
    # REGRESSION
    # --------------------------------------------------------

    X = analysis_df[
        [
            "promotion_spend",
            "units",
            "prescriptions"
        ]
    ]

    y = analysis_df["revenue"]


    model = LinearRegression()

    model.fit(
        X,
        y
    )


    predictions = model.predict(X)


    r2 = model.score(
        X,
        y
    )


    mae = mean_absolute_error(
        y,
        predictions
    )


    rmse = np.sqrt(
        mean_squared_error(
            y,
            predictions
        )
    )


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "R²",
        f"{r2:.3f}"
    )

    col2.metric(
        "MAE",
        f"₹{mae:,.0f}"
    )

    col3.metric(
        "RMSE",
        f"₹{rmse:,.0f}"
    )


    coefficients = pd.DataFrame(
        {
            "Variable": X.columns,
            "Coefficient": model.coef_
        }
    )


    st.subheader(
        "Regression Coefficients"
    )

    st.dataframe(
        coefficients,
        width="stretch"
    )


    # --------------------------------------------------------
    # PROMOTION SIGNIFICANCE
    # --------------------------------------------------------

    t_stat, p_value = stats.ttest_ind(
        analysis_df["revenue"],
        analysis_df["promotion_spend"],
        equal_var=False
    )


    st.subheader(
        "Statistical Test"
    )

    st.write(
        f"Test statistic: **{t_stat:.3f}**"
    )

    st.write(
        f"P-value: **{p_value:.5f}**"
    )

    st.caption(
        """
        Statistical significance should not be interpreted as
        proof of causality.
        """
    )


    # --------------------------------------------------------
    # SCATTER
    # --------------------------------------------------------

    fig = px.scatter(
        analysis_df,
        x="promotion_spend",
        y="revenue",
        trendline="ols",
        title="Monthly Promotion Spend vs Revenue"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# ============================================================
# PAGE 7 — FORECASTING
# ============================================================

elif page == "Forecasting":

    st.header("Revenue Forecasting")

    monthly = (
        filtered_df
        .groupby(
            filtered_df["date"].dt.to_period("M")
        )["revenue"]
        .sum()
        .reset_index()
    )

    monthly["month_number"] = (
        np.arange(len(monthly))
    )


    if len(monthly) >= 6:

        X = monthly[
            ["month_number"]
        ]

        y = monthly[
            "revenue"
        ]


        model = LinearRegression()

        model.fit(
            X,
            y
        )


        future_numbers = np.arange(
            len(monthly),
            len(monthly) + 6
        )


        future_predictions = model.predict(
            future_numbers.reshape(-1, 1)
        )


        last_period = monthly["date"].iloc[-1]

        future_dates = pd.period_range(
            start=last_period + 1,
            periods=6,
            freq="M"
        )


        forecast = pd.DataFrame(
            {
                "date": future_dates.astype(str),
                "revenue": future_predictions,
                "type": "Forecast"
            }
        )


        historical = monthly[
            ["date", "revenue"]
        ].copy()

        historical["date"] = (
            historical["date"].astype(str)
        )

        historical["type"] = "Historical"


        combined = pd.concat(
            [
                historical,
                forecast
            ]
        )


        fig = px.line(
            combined,
            x="date",
            y="revenue",
            color="type",
            markers=True,
            title="Historical Revenue and 6-Month Forecast"
        )


        st.plotly_chart(
            fig,
            width="stretch"
        )


        st.subheader(
            "Forecast Values"
        )

        st.dataframe(
            forecast,
            width="stretch"
        )


    else:

        st.warning(
            "At least 6 months of data are required."
        )


# ============================================================
# PAGE 8 — DATA EXPLORER
# ============================================================

elif page == "Data Explorer":

    st.header("Data Explorer")

    st.write(
        f"Showing {len(filtered_df):,} records."
    )


    st.dataframe(
        filtered_df,
        width="stretch",
        height=600
    )


    csv = filtered_df.to_csv(
        index=False
    )


    st.download_button(
        label="Download Filtered Data",
        data=csv,
        file_name="filtered_pharmaceutical_sales.csv",
        mime="text/csv"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Pharmaceutical Commercial Analytics | "
    "Python • SQL • Statistics • Streamlit • Plotly"
)