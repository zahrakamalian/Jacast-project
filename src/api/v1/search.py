from fastapi import APIRouter, Query, Depends
from typing import Annotated, List

from src.services.search import SearchService
from src.schemas.search import (SearchPodcastResponse, SearchEpisodeResponse, SearchPlaylistResponse,
                            SearchUserResponse, SearchResponse, CategoryPodcastsResponse,
                            BrowseResponse)
from src.schemas.category import PaginatedCategoryResponse, CategoryResponse
from src.api.v1.dependencies import get_search_service
from src.schemas.podcast import PodcastDisplay


search_router = APIRouter()
discover_router = APIRouter()


@search_router.get("/", response_model=SearchResponse)
def search_all(service: Annotated[SearchService, Depends(get_search_service)],
               q: str = Query(..., min_length=2, max_length=100),
               type: str = Query(
                   pattern="^(all|podcasts|episodes|users|playlists)$", default="all"),
               limit: int = Query(10, ge=1, le=50),
               page: int = Query(1, ge=1)):
    return service.search_all(q, type, limit, page)


@search_router.get("/podcasts", response_model=SearchPodcastResponse)
def search_podcasts(service: Annotated[SearchService, Depends(get_search_service)],
                    q: str = Query(..., min_length=2, max_length=100),
                    limit: int = Query(10, ge=1, le=50),
                    page: int = Query(1, ge=1)):
    return service.search_podcasts(q, limit, page)


@search_router.get("/episodes", response_model=SearchEpisodeResponse)
def search_episodes(service: Annotated[SearchService, Depends(get_search_service)],
                    q: str = Query(..., min_length=2, max_length=100),
                    limit: int = Query(10, ge=1, le=50),
                    page: int = Query(1, ge=1)):
    return service.search_episodes(q, limit, page)


@search_router.get("/users", response_model=SearchUserResponse)
def search_users(service: Annotated[SearchService, Depends(get_search_service)],
                 q: str = Query(..., min_length=2, max_length=100),
                 limit: int = Query(10, ge=1, le=50),
                 page: int = Query(1, ge=1)):
    return service.search_users(q, limit, page)


@search_router.get("/playlists", response_model=SearchPlaylistResponse)
def search_playlists(service: Annotated[SearchService, Depends(get_search_service)],
                     q: str = Query(..., min_length=2, max_length=100),
                     limit: int = Query(10, ge=1, le=50),
                     page: int = Query(1, ge=1)):
    return service.search_playlists(q, limit, page)


@discover_router.get("/browse", response_model=BrowseResponse)
def browse(service: Annotated[SearchService, Depends(get_search_service)]):
    return service.get_browse()


@discover_router.get("/categories", response_model=PaginatedCategoryResponse)
def get_categories(service: Annotated[SearchService, Depends(get_search_service)],
                   limit: int = Query(10, ge=1, le=50),
                   page: int = Query(1, ge=1)):
    return service.get_categories(limit, page)


@discover_router.get("/categories/{id}", response_model=CategoryResponse)
def get_category_detail(id: int,
                        service: Annotated[SearchService, Depends(get_search_service)]):
    return service.get_category_detail(id)


@discover_router.get("/categories/{id}/podcasts", response_model=CategoryPodcastsResponse)
def get_category_podcasts(id: int,
                          service: Annotated[SearchService, Depends(get_search_service)],
                          limit: int = Query(10, ge=1, le=50),
                          page: int = Query(1, ge=1)):
    return service.get_category_podcasts(id, limit, page)


@discover_router.get("/trending",  response_model=List[PodcastDisplay])
def get_trending(service: Annotated[SearchService, Depends(get_search_service)],
                 limit: int = Query(10, ge=1, le=50)):
    return service.get_trending(limit)


@discover_router.get("/popular")
def get_popular(service: Annotated[SearchService, Depends(get_search_service)],
                limit: int = Query(10, ge=1, le=50)):
    return service.get_popular(limit)
