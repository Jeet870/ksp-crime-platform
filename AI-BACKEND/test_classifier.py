from intent_classifier import classify_intent

CASES = [
    ("How many FIRs were filed last week?",         "sql_query"),
    ("Count chain snatching cases",                 "sql_query"),
    ("List all accused persons",                    "sql_query"),
    ("Who is connected to accused Raju?",           "graph_query"),
    ("Show the network of gang members",            "graph_query"),
    ("Who called Venkat in the last 30 days?",      "graph_query"),
    ("What is the modus operandi pattern here?",    "profiling"),
    ("Find similar cases with the same MO",         "profiling"),
    ("Are there habitual offenders in this area?",  "profiling"),
    ("Will crime spike next month?",                "forecasting"),
    ("Predict chain snatching for December",        "forecasting"),
    ("What is the forecast for Koramangala?",       "forecasting"),
    ("Export this as a PDF report",                 "pdf_export"),
    ("Download the conversation",                   "pdf_export"),
    ("Generate a report for this session",          "pdf_export"),
    ("How many FIRs from Whitefield?",              "sql_query"),
    ("Show crime statistics for this district",     "sql_query"),
    ("Find associates of the accused",              "graph_query"),
    ("Forecast crime for the next 3 months",        "forecasting"),
    ("Print the current session",                   "pdf_export"),
]

passed = 0
for q, expected in CASES:
    got = classify_intent(q)
    ok = got == expected
    if ok: passed += 1
    print(f"[{'PASS' if ok else 'FAIL'}] {q[:50]:<50} → {got}")

print(f"\n{passed}/20 passed — target: 18+")