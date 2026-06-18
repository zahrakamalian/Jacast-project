import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from typing import Annotated, List

from src.schemas.user import UserDisplay, UpdateUser, ChangePassword, ChangeEmail
from src.models.user import User
from src.api.v1.dependencies import get_current_user, get_user_service
from src.services.user import UserService
from src.config import settings


router = APIRouter()


@router.get("/me", response_model=UserDisplay)
def current_user(user: Annotated[User, Depends(get_current_user)],
                 service: Annotated[UserService, Depends(get_user_service)]):
    return service.current_user(user)


@router.patch("/me", response_model=UserDisplay)
def update_profile(data: UpdateUser, user: Annotated[User, Depends(get_current_user)],
                   service: Annotated[UserService, Depends(get_user_service)]):
    return service.update_user(data, user)


@router.delete("/me")
def delete_user(user: Annotated[User, Depends(get_current_user)],
                service: Annotated[UserService, Depends(get_user_service)]):
    service.delete_user(user)
    return {"message": "Deleted User Successfully"}


@router.patch("/me/avatar")
async def update_avatar(user: Annotated[User, Depends(get_current_user)],
                        service: Annotated[UserService, Depends(get_user_service)],
                        file: UploadFile = File(None)):
    await service.upload_avatar(user, file)
    return {"message": "Avatar uploaded successfully"}


@router.patch("/me/password")
def change_password(password: ChangePassword,
                    user: Annotated[User, Depends(get_current_user)],
                    service: Annotated[UserService, Depends(get_user_service)]):
    service.change_password(password, user)
    return {"message": "Password changed successfully"}


@router.patch("/me/email")
def change_email(data: ChangeEmail,
                 user: Annotated[User, Depends(get_current_user)],
                 service: Annotated[UserService, Depends(get_user_service)]):
    service.change_email(data, user)
    return {"message": "Email changed successfully"}


@router.get("/{id}", response_model=UserDisplay)
def public_profile(id: int,
                   service: Annotated[UserService, Depends(get_user_service)]):
    return service.public_profile(id)


@router.get("/{id}/followers", response_model=List[UserDisplay])
def get_followers(id: int,
                  service: Annotated[UserService, Depends(get_user_service)]):
    return service.get_followers(id)


@router.get("/{id}/following", response_model=List[UserDisplay])
def get_following(id: int,
                  service: Annotated[UserService, Depends(get_user_service)]):
    return service.get_following(id)


@router.post("/{id}/follow")
def follow_user(id: int,
                user: Annotated[User, Depends(get_current_user)],
                service: Annotated[UserService, Depends(get_user_service)]):
    service.follow_user(id, user)
    return {"message": "Successfully followed"}


@router.delete("/{id}/unfollow")
def unfollow_user(id: int,
                  user: Annotated[User, Depends(get_current_user)],
                  service: Annotated[UserService, Depends(get_user_service)]):
    service.unfollow_user(id, user)
    return {"message": "Successfully Unfollowed!"}


@router.get("/temp-avatars/{filename}")
async def get_temp_avatar(filename: str):
    if not os.getenv("RENDER"):
        file_path = settings.AVATAR_UPLOAD_DIR / filename
    else:
        file_path = Path("/tmp/avatars") / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Avatar not found")

    return FileResponse(file_path)
