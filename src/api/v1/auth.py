from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated, List, Union

from src.schemas.user import (UserCreate, UserDisplay, Token, SessionResponse,
                              ResetPassword, TwoFAUri)
from src.models.user import User
from src.api.v1.dependencies import get_current_user, get_auth_service
from src.api.v1.security import decode_token, oauth2_bearer
from src.services.auth import AuthService

router = APIRouter()


@router.post('/register', response_model=UserDisplay)
def register(service: Annotated[AuthService, Depends(get_auth_service)],
             user_data: UserCreate):
    return service.register_user(user_data)


@router.post('/login', response_model=Union[Token, dict])
def login(data: Annotated[OAuth2PasswordRequestForm, Depends()],
          service: Annotated[AuthService, Depends(get_auth_service)]):
    return service.login_user(data)


@router.post('/login/verify-2fa', response_model=Token)
def verify_2fa_login(service: Annotated[AuthService, Depends(get_auth_service)],
                     temp_token: str = Body(..., embed=True),
                     code: str = Body(..., embed=True)):
    return service.verify_2FA_login(temp_token, code)


@router.post('/logout')
def logout(token: Annotated[str, Depends(oauth2_bearer)],
           service: Annotated[AuthService, Depends(get_auth_service)],
           user: Annotated[User, Depends(get_current_user)]):
    payload = decode_token(token)
    service.logout_user(user, payload.jti)

    return {"detail": "Successfully logged out"}


@router.post('/refresh-token', response_model=Token)
def refresh_token(service: Annotated[AuthService, Depends(get_auth_service)],
                  token: str = Body(..., embed=True)):
    return service.refresh_token(token)


@router.post('/forgot-password')
def forget_password(service: Annotated[AuthService, Depends(get_auth_service)],
                    email: str = Body(..., embed=True)):
    return service.forget_password(email)


@router.post('/reset-password')
def reset_password(service: Annotated[AuthService, Depends(get_auth_service)],
                   data: ResetPassword):
    service.reset_password(data)
    return {"message": "Password changed successfully"}


@router.post('/verify-email')
def verify_email(service: Annotated[AuthService, Depends(get_auth_service)],
                 email: str = Body(..., embed=True)):
    token = service.request_email_verification(email)
    return {"message": "Verification token send successfully", "token": token["token"]}


@router.get('/verify-email/{token}')
def verify_email_token(service: Annotated[AuthService, Depends(get_auth_service)],
                       token: str):
    service.verify_email(token)
    return {"message": "Account verified successfully"}


@router.post('/two-factor/enable', response_model=TwoFAUri)
def enable_two_factor(service: Annotated[AuthService, Depends(get_auth_service)],
                      user: Annotated[User, Depends(get_current_user)]):
    return service.enable_2FA(user)


@router.post('/two-factor/verify')
def verify_two_factor(service: Annotated[AuthService, Depends(get_auth_service)],
                      user: Annotated[User, Depends(get_current_user)],
                      code: str = Body(..., embed=True)):
    service.verify_2FA(user, code)
    return {"message": "2FA activated and verified successfully"}


@router.delete("/sessions/{id}")
def delete_session(id: int,
                   service: Annotated[AuthService, Depends(get_auth_service)],
                   user: Annotated[User, Depends(get_current_user)]):
    service.delete_session(id, user)
    return {"message": "Session deactivated successfully"}


@router.get('/sessions', response_model=List[SessionResponse])
def active_sessions(service: Annotated[AuthService, Depends(get_auth_service)],
                    user: Annotated[User, Depends(get_current_user)]):
    return service.active_session(user)
