from fastapi import APIRouter, Depends, HTTPException
from schemas import UserCreate, UserLogin, UserRead, UserUpdate
from models import User
from security import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from sqlalchemy import select, update


router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserRead])
async def get_all_users(db: AsyncSession = Depends(get_db)):
    statement = select(User)
    result = await db.execute(statement)
    users = result.scalars().all()
    return users

@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=UserRead)
async def user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    statement = select(User).where(user_id == User.id)
    result = await db.execute(statement)
    existing_user = result.scalar_one_or_none()
    if not existing_user:
        raise HTTPException(404, "User not found")
    return existing_user 
    

@router.patch("/me", response_model=UserRead)
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)):
    
    data = update_data.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(current_user, field, value) # current_user.username = value 
                                            # or 
                                            # current_user.email = value
                                            # setattr и нужен, потому что
                                            # мы не знаем, что получаем.
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/me")
async def delete_me(current_user: User = Depends(get_current_user),
                    db: AsyncSession = Depends(get_db)):
    await db.delete(current_user)
    await db.commit()
    return {"detail": "User deleted"}
