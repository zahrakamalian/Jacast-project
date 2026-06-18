from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional, List
from src.models.playlist import Permissions


class PlaylistResponse(BaseModel):
    id: int = Field(...)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    cover_art_url: Optional[str] = None
    is_public: bool = Field(default=True)
    episodes_count: int = Field(ge=0)
    created_at: datetime


class PaginatedPlaylistResponse(BaseModel):
    items: List[PlaylistResponse] = Field(default=[])
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=100)
    pages: int = Field(..., ge=0)
    has_next: bool = False
    has_prev: bool = False


class PlaylistCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    cover_art_url: Optional[str] = None
    is_public: bool = True


class PlaylistUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    cover_art_url: Optional[str] = None


class PlaylistOwnerResponse(BaseModel):
    id: int
    display_name: str
    avatar_url: Optional[str] = None


class PlaylistEpisodeResponse(BaseModel):
    id: int
    podcast_id: int
    title: str = Field(..., min_length=1, max_length=255)
    duration: int = Field(..., gt=0)
    cover_art_url: Optional[str] = None
    position: int
    added_at: datetime


class PlaylistEpisodesResponse(BaseModel):
    playlist_id: int
    playlist_title: str
    total: int
    episodes: List[PlaylistEpisodeResponse] = Field(default=[])


class PlaylistDetailResponse(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    cover_art_url: Optional[str] = None
    is_public: bool = Field(default=True)
    created_at: datetime
    owner: PlaylistOwnerResponse
    episodes: List[PlaylistEpisodeResponse] = Field(default=[])


class AddEpisodeRequest(BaseModel):
    podcast_id: int = Field(..., gt=0)


class ReorderEpisodesRequest(BaseModel):
    order: List[int] = Field(..., min_length=1)


class BulkAddRequest(BaseModel):
    podcast_ids: List[int] = Field(..., min_length=1)


class BulkAddResponse(BaseModel):
    message: str
    added_count: int
    skipped_count: int
    skipped_ids: List[int]


class PlaylistShareResponse(BaseModel):
    share_url: str
    token: str


class CollaborateRequest(BaseModel):
    is_collaborative: bool = Field(...)


class CollaborateResponse(BaseModel):
    message: str
    is_collaborative: bool


class AddCollaboratorRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    permission: Permissions = Field(default=Permissions.EDIT)


class CollaboratorResponse(BaseModel):
    id: int
    playlist_id: int
    user_id: int
    user_name: str
    user_avatar: Optional[str] = None
    permission: Permissions
    added_at: datetime


class PublicPlaylistResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    cover_art_url: Optional[str] = None
    owner_name: str
    owner_avatar: Optional[str] = None
    episodes_count: int = Field(ge=0)
    created_at: datetime


class PaginatedPublicPlaylistResponse(BaseModel):
    items: List[PublicPlaylistResponse] = Field(default=[])
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=100)
    pages: int = Field(..., ge=0)
    has_next: bool = False
    has_prev: bool = False
