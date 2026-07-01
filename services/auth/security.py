import os
import bcrypt

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jose import jwt, JWTError
from datetime import datetime, timedelta

from models import User
from database import get_db

ALGORITHM = 'HS256'
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

security_scheme = HTTPBearer()

def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)):
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = int(payload.get("sub"))
    
    statement = select(User).where(User.id == user_id)
    
    result = await db.execute(statement)

    existing_user = result.scalar_one_or_none()
    
    if not existing_user:
        raise HTTPException(status_code=401, detail="User are not exists")
    return existing_user

async def user_by_login(db: AsyncSession = Depends(get_db), email=None, username=None):
    if email:
        statement = select(User).where(User.email == email)
    elif username:
        statement = select(User).where(User.username == username)
    
    result = await db.execute(statement)
    existing_user = result.scalar_one_or_none()
    return existing_user

def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())