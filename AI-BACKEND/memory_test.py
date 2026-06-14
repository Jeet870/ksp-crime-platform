from sql_agent_V2 import build_agent

ask = build_agent("Bengaluru East", "investigating_officer")

turns = [
    "Show me all chain snatching cases",
    "How many accused were involved in those cases?",
    "Were any of them arrested?",
]

for i, q in enumerate(turns, 1):
    print(f"\nTurn {i} — Q: {q}")
    ans = ask(q)
    print(f"         A: {ans}")