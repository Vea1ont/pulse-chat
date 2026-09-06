import json

import redis
import sentry_sdk
from cache import valkey
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from models import Chat, ChatMember, Message
from schemas import ChatCreate, ChatMemberRead, ChatRead, MessageCreate, MessageRead
from security import get_current_user_id
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("/")
async def make_chat(
    data: ChatCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    is_group = len(data.member_ids) >= 2
    new_chat = Chat(name=data.name, is_group=is_group)
    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)

    all_members_ids = set([current_user_id] + data.member_ids)

    for user_id in all_members_ids:
        member = ChatMember(chat_id=new_chat.id, user_id=user_id)
        db.add(member)

    await db.commit()
    for user_id in all_members_ids:
        keys = await valkey.keys(f"user:{user_id}:chats:*")
        if keys:
            await valkey.delete(*keys)

    return new_chat


@router.get("/")
async def my_chats(
    current_user_id: int = Depends(get_current_user_id),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):

    cache_key = f"user:{current_user_id}:chats:{limit}:{offset}"  # limit and offset нужны, потому что мы
    # храним чаты по блокам, в каждом блоке
    # их 20, следовательно, чтобы вернуть
    # нужный блок, он должен иметь определенный

    # ключ иначе страницы смешались бы.
    try:
        cached = await valkey.get(cache_key)
    except redis.RedisError as e:
        print(f"[cache] reading {cache_key} failed: {e}", flush=True)
        sentry_sdk.capture_exception(e)
        cached = None

    if cached:
        return json.loads(cached)

    statement = (
        select(Chat)
        .join(ChatMember, ChatMember.chat_id == Chat.id)
        .where(ChatMember.user_id == current_user_id)
        .order_by(Chat.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(statement)
    chats = result.scalars().all()

    data = [
        ChatRead.model_validate(c).model_dump(mode="json") for c in chats
    ]  # - В chats
    # хранятся ORM-объекты таблицы Chat. Их нельзя напрямую сериализовать в JSON,
    # поэтому сначала валидируем каждый объект по схеме ChatRead, а затем через
    # model_dump(mode="json") преобразуем его в обычный словарь с JSON-совместимыми данными.

    await valkey.set(cache_key, json.dumps(data), ex=60)  # TTL = 60 сек
    return data


@router.delete("/{chat_id}")
async def delete_chat():
    pass


@router.patch("/{chat_id}")
async def change_name_chat():
    pass


@router.post("/{chat_id}/messages")
async def send_message(
    chat_id: int,
    data: MessageCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    statement = select(ChatMember).where(
        ChatMember.chat_id == chat_id, ChatMember.user_id == current_user_id
    )
    result = await db.execute(statement)
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=403, detail="User aren't in chat")

    new_message = Message(chat_id=chat_id, sender_id=current_user_id, text=data.text)
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)

    keys = await valkey.keys(f"chat:{chat_id}:messages:*")
    if keys:
        await valkey.delete(*keys)

    return {"detail": "Message sent"}


@router.get("/{chat_id}/messages", response_model=list[MessageRead])
async def history(
    chat_id: int,
    limit: int = Query(20, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):

    check = select(ChatMember).where(
        ChatMember.chat_id == chat_id, ChatMember.user_id == current_user_id
    )  # найди строку, где совпадает И этот чат, И этот юзер

    result = await db.execute(check)
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=403, detail="User aren't in chat")

    cache_key = f"chat:{chat_id}:messages:{limit}:{offset}"
    cached = await valkey.get(cache_key)
    if cached:
        return json.loads(cached)

    statement = (
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(statement)
    messages = result.scalars().all()

    data = [MessageRead.model_validate(c).model_dump(mode="json") for c in messages]

    await valkey.set(cache_key, json.dumps(data), ex=60)
    return data


@router.get("/{chat_id}/members", response_model=list[ChatMemberRead])
async def users_in_chat(
    chat_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    check = select(ChatMember).where(
        ChatMember.chat_id == chat_id, ChatMember.user_id == current_user_id
    )  # проверяем
    # является ли этот пользователь участником этого чата

    result = await db.execute(check)
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=403, detail="User aren't in chat")

    statement = select(ChatMember).where(ChatMember.chat_id == chat_id)
    result = await db.execute(statement)
    return result.scalars().all()
