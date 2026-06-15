import uuid
import os
import secrets

from typing import List, Optional
from fastapi import HTTPException, UploadFile

from repository.user import UserRepository
from repository.podcast import PodcastRepository
from repository.subscription import SubscriptionRepository
from models.podcast import Podcast, Review, Report, ShareLink
from models.user import User
from schemas.user import UserDisplay
from schemas.podcast import (PodcastDisplay, PaginatedResponse, PodcastDetail, PaginatedReviewResponse,
                             ReviewResponse, ReviewCreate, ReportCreate, ShareLinkResponse, StatsResponse)
from config import settings


class PodcastService:
    def __init__(self, user_repo: UserRepository, podcast_repo: PodcastRepository, subscription_repo: SubscriptionRepository):
        self.user_repo = user_repo
        self.podcast_repo = podcast_repo
        self.subscription_repo = subscription_repo

    def _to_display(self, podcast: Podcast) -> PodcastDisplay:
        return PodcastDisplay(
            id=podcast.id,
            title=podcast.title,
            channel_name=podcast.channel.display_name,
            cover_art_url=podcast.cover_art_url,
            duration=podcast.duration,
            created_at=podcast.created_at
        )

    def _to_detail(self, podcast: Podcast) -> PodcastDetail:
        return PodcastDetail(
            id=podcast.id,
            title=podcast.title,
            channel_name=podcast.channel.display_name,
            cover_art_url=podcast.cover_art_url,
            audio_url=podcast.audio_url,
            duration=podcast.duration,
            created_at=podcast.created_at,
            description=podcast.description,
            play_count=podcast.play_count
        )

    def _to_response(self, review: Review) -> ReviewResponse:
        return ReviewResponse(
            id=review.id,
            user_id=review.user_id,
            user_name=review.author.display_name,
            avatar_url=review.author.avatar_url,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
            updated_at=review.updated_at)

    async def save_cover(self, image_file: UploadFile, user_id: int):
        MAX_IMAGE_SIZE = 5 * 1024 * 1024
        IMAGE_SUFFIXES = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp"
        }
        if image_file.content_type not in IMAGE_SUFFIXES:
            raise HTTPException(status_code=415, detail="Unsupported image format")

        image_extension = IMAGE_SUFFIXES[image_file.content_type]
        image_unique_name = f"cover_{user_id}_{uuid.uuid4().hex}{image_extension}"

        image_file_path = settings.PODCAST_COVER_DIR / image_unique_name

        content = await image_file.read()
        if len(content) > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail="Image too large. Max 5MB")

        with open(image_file_path, "wb") as f:
            f.write(content)

        if os.getenv("RENDER"):
            cover_url = f"/temp-covers/{image_unique_name}"
        else:
            cover_url = f"/resources/uploads/images/{image_unique_name}"
        return cover_url

    async def save_audio(self, audio_file: UploadFile, user_id: int):
        MAX_AUDIO_SIZE = 50 * 1024 * 1024

        AUDIO_SUFFIXES = {
            "audio/mpeg": ".mp3",
            "audio/mp4": ".m4a",
            "audio/aac": ".aac",
            "audio/ogg": ".ogg",
            "audio/wav": ".wav"
        }
        if audio_file.content_type not in AUDIO_SUFFIXES:
            raise HTTPException(status_code=415, detail="Unsupported audio format")

        audio_extension = AUDIO_SUFFIXES[audio_file.content_type]
        audio_unique_name = f"podcast_{user_id}_{uuid.uuid4().hex}{audio_extension}"

        audio_file_path = settings.PODCAST_AUDIO_DIR / audio_unique_name
        content = await audio_file.read()
        if len(content) > MAX_AUDIO_SIZE:
            raise HTTPException(status_code=400, detail="Audio file too large. Max 50MB")

        with open(audio_file_path, "wb") as f:
            f.write(content)
        if os.getenv("RENDER"):
            audio_url = f"/temp-audio/{audio_unique_name}"
        else:
            audio_url = f"/resources/uploads/audio/{audio_unique_name}"

        return audio_url

    def get_all_podcasts(self, limit: int, page: int) -> PaginatedResponse:
        offset = (page - 1) * limit

        podcasts = self.podcast_repo.get_all_podcasts(limit, offset)
        items = []
        for podcast in podcasts:
            item = self._to_display(podcast)
            items.append(item)

        total = self.podcast_repo.podcasts_count()
        pages = (total + limit - 1) // limit
        has_next = page < pages
        has_prev = page > 1

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )

    def get_trending_podcasts(self, limit: int) -> List[PodcastDisplay]:
        podcasts = self.podcast_repo.get_trending_podcasts(limit)
        items = []
        for podcast in podcasts:
            item = self._to_display(podcast)
            items.append(item)

        return items

    def get_top_ranked_podcasts(self, limit: int):
        podcasts = self.podcast_repo.get_top_ranked_podcasts(limit)
        items = []
        for podcast in podcasts:
            item = self._to_display(podcast)
            items.append(item)

        return items

    def get_new_podcasts(self, limit: int):
        podcasts = self.podcast_repo.get_new_podcasts(limit)
        items = []
        for podcast in podcasts:
            item = self._to_display(podcast)
            items.append(item)

        return items

    def get_podcast_details(self, id: int) -> PodcastDetail:
        podcast = self.podcast_repo.get_podcast_by_id(id)
        if not podcast:
            raise HTTPException(status_code=404, detail="Podcast Not Found")

        # if this endpoint plays the podcast
        # podcast.play_count += 1
        # self.podcast_repo.commit()

        return self._to_detail(podcast)

    async def create_podcast(self, user: User, title: str, description: str, duration: int,
                             audio_file: UploadFile, image_file: Optional[UploadFile] = None) -> PodcastDetail:
        if not user.is_channel:
            raise HTTPException(
                status_code=400, detail="You are not allowed to create podcast")

        if not audio_file or audio_file.size == 0:
            raise HTTPException(
                status_code=400, detail="Audio file is required")

        if image_file:
            cover_url = await self.save_cover(image_file, user.id)
        else:
            cover_url = None

        audio_url = await self.save_audio(audio_file, user.id)

        new_entry = Podcast(
            channel_id=user.id,
            title=title,
            description=description,
            cover_art_url=cover_url,
            audio_url=audio_url,
            duration=duration
        )

        new_podcast = self.podcast_repo.create_podcast(new_entry)
        return self._to_detail(new_podcast)

    async def update_podcast(self, user: User, id: int, title: Optional[str], description: Optional[str], duration: Optional[int],
                             audio_file: Optional[UploadFile]) -> PodcastDetail:

        podcast = self.podcast_repo.get_podcast_by_id(id)
        if not podcast:
            raise HTTPException(status_code=404, detail="Podcast not found")
        if user.id != podcast.channel_id:
            raise HTTPException(
                status_code=403, detail="You are not the owner")

        if audio_file:
            if podcast.audio_url:
                self.podcast_repo.delete_podcast_audio_file(podcast.audio_url)
            audio_url = await self.save_audio(audio_file, user.id)
        else:
            audio_url = podcast.audio_url

        updated_podcast = self.podcast_repo.update_podcast(
            podcast, title, description, audio_url, duration)

        return self._to_detail(updated_podcast)

    def delete_podcast(self, user: User, id: int) -> None:
        podcast = self.podcast_repo.get_podcast_by_id(id)
        if not podcast:
            raise HTTPException(status_code=404, detail="Podcast not found")
        if user.id != podcast.channel_id:
            raise HTTPException(
                status_code=403, detail="You are not the owner")
        self.podcast_repo.delete_podcast_audio_file(podcast.audio_url)
        self.podcast_repo.delete_podcast_cover_file(podcast.cover_art_url)
        self.podcast_repo.delete_podcast(podcast)

    async def update_cover_art(self, user: User, id: int, image_file: UploadFile):
        if not image_file or image_file.size == 0:
            raise HTTPException(
                status_code=400, detail="Cover image is required")

        podcast = self.podcast_repo.get_podcast_by_id(id)
        if not podcast:
            raise HTTPException(status_code=404, detail="Podcast not found")
        if user.id != podcast.channel_id:
            raise HTTPException(
                status_code=403, detail="You are not allowed to update cover image")

        if podcast.cover_art_url:
            self.podcast_repo.delete_podcast_cover_file(
                podcast.cover_art_url)
        cover_url = await self.save_cover(image_file, user.id)
        updated_podcast = self.podcast_repo.update_cover_art_url(
            podcast, cover_url)
        return self._to_detail(updated_podcast)

    def get_podcast_stats(self, id: int) -> StatsResponse:
        podcast = self.podcast_repo.get_podcast_by_id(id)
        if not podcast:
            raise HTTPException(status_code=404, detail="Podcast not found")

        total_play = podcast.play_count
        total_subscribers = self.subscription_repo.get_total_subscribers(
            podcast.channel_id)
        total_reviews = self.podcast_repo.get_review_count(id)
        average_rating = self.podcast_repo.get_average_rating(id)
        share_count = self.podcast_repo.get_share_count(id)
        created_at = podcast.created_at

        return StatsResponse(
            total_plays=total_play,
            total_subscribers=total_subscribers,
            total_reviews=total_reviews,
            average_rating=average_rating,
            share_count=share_count,
            created_at=created_at
        )

    def get_podcast_subscribers(self, id: int) -> List[UserDisplay]:
        podcast = self.podcast_repo.get_podcast_by_id(id)
        if not podcast:
            raise HTTPException(status_code=404, detail="Podcast not found")

        subscribers = self.subscription_repo.get_podcast_subscribers(
            podcast.channel_id)
        return [UserDisplay.model_validate(user) for user in subscribers]

    def get_podcast_reviews(self, id: int, limit: int, page: int) -> PaginatedReviewResponse:
        podcast = self.podcast_repo.get_podcast_by_id(id)
        if not podcast:
            raise HTTPException(status_code=404, detail="Podcast not found")

        offset = (page - 1) * limit

        reviews = self.podcast_repo.get_reviews_by_podcast_id(
            id, offset, limit)
        items = []
        for review in reviews:
            item = self._to_response(review)
            items.append(item)

        total = self.podcast_repo.count_reviews_by_podcast_id(id)
        pages = (total + limit - 1) // limit
        has_next = page < pages
        has_prev = page > 1

        return PaginatedReviewResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev
        )

    def add_podcast_review(self, user: User, id: int, data: ReviewCreate) -> ReviewResponse:
        podcast = self.podcast_repo.get_podcast_by_id(id)
        if not podcast:
            raise HTTPException(status_code=404, detail="Podcast not found")

        review = self.podcast_repo.get_user_review_by_podcast_id(user.id, id)
        if review:
            raise HTTPException(
                status_code=400, detail="You have already reviewed this podcast")

        new_entry = Review(
            user_id=user.id,
            podcast_id=id,
            rating=data.rating,
            comment=data.comment
        )

        new_review = self.podcast_repo.add_podcast_review(new_entry)

        return self._to_response(new_review)

    def update_podcast_review(self, user: User, id: int, review_id: int, rating: Optional[int] = None,
                              comment: Optional[str] = None) -> ReviewResponse:

        review = self.podcast_repo.get_review_by_id(review_id)
        if not review:
            raise HTTPException(
                status_code=404, detail="Review not found")

        if review.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="You are not the owner of this review")

        if review.podcast_id != id:
            raise HTTPException(
                status_code=400, detail="Review does not belong to this podcast")

        updated_review = self.podcast_repo.update_podcast_review(
            review, rating, comment)

        return self._to_response(updated_review)

    def delete_podcast_review(self, user: User, id: int, review_id: int) -> None:
        review = self.podcast_repo.get_review_by_id(review_id)
        if not review:
            raise HTTPException(
                status_code=404, detail="Review not found")

        if review.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="You are not the owner of this review")

        if review.podcast_id != id:
            raise HTTPException(
                status_code=400, detail="Review does not belong to this podcast")

        self.podcast_repo.delete_podcast_review(review)

    def report_podcast(self, user: User, id: int, data: ReportCreate) -> None:
        podcast = self.podcast_repo.get_podcast_by_id(id)
        if not podcast:
            raise HTTPException(status_code=404, detail="Podcast not found")

        report = self.podcast_repo.get_user_report_for_podcast(user.id, id)
        if report:
            raise HTTPException(
                status_code=400, detail="You have already reported this podcast")

        new_entry = Report(
            user_id=user.id,
            podcast_id=id,
            reason=data.reason,
            description=data.description,
        )

        self.podcast_repo.report_podcast(new_entry)

    def create_share_link(self, id: int) -> ShareLinkResponse:
        podcast = self.podcast_repo.get_podcast_by_id(id)
        if not podcast:
            raise HTTPException(status_code=404, detail="Podcast not found")

        share_token = secrets.token_urlsafe(12)
        new_entry = ShareLink(
            podcast_id=id,
            token=share_token
        )

        share_link = self.podcast_repo.create_share_link(new_entry)
        share_url = f"https://Jacast.com/s/{share_token}"

        return ShareLinkResponse(
            share_url=share_url,
            token=share_token
        )

    def redirect_to_podcast(self, token: str) -> str:
        share_link = self.podcast_repo.get_share_link_by_token(token)
        if not share_link:
            raise HTTPException(
                status_code=404, detail="Invalid of expired link")
        self.podcast_repo.increment_share_link_click(share_link.id)

        podcast = self.podcast_repo.get_podcast_by_id(share_link.podcast_id)
        if not podcast:
            raise HTTPException(status_code=404, detail="Podcast not found")

        return f"/podcast/{share_link.podcast_id}"
