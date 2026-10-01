import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Load data

sales = pd.read_csv(
    RAW_DIR / "sales_transactions.csv"
)

doctors = pd.read_csv(
    RAW_DIR / "doctors.csv"
)

sales_reps = pd.read_csv(
    RAW_DIR / "sales_reps.csv"
)

# ---------------------------------------------------
# BASIC CHECKS
# ---------------------------------------------------

print("\nSALES DATA")
print(sales.head())

print("\nSHAPE")
print(sales.shape)

print("\nMISSING VALUES")
print(sales.isnull().sum())

print("\nDUPLICATES")
print(sales.duplicated().sum())

# ---------------------------------------------------
# DATE CONVERSION
# ---------------------------------------------------

sales["date"] = pd.to_datetime(
    sales["date"]
)

# ---------------------------------------------------
# REMOVE DUPLICATES
# ---------------------------------------------------

sales = sales.drop_duplicates(
    subset=["transaction_id"]
)

# ---------------------------------------------------
# CREATE TIME FEATURES
# ---------------------------------------------------

sales["year"] = sales["date"].dt.year
sales["month"] = sales["date"].dt.month

sales["month_name"] = sales["date"].dt.month_name()

sales["quarter"] = (
    sales["date"].dt.quarter
)

# ---------------------------------------------------
# TARGET ACHIEVEMENT
# ---------------------------------------------------

sales["target_achievement"] = (
    sales["revenue"] /
    sales["target_sales"]
) * 100

# ---------------------------------------------------
# MERGE DOCTOR INFORMATION
# ---------------------------------------------------

sales = sales.merge(
    doctors,
    on="doctor_id",
    how="left"
)

# ---------------------------------------------------
# MERGE SALES REP INFORMATION
# ---------------------------------------------------

sales = sales.merge(
    sales_reps,
    on="sales_rep_id",
    how="left",
    suffixes=("", "_rep")
)

# ---------------------------------------------------
# SAVE CLEAN DATA
# ---------------------------------------------------

output_file = (
    PROCESSED_DIR /
    "pharmaceutical_sales_clean.csv"
)

sales.to_csv(
    output_file,
    index=False
)

print("\nCleaning completed.")
print(f"Final rows: {len(sales):,}")
print(f"Saved to: {output_file}")