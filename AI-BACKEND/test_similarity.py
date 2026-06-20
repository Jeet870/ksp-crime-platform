# test_similarity.py
import psycopg2
import os
from dotenv import load_dotenv
from mo_similarity import find_similar_firs, find_similar_by_text

load_dotenv()

def get_fir_text(fir_id):
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST","localhost"),
        port=os.getenv("DB_PORT","5432"),
        dbname=os.getenv("DB_NAME","ksp_crime_db"),
        user=os.getenv("DB_USER","postgres"),
        password=os.getenv("DB_PASSWORD","password"),
        sslmode=os.getenv("DB_SSLMODE","require")
    )
    cur = conn.cursor()
    cur.execute("SELECT fir_number, crime_type, description_text FROM firs WHERE fir_id=%s", (fir_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row

# Test 1: Find similar FIRs for FIR ID 1
print("=== TEST 1: Find similar FIRs for FIR ID 1 ===")
fir = get_fir_text(1)
if fir:
    print(f"Query FIR: {fir[0]} ({fir[1]})")
    print(f"Text: {fir[2][:150]}...")
    similar = find_similar_firs(1, top_k=5)
    print(f"\nTop {len(similar)} similar FIRs:")
    for s in similar:
        print(f"  {s['fir_number']} ({s['crime_type']}) — score: {s['similarity_score']}")
        print(f"    MO: {s['mo_method'][:80]}")

print()

# Test 2: Find similar FIRs using raw text
print("=== TEST 2: Find similar FIRs using raw text ===")
test_text = "Unknown persons entered the house by cutting the rear window grille after disabling the power supply. Gold jewellery worth Rs 50000 was stolen."
print(f"Query text: {test_text}")
similar = find_similar_by_text(test_text, top_k=3)
print(f"\nTop {len(similar)} similar FIRs:")
for s in similar:
    print(f"  {s['fir_number']} ({s['crime_type']}) — score: {s['similarity_score']}")

print("\nTest complete")