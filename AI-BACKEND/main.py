import os
import sys
import json
import psycopg2
import redis
import uvicorn
from graph_agent import GraphAgent
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from auth import verify_password, create_token, decode_token
from search_indexer import search_firs as ms_search

# This line adds the AI-BACKEND folder to Python's search path
# so we can import intent_classifier.py which Person A created
sys.path.append(os.path.dirname(__file__))
from intent_classifier import classify_intent

load_dotenv()

app = FastAPI(title="KSP Crime Intelligence API", version="2.0.0")

app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def get_pg():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode=os.getenv("DB_SSLMODE", "require")
    )

valkey = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
bearer = HTTPBearer()

def get_officer(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        return decode_token(creds.credentials)
    except Exception:
        raise HTTPException(401, "Invalid or expired token")


class LoginReq(BaseModel):
    username: str
    password: str


class LoginRes(BaseModel):
    token: str
    role: str
    district: str
    name: str


class AskReq(BaseModel):
    question: str
    session_id: str


class AskRes(BaseModel):
    answer:        str
    response_type: str
    session_id:    str
    intent:        str
    xai_trace:     Optional[dict] = None


@app.post("/login", response_model=LoginRes)
def login(req: LoginReq):

    conn = get_pg()
    cur = conn.cursor()

    cur.execute(
        "SELECT officer_id,name,role,district,password_hash FROM officers WHERE badge_number=%s",
        (req.username,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        raise HTTPException(401, "Invalid credentials")

    oid, name, role, district, phash = row

    if not verify_password(req.password, phash):
        raise HTTPException(401, "Invalid credentials")

    return LoginRes(
        token=create_token(oid, name, role, district),
        role=role,
        district=district,
        name=name
    )


@app.post("/ask", response_model=AskRes)
def ask(req: AskReq, officer=Depends(get_officer)):

    if not req.question.strip():
        raise HTTPException(400, "Question cannot be empty")

    role     = officer["role"]
    district = officer["district"]
    key      = f"session:{req.session_id}"

    raw = valkey.get(key)
    history = json.loads(raw) if raw else []

    intent = classify_intent(req.question)
    answer = ""

    if intent == "sql_query":

        from sql_agent_v2 import ask as sql_ask

        result = sql_ask(
            req.question,
            district,
            role
        )

        answer = result["answer"]


    elif intent == "graph_query":

        answer = "Graph analysis coming in Week 3."


    elif intent == "profiling":

        answer = "MO profiling coming in Week 3."


    elif intent == "forecasting":

        answer = "Forecasting coming in Week 4."


    elif intent == "pdf_export":

        answer = f"PDF export coming in Week 4. Session: {req.session_id[:8]}"


    history.extend([
        {"role": "user", "content": req.question},
        {"role": "ai",   "content": answer}
    ])

    history = history[-10:]

    valkey.setex(
        key,
        86400,
        json.dumps(history)
    )


    xai_trace = None

    if intent == "sql_query" and answer and "error" not in answer.lower():

        try:

            from xai_builder import build_xai_trace
            from mo_similarity import find_similar_by_text


            if any(
                word in req.question.lower()
                for word in ["case", "fir", "accused", "suspect"]
            ):

                similar = find_similar_by_text(
                    req.question,
                    top_k=3
                )


                xai_trace = build_xai_trace(
                    fir_id=0,
                    similar_firs=similar
                )


        except Exception:

            pass


    return AskRes(

        answer=answer,

        response_type="text",

        session_id=req.session_id,

        intent=intent,

        xai_trace=xai_trace
    )


@app.get("/graph")
def get_graph(fir_id: int, officer=Depends(get_officer)):

    district = officer["district"]

    try:

        agent = GraphAgent()

        result = agent.get_fir_network(
            fir_id=fir_id,
            district=district
        )

        agent.close()


        if "error" in result:
            raise HTTPException(
                500,
                f"Graph error: {result['error']}"
            )


        return {

            "fir_id": fir_id,

            "nodes": result.get("nodes", []),

            "edges": result.get("edges", []),

            "count": {

                "nodes": len(result.get("nodes", [])),

                "edges": len(result.get("edges", [])),

            }

        }


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(500, str(e))



@app.get("/search")
def search(q: str, officer=Depends(get_officer)):

    if not q or not q.strip():

        raise HTTPException(
            400,
            "Search query cannot be empty"
        )


    district = officer["district"]


    try:

        results = ms_search(
            query=q,
            district=district,
            limit=20
        )


        return {

            "query": q,

            "results": results,

            "total": len(results),

        }


    except Exception as e:

        raise HTTPException(
            500,
            f"Search error: {str(e)}"
        )



@app.get("/health")
def health():

    try:

        valkey.ping()

        vs = "ok"


    except Exception:

        vs = "unreachable"


    return {

        "status": "ok",

        "valkey": vs

    }



if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )