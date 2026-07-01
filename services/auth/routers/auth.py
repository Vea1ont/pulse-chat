from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from security import hash_password, verify_password, user_by_login, create_access_token, get_current_user
from database import get_db

from schemas import UserCreate, UserLogin, UserRead

from models import User

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserRead)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    statement = select(User).where(User.email == user_data.email)
    result = await db.execute(statement)
    existing_user = result.scalar_one_or_none() # None - нет пользователей, 
    # один - вернет User, больше одного - кинет ошибку  
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user_data.password)
    
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/login")
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    if not user_data.email and not user_data.username:
        raise HTTPException(status_code=400, detail="User not input email and name")
    
    elif user_data.email:
        existing_user = await user_by_login(db, email=user_data.email)
    elif user_data.username:
        existing_user = await user_by_login(db, username=user_data.username)
                
    
    if not existing_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(user_data.password, existing_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(existing_user.id)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/refresh")
async def refresh_token():
    pass

@router.post("/logout")
async def logout():
    pass

@router.post("/change-password")
async def change_password():
    pass
    
    


