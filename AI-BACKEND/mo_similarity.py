# mo_similarity.py
# Finds FIRs with similar crime patterns using vector similarity search
# NOTE: This file makes NO direct LLM calls except via extract_mo() (Groq)
# when searching by raw text. The embedding model and Chroma search run locally.

import os
import psycopg2
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from mo_extractor import extract_mo, mo_to_string

load_dotenv()

print("Loading embedding model...")
embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

chroma_client = chromadb.PersistentClient(path="./chroma_db")
mo_collection = chroma_client.get_or_create_collection(
    name="fir_mo_vectors",
    metadata={"hnsw:space": "cosine"}
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


def find_similar_firs(fir_id: int, top_k: int = 5) -> list:
    """
    Given a FIR ID, finds the top_k most similar FIRs
    based on their Modus Operandi vectors.

    Returns a list of dicts, each containing:
        fir_id, fir_number, crime_type, district,
        similarity_score, mo_method
    """
    # Step 1: Get the vector for the query FIR from Chroma
    result = mo_collection.get(
        ids=[str(fir_id)],
        include=["embeddings"]
    )

    if not result["embeddings"]:
        return []

    query_vector = result["embeddings"][0]

    # Step 2: Search Chroma for similar vectors
    # n_results + 1 because Chroma includes the query FIR itself
    search_result = mo_collection.query(
        query_embeddings=[query_vector],
        n_results=top_k + 1,
        include=["metadatas", "distances"]
    )

    similar = []
    for metadata, distance in zip(
        search_result["metadatas"][0],
        search_result["distances"][0]
    ):
        # Skip the query FIR itself
        if metadata["fir_id"] == fir_id:
            continue

        # Convert distance to similarity score
        # Chroma returns cosine distance (0=identical, 2=opposite)
        # We convert to similarity (1=identical, 0=completely different)
        similarity = round(1 - (distance / 2), 4)

        similar.append({
            "fir_id":          metadata["fir_id"],
            "fir_number":      metadata["fir_number"],
            "crime_type":      metadata["crime_type"],
            "district":        metadata["district"],
            "mo_method":       metadata.get("mo_method","unknown"),
            "similarity_score":similarity,
        })

    # Sort by similarity descending
    similar.sort(key=lambda x: x["similarity_score"], reverse=True)
    return similar[:top_k]


def find_similar_by_text(fir_text: str, top_k: int = 5,
                         exclude_fir_id: int = None) -> list:
    """
    Given raw FIR text (not an existing FIR ID), finds similar FIRs.
    Useful for new FIRs that are not yet in the database.
    """
    mo     = extract_mo(fir_text)
    mo_str = mo_to_string(mo)
    vector = embedding_model.encode(mo_str).tolist()

    search_result = mo_collection.query(
        query_embeddings=[vector],
        n_results=top_k + 1,
        include=["metadatas","distances"]
    )

    similar = []
    for metadata, distance in zip(
        search_result["metadatas"][0],
        search_result["distances"][0]
    ):
        if exclude_fir_id and metadata["fir_id"] == exclude_fir_id:
            continue

        similarity = round(1 - (distance / 2), 4)
        similar.append({
            "fir_id":          metadata["fir_id"],
            "fir_number":      metadata["fir_number"],
            "crime_type":      metadata["crime_type"],
            "district":        metadata["district"],
            "mo_method":       metadata.get("mo_method","unknown"),
            "similarity_score":similarity,
        })

    similar.sort(key=lambda x: x["similarity_score"], reverse=True)
    return similar[:top_k]