# Валидация данных через Pydantic.
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=5, max_length=15)
    password: str 


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str
    
    model_config = {"from_attributes": True} # from_attributes=True — чтобы Pydantic мог читать SQLAlchemy-объекты напрямую

class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str
    
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None