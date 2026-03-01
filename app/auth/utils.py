import secrets
import hashlib
from datetime import datetime, timedelta

def generate_reset_token():
    return secrets.token_urlsafe(32)

def hash_reset_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()

def reset_token_expiry(minutes=30):
    return datetime.utcnow() + timedelta(minutes=minutes)
