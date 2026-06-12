"""
load_to_neon.py
---------------
KSP Datathon 2026 – Final data loader for Neon PostgreSQL.

Steps this script performs:
  1. Connects to Neon using credentials from .env
  2. Inserts placeholder officers for every officer_id referenced in the CSV
     (so the foreign-key constraint on firs.filed_by_officer_id is satisfied)
  3. Loads all FIR rows from bangalore_firs_schema_NEW.csv

Safe to re-run – all inserts use ON CONFLICT DO NOTHING.

USAGE
-----
1. Make sure your .env file contains:
       DB_HOST=<your-neon-host>.neon.tech
       DB_PORT=5432
       DB_NAME=<your-db-name>
       DB_USER=<your-db-user>
       DB_PASSWORD=<your-neon-password>

2. Place this script in the same folder as bangalore_firs_schema_NEW.csv

3. Run:
       python load_to_neon.py
"""

import os
import csv
import psycopg2
from dotenv import load_dotenv

# ── Load .env ────────────────────────────────────────────────────────────────
load_dotenv(r"C:\Users\ISHAAN BANSAL\Desktop\ksp-crime-platform\AI-BACKEND\.env")

DB_CONFIG = {
    "host":     os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port":     os.getenv("DB_PORT", "5432"),
    "sslmode":  "require",   # Neon requires SSL
}

CSV_FILE = "bangalore_firs_schema_NEW.csv"

# ── Connect ───────────────────────────────────────────────────────────────────
print("Connecting to Neon PostgreSQL...")
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()
print("✅ Connected!")

# ── Step 1: Read the CSV once to collect all unique officer IDs ───────────────
print(f"Reading {CSV_FILE}...")
rows = []
officer_ids_needed = set()

with open(CSV_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)
        oid = row["filed_by_officer_id"].strip()
        if oid:
            officer_ids_needed.add(int(oid))

print(f"   → {len(rows)} FIR rows found")
print(f"   → {len(officer_ids_needed)} unique officer IDs referenced")

# ── Step 2: Insert placeholder officers for every referenced ID ───────────────
# The officers table has: officer_id (SERIAL PK), name, badge_number (UNIQUE),
# role, district, police_station, password_hash, created_at
#
# We use a placeholder password hash (not real – swap before production).
PLACEHOLDER_HASH = "$2b$12$placeholderhashforseeddataonly000000000000000000000"

print("\nInserting placeholder officers (if not already present)...")
inserted_officers = 0

for oid in sorted(officer_ids_needed):
    cursor.execute("""
        INSERT INTO officers (officer_id, name, badge_number, role, district,
                              police_station, password_hash)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (officer_id) DO NOTHING;
    """, (
        oid,
        f"Officer {oid}",
        f"KSP-{oid:04d}",
        "Sub-Inspector",
        "Bengaluru",
        "Central PS",
        PLACEHOLDER_HASH,
    ))
    inserted_officers += 1

# Reset the officers SERIAL sequence so future inserts don't collide
max_oid = max(officer_ids_needed) if officer_ids_needed else 0
cursor.execute(f"SELECT setval('officers_officer_id_seq', {max_oid}, true);")

conn.commit()
print(f"✅ Officer placeholders ready ({inserted_officers} processed)")

# ── Step 3: Insert FIR rows ───────────────────────────────────────────────────
print("\nInserting FIR rows...")
inserted = 0
skipped = 0

for row in rows:
    officer_id_raw = row["filed_by_officer_id"].strip()
    officer_id = int(officer_id_raw) if officer_id_raw else None

    try:
        cursor.execute("""
            INSERT INTO firs (
                fir_number, date_filed, time_filed, police_station, district,
                crime_type, ipc_sections, location_description,
                latitude, longitude, description_text, status,
                filed_by_officer_id, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (fir_number) DO NOTHING;
        """, (
            row["fir_number"],
            row["date_filed"],
            row["time_filed"] or None,
            row["police_station"],
            row["district"],
            row["crime_type"],
            row["ipc_sections"] or None,
            row["location_description"] or None,
            float(row["latitude"])  if row["latitude"]  else None,
            float(row["longitude"]) if row["longitude"] else None,
            row["description_text"],
            row["status"] or "open",
            officer_id,
            row["created_at"] or None,
        ))

        if cursor.rowcount > 0:
            inserted += 1
        else:
            skipped += 1

    except Exception as e:
        print(f"   ⚠️  Skipped row {row['fir_number']}: {e}")
        conn.rollback()
        # Re-open transaction after rollback
        cursor = conn.cursor()

conn.commit()
print(f"✅ FIRs inserted: {inserted}  |  already existed (skipped): {skipped}")

# ── Step 4: Quick verification ────────────────────────────────────────────────
print("\nVerification counts:")
for table in ["officers", "firs"]:
    cursor.execute(f"SELECT COUNT(*) FROM {table};")
    count = cursor.fetchone()[0]
    print(f"   {table}: {count} rows")

cursor.close()
conn.close()
print("\n✅ All done! Your Neon database is loaded and ready.")
