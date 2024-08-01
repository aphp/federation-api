from datetime import datetime
from typing import Optional

from pydantic import EmailStr, BaseModel


class UserBase(BaseModel):
    username: str
    firstname: str
    lastname: str
    email: EmailStr
    role_id: Optional[str]
    expiration_date: Optional[datetime]


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: str

    class ConfigDict:
        from_attributes = True
