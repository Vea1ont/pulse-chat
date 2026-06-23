from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    # is_group, name, created_at — добавишь сам


class ChatMember(Base):
    __tablename__ = "chat_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    # chat_id, user_id — добавишь сам


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    # chat_id, sender_id, text, created_at, is_read — добавишь сам
