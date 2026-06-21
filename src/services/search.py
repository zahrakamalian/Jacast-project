from typing import List
from fastapi import HTTPException

from src.repository.user import UserRepository
from src.repository.podcast import PodcastRepository
from src.repository.playlist import PlaylistRepository
from src.repository.category import CategoryRepository
from src.data.models.podcast import Podcast
from src.data.models.user import User
from src.data.models.playlist import Playlist
from src.schemas.search import (SearchPodcastItem, SearchPodcastResponse, SearchEpisodeItem, SearchEpisodeResponse,
                                SearchPlaylistItem, SearchPlaylistResponse, SearchUserItem, SearchUserResponse, SearchResponse,
                                SearchCategoryResult, CategoryPodcastsResponse, BrowseResponse)
from src.schemas.podcast import PodcastDisplay
from src.schemas.category import PaginatedCategoryResponse, CategoryResponse
from src.services.podcast import PodcastService
from src.services.category import CategoryService


class SearchService:
    def __init__(self, user_repo: UserRepository, podcast_repo: PodcastRepository, playlist_repo: PlaylistRepository,
                 category_repo: CategoryRepository, podcast_service: PodcastService, category_service: CategoryService):
        self.user_repo = user_repo
        self.podcast_repo = podcast_repo
        self.playlist_repo = playlist_repo
        self.category_repo = category_repo
        self.podcast_service = podcast_service
        self.category_service = category_service

    def _search_category(self, repo_method, count_method, query, offset, limit, converter_func):
        items = repo_method(query, offset, limit)
        total = count_method(query)
        converted_items = [converter_func(item) for item in items]
        return converted_items, total

    def _to_search_podcast_item(self, podcast: Podcast) -> SearchPodcastItem:
        return SearchPodcastItem(
            id=podcast.id,
            title=podcast.title,
            channel_name=podcast.channel.display_name,
            cover_art_url=podcast.cover_art_url,
            description=podcast.description,
            created_at=podcast.created_at
        )

    def _to_search_episode_item(self, episode: Podcast) -> SearchEpisodeItem:
        return SearchEpisodeItem(
            id=episode.id,
            title=episode.title,
            channel_name=episode.channel.display_name,
            cover_art_url=episode.cover_art_url,
            duration=episode.duration,
            created_at=episode.created_at
        )

    def _to_search_user_item(self, user: User) -> SearchUserItem:
        return SearchUserItem(
            id=user.id,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            is_channel=user.is_channel
        )

    def _to_search_playlist_item(self, playlist: Playlist) -> SearchPlaylistItem:
        episodes_count = self.playlist_repo.count_playlist_episodes(
            playlist.id)
        return SearchPlaylistItem(
            id=playlist.id,
            title=playlist.title,
            description=playlist.description,
            cover_art_url=playlist.cover_art_url,
            owner_name=playlist.user.display_name,
            owner_avatar=playlist.user.avatar_url,
            episodes_count=episodes_count,
            created_at=playlist.created_at
        )

    def _to_podcast_display(self, podcast) -> PodcastDisplay:
        return PodcastDisplay(
            id=podcast.id,
            title=podcast.title,
            channel_name=podcast.channel.display_name,
            cover_art_url=podcast.cover_art_url,
            duration=podcast.duration,
            created_at=podcast.created_at
        )

    def search_all(self, q: str, type: str, limit: int, page: int) -> SearchResponse:
        if not q or len(q) < 2:
            raise HTTPException(
                status_code=400, detail="Search query must be at least 2 characters")

        offset = (page-1) * limit
        results = {}
        total_all = 0

        if type in ["all", "podcasts"]:
            podcasts, total = self._search_category(self.podcast_repo.search_podcasts, self.podcast_repo.count_search_podcasts,
                                                    q, offset, limit, self._to_search_podcast_item)
            results["podcasts"] = SearchCategoryResult(
                items=podcasts, total=total)
            total_all += total

        if type in ["all", "episodes"]:
            episodes, total = self._search_category(self.podcast_repo.search_episodes, self.podcast_repo.count_search_episodes,
                                                    q, offset, limit, self._to_search_episode_item)
            results["episodes"] = SearchCategoryResult(
                items=episodes, total=total)
            total_all += total

        if type in ["all", "users"]:
            users, total = self._search_category(self.user_repo.search_users, self.user_repo.count_search_users,
                                                 q, offset, limit, self._to_search_user_item)
            results["users"] = SearchCategoryResult(items=users, total=total)
            total_all += total

        if type in ["all", "playlists"]:
            playlists, total = self._search_category(self.playlist_repo.search_public_playlists, self.playlist_repo.count_search_public_playlists,
                                                     q, offset, limit, self._to_search_playlist_item)
            results["playlists"] = SearchCategoryResult(
                items=playlists, total=total)
            total_all += total

        pages = (total_all + limit - 1) // limit if total_all > 0 else 0

        return SearchResponse(
            query=q,
            total=total_all,
            page=page,
            limit=limit,
            pages=pages,
            podcasts=results.get(
                "podcasts", SearchCategoryResult(items=[], total=0)),
            episodes=results.get(
                "episodes", SearchCategoryResult(items=[], total=0)),
            users=results.get(
                "users", SearchCategoryResult(items=[], total=0)),
            playlists=results.get(
                "playlists", SearchCategoryResult(items=[], total=0))
        )

    def search_podcasts(self, q: str, limit: int, page: int) -> SearchPodcastResponse:
        if not q or len(q) < 2:
            raise HTTPException(
                status_code=400, detail="Search query must be at least 2 characters")

        offset = (page-1) * limit
        items, total = self._search_category(self.podcast_repo.search_podcasts,
                                             self.podcast_repo.count_search_podcasts,
                                             q, offset, limit, self._to_search_podcast_item
                                             )

        pages = (total + limit - 1)//limit
        return SearchPodcastResponse(
            query=q,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            items=items
        )

    def search_episodes(self, q: str, limit: int, page: int) -> SearchEpisodeResponse:
        if not q or len(q) < 2:
            raise HTTPException(
                status_code=400, detail="Search query must be at least 2 characters")

        offset = (page-1) * limit
        items, total = self._search_category(self.podcast_repo.search_episodes,
                                             self.podcast_repo.count_search_episodes,
                                             q, offset, limit,
                                             self._to_search_episode_item
                                             )

        pages = (total + limit - 1)//limit
        return SearchEpisodeResponse(
            query=q,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            items=items
        )

    def search_users(self, q: str, limit: int, page: int) -> SearchUserResponse:
        if not q or len(q) < 2:
            raise HTTPException(
                status_code=400, detail="Search query must be at least 2 characters")

        offset = (page-1) * limit
        items, total = self._search_category(self.user_repo.search_users,
                                             self.user_repo.count_search_users,
                                             q, offset, limit,
                                             self._to_search_user_item
                                             )

        pages = (total + limit - 1)//limit
        return SearchUserResponse(
            query=q,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            items=items
        )

    def search_playlists(self, q: str, limit: int, page: int) -> SearchPlaylistResponse:
        if not q or len(q) < 2:
            raise HTTPException(
                status_code=400, detail="Search query must be at least 2 characters")

        offset = (page-1) * limit
        items, total = self._search_category(self.playlist_repo.search_public_playlists,
                                             self.playlist_repo.count_search_public_playlists,
                                             q, offset, limit,
                                             self._to_search_playlist_item
                                             )

        pages = (total + limit - 1)//limit
        return SearchPlaylistResponse(
            query=q,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            items=items
        )

    def get_browse(self) -> BrowseResponse:
        new_podcasts = self.podcast_repo.get_new_podcasts(5)
        new_releases = [self._to_podcast_display(p) for p in new_podcasts]

        trending_podcasts = self.podcast_repo.get_trending_podcasts(5)
        trending = [self._to_podcast_display(p) for p in trending_podcasts]

        popular_podcasts = self.podcast_repo.get_top_ranked_podcasts(5)
        popular = [self._to_podcast_display(p) for p in popular_podcasts]

        categories = self.category_repo.get_all_categories(limit=4, offset=0)
        category_response = [
            self.category_service._to_category_response(c) for c in categories]

        return BrowseResponse(
            new_releases=new_releases,
            trending=trending,
            popular=popular,
            categories=category_response,
        )

    def get_categories(self, limit: int, page: int) -> PaginatedCategoryResponse:
        return self.category_service.get_all_categories(limit, page)

    def get_category_detail(self, id: int) -> CategoryResponse:
        return self.category_service.get_category_detail(id)

    def get_category_podcasts(self, category_id: int, limit: int, page: int) -> CategoryPodcastsResponse:
        category = self.category_repo.get_category_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        podcast_ids = self.category_repo.get_category_podcast_ids(category_id)
        if not podcast_ids:
            return CategoryPodcastsResponse(
                category_id=category.id,
                category_name=category.name,
                total=0,
                page=page,
                limit=limit,
                pages=0,
                items=[]
            )

        offset = (page - 1) * limit
        podcasts = self.podcast_repo.get_podcasts_by_ids(
            podcast_ids, limit, offset)
        total = len(podcast_ids)
        pages = (total + limit - 1) // limit
        items = [self._to_podcast_display(p) for p in podcasts]

        return CategoryPodcastsResponse(
            category_id=category.id,
            category_name=category.name,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            items=items
        )

    def get_trending(self, limit: int) -> List[PodcastDisplay]:
        return self.podcast_service.get_trending_podcasts(limit)

    def get_popular(self, limit: int) -> List[PodcastDisplay]:
        return self.podcast_service.get_top_ranked_podcasts(limit)
