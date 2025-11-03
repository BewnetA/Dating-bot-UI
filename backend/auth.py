from fastapi import HTTPException, status, Depends, Request
import secrets
import time
from config import settings

# Simple session storage
sessions = {}

def verify_password(plain_password, hashed_password):
    # Simple password comparison
    return plain_password == hashed_password

def get_password_hash(password):
    # Simple hash simulation
    return password  # This is just for demo

def authenticate_user(username: str, password: str):
    if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
        return {"username": username}
    return None

def create_access_token(data: dict):
    # Simple session token
    session_token = secrets.token_hex(32)
    sessions[session_token] = {
        **data,
        "created_at": time.time()
    }
    return session_token

async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    token = auth_header.replace("Bearer ", "")
    user_data = sessions.get(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    # Check if token is expired (24 hours)
    if time.time() - user_data["created_at"] > 24 * 60 * 60:
        del sessions[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    
    return {"username": user_data.get("username")}