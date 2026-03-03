from pydantic import BaseModel, EmailStr
import enum
from typing import Optional
from datetime import datetime


class UserRole(str, enum.Enum):
    candidate = "candidate"
    employer = "employer"


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: UserRole


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: UserRole
    email_verified: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

