from pydantic import BaseModel


class UserCreate(BaseModel):
    pass  # поля для создания пользователя


class UserRead(BaseModel):
    id: int

    model_config = {"from_attributes": True}
    # from_attributes=True — чтобы Pydantic мог читать SQLAlchemy-объекты напрямую
