import os
import psycopg2
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain):
    return pwd.hash(plain)

conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_NAME", "ksp_crime_db"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "password")
)
cur = conn.cursor()

OFFICERS = [
    ("KSP-CON-001", "Constable Ramesh",  "constable",             "Bengaluru Urban", "Koramangala PS"),
    ("KSP-IO-001",  "IO Priya Sharma",   "investigating_officer",  "Bengaluru Urban", "BTM Layout PS"),
    ("KSP-SP-001",  "SP Venkatesh",      "district_sp",           "Bengaluru Urban", None),
    ("KSP-ANA-001", "Analyst Deepa",     "scrb_analyst",          "Bengaluru Urban", None),
    ("KSP-DIR-001", "Director Krishnan", "scrb_director",         "Bengaluru Urban", None),
]

for badge, name, role, district, ps in OFFICERS:
    cur.execute("""
        INSERT INTO officers (name, badge_number, role, district, police_station, password_hash)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (badge_number) DO NOTHING
    """, (name, badge, role, district, ps, hash_password("ksp1234")))

conn.commit()
cur.close()
conn.close()
print("Officers created successfully. Password for all: ksp1234")
for badge, name, role, *_ in OFFICERS:
    print(f"  {badge} | {role}")