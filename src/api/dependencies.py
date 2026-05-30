from fastapi import HTTPException, Depends
from typing import Annotated

from api.security import decode_token, oauth2_bearer
from models.user import User
from repository.user import UserRepository
from services.auth import AuthService
from services.user import UserService
from connections.database import db_dependency


def get_user_repository(db: db_dependency) -> UserRepository:
    return UserRepository(db)


def get_auth_service(repository: Annotated[UserRepository, Depends(get_user_repository)]) -> AuthService:
    return AuthService(repository)


def get_user_service(repository: Annotated[UserRepository, Depends(get_user_repository)]) -> UserService:
    return UserService(repository)


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
