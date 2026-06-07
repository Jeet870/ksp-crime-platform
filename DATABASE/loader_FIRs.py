import psycopg2
import csv

# ✅ Change these if your setup is different
DB_CONFIG = {
    "host": "localhost",
    "database": "ksp_datathon",
    "user": "postgres",
    "password": "Jeet",  # ← put your PostgreSQL password here
    "port": "5432"
}

# Step 1: Connect to PostgreSQL
print("Connecting to PostgreSQL...")
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()
print("✅ Connected!")

# Step 2: Create the table
print("Creating table...")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS firs (
        id SERIAL PRIMARY KEY,
        fir_number VARCHAR(50),
        date DATE,
        location VARCHAR(100),
        crime_type VARCHAR(100),
        complainant_name VARCHAR(100),
        complainant_phone VARCHAR(50),
        officer_name VARCHAR(100),
        description TEXT
    );
""")
conn.commit()
print("✅ Table created!")

# Step 3: Read CSV and insert rows
print("Inserting rows from CSV...")
with open("bangalore_firs.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    count = 0
    for row in reader:
        cursor.execute("""
            INSERT INTO firs (fir_number, date, location, crime_type,
                              complainant_name, complainant_phone,
                              officer_name, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row["FIR_Number"],
            row["Date"],
            row["Location"],
            row["Crime_Type"],
            row["Complainant_Name"],
            row["Complainant_Phone"],
            row["Officer_Name"],
            row["Description"]
        ))
        count += 1

conn.commit()
print(f"✅ {count} rows inserted successfully!")

cursor.close()
conn.close()
print("✅ Done! Database connection closed.")