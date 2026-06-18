from datetime import datetime, timezone
import os
import uuid

from fastapi import HTTPException, UploadFile
from typing import List

from src.repository.user import UserRepository
from src.schemas.user import UserDisplay, UpdateUser, ChangePassword, ChangeEmail
from src.models.user import User, FollowUser
from src.api.v1.security import verify_password_hash, get_password_hash
from src.config import settings


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def current_user(self, user: User) -> UserDisplay:
        return UserDisplay.model_validate(user)

    def update_user(self, data: UpdateUser, user: User) -> User:
        if not data:
            raise HTTPException(
                status_code=400, detail="Updated Field Required")
        return self.user_repo.update_user(user, display_name=data.display_name,
                                          bio=data.bio, is_channel=data.is_channel)

    def delete_user(self, user: User) -> None:
        self.user_repo.delete_user_avatar_file(user)
        self.user_repo.delete_user_sessions(user.id)
        self.user_repo.delete_user_follows(user.id)
        self.user_repo.delete_user_tokens(user.id)
        self.user_repo.delete_user_permanently(user)

    async def upload_avatar(self, user: User, file: UploadFile):
        if file is None:
            raise HTTPException(status_code=400, detail="No file uploaded")

        valid_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        suffixes = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp"
        }

        if file.content_type not in valid_types:
            raise HTTPException(
                status_code=415, detail="Unsupported media type. Only JPEG, PNG, GIF, WEBP are allowed")

        MAX_FILE_SIZE = 5 * 1024 * 1024
        extension = suffixes[file.content_type]
        unique_name = f"avatar_{user.id}_{uuid.uuid4().hex}{extension}"

        file_path = settings.AVATAR_UPLOAD_DIR / unique_name
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(400, "File too large. Max 5MB")

        with open(file_path, "wb") as f:
            f.write(content)

        if os.getenv("RENDER"):
            image_url = f"/temp-avatars/{unique_name}"
        else:
            image_url = f"/resources/uploads/images/{unique_name}"

        if user.avatar_url:
            old_file_name = user.avatar_url.split('/')[-1]
            old_file_path = settings.AVATAR_UPLOAD_DIR / old_file_name
            if old_file_path.exists():
                old_file_path.unlink()

        user.avatar_url = image_url
        self.user_repo.commit_session()

    def change_password(self, data: ChangePassword, user: User) -> None:
        if not verify_password_hash(data.current_password, user.password_hash):
            raise HTTPException(status_code=401, detail="Incorrect password")
        if verify_password_hash(data.new_password, user.password_hash):
            raise HTTPException(
                400, "New password must be different from current password")
        if data.new_password != data.confirm_password:
            raise HTTPException(
                status_code=400, detail="New password and confirm password do not match")

        new_hashed_password = get_password_hash(data.new_password)
        user.password_hash = new_hashed_password

        self.user_repo.commit_session()

    def change_email(self, data: ChangeEmail, user: User) -> None:
        if data.email != user.email:
            raise HTTPException(
                status_code=401, detail="Incorrect Email address")
        if data.email == data.new_email:
            raise HTTPException(
                status_code=400, detail="New email must be different from current email")

        user.email = data.new_email
        self.user_repo.commit_session()

    def public_profile(self, id: int) -> UserDisplay:
        user = self.user_repo.get_user_by_id(id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserDisplay.model_validate(user)

    def get_followers(self, id: int) -> List[UserDisplay]:
        user = self.user_repo.get_user_by_id(id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        followers = self.user_repo.get_followers(id)
        return [UserDisplay.model_validate(f) for f in followers]

    def get_following(self, id: int) -> List[UserDisplay]:
        user = self.user_repo.get_user_by_id(id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        followings = self.user_repo.get_following(id)
        return [UserDisplay.model_validate(f) for f in followings]

    def follow_user(self, id: int, user: User) -> None:
        target_user = self.user_repo.get_user_by_id(id)
        if not target_user:
            raise HTTPException(
                status_code=404, detail="Target User not found")
        if id == user.id:
            raise HTTPException(
                status_code=400, detail="You can not follow yourself")

        follow_record = self.user_repo.get_follow(user.id, id)
        if follow_record:
            raise HTTPException(status_code=400, detail="Already followed")

        new_entry = FollowUser(follower_id=user.id,
                               following_id=id,
                               followed_at=datetime.now(timezone.utc))
        self.user_repo.follow_user(new_entry)

    def unfollow_user(self, id: int, user: User) -> None:
        target_user = self.user_repo.get_user_by_id(id)
        if not target_user:
            raise HTTPException(
                status_code=404, detail="Target User not found")
        if id == user.id:
            raise HTTPException(
                status_code=400, detail="You can not Unfollow yourself")

        follow_record = self.user_repo.get_follow(user.id, id)
        if not follow_record:
            raise HTTPException(400, "You are not following this user")

        self.user_repo.unfollow_user(follow_record.id)
