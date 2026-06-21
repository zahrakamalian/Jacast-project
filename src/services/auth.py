import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import pyotp

from src.repository.user import UserRepository
from src.schemas.user import UserCreate, ResetPassword
from src.data.models.user import TokenType, User, PasswordResetToken, EmailVerificationToken
from src.data.models.user import UserSession
from src.api.v1.security import (get_password_hash, hash_refresh_token, create_access_token, create_refresh_token,
                                 decode_token, create_temp_2fa_token, verify_password_hash, verify_refresh_token)
from src.config import settings


def is_expired(expires_at: datetime) -> bool:
    if expires_at.tzinfo is None: 
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) > expires_at


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def _create_final_token(self, user: User) -> dict:
        try:
            jti = str(uuid.uuid4())
            expires_at = (datetime.now(timezone.utc) +
                          timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
            access_token = create_access_token(user.id)
            refresh_token = create_refresh_token(user.id, jti)
            hashed_refresh_token = hash_refresh_token(refresh_token)
            new_session = UserSession(
                user_id=user.id,
                jti=jti,
                hashed_refresh_token=hashed_refresh_token,
                is_active=True,
                expires_at=expires_at,
            )
            self.user_repo.create_session(new_session)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        except Exception:
            raise HTTPException(
                status_code=500, detail="Could not create login session")

    def register_user(self, user_data: UserCreate) -> User:
        existing_user = self.user_repo.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=400, detail="Email Already Registered")

        hashed_password = get_password_hash(user_data.password)
        new_user = User(email=user_data.email,
                        display_name=user_data.display_name,
                        avatar_url=user_data.avatar_url,
                        bio=user_data.bio,
                        is_channel=user_data.is_channel,
                        password_hash=hashed_password
                        )

        return self.user_repo.create_user(new_user)

    def login_user(self, form_data: OAuth2PasswordRequestForm) -> dict:
        user = self.user_repo.get_user_by_email(form_data.username)
        if not user or not verify_password_hash(form_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Unauthorized")
        if user.is_2FA_enabled:
            temp_token = create_temp_2fa_token(user.id)
            return {
                "requires_2fa": True,
                "temp_token": temp_token,
                "message": "2FA code required"
            }

        return self._create_final_token(user)

    def refresh_token(self, token: str) -> dict:
        payload = decode_token(token)
        if not payload or payload.type != TokenType.REFRESH:
            raise HTTPException(status_code=401, detail="Invalid token")

        session = self.user_repo.get_session_by_jti(payload.jti)
        if not session or not session.is_active:
            raise HTTPException(
                status_code=401, detail="Invalid or inactive session")

        if not verify_refresh_token(token, session.hashed_refresh_token):
            raise HTTPException(status_code=401, detail="Invalid token")

        user = self.user_repo.get_user_by_id(session.user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        session.is_active = False
        self.user_repo.commit_session()

        return self._create_final_token(user)

    def logout_user(self, user: User, jti: str = None) -> None:
        if jti:
            session = self.user_repo.get_session_by_jti(jti)
        else:
            session = self.user_repo.get_active_session_by_user_id(user.id)
        if session and session.user_id == user.id:
            session.is_active = False
            self.user_repo.commit_session()

    def forget_password(self, email: str) -> dict:
        user = self.user_repo.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=200, detail="If email exists, token sent")

        self.user_repo.delete_old_reset_tokens_by_id(user)

        password_token = str(uuid.uuid4())
        expires = datetime.now(timezone.utc) + timedelta(minutes=15)

        new_password_token = PasswordResetToken(user_id=user.id,
                                                token=password_token,
                                                expires_at=expires)

        self.user_repo.create_reset_token(new_password_token)

        return {"token": password_token, "exp": expires}

    def reset_password(self, data: ResetPassword) -> None:
        token = self.user_repo.get_reset_token_by_string(data.token)
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")

        if is_expired(token.expires_at):
            raise HTTPException(status_code=400, detail="Token has expired")

        user = self.user_repo.get_user_by_id(token.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_hashed_password = get_password_hash(data.new_password)
        user.password_hash = new_hashed_password

        self.user_repo.commit_session()
        self.user_repo.delete_old_reset_tokens_by_id(user)

    def request_email_verification(self, email: str) -> dict:
        user = self.user_repo.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.is_verified:
            raise HTTPException(
                status_code=400, detail="This Account is already verified")

        self.user_repo.delete_old_verification_tokens_by_id(user)
        email_token = str(uuid.uuid4())
        expires = datetime.now(timezone.utc) + timedelta(hours=2)

        new_token = EmailVerificationToken(user_id=user.id,
                                           token=email_token,
                                           expires_at=expires)

        self.user_repo.create_verification_token(new_token)
        return {"token": email_token}

    def verify_email(self, token: str) -> dict:
        existing_token = self.user_repo.get_verification_token(token)
        if not existing_token:
            raise HTTPException(status_code=404, detail="Token not found")

        if is_expired(existing_token.expires_at):
            raise HTTPException(status_code=400, detail="Token has expired")

        user = self.user_repo.get_user_by_id(existing_token.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.is_verified = True
        self.user_repo.commit_session()
        self.user_repo.delete_verification_token(existing_token)

    def enable_2FA(self, user: User) -> dict:
        if user.is_2FA_enabled:
            raise HTTPException(
                status_code=400, detail="This feature has already actived")
        secret_key = pyotp.random_base32()
        user.secret_key = secret_key

        totp = pyotp.TOTP(secret_key)
        uri = totp.provisioning_uri(name=user.email, issuer_name="Jacast")
        self.user_repo.commit_session()

        return {"secret_key": secret_key, "uri": uri}

    def verify_2FA(self, user: User, code: str) -> None:
        if not user.secret_key:
            raise HTTPException(status_code=400, detail="Please enable 2FA")

        totp = pyotp.TOTP(user.secret_key)

        if not totp.verify(code, valid_window=1):
            raise HTTPException(
                status_code=400, detail="Invalid or expired code")

        user.is_2FA_enabled = True
        self.user_repo.commit_session()

    def verify_2FA_login(self, temp_token: str, code: str) -> dict:
        payload = decode_token(temp_token)
        if not payload or payload.type != TokenType.TEMP_2FA:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = self.user_repo.get_user_by_id(int(payload.sub))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        totp = pyotp.TOTP(user.secret_key)
        if not totp.verify(code, valid_window=1):
            raise HTTPException(
                status_code=400, detail="Invalid or expired code")
        return self._create_final_token(user)

    def active_session(self, user: User) -> list[UserSession]:
        return self.user_repo.get_active_sessions(user)

    def delete_session(self, session_id: int, user: User) -> None:
        session = self.user_repo.get_session_by_id(session_id, user)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session.user_id != user.id:
            raise HTTPException(
                status_code=403, detail="You can only delete your own sessions")

        session.is_active = False
        self.user_repo.commit_session()
