# 💊 Pharmaceutical Commercial Analytics & Decision Support Dashboard

An end-to-end **Data Analytics and Business Intelligence project** designed to analyze pharmaceutical sales performance, customer behavior, product performance, territory effectiveness, and revenue trends through an interactive Streamlit dashboard.

The project combines **Python, SQL, statistical analysis, machine learning, and interactive visualization** to transform raw transactional data into actionable business insights.

---

## 🚀 Live Dashboard

🔗 **Streamlit Dashboard:**
*Add your deployed Streamlit URL here*

🔗 **GitHub Repository:**
https://github.com/anurag3401/data_analytics

---

## 📌 Project Overview

Pharmaceutical organizations generate large volumes of sales and customer data across products, territories, sales representatives, and healthcare professionals.

This project builds an interactive analytics platform that answers questions such as:

* Which products generate the most revenue?
* Which territories are meeting their sales targets?
* Which customer segments generate the highest revenue?
* How is revenue changing over time?
* What is the relationship between promotional spending and revenue?
* Which customers are high-value or potentially at risk?
* Which sales transactions or territories show unusual behavior?
* What could happen to revenue under different business assumptions?
* What does the historical data suggest about future revenue?

The dashboard allows users to dynamically filter the data and immediately recalculate KPIs, visualizations, customer segments, statistical results, and forecasts.

---

# 🛠️ Tech Stack

| Technology       | Purpose                                |
| ---------------- | -------------------------------------- |
| **Python**       | Data processing and analytics          |
| **Pandas**       | Data cleaning and manipulation         |
| **NumPy**        | Numerical computation                  |
| **SQL / SQLite** | Data storage and business analysis     |
| **Scikit-learn** | Regression and predictive modeling     |
| **SciPy**        | Statistical analysis                   |
| **Statsmodels**  | Statistical modeling                   |
| **Plotly**       | Interactive visualizations             |
| **Streamlit**    | Interactive dashboard                  |
| **Git & GitHub** | Version control and project management |

---

# 📊 Dashboard Modules

## 1. Executive Overview

The executive dashboard provides a high-level view of commercial performance.

### KPIs

* Total Revenue
* Revenue Growth
* Target Achievement
* Units Sold
* Prescriptions
* Average Customer Value

### Visualizations

* Monthly Revenue vs Target
* Revenue by Product
* Revenue by Region
* Interactive filtering

---

## 2. Product Analytics

Analyzes the performance of individual pharmaceutical products.

### Metrics

* Product Revenue
* Units Sold
* Prescriptions
* Target Achievement
* Revenue Contribution

Users can compare products and identify major contributors to overall revenue.

---

## 3. Territory Analytics

Evaluates performance across geographical territories.

### Metrics

* Territory Revenue
* Sales Target
* Target Achievement
* Number of Customers
* Prescriptions
* Revenue per Customer

A performance matrix is used to compare territory revenue against target achievement.

---

## 4. Customer Analytics

Customer-level analytics is performed using **RFM Analysis**.

### RFM Framework

**Recency**
How recently a customer made a purchase.

**Frequency**
How frequently the customer purchased.

**Monetary Value**
How much revenue the customer generated.

Customers are classified into segments such as:

* Champions
* Loyal Customers
* Potential Growth
* At Risk
* Low Value

This allows the business to identify high-value and potentially declining customer groups.

---

# 🔬 Statistical Analytics

The project includes statistical and predictive analysis.

### Correlation Analysis

Examines relationships between:

* Revenue
* Promotion Spend
* Units Sold
* Prescriptions

### Multiple Linear Regression

Revenue is modeled using business variables such as:

```text
Revenue =
β₀
+ β₁(Promotion Spend)
+ β₂(Units Sold)
+ β₃(Prescriptions)
+ ε
```

### Model Metrics

* R²
* Mean Absolute Error (MAE)
* Root Mean Squared Error (RMSE)

The dashboard also displays regression coefficients to understand the relationship between explanatory variables and revenue.

> Statistical association is not interpreted as proof of causality.

---

# 🔮 Revenue Forecasting

The dashboard includes a revenue forecasting module.

Historical monthly revenue is used to generate future revenue estimates.

The forecasting module provides:

* Historical revenue
* Forecasted revenue
* Six-month forecast horizon
* Interactive visualization
* Forecast table

The forecasting component is intended as an analytical estimate rather than a guaranteed future outcome.

---

# 🎯 What-If Revenue Simulator

The project includes an interactive scenario analysis tool.

Users can modify:

* Promotion Spend
* Price
* Units Sold

The dashboard immediately recalculates the simulated revenue.

### Example

A user can test:

```text
Promotion Spend: +20%
Price: +5%
Units Sold: +10%
```

and observe the corresponding simulated revenue impact.

This provides an interactive way to explore business scenarios.

