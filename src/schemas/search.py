from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional, List, Union
from schemas.podcast import PodcastDisplay
from schemas.category import CategoryResponse


class SearchPodcastItem(BaseModel):
    id: int
    title: str
    channel_name: str
    cover_art_url: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime


class SearchPodcastResponse(BaseModel):
    query: str
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=50)
    pages: int = Field(..., ge=0)
    items: List[SearchPodcastItem] = Field(default=[])


class SearchEpisodeItem(BaseModel):
    id: int
    title: str
    channel_name: str
    cover_art_url: Optional[str] = None
    duration: int = Field(..., gt=0)
    created_at: datetime


class SearchEpisodeResponse(BaseModel):
    query: str
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=50)
    pages: int = Field(..., ge=0)
    items: List[SearchEpisodeItem] = Field(default=[])


class SearchUserItem(BaseModel):
    id: int
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_channel: bool = False


class SearchUserResponse(BaseModel):
    query: str
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=50)
    pages: int = Field(..., ge=0)
    items: List[SearchUserItem] = Field(default=[])


class SearchPlaylistItem(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    cover_art_url: Optional[str] = None
    owner_name: str
    owner_avatar: Optional[str] = None
    episodes_count: int = Field(ge=0)
    created_at: datetime


class SearchPlaylistResponse(BaseModel):
    query: str
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=50)
    pages: int = Field(..., ge=0)
    items: List[SearchPlaylistItem] = Field(default=[])


class SearchCategoryResult(BaseModel):
    items: List[Union[SearchPodcastItem, SearchEpisodeItem,
                      SearchUserItem, SearchPlaylistItem]] = Field(default=[])
    total: int = Field(..., ge=0)


class SearchResponse(BaseModel):
    query: str
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=50)
    pages: int = Field(..., ge=0)
    podcasts: SearchCategoryResult
    episodes: SearchCategoryResult
    users: SearchCategoryResult
    playlists: SearchCategoryResult


class CategoryPodcastsResponse(BaseModel):
    category_id: int
    category_name: str
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=50)
    pages: int = Field(..., ge=0)
    items: List[PodcastDisplay] = Field(default=[])


class BrowseResponse(BaseModel):
    new_releases: List[PodcastDisplay] = []
    trending: List[PodcastDisplay] = []
    popular: List[PodcastDisplay] = []
    categories: List[CategoryResponse] = []
