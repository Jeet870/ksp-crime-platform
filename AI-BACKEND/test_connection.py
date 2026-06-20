import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

print("Connecting with these details:")
print(f"  HOST: {os.getenv('DB_HOST')}")
print(f"  PORT: {os.getenv('DB_PORT')}")
print(f"  NAME: {os.getenv('DB_NAME')}")
print(f"  USER: {os.getenv('DB_USER')}")
print(f"  SSL:  {os.getenv('DB_SSLMODE')}")

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode=os.getenv("DB_SSLMODE", "require")
    )
    print("\nConnection SUCCESS")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM officers")
    print(f"Officers table has: {cur.fetchone()[0]} rows")
    cur.close()
    conn.close()
except Exception as e:
    print(f"\nConnection FAILED: {e}")