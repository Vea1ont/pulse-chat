import asyncio
from database import SessionLocal
from models import Chat, ChatMember, Message

async def seed_chats(user_id, count):
    async with SessionLocal() as db:
        for i in range(count):
            chat = Chat(name=f"chat {i}", is_group=False)
            db.add(chat)
            
            await db.flush()
            db.add(ChatMember(chat_id=chat.id, user_id=user_id))
        await db.commit()
        
async def seed_messages(chat_id, sender_id, count):
    async with SessionLocal() as db:
        for i in range(count):
            text = f"msg {i}"
            db.add(Message(chat_id=chat_id, sender_id=sender_id, text=text))
        await db.commit()
         
if __name__ == "__main__":
    asyncio.run(seed_messages(1, 34, 10000))