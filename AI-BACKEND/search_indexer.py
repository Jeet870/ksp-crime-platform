# search_indexer.py
# Indexes all FIRs into Meilisearch for full-text search

import os
import psycopg2
import meilisearch
from dotenv import load_dotenv

load_dotenv(r"C:\ksp-crime-platform\AI-BACKEND\.env")

MEILI_KEY = os.getenv("MEILI_MASTER_KEY")
ms = meilisearch.Client("http://localhost:7700", MEILI_KEY)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode=os.getenv("DB_SSLMODE")
    )


def index_all_firs():
    """Reads all FIRs from PostgreSQL and indexes them in Meilisearch."""
    conn = get_db_connection()
    cur  = conn.cursor()

    cur.execute("""
        SELECT fir_id, fir_number, date_filed, police_station,
               district, crime_type, location_description,
               description_text, status
        FROM firs
        ORDER BY fir_id
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    documents = []
    for row in rows:
        fir_id, fir_number, date_filed, ps, district, crime_type, location, desc, status = row
        documents.append({
            "id":          fir_id,
            "fir_id":      fir_id,
            "fir_number":  fir_number,
            "date_filed":  str(date_filed),
            "police_station": ps,
            "district":    district,
            "crime_type":  crime_type,
            "location":    location or "",
            "description": desc or "",
            "status":      status or "open",
        })

    index = ms.index("firs")

    index.update_searchable_attributes([
        "description", "crime_type", "location",
        "fir_number", "police_station"
    ])

    index.update_filterable_attributes(["district", "crime_type", "status"])

    batch_size = 50
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        index.add_documents(batch, primary_key="id")
        print(f"  Indexed {min(i+batch_size, len(documents))}/{len(documents)} FIRs")

    print(f"\nTotal indexed: {len(documents)} FIRs")


def search_firs(query: str, district: str, limit: int = 10) -> list:
    """
    Searches FIRs in Meilisearch.
    Always filters by district for RBAC compliance.
    """
    index  = ms.index("firs")
    result = index.search(query, {
        "limit":  limit,
        "filter": f'district = "{district}"',
    })

    hits = []
    for hit in result["hits"]:
        hits.append({
            "fir_id":     hit["fir_id"],
            "fir_number": hit["fir_number"],
            "crime_type": hit["crime_type"],
            "date_filed": hit["date_filed"],
            "location":   hit["location"],
            "description":hit["description"][:200],
            "status":     hit["status"],
        })
    return hits


if __name__ == "__main__":
    print("Indexing all FIRs into Meilisearch...")
    index_all_firs()
    print("\nTesting search...")
    results = search_firs("chain snatching motorcycle", "Bengaluru South")
    print(f"Found {len(results)} results for 'chain snatching motorcycle'")
    for r in results[:3]:
        print(f"  {r['fir_number']} — {r['crime_type']} — {r['description'][:80]}...")