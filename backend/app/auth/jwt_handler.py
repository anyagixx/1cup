# FILE: backend/app/auth/jwt_handler.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: JWT token creation and validation
#   SCOPE: Access token, refresh token generation and verification
#   DEPENDS: M-BE-CORE (config)
#   LINKS: M-BE-AUTH
# END_MODULE_CONTRACT

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError

from app.config import get_settings

settings = get_settings()


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    extra_data: Optional[dict] = None,
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "access",
    }
    if extra_data:
        to_encode.update(extra_data)
    
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "refresh",
    }
    
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None


def get_token_expiry(token: str) -> Optional[datetime]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        exp = payload.get("exp")
        if exp:
            return datetime.fromtimestamp(exp)
        return None
    except JWTError:
        return None
