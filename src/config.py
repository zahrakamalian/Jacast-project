import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "sqlite:///./jacast.db"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    TEMP_2FA_TOKEN_EXPIRE_MINUTES: int = 5

    model_config = SettingsConfigDict(env_file=str(ENV_FILE))

    @property
    def AVATAR_UPLOAD_DIR(self) -> Path:
        if os.getenv("RENDER"):
            return Path("/tmp/avatars")
        else:
            return BASE_DIR / "resources" / "uploads" / "images"

    @property
    def PODCAST_AUDIO_DIR(self) -> Path:
        if os.getenv("RENDER"):
            return Path("/tmp/podcast_audio")
        else:
            return BASE_DIR / "resources" / "uploads" / "audio"

    @property
    def PODCAST_COVER_DIR(self) -> Path:
        if os.getenv("RENDER"):
            return Path("/tmp/podcast_covers")
        else:
            return BASE_DIR / "resources" / "uploads" / "images"

    def ensure_directories(self):
        self.AVATAR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.PODCAST_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        self.PODCAST_COVER_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
