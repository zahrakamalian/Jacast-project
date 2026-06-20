from fastapi import HTTPException, Depends
from typing import Annotated, Optional

from src.api.v1.security import decode_token, oauth2_bearer
from src.data.models.user import User
from src.repository.user import UserRepository
from src.repository.podcast import PodcastRepository
from src.repository.subscription import SubscriptionRepository
from src.repository.category import CategoryRepository
from src.repository.playlist import PlaylistRepository
from src.services.auth import AuthService
from src.services.user import UserService
from src.services.podcast import PodcastService
from src.services.subscription import SubscriptionService
from src.services.playlist import PlaylistService
from src.services.search import SearchService
from src.services.category import CategoryService
from src.data.database.database import db_dependency


def get_user_repository(db: db_dependency) -> UserRepository:
    return UserRepository(db)


def get_podcast_repository(db: db_dependency) -> PodcastRepository:
    return PodcastRepository(db)


def get_subscription_repository(db: db_dependency) -> SubscriptionRepository:
    return SubscriptionRepository(db)


def get_playlist_repository(db: db_dependency) -> PlaylistRepository:
    return PlaylistRepository(db)


def get_category_repository(db: db_dependency) -> CategoryRepository:
    return CategoryRepository(db)


def get_auth_service(repository: Annotated[UserRepository, Depends(get_user_repository)]) -> AuthService:
    return AuthService(repository)


def get_user_service(repository: Annotated[UserRepository, Depends(get_user_repository)]) -> UserService:
    return UserService(repository)


def get_podcast_service(repository: Annotated[PodcastRepository, Depends(get_podcast_repository)],
                        user_repo: Annotated[UserRepository, Depends(get_user_repository)],
                        sub_repo: Annotated[SubscriptionRepository, Depends(get_subscription_repository)]) -> PodcastService:
    return PodcastService(user_repo, repository, sub_repo)


def get_subscription_service(sub_repo: Annotated[SubscriptionRepository, Depends(get_subscription_repository)],
                             user_repo: Annotated[UserRepository, Depends(get_user_repository)]) -> SubscriptionService:
    return SubscriptionService(sub_repo, user_repo)


def get_playlist_service(user_repo: Annotated[UserRepository, Depends(get_user_repository)],
                         playlist_repo: Annotated[PlaylistRepository, Depends(get_playlist_repository)],
                         podcast_repo: Annotated[PodcastRepository, Depends(get_podcast_repository)]) -> PlaylistService:
    return PlaylistService(user_repo, playlist_repo, podcast_repo)


def get_category_service(category_repo: Annotated[CategoryRepository, Depends(get_category_repository)]) -> CategoryService:
    return CategoryService(category_repo)


def get_search_service(user_repo: Annotated[UserRepository, Depends(get_user_repository)],
                       podcast_repo: Annotated[PodcastRepository, Depends(get_podcast_repository)],
                       playlist_repo: Annotated[PlaylistRepository, Depends(get_playlist_repository)],
                       category_repo: Annotated[CategoryRepository, Depends(get_category_repository)],
                       podcast_service: Annotated[PodcastService, Depends(get_podcast_service)],
                       category_service: Annotated[CategoryService, Depends(get_category_service)]) -> SearchService:
    return SearchService(user_repo, podcast_repo, playlist_repo, category_repo, podcast_service, category_service)


async def get_current_user_optional(token: Annotated[str, Depends(oauth2_bearer)],
                                    repository: Annotated[UserRepository, Depends(get_user_repository)]) -> Optional[User]:
    if not token:
        return None
    try:
        payload = decode_token(token)
        if not payload or payload.type != "access":
            return None

        user = repository.get_user_by_id(int(payload.sub))
        if not user or not user.is_verified:
            return None
        return user

    except Exception:
        return None


def get_current_user(token: Annotated[str | None, Depends(oauth2_bearer)],
                     repository: Annotated[UserRepository, Depends(get_user_repository)]) -> User:

    if token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_token(token)
    if payload.type != "access":
        raise HTTPException(status_code=401, detail="Invalid token type",)

    user = repository.get_user_by_id(int(payload.sub))
    if not user:
        raise HTTPException(
            status_code=404, detail="Invalid token: user not found")

    if not user.is_verified:
        raise HTTPException(
            status_code=403, detail="Invalid token: user not verified")
    return user
