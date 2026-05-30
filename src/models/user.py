from enum import Enum

from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as sqlenum, ForeignKey
from sqlalchemy.orm import relationship

from connections.database import Base


class UserStatusType(str, Enum):
    Online = "Online"
    Deactive = "Deactive"
    Logged_In = "Logged In"


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    TEMP_2FA = "temp_2fa"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    avatar_url = Column(String)
    bio = Column(String)
    is_channel = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    status = Column(sqlenum(UserStatusType), default=UserStatusType.Logged_In)
    last_activity = Column(DateTime, default=func.now())
    is_verified = Column(Boolean, default=False)
    is_2FA_enabled = Column(Boolean, default=False)
    secret_key = Column(String)


class FollowUser(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True)
    follower_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    following_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    followed_at = Column(DateTime, default=func.now())


class UserSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, index=True)
    jti = Column(String, nullable=False, index=True, unique=True)
    hashed_refresh_token = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())


class PasswordResetToken(Base):
    __tablename__ = "reset-password"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String)
    expires_at = Column(DateTime)


class EmailVerificationToken(Base):
    __tablename__ = "verify-email"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String)
    expires_at = Column(DateTime)
