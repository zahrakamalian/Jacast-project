from api.auth import router as auth_router
from api.user import router as user_router
from api.podcast import router as podcast_router
from api.subscription import router as subscription_router
from api.playlist import router as playlist_router

__all__ = ["auth_router",
           "user_router",
           "podcast_router",
           "subscription_router",
           "playlist_router"]
