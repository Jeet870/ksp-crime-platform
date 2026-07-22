from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json, base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

FAKE_USERS = {
    "KSP-CON-001": {"password": "ksp1234", "role": "Constable", "name": "Ravi Kumar"},
    "KSP-IO-001":  {"password": "ksp1234", "role": "IO",        "name": "Suresh Naik"},
    "KSP-SP-001":  {"password": "ksp1234", "role": "SP",        "name": "Priya Sharma"},
    "KSP-ANA-001": {"password": "ksp1234", "role": "Analyst",   "name": "Meena Rao"},
    "KSP-DIR-001": {"password": "ksp1234", "role": "Director",  "name": "Vikram Singh"},
}

class LoginRequest(BaseModel):
    username: str
    password: str

class AskRequest(BaseModel):
    message: str
    token: str

def make_fake_jwt(username: str, role: str, name: str) -> str:
    header  = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip("=")
    payload = base64.urlsafe_b64encode(
        json.dumps({"sub": username, "role": role, "name": name}).encode()
    ).decode().rstrip("=")
    return f"{header}.{payload}.fakesignature"

def decode_fake_jwt(token: str) -> dict:
    try:
        payload_part = token.split(".")[1]
        padding = 4 - len(payload_part) % 4
        payload_part += "=" * padding
        return json.loads(base64.urlsafe_b64decode(payload_part))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/login")
def login(req: LoginRequest):
    user = FAKE_USERS.get(req.username)
    if not user or user["password"] != req.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    token = make_fake_jwt(req.username, user["role"], user["name"])
    return {"token": token, "role": user["role"], "name": user["name"]}

@app.post("/ask")
def ask(req: AskRequest):
    user_data = decode_fake_jwt(req.token)
    echo = f"[{user_data['role']}] You said: {req.message}"
    return {"reply": echo}
