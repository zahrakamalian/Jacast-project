from datetime import datetime

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional

from src.models.user import UserStatusType, TokenType


class UserBase(BaseModel):
    email: EmailStr
    display_name: str = Field(..., max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_channel: bool = Field(default=False)


class UserDisplay(UserBase):
    id: int
    created_at: datetime
    status: UserStatusType = Field(default=UserStatusType.Logged_In)
    last_activity: Optional[datetime] = None
    model_config = {"from_attributes": True}


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    model_config = ConfigDict(extra='ignore')

    sub: str
    type: TokenType
    iat: int
    exp: int
    jti: Optional[str] = None


class SessionResponse(BaseModel):
    id: int
    expires_at: datetime


class ResetPassword(BaseModel):
    new_password: str = Field(..., min_length=8)
    token: str


class UserLogin(BaseModel):
    email: EmailStr
    display_name: Optional[str] = Field(max_length=100)
    phone_num: Optional[str] = Field(max_length=15)


class TwoFAUri(BaseModel):
    secret_key: str
    uri: str


class UpdateUser(BaseModel):
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    is_channel: Optional[bool] = None


class ChangePassword(BaseModel):
    current_password: str = Field(min_length=6)
    new_password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)


class ChangeEmail(BaseModel):
    email: EmailStr
    new_email: EmailStr
