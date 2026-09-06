from fastapi import FastAPI, Depends, HTTPException
from schemas import UserLogin
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User
from database import get_db
from security import create_access_token
import bcrypt

app = FastAPI()


@app.post("/login")
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    if not user_data.email and not user_data.username:
        raise HTTPException(status_code=400, detail="User not input email and name")
       
    elif user_data.email:
        statement = select(User).where(User.email == user_data.email)
        
    elif user_data.username:
        statement = select(User).where(User.username == user_data.username)
    
    result = await db.execute(statement)
    existing_user = result.scalar_one_or_none()
    if not existing_user:
        raise HTTPException(status_code=401, detail='Invalid credentials')

    if not bcrypt.checkpw(user_data.password.encode(), existing_user.hashed_password.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(existing_user.id)
    return {"access_token": token, "token_type": "bearer"}
