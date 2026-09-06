from database import get_db
from events import publish_user_deleted
from fastapi import APIRouter, Depends, HTTPException, Query
from models import User
from schemas import UserRead, UserUpdate
from security import get_current_user
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserRead])
async def get_all_users(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user_id: User = Depends(get_current_user),
):
    statement = (
        select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
    )
    result = await db.execute(statement)
    users = result.scalars().all()
    return users


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/search", response_model=list[UserRead])
async def user_search(q: str, db: AsyncSession = Depends(get_db)):
    statement = select(User).where(User.username.ilike(f"%{q}%")).limit(20)
    result = await db.execute(statement)
    users = result.scalars().all()
    return users


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
    db: AsyncSession = Depends(get_db),
):

    data = update_data.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(current_user, field, value)  # current_user.username = value
        # or
        # current_user.email = value
        # setattr и нужен, потому что
        # мы не знаем, что получаем.
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/me")
async def delete_me(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):

    user_id = current_user.id

    await db.delete(current_user)
    await db.commit()
    await publish_user_deleted(user_id)

    return {"detail": "User deleted"}
