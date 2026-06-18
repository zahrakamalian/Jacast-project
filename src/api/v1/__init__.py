from .auth import router as auth_router
from .user import router as user_router
from .podcast import router as podcast_router
from .subscription import router as subscription_router
from .playlist import router as playlist_router
from .search import search_router, discover_router
from .category import router as category_router

__all__ = ["auth_router",
           "user_router",
           "podcast_router",
           "subscription_router",
           "playlist_router",
           "search_router",
           "discover_router",
           "category_router"
           ]
