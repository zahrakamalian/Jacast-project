from uuid import uuid4
from src.data.models.user import User


def create_user_data(**kwargs):
    data = {
        "email": f"{uuid4().hex}@example.com",
        "display_name": "test_user",
        "password": "StrongPassword123!",
        "avatar_url": None,
        "bio": None,
        "is_channel": False
    }
    data.update(kwargs)
    return data


def create_login_data(email: str, password: str):
    return {
        "username": email,
        "password": password
    }


def create_channel_data(emali: str = "channel@test.com", display_name: str = "Tech Channel", password_hash: str = "hashed"):
    return User(
        email=emali,
        display_name=display_name,
        password_hash=password_hash,
        is_verified=True,
        is_channel=True,
    )
