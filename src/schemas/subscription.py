from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional, List


class SubscriptionCreate(BaseModel):
    channel_id: int


class SubscriptionDetail(BaseModel):
    id: int
    channel_name: str
    avatar_url: Optional[str] = None
    created_at: datetime
    subscribed_at: datetime


class SubscriptionResponse(SubscriptionDetail):
    notifications_enabled: Optional[bool] = Field(default=None)
    custom_name: Optional[str] = Field(default=None)
    playback_speed: Optional[float] = Field(default=None, ge=0.5, le=2.0)


class PaginatedResponse(BaseModel):
    items: List[SubscriptionResponse] = Field(default=[])
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=100)
    pages: int = Field(..., ge=0)
    has_next: bool = False
    has_prev: bool = False


class SubscriptionUpdate(BaseModel):
    notifications_enabled: Optional[bool] = None
    custom_name: Optional[str] = None
    playback_speed: Optional[float] = Field(default=None, ge=0.5, le=2.0)


class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1)


class GroupDetail(BaseModel):
    id: int
    name: str
    subscriptions: List[SubscriptionDetail] = Field(default=[])


class GroupsListResponse(BaseModel):
    groups: list[GroupDetail] = Field(default=[])
