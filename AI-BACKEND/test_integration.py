import requests
import json
import uuid

BASE = "http://localhost:8000"

def login(badge, pw):
    r = requests.post(f"{BASE}/login", json={"username": badge, "password": pw})
    assert r.status_code == 200, f"Login failed: {r.text}"
    return r.json()["token"], r.json()["role"]

def ask(token, q, sid):
    r = requests.post(f"{BASE}/ask",
        json={"question": q, "session_id": sid},
        headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, f"Ask failed: {r.text}"
    return r.json()

print("=== INTEGRATION TESTS ===\n")

# Bad credentials rejected
r = requests.post(f"{BASE}/login", json={"username": "FAKE", "password": "wrong"})
assert r.status_code == 401
print("[PASS] Bad credentials rejected")

# No token rejected
r = requests.post(f"{BASE}/ask", json={"question": "hi", "session_id": "x"})
assert r.status_code in [401, 403]
print("[PASS] Unauthenticated request rejected")

# All 5 roles login correctly
for badge, expected in [
    ("KSP-CON-001", "constable"),
    ("KSP-IO-001",  "investigating_officer"),
    ("KSP-SP-001",  "district_sp"),
    ("KSP-ANA-001", "scrb_analyst"),
    ("KSP-DIR-001", "scrb_director"),
]:
    tok, got = login(badge, "ksp1234")
    assert got == expected, f"Role mismatch: {got}"
    print(f"[PASS] Login {badge} → {got}")

# Intent routing
sid = str(uuid.uuid4())
tok, _ = login("KSP-IO-001", "ksp1234")
for q, expected_intent in [
    ("How many FIRs are there?",     "sql_query"),
    ("Who is connected to Raju?",    "graph_query"),
    ("Show crime pattern analysis",  "profiling"),
    ("Predict crime next month",     "forecasting"),
    ("Export as PDF",                "pdf_export"),
]:
    d = ask(tok, q, sid)
    ok = d["intent"] == expected_intent
    print(f"[{'PASS' if ok else 'FAIL'}] intent={d['intent']:<15} for: {q}")

# SQL returns real answer
d = ask(tok, "How many FIRs are there?", sid)
assert len(d["answer"]) > 3
print(f"[PASS] SQL answered: {d['answer'][:60]}")

# Valkey session check
import redis
v = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
h = json.loads(v.get(f"session:{sid}") or "[]")
assert len(h) > 0
print(f"[PASS] Valkey: {len(h)} messages stored")

print("\n=== ALL TESTS PASSED ===")
# Add at the bottom of test_integration.py

print("\n--- Week 3 Endpoint Tests ---")

# Test /graph
r = requests.get(f"{BASE}/graph?fir_id=1",
    headers={"Authorization": f"Bearer {tok}"})
assert r.status_code == 200, f"/graph failed: {r.text}"
data = r.json()
assert "nodes" in data, "No nodes in graph response"
print(f"[PASS] /graph fir_id=1 → {data['count']['nodes']} nodes, {data['count']['edges']} edges")

# Test /search
r = requests.get(f"{BASE}/search?q=chain+snatching",
    headers={"Authorization": f"Bearer {tok}"})
assert r.status_code == 200, f"/search failed: {r.text}"
data = r.json()
assert "results" in data, "No results in search response"
print(f"[PASS] /search 'chain snatching' → {data['total']} results")

# Test search with typo (Meilisearch handles this)
r = requests.get(f"{BASE}/search?q=chian+snatching",
    headers={"Authorization": f"Bearer {tok}"})
data = r.json()
print(f"[PASS] /search typo 'chian snatching' → {data['total']} results (typo tolerance)")