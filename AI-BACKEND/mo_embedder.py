# mo_embedder.py
# Converts MO strings into vectors and stores them in Chroma
# Chroma is a local vector database — runs on your machine, no cloud needed
# NOTE: This file makes NO LLM API calls itself — it only calls extract_mo()
# from mo_extractor.py (which now uses Groq) and runs embeddings locally.

import os
import psycopg2
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from mo_extractor import extract_mo, mo_to_string
import time

load_dotenv()

# Load the multilingual embedding model
# This model supports Kannada and English
# First run downloads ~90MB — subsequent runs use the cached version
# This runs 100% locally — no API calls, no rate limits, no cost
print("Loading embedding model...")
embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print("Embedding model loaded")

# Set up Chroma — stores vectors locally in a folder called chroma_db/
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Get or create a collection called "fir_mo_vectors"
# A collection is like a table in a regular database
mo_collection = chroma_client.get_or_create_collection(
    name="fir_mo_vectors",
    metadata={"hnsw:space": "cosine"}  # use cosine similarity for matching
)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode=os.getenv("DB_SSLMODE", "require")
    )


def embed_mo(mo_dict: dict) -> list:
    """
    Converts a MO dict into a vector (list of numbers).
    The vector has 384 dimensions — each number captures
    a different aspect of the crime method's meaning.
    """
    mo_str = mo_to_string(mo_dict)
    vector = embedding_model.encode(mo_str).tolist()
    return vector


def store_fir_vector(fir_id: int, fir_number: str, crime_type: str,
                     district: str, mo_dict: dict):
    """
    Converts the MO to a vector and stores it in Chroma.
    Also stores metadata (fir_id, crime_type etc.) so we can
    retrieve FIR details when a match is found.
    """
    vector = embed_mo(mo_dict)

    mo_collection.upsert(
        ids=[str(fir_id)],
        embeddings=[vector],
        metadatas=[{
            "fir_id":     fir_id,
            "fir_number": fir_number,
            "crime_type": crime_type,
            "district":   district,
            "mo_method":  mo_dict.get("method","unknown"),
            "mo_category":mo_dict.get("crime_category","other"),
        }],
        documents=[mo_to_string(mo_dict)]
    )


def run_full_pipeline(batch_size=10):
    """
    Runs the full pipeline for all FIRs in the database:
    1. Fetch FIRs from PostgreSQL
    2. Extract MO from description_text using Groq (llama-3.1-8b-instant)
    3. Convert MO to vector (local, no API call)
    4. Store in Chroma (local, no API call)

    Groq free tier allows 30 requests/min and 14,400/day,
    so batching is just a courtesy pause, not a strict requirement.
    """
    conn = get_db_connection()
    cur  = conn.cursor()

    cur.execute("SELECT fir_id, fir_number, crime_type, district, description_text FROM firs ORDER BY fir_id")
    firs = cur.fetchall()
    cur.close()
    conn.close()

    print(f"Processing {len(firs)} FIRs...")
    success = 0
    failed  = 0

    for i, (fir_id, fir_number, crime_type, district, description) in enumerate(firs, 1):
        try:
            mo   = extract_mo(description)
            store_fir_vector(fir_id, fir_number, crime_type, district, mo)
            success += 1
            print(f"  [{i}/{len(firs)}] FIR {fir_number} — {mo.get('crime_category','?')}")

            # Small pause every batch to stay well under 30 req/min
            if i % batch_size == 0:
                print(f"  Pausing 2 seconds...")
                time.sleep(2)

        except Exception as e:
            failed += 1
            print(f"  [{i}/{len(firs)}] FAILED FIR {fir_number}: {e}")
            time.sleep(2)

    total = mo_collection.count()
    print(f"\nPipeline complete: {success} success, {failed} failed")
    print(f"Chroma collection now has {total} vectors")