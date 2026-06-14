# sql_agent_v2.py — uses free HuggingFace InferenceClient
import os
import psycopg2
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN  = os.getenv("HUGGINGFACE_API_TOKEN")
DB_HOST   = os.getenv("DB_HOST", "localhost")
DB_PORT   = os.getenv("DB_PORT", "5432")
DB_NAME   = os.getenv("DB_NAME", "ksp_crime_db")
DB_USER   = os.getenv("DB_USER", "postgres")
DB_PASS   = os.getenv("DB_PASSWORD", "password")
DB_SSL    = os.getenv("DB_SSLMODE", "require")

ROLE_TABLES = {
    "constable":             ["firs", "accused", "fir_accused"],
    "investigating_officer": ["firs", "accused", "fir_accused", "victims", "vehicles"],
    "district_sp":           ["firs", "accused", "fir_accused", "victims", "vehicles"],
    "scrb_analyst":          ["firs", "accused", "fir_accused", "victims", "vehicles", "bank_transactions"],
    "scrb_director":         ["firs", "accused", "fir_accused", "victims", "vehicles", "bank_transactions"],
}

# Free model — runs on HuggingFace free servers
client = InferenceClient(
    model="Qwen/Qwen2.5-72B-Instruct",
    token=HF_TOKEN,
    timeout=60,
)

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS, sslmode=DB_SSL
    )

def get_table_schema(tables):
    """Fetches actual column info from the database for the given tables."""
    conn = get_db_connection()
    cur  = conn.cursor()
    schema_parts = []
    for table in tables:
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY ordinal_position
        """, (table,))
        cols = cur.fetchall()
        if cols:
            col_str = ", ".join(f"{c[0]} ({c[1]})" for c in cols)
            schema_parts.append(f"Table '{table}': {col_str}")
    cur.close()
    conn.close()
    return "\n".join(schema_parts)

def generate_sql(question, district, role):
    """Uses Qwen to convert a natural language question to a SQL query."""
    tables  = ROLE_TABLES.get(role, ["firs"])
    schema  = get_table_schema(tables)

    prompt = f"""You are a PostgreSQL expert. Convert the question to a SQL query.

Database schema:
{schema}

Rules:
1. ALWAYS include WHERE district = '{district}' when querying the firs table
2. ALWAYS add LIMIT 50 to queries that return rows
3. Return ONLY the SQL query, nothing else
4. No explanation, no markdown, no backticks

Question: {question}

SQL:"""

    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.2,
    )
    sql = response.choices[0].message.content.strip()
    # Clean up any accidental markdown
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

def run_sql(sql):
    """Executes the SQL and returns results as a list of dicts."""
    conn = get_db_connection()
    cur  = conn.cursor()
    try:
        cur.execute(sql)
        if cur.description:
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            result = [dict(zip(cols, row)) for row in rows]
        else:
            result = []
        conn.commit()
    except Exception as e:
        result = {"error": str(e)}
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    return result

def explain_result(question, sql, result):
    """Uses Qwen to explain the SQL result in plain English."""
    if isinstance(result, dict) and "error" in result:
        return f"There was a database error: {result['error']}"

    if not result:
        return "No records found for your query."

    prompt = f"""A police officer asked: "{question}"

The database returned these results:
{str(result[:10])}

Write a clear, simple 1-3 sentence answer explaining what was found.
Be direct. Use plain English. Do not mention SQL."""

    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

# Conversation memory — simple list of last 5 Q&A pairs
conversation_history = []

def ask(question, district, role):
    """
    Main function — takes a question, returns a natural language answer.
    Maintains conversation history for multi-turn context.
    """
    global conversation_history

    # Build context from history
    context = ""
    if conversation_history:
        context = "Previous conversation:\n"
        for qa in conversation_history[-3:]:  # last 3 turns
            context += f"Q: {qa['question']}\nA: {qa['answer']}\n"
        context += "\n"

    # If question has pronouns, resolve them using context
    resolved_question = question
    if any(word in question.lower() for word in ["those", "them", "their", "these", "that"]):
        if conversation_history:
            resolve_prompt = f"""{context}
Current question: "{question}"
Rewrite the question replacing pronouns with their actual references from the conversation above.
Return only the rewritten question, nothing else."""
            response = client.chat_completion(
                messages=[{"role": "user", "content": resolve_prompt}],
                max_tokens=100,
                temperature=0.1,
            )
            resolved_question = response.choices[0].message.content.strip()

    # Generate and run SQL
    sql     = generate_sql(resolved_question, district, role)
    result  = run_sql(sql)
    answer  = explain_result(question, sql, result)

    # Save to history
    conversation_history.append({"question": question, "answer": answer})
    if len(conversation_history) > 5:
        conversation_history.pop(0)

    return {
        "question":          question,
        "resolved_question": resolved_question,
        "sql":               sql,
        "result_count":      len(result) if isinstance(result, list) else 0,
        "answer":            answer,
    }


if __name__ == "__main__":
    print("Testing SQL agent with free Qwen model...\n")

    tests = [
        "How many FIRs are there in total?",
        "Show me all chain snatching cases",
        "How many accused were involved in those cases?",
    ]

    for q in tests:
        print(f"Q: {q}")
        r = ask(q, "Bengaluru East", "investigating_officer")
        print(f"SQL: {r['sql']}")
        print(f"A: {r['answer']}")
        print()