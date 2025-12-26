from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    plan_name: Optional[str] = "Leveler"


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    plan_name: str
    max_tokens: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    plan_name: str
    max_tokens: int
    price: float
    api_key: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse