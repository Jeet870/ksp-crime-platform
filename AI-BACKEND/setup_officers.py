import os
import psycopg2
from dotenv import load_dotenv
from auth import hash_password

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    sslmode=os.getenv("DB_SSLMODE", "require")
)
cur = conn.cursor()

OFFICERS = [
    ("KSP-CON-001", "Constable Ramesh",   "constable",            "Bengaluru South", "Koramangala PS"),
    ("KSP-IO-001",  "IO Priya Sharma",    "investigating_officer", "Bengaluru South", "BTM Layout PS"),
    ("KSP-SP-001",  "SP Venkatesh",       "district_sp",          "Bengaluru South", None),
    ("KSP-ANA-001", "Analyst Deepa",      "scrb_analyst",         "Bengaluru South", None),
    ("KSP-DIR-001", "Director Krishnan",  "scrb_director",        "Bengaluru South", None),
]

for badge, name, role, district, ps in OFFICERS:
    cur.execute("""
        INSERT INTO officers (name, badge_number, role, district, police_station, password_hash)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (badge_number) DO NOTHING
    """, (name, badge, role, district, ps, hash_password("ksp1234")))
    print(f"  Created: {badge} | {name} | {role}")

conn.commit()
cur.close()
conn.close()
print("\nAll 5 officers created. Password for all accounts: ksp1234")