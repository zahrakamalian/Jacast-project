from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy.orm import Session
from models.user import User, UserSession, PasswordResetToken, EmailVerificationToken, FollowUser
from config import settings


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User:
        user = self.db.query(User).filter(User.email == email).first()
        return user

    def get_session_by_jti(self, jti: str) -> UserSession:
        session = self.db.query(UserSession).filter(
            UserSession.jti == jti).first()
        return session

    def get_user_by_id(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        return user

    def get_reset_token_by_string(self, token: str) -> PasswordResetToken:
        token = self.db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token).first()
        return token

    def get_verification_token(self, token: str) -> EmailVerificationToken:
        verification_token = self.db.query(EmailVerificationToken).filter(
            EmailVerificationToken.token == token).first()
        return verification_token

    def get_session_by_id(self, id: int, user: User) -> UserSession:
        session = self.db.query(UserSession).filter(
            UserSession.user_id == user.id, UserSession.id == id).first()
        return session

    def get_active_sessions(self, user: User) -> list[UserSession]:
        now = datetime.now(timezone.utc)
        session_list = self.db.query(UserSession).filter(
            user.id == UserSession.user_id, UserSession.is_active == True, UserSession.expires_at > now).all()
        return session_list

    def get_active_session_by_user_id(self, user_id: int) -> UserSession:
        return self.db.query(UserSession).filter(UserSession.user_id == user_id, UserSession.is_active == True).order_by(UserSession.created_at.desc()).first()

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_session(self, session_data: UserSession) -> UserSession:
        self.db.add(session_data)
        self.db.commit()
        self.db.refresh(session_data)
        return session_data

    def create_reset_token(self, token: PasswordResetToken) -> PasswordResetToken:
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def create_verification_token(self, token: EmailVerificationToken) -> None:
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)

    def commit_session(self) -> None:
        self.db.commit()

    def delete_old_reset_tokens_by_id(self, user: User) -> None:
        self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id).delete()
        self.db.commit()

    def delete_old_verification_tokens_by_id(self, user: User) -> None:
        self.db.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user.id).delete()
        self.db.commit()

    def delete_verification_token(self, token: EmailVerificationToken) -> None:
        self.db.delete(token)
        self.db.commit()

    def update_user(self, user: User, display_name: Optional[str] = None,
                    bio: Optional[str] = None, is_channel: Optional[bool] = None,
                    avatar_url: Optional[str] = None
                    ) -> User:
        if display_name is not None:
            user.display_name = display_name
        if bio is not None:
            user.bio = bio
        if is_channel is not None:
            user.is_channel = is_channel
        if avatar_url is not None:
            user.avatar_url = avatar_url

        self.db.commit()
        self.db.refresh(user)
        return user

    def get_follow(self, follower_id: int, following_id: int) -> FollowUser:
        return self.db.query(FollowUser).filter(FollowUser.follower_id == follower_id, FollowUser.following_id == following_id).one_or_none()

    def get_followers(self, id: int) -> List[User]:
        return self.db.query(User).join(FollowUser, FollowUser.follower_id == User.id).filter(FollowUser.following_id == id).all()

    def get_following(self, id: int) -> List[User]:
        return self.db.query(User).join(FollowUser, FollowUser.following_id == User.id).filter(FollowUser.follower_id == id).all()

    def follow_user(self, data: FollowUser) -> None:
        self.db.add(data)
        self.db.commit()
        self.db.refresh(data)

    def unfollow_user(self, follow_id: int) -> None:
        self.db.query(FollowUser).filter(FollowUser.id == follow_id).delete()
        self.db.commit()

    def delete_user_avatar_file(self, user: User) -> None:
        if user.avatar_url:
            file_name = user.avatar_url.split('/')[-1]
            file_path = settings.AVATAR_UPLOAD_DIR / file_name
            if file_path.exists():
                file_path.unlink()

    def delete_user_sessions(self, user_id: int) -> None:
        self.db.query(UserSession).filter(
            UserSession.user_id == user_id).delete()
        self.db.commit()

    def delete_user_follows(self, user_id: int) -> None:
        self.db.query(FollowUser).filter(
            FollowUser.follower_id == user_id).delete()
        self.db.query(FollowUser).filter(
            FollowUser.following_id == user_id).delete()
        self.db.commit()

    def delete_user_tokens(self, user_id: int) -> None:
        self.db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id).delete()
        self.db.query(EmailVerificationToken).filter(
            EmailVerificationToken.user_id == user_id).delete()
        self.db.commit()

    def delete_user_permanently(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
