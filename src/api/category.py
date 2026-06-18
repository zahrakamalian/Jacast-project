from fastapi import APIRouter, Depends, Query
from typing import Annotated, List

from api.dependencies import get_category_service
from services.category import CategoryService
from schemas.category import PaginatedCategoryResponse, CategoryResponse
from schemas.podcast import PodcastDisplay

router = APIRouter()


@router.get("/", response_model=PaginatedCategoryResponse)
def get_all_categories(service: Annotated[CategoryService, Depends(get_category_service)],
                       limit: int = Query(20, ge=1, le=50),
                       page: int = Query(1, ge=1)):
    return service.get_all_categories(limit, page)


@router.get("/popular", response_model=List[CategoryResponse])
def get_popular_categories(service: Annotated[CategoryService, Depends(get_category_service)],
                           limit: int = Query(20, ge=1, le=50)):
    return service.get_popular_categories(limit)


@router.get("/{id}", response_model=CategoryResponse)
def get_category_by_id(id: int,
                       service: Annotated[CategoryService, Depends(get_category_service)]):
    return service.get_category_detail(id)


@router.get("/{id}/top-podcasts", response_model=List[PodcastDisplay])
def get_category_top_podcasts(id: int,
                              service: Annotated[CategoryService, Depends(get_category_service)],
                              limit: int = Query(20, ge=1, le=50)):
    return service.get_category_top_podcasts(id, limit)


@router.get("/{id}/trending", response_model=List[PodcastDisplay])
def get_category_trending_podcasts(id: int,
                                   service: Annotated[CategoryService, Depends(get_category_service)],
                                   limit: int = Query(20, ge=1, le=50)):
    return service.get_category_trending_podcasts(id, limit)
