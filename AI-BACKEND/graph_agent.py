# graph_agent.py
# Converts natural language questions to Cypher queries
# and runs them on the Neo4j graph database using Groq AI

import os
import re
from neo4j import GraphDatabase
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def enforce_rbac(cypher: str, district: str, role: str) -> str:
    """
    Safety net: ensures every Cypher query has a district filter.
    Even if the AI forgets to add it, this function injects it.
    This prevents officers from seeing data from other districts.
    """
    district_filter = f"'{district}'"

    if district_filter in cypher:
        return cypher

    if "WHERE" in cypher.upper():
        cypher = re.sub(
            r'(WHERE\s)',
            f'WHERE a.district = {district_filter} AND ',
            cypher,
            count=1,
            flags=re.IGNORECASE
        )
    else:
        cypher = re.sub(
            r'(MATCH\s*\([^)]+\))',
            f'\\1 WHERE a.district = {district_filter}',
            cypher,
            count=1,
            flags=re.IGNORECASE
        )

    return cypher


class GraphAgent:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(
                os.getenv("NEO4J_USER"),
                os.getenv("NEO4J_PASSWORD")
            )
        )
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")

    def close(self):
        self.driver.close()

    def _generate_cypher(self, question: str, district: str) -> str:
        """
        Sends the question to Groq AI with the graph schema.
        Groq reads the schema and returns a valid Cypher query.
        """
        schema = """
Graph schema:
Nodes:
  (a:Accused) — properties: accused_id, name, alias, district, prior_cases, phone
  (f:FIR)     — properties: fir_id, fir_number, crime_type, date_filed, district, status

Relationships:
  (a:Accused)-[:ACCUSED_IN]->(f:FIR)   — properties: role_in_case, arrest_status
  (a:Accused)-[:CALLED]->(a:Accused)   — properties: duration, call_date
"""

        prompt = f"""{schema}

Rules:
1. ALWAYS filter by district: WHERE a.district = '{district}' or WHERE f.district = '{district}'
2. ALWAYS add LIMIT 25 to all queries
3. Return ONLY the Cypher query, no explanation, no markdown, no backticks

Question: {question}

Cypher:"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.1,
        )
        cypher = response.choices[0].message.content.strip()
        cypher = cypher.replace("```cypher", "").replace("```", "").strip()
        return cypher

    def query(self, question: str, district: str = "Bengaluru East", role: str = "constable") -> dict:
        """
        Main method: takes English question → generates Cypher → runs on Neo4j → returns results.
        """
        cypher = self._generate_cypher(question, district)
        cypher = enforce_rbac(cypher, district, role)  # Safety RBAC check

        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(cypher)
                records = []
                for record in result:
                    row = {}
                    for key in record.keys():
                        val = record[key]
                        if hasattr(val, '_properties'):
                            row[key] = dict(val._properties)
                        else:
                            row[key] = val
                    records.append(row)

            return {
                "success": True,
                "cypher":  cypher,
                "records": records,
                "count":   len(records),
            }

        except Exception as e:
            return {
                "success": False,
                "cypher":  cypher,
                "error":   str(e),
                "records": [],
                "count":   0,
            }

    def get_fir_network(self, fir_id: int, district: str) -> dict:
        """
        Gets the full network of accused persons for a specific FIR.
        This is used to draw the investigation board visually in the frontend.
        """
        cypher = f"""
MATCH (a:Accused)-[r:ACCUSED_IN]->(f:FIR {{fir_id: {fir_id}}})
WHERE a.district = '{district}'
WITH a, f, r
OPTIONAL MATCH (a)-[call:CALLED]->(other:Accused)
WHERE other.district = '{district}'
RETURN a, f, r, collect({{caller: a.accused_id, receiver: other.accused_id,
       date: call.call_date, duration: call.duration}}) AS calls
LIMIT 25
"""
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(cypher)
                nodes  = {}
                edges  = []

                for record in result:
                    accused = dict(record["a"]._properties)
                    fir     = dict(record["f"]._properties)
                    rel     = dict(record["r"]._properties)
                    calls   = record["calls"]

                    aid = str(accused.get("accused_id", ""))
                    if aid not in nodes:
                        nodes[aid] = {
                            "data": {
                                "id":          aid,
                                "label":       accused.get("name", "Unknown"),
                                "type":        "accused",
                                "prior_cases": accused.get("prior_cases", 0),
                                "district":    accused.get("district", ""),
                            }
                        }

                    fid = f"fir_{fir.get('fir_id', '')}"
                    if fid not in nodes:
                        nodes[fid] = {
                            "data": {
                                "id":         fid,
                                "label":      fir.get("fir_number", "?"),
                                "type":       "fir",
                                "crime_type": fir.get("crime_type", ""),
                                "date":       str(fir.get("date_filed", "")),
                            }
                        }

                    edges.append({
                        "data": {
                            "source":   aid,
                            "target":   fid,
                            "relation": "ACCUSED_IN",
                            "role":     rel.get("role_in_case", "accused"),
                            "arrested": rel.get("arrest_status", "unknown"),
                        }
                    })

                    for call in calls:
                        if call.get("receiver"):
                            edges.append({
                                "data": {
                                    "source":   str(call["caller"]),
                                    "target":   str(call["receiver"]),
                                    "relation": "CALLED",
                                    "date":     str(call.get("date", "")),
                                }
                            })

            return {"nodes": list(nodes.values()), "edges": edges}

        except Exception as e:
            return {"nodes": [], "edges": [], "error": str(e)}