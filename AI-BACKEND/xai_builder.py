# xai_builder.py
# Builds explainability traces for AI flags
# Every suspect flag must have a transparent reasoning chain

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST","localhost"),
        port=os.getenv("DB_PORT","5432"),
        dbname=os.getenv("DB_NAME","ksp_crime_db"),
        user=os.getenv("DB_USER","postgres"),
        password=os.getenv("DB_PASSWORD","password"),
        sslmode=os.getenv("DB_SSLMODE","require")
    )


def get_fir_details(fir_id: int) -> dict:
    """Fetches FIR details from database."""
    conn = get_db_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT f.fir_number, f.crime_type, f.date_filed, f.district,
               f.location_description, f.description_text,
               COUNT(fa.accused_id) AS accused_count
        FROM firs f
        LEFT JOIN fir_accused fa ON f.fir_id = fa.fir_id
        WHERE f.fir_id = %s
        GROUP BY f.fir_id, f.fir_number, f.crime_type, f.date_filed,
                 f.district, f.location_description, f.description_text
    """, (fir_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row:
        return {}
    return {
        "fir_number":   row[0],
        "crime_type":   row[1],
        "date_filed":   str(row[2]),
        "district":     row[3],
        "location":     row[4],
        "description":  row[5],
        "accused_count":row[6],
    }


def get_accused_history(fir_id: int) -> list:
    """Gets accused persons and their prior case counts for a FIR."""
    conn = get_db_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT a.name, a.prior_cases_count, fa.role_in_case, fa.arrest_status
        FROM accused a
        JOIN fir_accused fa ON a.accused_id = fa.accused_id
        WHERE fa.fir_id = %s
        ORDER BY a.prior_cases_count DESC
    """, (fir_id,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [
        {"name": r[0], "prior_cases": r[1], "role": r[2], "arrested": r[3]}
        for r in rows
    ]


def build_xai_trace(fir_id: int, similar_firs: list = None,
                    graph_connections: list = None) -> dict:
    """
    Builds a full explainability trace for a FIR.

    Parameters:
        fir_id           - the FIR being analysed
        similar_firs     - list of dicts from find_similar_firs()
        graph_connections- list of dicts from GraphAgent

    Returns:
        {
            risk_level: "high" / "medium" / "low",
            risk_score: 0-100,
            reasons: ["reason 1", "reason 2", ...],
            fir_details: {...},
            disclaimer: "..."
        }
    """
    reasons    = []
    risk_score = 0

    fir_details     = get_fir_details(fir_id)
    accused_history = get_accused_history(fir_id)

    # Reason 1: MO similarity matches
    if similar_firs:
        for sf in similar_firs[:3]:
            score_pct = round(sf.get("similarity_score", 0) * 100)
            if score_pct >= 80:
                reasons.append(
                    f"{score_pct}% MO similarity with {sf['fir_number']} "
                    f"({sf['crime_type']}, {sf.get('date_filed','')})"
                )
                risk_score += score_pct * 0.3
            elif score_pct >= 60:
                reasons.append(
                    f"Moderate MO similarity ({score_pct}%) with {sf['fir_number']}"
                )
                risk_score += score_pct * 0.15

    # Reason 2: Accused prior history
    for acc in accused_history:
        prior = acc.get("prior_cases", 0)
        if prior >= 3:
            reasons.append(
                f"{acc['name']} ({acc['role']}) has {prior} prior cases — classified as habitual offender"
            )
            risk_score += 20
        elif prior >= 1:
            reasons.append(
                f"{acc['name']} ({acc['role']}) has {prior} prior case(s) on record"
            )
            risk_score += 8

    # Reason 3: Arrest status
    not_arrested = [a for a in accused_history if a.get("arrested") == "not_arrested"]
    absconding   = [a for a in accused_history if a.get("arrested") == "absconding"]
    if absconding:
        names = ", ".join(a["name"] for a in absconding)
        reasons.append(f"Accused person(s) absconding: {names}")
        risk_score += 15
    if not_arrested and len(not_arrested) > 1:
        reasons.append(f"{len(not_arrested)} accused persons not yet arrested")
        risk_score += 10

    # Reason 4: Graph connections
    if graph_connections:
        for gc in graph_connections[:2]:
            reasons.append(
                f"Phone contact established with known associate: {gc.get('name','Unknown')}"
            )
            risk_score += 10

    # Determine risk level
    risk_score = min(risk_score, 100)
    if risk_score >= 60:
        risk_level = "high"
    elif risk_score >= 30:
        risk_level = "medium"
    else:
        risk_level = "low"

    # If no reasons found, add a neutral statement
    if not reasons:
        reasons.append("No significant risk factors identified in available data")

    return {
        "fir_id":      fir_id,
        "risk_level":  risk_level,
        "risk_score":  round(risk_score),
        "reasons":     reasons,
        "fir_details": fir_details,
        "disclaimer":  "AI-generated assessment. Human judgment required. Not admissible as sole evidence.",
    }