> The simulator uses explicit modeling assumptions and should not be interpreted as a causal prediction.

---

# ⚠️ Anomaly Detection

The project is designed to identify unusual sales behavior.

Potential applications include detecting:

* Unusually high-value transactions
* Unusual territory performance
* Unexpected revenue changes
* Potential data-quality issues

This can help analysts investigate areas requiring further attention.

---

# 🧮 SQL Analytics

The project uses **SQLite** as the analytical database.

SQL is used for:

* Product-level aggregation
* Regional performance
* Revenue analysis
* Customer analysis
* Target achievement
* Business KPI calculations

Example:

```sql
SELECT
    product,
    SUM(revenue) AS total_revenue
FROM sales
GROUP BY product
ORDER BY total_revenue DESC;
```

This demonstrates the integration of SQL with Python-based analytics.

---

# 🔄 Data Pipeline

The overall workflow is:

```text
Raw Data
    ↓
Data Cleaning
    ↓
Data Validation
    ↓
SQLite Database
    ↓
SQL Analysis
    ↓
Python Analytics
    ↓
Statistical Modeling
    ↓
Customer Segmentation
    ↓
Forecasting
    ↓
Interactive Streamlit Dashboard
    ↓
Business Insights
```

---

# 📁 Project Structure

```text
data_analytics/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── raw/
│   │   ├── doctors.csv
│   │   ├── sales_reps.csv
│   │   └── sales_transactions.csv
│   │
│   └── processed/
│       └── pharmaceutical_sales_clean.csv
│
├── database/
│   └── pharma_analytics.db
│
├── sql/
│   ├── 01_schema.sql
│   ├── 02_business_analysis.sql
│   └── 03_advanced_analysis.sql
│
└── src/
    ├── generate_data.py
    ├── data_cleaning.py
    ├── database.py
    ├── analysis.py
    ├── rfm.py
    └── anomaly_detection.py
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

```bash
cd data_analytics
```

---

## 2. Create a virtual environment

```bash
python -m venv venv
```

### Windows

```powershell
venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

# ▶️ Running the Project

First create/update the SQLite database:

```bash
python src/database.py
```

Then launch the Streamlit application:

```bash
python -m streamlit run app.py
```

The application will open in your browser.

---

# 📈 Key Analytical Capabilities

The project demonstrates practical experience with:

* Data cleaning
* Exploratory Data Analysis
* SQL querying
* KPI development
* Business performance analysis
* Customer segmentation
* RFM analysis
* Statistical analysis
* Regression modeling
* Revenue forecasting
* Scenario analysis
* Anomaly detection
* Interactive dashboards
* Data visualization
* Data-driven decision support

---

# 💡 Example Business Questions

The dashboard can be used to investigate questions such as:

### Sales

> How has revenue changed over time?

### Products

> Which products contribute the most to total revenue?

### Territories

> Which territories are above or below their sales targets?

### Customers

> Which customer segments generate the highest revenue?

### Marketing

> How is promotional spending associated with revenue?

### Forecasting

> What does the historical revenue trend suggest for upcoming months?

### Scenario Analysis

> How does simulated revenue change under different pricing, promotion, and volume assumptions?

---

# 📊 Business Value

The project demonstrates how raw transactional data can be converted into an interactive analytical system that supports:

* Performance monitoring
* Customer prioritization
* Product analysis
* Territory evaluation
* Revenue planning
* Scenario analysis
* Statistical investigation
* Data-driven decision making

---

# 🔐 Data Disclaimer

The project uses **synthetic/anonymized data for educational and portfolio purposes**.

It does not contain confidential pharmaceutical company data or real patient information.

The analytical results should therefore be interpreted as demonstrations of the methodology rather than real-world pharmaceutical market conclusions.

---

# 👨‍💻 Skills Demonstrated

### Programming

```text
Python
Pandas
NumPy
```

### Analytics

```text
Exploratory Data Analysis
KPI Analysis
Customer Segmentation
RFM Analysis
Statistical Analysis
Regression
Forecasting
Anomaly Detection
```

### Database

```text
SQL
SQLite
Data Aggregation
Business Queries
```

### Visualization

```text
Plotly
Streamlit
Interactive Dashboards
```

### Engineering

```text
Git
GitHub
Virtual Environments
Application Deployment
```

---

# 🚀 Future Improvements

Planned improvements include:

* Advanced time-series forecasting
* Automated anomaly detection
* Additional customer lifetime-value metrics
* Automated insight generation
* More advanced scenario modeling
* Cloud database integration
* Scheduled data refresh
* Role-based dashboard views

---

## ⭐ Project Goal

The goal of this project is to demonstrate an end-to-end **data analytics workflow**, from raw transactional data to SQL analysis, statistical modeling, interactive visualization, and business decision support.

**Python • SQL • Statistics • Machine Learning • Streamlit • Plotly • GitHub**
