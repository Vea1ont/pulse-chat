from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatCreate(BaseModel):
    name: Optional[str] = None
    member_ids: list[int]


class ChatRead(BaseModel):
    id: int
    name: str | None
    is_group: bool
    created_at: datetime
    model_config = {"from_attributes": True}
    
class ChatMemberRead(BaseModel):
    user_id: int
    joined_at: datetime
    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    text: str


class MessageRead(BaseModel):
    id: int
    text: str
    sender_id: int
    created_at: datetime
    model_config = {"from_attributes": True}
