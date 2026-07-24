import uuid

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: uuid.UUID
    is_verified: bool
    plan_type: str
    niche: str | None = None
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    niche: str | None = None


class UserLogin(UserBase):
    password: str
