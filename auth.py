from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM")

def _normalize_password(password: str) -> str:
    """Hash previo para evitar límite de 72 bytes de bcrypt."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def hash_password(password: str):
    print("Using normalized hash")
    normalized = _normalize_password(password)
    return pwd_context.hash(normalized)

def verify_password(plain: str, hashed: str):
    normalized = _normalize_password(plain)
    return pwd_context.verify(normalized, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)