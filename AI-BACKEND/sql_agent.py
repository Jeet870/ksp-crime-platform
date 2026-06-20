# sql_agent.py
# A SQL agent that answers questions about our KSP crime database
# Uses Qwen2.5-72B via HuggingFace InferenceClient directly (no streaming issues)
 
import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from huggingface_hub import InferenceClient
 
# ─── STEP 1: Load environment variables ──────────────────────────────────────
load_dotenv(r"C:\Users\ISHAAN BANSAL\Desktop\ksp-crime-platform\AI-BACKEND\.env")
 
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
 
# ─── STEP 2: Connect to the PostgreSQL database ───────────────────────────────
# SQLDatabase is a LangChain object that wraps our database connection.
# It automatically reads table names and columns so the AI knows what's available.
connection_string = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?sslmode=require"
)

db = SQLDatabase.from_uri(
    connection_string,
    include_tables=["firs", "accused", "fir_accused", "victims"]
)
print("Connected to database. Available tables:", db.get_usable_table_names())
 
# ─── STEP 3: Set up the AI model ─────────────────────────────────────────────
# Using InferenceClient directly — avoids all the streaming/task-type issues
# that HuggingFaceEndpoint has with newer huggingface_hub versions.
client = InferenceClient(
    model="Qwen/Qwen2.5-72B-Instruct",
    token=HUGGINGFACE_TOKEN,
)
 
# ─── STEP 4: Define the SQL agent logic manually ─────────────────────────────
# Instead of LangChain's create_sql_agent (which forces streaming),
# we build the same loop ourselves: get schema → ask Qwen for SQL → run SQL → explain.
 
def run_sql_agent(question: str) -> str:
    # 4a. Get the schema so the model knows what tables/columns exist
    schema = db.get_table_info()
 
    # 4b. Build the prompt — tell Qwen exactly what we need
    system_prompt = """You are an expert SQL assistant for a Karnataka State Police crime database.
Given a question and the database schema, you must:
1. Write a valid PostgreSQL SQL query to answer the question.
2. Return ONLY the SQL query, nothing else. No explanation, no markdown, no backticks.
Just the raw SQL query ending with a semicolon."""
 
    user_prompt = f"""Database schema:
{schema}
 
Question: {question}
 
SQL query:"""
 
    # 4c. Call Qwen via chat_completion (conversational task — works correctly)
    response = client.chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        max_tokens=256,
        temperature=0.1,
    )
 
    sql_query = response.choices[0].message.content.strip()
 
    # Clean up in case the model wraps it in markdown anyway
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
 
    print(f"\nGenerated SQL:\n{sql_query}\n")
 
    # 4d. Run the SQL query against Neon
    try:
        result = db.run(sql_query)
    except Exception as e:
        return f"SQL execution failed: {e}"
 
    print(f"Raw result: {result}\n")
 
    # 4e. Ask Qwen to turn the raw result into plain English
    explain_prompt = f"""The user asked: "{question}"
The SQL query returned this result: {result}
Please give a clear, concise answer in plain English."""
 
    explanation = client.chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful police data analyst. Answer clearly and concisely."},
            {"role": "user",   "content": explain_prompt},
        ],
        max_tokens=256,
        temperature=0.1,
    )
 
    return explanation.choices[0].message.content.strip()
 
 
# ─── STEP 5: Ask a question ───────────────────────────────────────────────────
question = "give the details of a fir which has a very interesting case?"
print(f"\nQuestion: {question}")
print("Thinking...\n")
 
answer = run_sql_agent(question)
print("\nAnswer:", answer)
