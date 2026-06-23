from pydantic import BaseModel


class ChatCreate(BaseModel):
    pass


class ChatRead(BaseModel):
    id: int

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    pass


class MessageRead(BaseModel):
    id: int

    model_config = {"from_attributes": True}
