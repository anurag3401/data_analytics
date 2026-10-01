import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)

# ---------------------------------------------------
# PROJECT PATH
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------
# MASTER DATA
# ---------------------------------------------------

regions = [
    "North",
    "South",
    "East",
    "West",
    "Central",
    "Northeast",
    "Southeast",
    "Southwest"
]

products = [
    "CardioMax",
    "Diabeta",
    "NeuroCare",
    "Respira",
    "GastroPlus",
    "Dermacure",
    "ImmunoX",
    "PainRelief",
    "RenalPro",
    "OncoSafe"
]

product_price = {
    "CardioMax": 420,
    "Diabeta": 350,
    "NeuroCare": 500,
    "Respira": 280,
    "GastroPlus": 300,
    "Dermacure": 450,
    "ImmunoX": 600,
    "PainRelief": 220,
    "RenalPro": 550,
    "OncoSafe": 750
}

segments = [
    "High Value",
    "Growth",
    "Regular",
    "Low Frequency"
]

specialties = [
    "Cardiology",
    "Diabetology",
    "Neurology",
    "Pulmonology",
    "Gastroenterology",
    "Dermatology",
    "General Medicine",
    "Oncology"
]

# ---------------------------------------------------
# DOCTORS
# ---------------------------------------------------

n_doctors = 2000

doctor_ids = [f"D{str(i).zfill(5)}" for i in range(1, n_doctors + 1)]

doctors = pd.DataFrame({
    "doctor_id": doctor_ids,
    "specialty": np.random.choice(
        specialties,
        n_doctors,
        p=[0.15, 0.15, 0.12, 0.12, 0.10, 0.10, 0.16, 0.10]
    ),
    "region": np.random.choice(regions, n_doctors),
    "customer_segment": np.random.choice(
        segments,
        n_doctors,
        p=[0.20, 0.25, 0.40, 0.15]
    )
})

# ---------------------------------------------------
# SALES REPRESENTATIVES
# ---------------------------------------------------

n_reps = 100

rep_ids = [f"SR{str(i).zfill(3)}" for i in range(1, n_reps + 1)]

sales_reps = pd.DataFrame({
    "sales_rep_id": rep_ids,
    "sales_rep_name": [f"Sales Rep {i}" for i in range(1, n_reps + 1)],
    "region": np.random.choice(regions, n_reps)
})

# ---------------------------------------------------
# SALES TRANSACTIONS
# ---------------------------------------------------

n_transactions = 50000

dates = pd.date_range(
    start="2024-01-01",
    end="2025-12-31",
    freq="D"
)

transaction_dates = np.random.choice(dates, n_transactions)

transaction_doctors = np.random.choice(
    doctor_ids,
    n_transactions
)

transaction_products = np.random.choice(
    products,
    n_transactions
)

transaction_reps = np.random.choice(
    rep_ids,
    n_transactions
)

df = pd.DataFrame({
    "transaction_id": [
        f"T{str(i).zfill(6)}"
        for i in range(1, n_transactions + 1)
    ],
    "date": transaction_dates,
    "doctor_id": transaction_doctors,
    "product": transaction_products,
    "sales_rep_id": transaction_reps
})

# ---------------------------------------------------
# PRODUCT PRICE
# ---------------------------------------------------

df["unit_price"] = df["product"].map(product_price)

# ---------------------------------------------------
# PROMOTION SPEND
# ---------------------------------------------------

df["promotion_spend"] = np.random.gamma(
    shape=2,
    scale=500,
    size=n_transactions
)

# ---------------------------------------------------
# PRESCRIPTIONS
# ---------------------------------------------------

base_prescriptions = np.random.poisson(
    lam=8,
    size=n_transactions
)

promotion_effect = (
    1 + df["promotion_spend"] / 10000
)

df["prescriptions"] = np.maximum(
    1,
    (base_prescriptions * promotion_effect).astype(int)
)

# ---------------------------------------------------
# UNITS SOLD
# ---------------------------------------------------

df["units_sold"] = np.maximum(
    1,
    (
        df["prescriptions"] *
        np.random.uniform(0.8, 1.4, n_transactions)
    ).astype(int)
)

# ---------------------------------------------------
# REVENUE
# ---------------------------------------------------

df["revenue"] = (
    df["units_sold"] *
    df["unit_price"]
)

# ---------------------------------------------------
# TARGET
# ---------------------------------------------------

df["target_sales"] = (
    df["revenue"] *
    np.random.uniform(0.9, 1.15, n_transactions)
)

# ---------------------------------------------------
# SAVE FILES
# ---------------------------------------------------

doctors.to_csv(
    RAW_DIR / "doctors.csv",
    index=False
)

sales_reps.to_csv(
    RAW_DIR / "sales_reps.csv",
    index=False
)

df.to_csv(
    RAW_DIR / "sales_transactions.csv",
    index=False
)

print("Data generation completed.")
print(f"Transactions: {len(df):,}")
print(f"Doctors: {len(doctors):,}")
print(f"Sales Representatives: {len(sales_reps):,}")