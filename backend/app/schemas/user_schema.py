from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID | str
    full_name: str
    email: EmailStr

    model_config = {
        "from_attributes": True
    }