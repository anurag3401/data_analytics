import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "pharmaceutical_sales_clean.csv"
)

DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "pharma_analytics.db"


def create_database():

    df = pd.read_csv(DATA_PATH)

    conn = sqlite3.connect(DATABASE_PATH)

    df.to_sql(
        "sales",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print("Database created successfully.")


if __name__ == "__main__":
    create_database()