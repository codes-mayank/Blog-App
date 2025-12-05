from fastapi import Request, HTTPException
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.models import User
from app.schemas import Token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_token_payload(user_db: User) -> Token:
    return Token(
        sub=user_db.username,
        user_id=user_db.id,
        email=user_db.email
    )

def verify_token(token: str) -> Optional[Token]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return Token(**payload)
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
def get_current_user(request: Request) -> Optional[Token]:
    token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)
    print("Token from cookie:", token)
    if not token:
        return None
    payload = verify_token(token)
    if payload:
        return payload
    return None