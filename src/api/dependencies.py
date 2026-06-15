from fastapi import HTTPException, Depends
from typing import Annotated, Optional

from api.security import decode_token, oauth2_bearer
from models.user import User
from repository.user import UserRepository
from repository.podcast import PodcastRepository
from repository.subscription import SubscriptionRepository
from repository.playlist import PlaylistRepository
from services.auth import AuthService
from services.user import UserService
from services.podcast import PodcastService
from services.subscription import SubscriptionService
from services.playlist import PlaylistService
from connections.database import db_dependency


def get_user_repository(db: db_dependency) -> UserRepository:
    return UserRepository(db)


def get_podcast_repository(db: db_dependency) -> PodcastRepository:
    return PodcastRepository(db)


def get_subscription_repository(db: db_dependency) -> SubscriptionRepository:
    return SubscriptionRepository(db)


def get_playlist_repository(db: db_dependency) -> PlaylistRepository:
    return PlaylistRepository(db)


def get_auth_service(repository: Annotated[UserRepository, Depends(get_user_repository)]) -> AuthService:
    return AuthService(repository)


def get_user_service(repository: Annotated[UserRepository, Depends(get_user_repository)]) -> UserService:
    return UserService(repository)


def get_podcast_service(repository: Annotated[PodcastRepository, Depends(get_podcast_repository)]) -> PodcastService:
    return PodcastService(repository)


def get_subscription_service(sub_repo: Annotated[SubscriptionRepository, Depends(get_subscription_repository)],
                             user_repo: Annotated[UserRepository, Depends(get_user_repository)]) -> SubscriptionService:
    return SubscriptionService(sub_repo, user_repo)


def get_playlist_service(user_repo: Annotated[UserRepository, Depends(get_user_repository)], playlist_repo: Annotated[PlaylistRepository, Depends(get_playlist_repository)],
                         podcast_repo: Annotated[PodcastRepository, Depends(get_podcast_repository)]) -> PlaylistService:
    return PlaylistService(user_repo, playlist_repo, podcast_repo)


async def get_current_user_optional(token: Annotated[str, Depends(oauth2_bearer)], repository: Annotated[UserRepository, Depends(get_user_repository)]) -> Optional[User]:
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


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], repository: Annotated[UserRepository, Depends(get_user_repository)]) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=401, detail="Invalid token")

    if payload.type != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user = repository.get_user_by_id(int(payload.sub))

    if not user:
        raise HTTPException(
            status_code=404, detail="Invalid token: user not found")
    if not user.is_verified:
        raise HTTPException(
            status_code=403, detail="Invalid token: user not verified")
    return user
