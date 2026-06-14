import os
import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# Password hashing setup
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain):
    return pwd.hash(plain)

def verify_password(plain, hashed):
    return pwd.verify(plain, hashed)

# JWT setup
SECRET = os.getenv("JWT_SECRET_KEY", "ksp-hackathon-dev-secret")
ALGO   = "HS256"

def create_token(officer_id, name, role, district):
    payload = {
        "sub":      str(officer_id),
        "name":     name,
        "role":     role,
        "district": district,
        "exp":      datetime.now(timezone.utc) + timedelta(hours=12)
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)

def decode_token(token):
    return jwt.decode(token, SECRET, algorithms=[ALGO])