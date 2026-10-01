import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

DATABASE_PATH = (
    BASE_DIR
    / "database"
    / "pharma_analytics.db"
)

conn = sqlite3.connect(DATABASE_PATH)

query = """
SELECT
    product,
    SUM(revenue) AS total_revenue
FROM sales
GROUP BY product
ORDER BY total_revenue DESC;
"""

cursor = conn.execute(query)

for row in cursor.fetchall():
    print(row)

conn.close()