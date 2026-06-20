# test_week2.py — updated for new sql_agent_v2
from sql_agent_V2 import ask

QUESTIONS = [
    "How many FIRs are there in total?",
    "How many chain snatching cases are there?",
    "How many FIRs were filed in the last 30 days?",
    "List all crime types and their counts",
    "How many unique accused persons are in the database?",
    "Which police station has the most FIRs?",
    "How many FIRs have status open?",
    "What are the top 3 most common crime types?",
    "How many FIRs are from Koramangala PS?",
    "Show me the 5 most recent FIRs",
]

passed = 0
for i, q in enumerate(QUESTIONS, 1):
    try:
        r = ask(q, "Bengaluru East", "investigating_officer")
        ans = r["answer"]
        ok  = "error" not in ans.lower() and len(ans) > 5
        print(f"[{'PASS' if ok else 'FAIL'}] {i}. {q[:55]}")
        print(f"       SQL: {r['sql']}")
        print(f"       ANS: {ans}")
        print()
        if ok: passed += 1
    except Exception as e:
        print(f"[ERROR] {i}. {e}")
        print()

print(f"{passed}/10 passed")