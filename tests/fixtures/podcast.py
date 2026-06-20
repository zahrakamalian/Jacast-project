from datetime import datetime, timezone
from io import BytesIO

from src.data.models.podcast import Podcast


def create_podcast_data(channel_id: int, title: str = "Episode 1",
                        description: str = "Test podcast", cover_art_url: str = "/covers/test.png",
                        audio_url: str = "/audio/test.mp3", duration: int = 1000, play_count: int = 100):
    return Podcast(
        channel_id=channel_id,
        title=title,
        description=description,
        cover_art_url=cover_art_url,
        audio_url=audio_url,
        duration=duration,
        play_count=play_count,
        created_at=datetime.now(timezone.utc)
    )


def create_audio_upload(filename: str = "test.mp3", content: bytes = b"fake mp3 content"):
    return (
        filename,
        BytesIO(content),
        "audio/mpeg"
    )


def create_image_upload(filename: str = "cover.png", content: bytes = b"fake png content"):
    return (
        filename,
        BytesIO(content),
        "image/png",
    )
