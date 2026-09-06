import os

from cache import valkey
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

ALGORITHM = "HS256"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

security_scheme = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = int(payload["sub"])
    is_blacklisted = await valkey.exists(f"blacklist:user:{user_id}")
    if is_blacklisted:
        raise HTTPException(status_code=401, detail="User deleted")
    
    return user_id
