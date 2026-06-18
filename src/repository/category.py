from datetime import datetime, timezone, timedelta

from typing import List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from src.models.category import Category, CategoryPodcast
from src.models.podcast import Podcast


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_categories(self, limit: int, offset: int) -> List[Category]:
        return self.db.query(Category).options(joinedload(Category.podcasts)).limit(limit).offset(offset).all()

    def count_categories(self) -> int:
        return self.db.query(Category).count()

    def get_category_by_id(self, id: int) -> Category | None:
        return self.db.query(Category).options(joinedload(Category.podcasts)).filter(Category.id == id).first()

    def get_category_podcast_ids(self, category_id: int) -> List[int]:
        result = self.db.query(CategoryPodcast.podcast_id).filter(
            CategoryPodcast.category_id == category_id).all()
        return [row[0] for row in result]

    def count_category_podcasts(self, category_id: int) -> int:
        return self.db.query(CategoryPodcast).filter(CategoryPodcast.category_id == category_id).count()

    def get_popular_categories(self, limit: int) -> List[Category]:
        subq = self.db.query(CategoryPodcast.category_id, func.count().label(
            'podcast_count')).group_by(CategoryPodcast.category_id).subquery()
        return self.db.query(Category).outerjoin(subq, Category.id == subq.c.category_id)\
            .order_by(func.coalesce(subq.c.podcast_count, 0).desc()).limit(limit).all()

    def get_category_top_podcasts(self, category_id: int, limit: int) -> List[Podcast]:
        return self.db.query(Podcast).join(CategoryPodcast, CategoryPodcast.podcast_id == Podcast.id)\
            .options(joinedload(Podcast.channel)).filter(CategoryPodcast.category_id == category_id)\
            .order_by(Podcast.play_count.desc()).limit(limit).all()

    def get_category_trending_podcasts(self, category_id: int, limit: int, days: int = 1) -> List[Podcast]:
        date = datetime.now(timezone.utc) - timedelta(days=days)
        return self.db.query(Podcast).join(CategoryPodcast, CategoryPodcast.podcast_id == Podcast.id)\
            .options(joinedload(Podcast.channel)).filter(CategoryPodcast.category_id == category_id, Podcast.created_at >= date)\
            .order_by(Podcast.play_count.desc(), Podcast.created_at.desc()).limit(limit).all()

    def get_category_trending_podcasts(self, category_id: int, limit: int, days: int = 1) -> List[Podcast]:
        date = datetime.now(timezone.utc) - timedelta(days=days)
        return self.db.query(Podcast).join(CategoryPodcast, CategoryPodcast.podcast_id == Podcast.id)\
            .options(joinedload(Podcast.channel)).filter(CategoryPodcast.category_id == category_id, Podcast.created_at >= date)\
            .order_by(Podcast.play_count.desc(), Podcast.created_at.desc()).limit(limit).all()
