from typing import List
from fastapi import HTTPException

from src.repository.category import CategoryRepository
from src.schemas.category import CategoryResponse, PaginatedCategoryResponse
from src.schemas.podcast import PodcastDisplay
from src.models.category import Category
from src.models.podcast import Podcast


class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    def _to_category_response(self, category: Category) -> CategoryResponse:
        return CategoryResponse(
            id=category.id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            icon_url=category.icon_url,
            podcasts_count=len(category.podcasts) if category.podcasts else 0,
            created_at=category.created_at
        )

    def _to_podcast_display(podcast: Podcast) -> PodcastDisplay:
        return PodcastDisplay(
            id=podcast.id,
            title=podcast.title,
            channel_name=podcast.channel.display_name,
            cover_art_url=podcast.cover_art_url,
            duration=podcast.duration,
            created_at=podcast.created_at
        )

    def get_all_categories(self, limit: int, page: int) -> PaginatedCategoryResponse:
        offset = (page-1) * limit
        categories = self.category_repo.get_all_categories(limit, offset)
        total = self.category_repo.count_categories()
        items = []
        for category in categories:
            item = self._to_category_response(category)
            items.append(item)

        pages = (total + limit - 1)//limit
        return PaginatedCategoryResponse(
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            items=items
        )

    def get_category_detail(self, id: int) -> CategoryResponse:
        category = self.category_repo.get_category_by_id(id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        return self._to_category_response(category)

    def get_popular_categories(self, limit: int) -> List[CategoryResponse]:
        categories = self.category_repo.get_popular_categories(limit)
        return [self._to_category_response(category) for category in categories]

    def get_category_top_podcasts(self, category_id: int, limit: int) -> List[PodcastDisplay]:
        category = self.category_repo.get_category_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        podcasts = self.category_repo.get_category_top_podcasts(
            category_id, limit)
        return [self._to_podcast_display(podcast) for podcast in podcasts]

    def get_category_top_podcasts(self, category_id: int, limit: int) -> List[PodcastDisplay]:
        category = self.category_repo.get_category_by_id(category_id)
        if not category:
            raise HTTPException(404, "Category not found")

        podcasts = self.category_repo.get_category_trending_podcasts(
            category_id, limit)
        return [self._to_podcast_display(podcast) for podcast in podcasts]

    def get_category_trending_podcasts(self, category_id: int, limit: int) -> List[PodcastDisplay]:
        category = self.category_repo.get_category_by_id(category_id)
        if not category:
            raise HTTPException(404, "Category not found")

        podcasts = self.category_repo.get_category_trending_podcasts(
            category_id, limit)
        return [self._to_podcast_display(p) for p in podcasts]
