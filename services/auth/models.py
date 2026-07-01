# model.py опицание таблиц в БД через ORM SQLAlchemy. Один класс = одна таблица. Внутри класса описываются поля таблицы.
from database import Base

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    
class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    birthdate: Mapped[datetime] = mapped_column()
    avatar_url: Mapped[str] = mapped_column()