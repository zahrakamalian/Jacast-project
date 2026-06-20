from datetime import datetime, timezone
from src.data.models.playlist import Playlist
from src.data.models.playlist import PlaylistPodcast


def create_playlist_data(user_id: int, title: str = "My Playlist",
                         description: str = "Test playlist", cover_art_url: str | None = None,
                         is_public: bool = True):
    return Playlist(
        user_id=user_id,
        title=title,
        description=description,
        cover_art_url=cover_art_url,
        is_public=is_public,
        created_at=datetime.now(timezone.utc)
    )


def create_playlist_episode(
    playlist_id,
    podcast_id,
    position=0,
):
    return PlaylistPodcast(
        playlist_id=playlist_id,
        podcast_id=podcast_id,
        position=position,
    )
