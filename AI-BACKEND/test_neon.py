import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
print("HOST:", os.getenv("DB_HOST"))

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require",
        connect_timeout=15
    )
    print("CONNECTED SUCCESSFULLY")
    conn.close()
except Exception as e:
    print("FAILED:", e)