from pathlib import Path
import os


from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


from src.database.database import engine, Base
from src.config import BASE_DIR
from src.api.v1 import (auth_router, user_router, podcast_router, subscription_router,
                     playlist_router, search_router, discover_router, category_router
                     )


app = FastAPI(
    title="Jacast",
    version="1.0.0",
)


app.include_router(auth_router, prefix='/auth', tags=["auth"])
app.include_router(user_router, prefix='/users', tags=["users"])
app.include_router(podcast_router, prefix='/podcasts', tags=["podcasts"])
app.include_router(subscription_router,
                   prefix='/subscriptions', tags=["subscriptions"])
app.include_router(playlist_router, prefix='/playlists', tags=["playlists"])
app.include_router(search_router, prefix='/search', tags=["search"])
app.include_router(discover_router, prefix='/discover', tags=["discover"])
app.include_router(category_router, prefix='/categories', tags=["categories"])


if not os.getenv("RENDER"):
    app.mount("/resources", StaticFiles(directory=str(BASE_DIR /
              "resources")), name="resources")
