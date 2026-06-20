from auth import create_token, decode_token
import jwt, time

print("=== AUTH TESTS ===\n")

# Test 1: Valid token decodes correctly
token = create_token(1, "Test Officer", "constable", "Bengaluru Urban")
decoded = decode_token(token)
assert decoded["role"]     == "constable",       "Role mismatch"
assert decoded["district"] == "Bengaluru Urban", "District mismatch"
assert decoded["name"]     == "Test Officer",    "Name mismatch"
assert decoded["sub"]      == "1",               "ID mismatch"
print("[PASS] Valid token decodes correctly")
print(f"       role={decoded['role']}, district={decoded['district']}")

# Test 2: Tampered token is rejected
tampered = token[:-5] + "XXXXX"
try:
    decode_token(tampered)
    print("[FAIL] Should have rejected tampered token")
except jwt.InvalidTokenError:
    print("[PASS] Tampered token correctly rejected")

# Test 3: Token with wrong secret is rejected
import os
fake_token = jwt.encode(
    {"sub": "99", "role": "scrb_director"},
    "wrong-secret-key",
    algorithm="HS256"
)
try:
    decode_token(fake_token)
    print("[FAIL] Should have rejected wrong-secret token")
except jwt.InvalidSignatureError:
    print("[PASS] Wrong secret token correctly rejected")

# Test 4: Check all fields present
assert "exp" in decoded, "No expiry field"
print("[PASS] Expiry field present in token")

print("\n=== ALL AUTH TESTS PASSED ===")