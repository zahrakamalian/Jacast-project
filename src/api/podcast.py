from fastapi import APIRouter, Depends, Query, UploadFile, Form, File, Body
from fastapi.responses import RedirectResponse
from typing import Annotated, List, Optional

from schemas.user import UserDisplay
from schemas.podcast import (PodcastDisplay, PaginatedResponse, PodcastDetail, PaginatedReviewResponse,
                             ReviewCreate, ReviewResponse, ReportCreate, ShareLinkResponse, StatsResponse)
from api.dependencies import get_podcast_service, get_current_user
from services.podcast import PodcastService
from models.user import User
router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
def get_all_podcasts(service: Annotated[PodcastService, Depends(get_podcast_service)], limit: int = 10, page: int = 1):
    return service.get_all_podcasts(limit, page)


@router.get("/trending", response_model=List[PodcastDisplay])
def get_trending_podcasts(service: Annotated[PodcastService, Depends(get_podcast_service)], limit: int = Query(10, ge=1, le=50)):
    return service.get_trending_podcasts(limit)


@router.get("/top-charts", response_model=List[PodcastDisplay])
def get_top_ranked_podcast(service: Annotated[PodcastService, Depends(get_podcast_service)], limit: int = Query(10, ge=1, le=50)):
    return service.get_top_ranked_podcasts(limit)


@router.get("/new", response_model=List[PodcastDisplay])
def get_new_podcast(service: Annotated[PodcastService, Depends(get_podcast_service)], limit: int = Query(10, ge=1, le=50)):
    return service.get_new_podcasts(limit)


@router.get("/{id}", response_model=PodcastDetail)
def get_podcast_details(service: Annotated[PodcastService, Depends(get_podcast_service)], id: int):
    return service.get_podcast_details(id)


@router.post("/", response_model=PodcastDetail)
async def create_podcast(user: Annotated[User, Depends(get_current_user)], service: Annotated[PodcastService, Depends(get_podcast_service)],
                         title: str = Form(..., min_length=3, max_length=255), description: Optional[str] = Form(None), duration: int = Form(..., gt=0),
                         audio_file: UploadFile = File(...), image_file: Optional[UploadFile] = File(None)):

    return await service.create_podcast(user, title, description, duration, audio_file, image_file)


@router.put("/{id}", response_model=PodcastDetail)
async def update_podcast(user: Annotated[User, Depends(get_current_user)], service: Annotated[PodcastService, Depends(get_podcast_service)], id: int,
                         title: Optional[str] = Form(default=None, min_length=3, max_length=255), description: Optional[str] = Form(None), duration: Optional[int] = Form(default=None, gt=0),
                         audio_file: Optional[UploadFile] = File(None), cover_image: Optional[UploadFile] = File(None)):

    return await service.update_podcast(user, id, title, description, duration, audio_file, cover_image)


@router.delete("/{id}")
def delete_podcast(user: Annotated[User, Depends(get_current_user)], service: Annotated[PodcastService, Depends(get_podcast_service)], id: int):
    service.delete_podcast(user, id)
    return {"message": "Podcast deleted successfully"}


@router.patch("/{id}/cover-art", response_model=PodcastDetail)
async def update_cover_art(user: Annotated[User, Depends(get_current_user)], service: Annotated[PodcastService, Depends(get_podcast_service)],
                           id: int, image_file: UploadFile = File(...)):
    return await service.update_cover_art(user, id, image_file)


@router.get("/{id}/stats", response_model=StatsResponse)
def get_podcast_stats(service: Annotated[PodcastService, Depends(get_podcast_service)], id: int):
    return service.get_podcast_stats(id)


@router.get("/{id}/subscribers", response_model=List[UserDisplay])
def podcast_subscribers(service: Annotated[PodcastService, Depends(get_podcast_service)], id: int):
    return service.get_podcast_subscribers(id)


@router.get("/{id}/reviews", response_model=PaginatedReviewResponse)
def get_podcast_reviews(service: Annotated[PodcastService, Depends(get_podcast_service)],
                        id: int, limit: int = Query(10, ge=1, le=100), page: int = Query(1, ge=1)):
    return service.get_podcast_reviews(id, limit, page)


@router.post("/{id}/reviews", response_model=ReviewResponse)
def add_podcast_review(user: Annotated[User, Depends(get_current_user)], service: Annotated[PodcastService, Depends(get_podcast_service)],
                       id: int, data: ReviewCreate):
    return service.add_podcast_review(user, id, data)


@router.put("/{id}/reviews/{review_id}", response_model=ReviewResponse)
def update_podcast_review(user: Annotated[User, Depends(get_current_user)], service: Annotated[PodcastService, Depends(get_podcast_service)],
                          id: int, review_id: int, rating: Optional[int] = Body(None, ge=1, le=5), comment: Optional[str] = Body(None)):
    return service.update_podcast_review(user, id, review_id, rating, comment)


@router.delete("/{id}/reviews/{review_id}")
def delete_podcast_review(user: Annotated[User, Depends(get_current_user)], service: Annotated[PodcastService, Depends(get_podcast_service)],
                          id: int, review_id: int):
    service.delete_podcast_review(user, id, review_id)
    return {"message": "Review deleted successfully"}


@router.post("/{id}/report")
def report_podcast(user: Annotated[User, Depends(get_current_user)], service: Annotated[PodcastService, Depends(get_podcast_service)],
                   id: int, data: ReportCreate):
    service.report_podcast(user, id, data)
    return {"message": "Report submitted successfully"}


@router.post("/{id}/share", response_model=ShareLinkResponse)
def create_share_link(service: Annotated[PodcastService, Depends(get_podcast_service)], id: int):
    return service.create_share_link(id)


@router.get("/s/{token}")
def redirect_share_link(service: Annotated[PodcastService, Depends(get_podcast_service)], token: str):
    redirect_url = service.redirect_to_podcast(token)
    return RedirectResponse(url=redirect_url, status_code=302)
