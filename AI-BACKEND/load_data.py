import csv
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode=os.getenv("DB_SSLMODE", "require"),
        connect_timeout=30,
        keepalives=1,
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=5,
    )

def load(csv_file, table, columns, types=None):
    # Fresh connection for every table
    conn = get_conn()
    cur  = conn.cursor()

    path = f"data/{csv_file}"
    if not os.path.exists(path):
        print(f"  MISSING: {path}")
        cur.close(); conn.close()
        return

    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print(f"  EMPTY: {csv_file}")
        cur.close(); conn.close()
        return

    col_str = ", ".join(columns)
    phs     = ", ".join(["%s"] * len(columns))
    sql     = f"INSERT INTO {table} ({col_str}) VALUES ({phs}) ON CONFLICT DO NOTHING"

    data = []
    for row in rows:
        record = []
        for col in columns:
            val = row.get(col, None)
            if val == "" or val is None:
                val = None
            elif types and col in types:
                try:
                    val = types[col](val)
                except:
                    val = None
            record.append(val)
        data.append(tuple(record))

    # Insert in small batches of 50 to avoid timeout
    batch_size = 50
    total = 0
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        try:
            cur.executemany(sql, batch)
            conn.commit()
            total += len(batch)
        except Exception as e:
            conn.rollback()
            print(f"  ERROR in batch {i}-{i+batch_size}: {e}")
            # Reconnect and continue
            cur.close(); conn.close()
            conn = get_conn(); cur = conn.cursor()

    cur.close(); conn.close()
    print(f"  Loaded {total} rows into {table}")


print("Loading all tables...\n")

load("accused.csv", "accused",
     ["accused_id","name","alias","age","gender","address",
      "phone_number","aadhaar_last4","prior_cases_count","district"],
     {"accused_id":int,"age":int,"prior_cases_count":int})

load("firs.csv", "firs",
     ["fir_id","fir_number","date_filed","time_filed","police_station",
      "district","crime_type","ipc_sections","location_description",
      "latitude","longitude","description_text","status"],
     {"fir_id":int,"latitude":float,"longitude":float})

load("fir_accused.csv", "fir_accused",
     ["fir_id","accused_id","role_in_case","arrest_status"],
     {"fir_id":int,"accused_id":int})

load("victims.csv", "victims",
     ["victim_id","fir_id","name","age","gender","address",
      "phone_number","injury_details"],
     {"victim_id":int,"fir_id":int,"age":int})

load("vehicles.csv", "vehicles",
     ["vehicle_id","registration_number","vehicle_type","make_model",
      "color","owner_accused_id","fir_id"],
     {"vehicle_id":int,"owner_accused_id":int,"fir_id":int})

load("bank_transactions.csv", "bank_transactions",
     ["transaction_id","account_number","accused_id","amount",
      "transaction_date","transaction_type","counterparty_account",
      "flagged","flag_reason"],
     {"transaction_id":int,"accused_id":int,"amount":float,
      "flagged":lambda x: x.lower()=="true"})

# Verification
print("\nVerification:")
conn = get_conn(); cur = conn.cursor()
for table in ["officers","firs","accused","fir_accused","victims","vehicles","bank_transactions"]:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"  {table:<22} {cur.fetchone()[0]} rows")
cur.close(); conn.close()
print("\nAll done.")