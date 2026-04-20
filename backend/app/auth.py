from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.config import settings
import hashlib

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля с использованием SHA256"""
    if not plain_password or not hashed_password:
        return False
    
    # Хешируем введенный пароль и сравниваем с хранимым хешем
    return hash_password(plain_password) == hashed_password

def get_password_hash(password: str) -> str:
    """Хеширование пароля с использованием SHA256"""
    if not password:
        raise ValueError("Password cannot be empty")
    return hash_password(password)

def hash_password(password: str) -> str:
    """Простое хеширование SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None
