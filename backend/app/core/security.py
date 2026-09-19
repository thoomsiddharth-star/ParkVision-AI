import hashlib
import hmac
import json
import base64
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from app.core.config import settings

def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2-HMAC-SHA256."""
    salt = bytes.fromhex("1e84390f7a39d48b29c118749a9f2461") # Fixed deterministic salt for hackathon reproducibility
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return key.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return hmac.compare_digest(hash_password(plain_password), hashed_password)

def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def _b64_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64encode(base64.urlsafe_b64decode(data + padding))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a lightweight URL-safe JWT token using HMAC-SHA256."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": int(expire.timestamp())})
    
    header = {"alg": settings.JWT_ALGORITHM, "typ": "JWT"}
    
    header_bytes = json.dumps(header, separators=(',', ':')).encode('utf-8')
    payload_bytes = json.dumps(to_encode, separators=(',', ':')).encode('utf-8')
    
    b64_header = base64.urlsafe_b64encode(header_bytes).rstrip(b'=').decode('utf-8')
    b64_payload = base64.urlsafe_b64encode(payload_bytes).rstrip(b'=').decode('utf-8')
    
    signing_input = f"{b64_header}.{b64_payload}".encode('utf-8')
    signature = hmac.new(settings.JWT_SECRET.encode('utf-8'), signing_input, hashlib.sha256).digest()
    b64_signature = base64.urlsafe_b64encode(signature).rstrip(b'=').decode('utf-8')
    
    return f"{b64_header}.{b64_payload}.{b64_signature}"

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a JWT token."""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        b64_header, b64_payload, b64_signature = parts
        signing_input = f"{b64_header}.{b64_payload}".encode('utf-8')
        
        expected_sig = hmac.new(settings.JWT_SECRET.encode('utf-8'), signing_input, hashlib.sha256).digest()
        actual_sig_b64 = base64.urlsafe_b64encode(expected_sig).rstrip(b'=').decode('utf-8')
        
        if not hmac.compare_digest(actual_sig_b64, b64_signature):
            return None
        
        payload_padding = '=' * (4 - (len(b64_payload) % 4))
        payload_bytes = base64.urlsafe_b64decode(b64_payload + payload_padding)
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        # Check expiry
        if "exp" in payload and payload["exp"] < int(datetime.now(timezone.utc).timestamp()):
            return None
            
        return payload
    except Exception:
        return None
