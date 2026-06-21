from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional, List
from src.data.models.podcast import ReportReason


class PodcastBase(BaseModel):
    title: str
    channel_name: str
    cover_art_url: Optional[str] = None
    duration: int = Field(..., gt=0)


class PodcastDisplay(PodcastBase):
    id: int
    created_at: datetime


class PodcastDetail(PodcastDisplay):
    description: Optional[str] = None
    audio_url: str
    play_count: int = Field(default=0, ge=0)


class PaginatedResponse(BaseModel):
    items: List[PodcastDisplay] = Field(default=[])
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=100)
    pages: int = Field(..., ge=0)
    has_next: bool = False
    has_prev: bool = False


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    user_name: str
    avatar_url: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class PaginatedReviewResponse(BaseModel):
    items: List[ReviewResponse] = Field(default=[])
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=100)
    pages: int = Field(..., ge=0)
    has_next: bool = False
    has_prev: bool = False


class ReportCreate(BaseModel):
    reason: ReportReason = Field(...)
    description: Optional[str] = Field(None, max_length=500)


class ShareLinkResponse(BaseModel):
    share_url: str
    token: str


class StatsResponse(BaseModel):
    total_plays: int = Field(default=0)
    total_subscribers: int = Field(default=0)
    total_reviews: int = Field(default=0)
    average_rating: Optional[float] = Field(default=None, ge=1, le=5)
    share_count: int = Field(default=0)
    created_at: datetime
