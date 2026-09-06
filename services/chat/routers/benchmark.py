from database import get_db
from fastapi import APIRouter, Depends
from models import Chat, ChatMember
from security import get_current_user_id
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["benchmark"]) # tags - это только ярлык для 
                                       # для группировки в Swagger


@router.get("/nocache_my_chats")
async def nocache_get_my_chats(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    check = (
        select(Chat)
        .join(  # хочу получить чаты
            ChatMember,
            ChatMember.chat_id == Chat.id,  # приклей chat_members, стыкуя по chat.id
        )
        .where(ChatMember.user_id == current_user_id)
    )  # где есть такой пользователь

    result = await db.execute(check)
    chats = result.scalars().all()

    return chats
