from datetime import datetime, timezone, timedelta

from models.podcast import Podcast, Review, Report, ShareLink
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from config import settings


class PodcastRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_podcasts(self, limit: int, offset: int):
        return self.db.query(Podcast).options(joinedload(Podcast.channel)).order_by(Podcast.created_at.desc()).limit(limit).offset(offset).all()

    def podcasts_count(self) -> int:
        return self.db.query(Podcast).count()

    def get_trending_podcasts(self, limit: int):
        return self.db.query(Podcast).order_by(Podcast.play_count.desc(), Podcast.created_at.desc()).limit(limit).all()

    def get_top_ranked_podcasts(self, limit: int, days: int = 30):
        date = datetime.now(timezone.utc) - timedelta(days=days)
        return self.db.query(Podcast).filter(Podcast.created_at >= date).order_by(Podcast.play_count.desc(), Podcast.created_at.desc()).limit(limit).all()

    def get_new_podcasts(self, limit: int, days: int = 7):
        date = datetime.now(timezone.utc) - timedelta(days=days)
        return self.db.query(Podcast).filter(Podcast.created_at >= date).order_by(Podcast.play_count.desc(), Podcast.created_at.desc()).limit(limit).all()

    def get_podcast_by_id(self, id: int) -> Podcast:
        return self.db.query(Podcast).filter(Podcast.id == id).first()

    def create_podcast(self, podcast: Podcast) -> Podcast:
        self.db.add(podcast)
        self.db.commit()
        self.db.refresh(podcast)
        return podcast

    def update_podcast(self, podcast: Podcast, title: str, description: str, audio_url: str, duration: int) -> Podcast:
        if title is not None and title != podcast.title:
            podcast.title = title
        if description is not None and description != podcast.description:
            podcast.description = description
        if audio_url and audio_url != podcast.audio_url:
            podcast.audio_url = audio_url
        if duration is not None and duration != podcast.duration:
            podcast.duration = duration

        self.db.commit()
        self.db.refresh(podcast)
        return podcast

    def delete_podcast_audio_file(self, audio_url: str) -> None:
        if audio_url:
            file_name = audio_url.split('/')[-1]
            file_path = settings.PODCAST_AUDIO_DIR / file_name
            if file_path.exists():
                file_path.unlink()

    def delete_podcast_cover_file(self, cover_url: str) -> None:
        if cover_url:
            file_name = cover_url.split('/')[-1]
            file_path = settings.PODCAST_COVER_DIR / file_name
            if file_path.exists():
                file_path.unlink()

    def delete_podcast(self, podcast: Podcast) -> None:
        self.db.delete(podcast)
        self.db.commit()

    def update_cover_art_url(self, podcast: Podcast, cover_art_url: str) -> Podcast:
        if cover_art_url and cover_art_url != podcast.cover_art_url:
            podcast.cover_art_url = cover_art_url
            self.db.commit()
            self.db.refresh(podcast)

        return podcast

    def get_reviews_by_podcast_id(self, id: int, offset: int, limit: int):
        return self.db.query(Review).options(joinedload(Review.author)).filter(Review.podcast_id == id).order_by(Review.created_at.desc()).limit(limit).offset(offset).all()

    def count_reviews_by_podcast_id(self, id: int):
        return self.db.query(Review).filter(Review.podcast_id == id).count()

    def get_user_review_by_podcast_id(self, user_id: int, podcast_id: int) -> Review:
        return self.db.query(Review).filter(Review.user_id == user_id, Review.podcast_id == podcast_id).first()

    def add_podcast_review(self, review: Review) -> Review:
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_review_by_id(self, review_id: int) -> Review | None:
        return self.db.query(Review).filter(Review.id == review_id).first()

    def update_podcast_review(self, review: Review, rating: int, comment: str):
        if rating is not None and rating != review.rating:
            review.rating = rating
        if comment is not None and comment != review.comment:
            review.comment = comment
        review.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete_podcast_review(self, review: Review) -> None:
        self.db.delete(review)
        self.db.commit()

    def get_user_report_for_podcast(self, user_id: int, id: int) -> Report | None:
        return self.db.query(Report).filter(Report.user_id ==
                                            user_id, Report.podcast_id == id).first()

    def report_podcast(self, report: Report):
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def create_share_link(self, share_link: ShareLink) -> ShareLink:
        self.db.add(share_link)
        self.db.commit()
        self.db.refresh(share_link)
        return share_link

    def get_share_link_by_token(self, token: str) -> ShareLink | None:
        return self.db.query(ShareLink).filter(
            ShareLink.token == token).first()

    def increment_share_link_click(self, share_link_id: int) -> None:
        self.db.query(ShareLink).filter(ShareLink.id == share_link_id).update(
            {"click_count": ShareLink.click_count + 1})
        self.db.commit()

    def get_review_count(self, id: int) -> int:
        return self.db.query(Review).filter(Review.podcast_id == id).count()

    def get_average_rating(self, id: int) -> float | None:
        result = self.db.query(func.avg(Review.rating)).filter(
            Review.podcast_id == id).scalar()
        return float(result) if result else None

    def get_share_count(self, id: int) -> int:
        result = self.db.query(func.sum(ShareLink.click_count)).filter(
            ShareLink.podcast_id == id).scalar()
        return result or 0
