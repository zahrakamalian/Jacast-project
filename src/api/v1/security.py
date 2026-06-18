from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
from jose import ExpiredSignatureError, jwt, JWTError
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

from src.schemas.user import TokenPayload
from src.models.user import TokenType
from src.config import settings


if not settings.SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in .env file")

if not settings.ALGORITHM:
    raise RuntimeError("ALGORITHM is not set in .env file")


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)


def verify_password_hash(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def hash_refresh_token(token: str) -> str:
    return bcrypt_context.hash(token)


def verify_refresh_token(token: str, hashed_token: str) -> bool:
    return bcrypt_context.verify(token, hashed_token)


def create_access_token(user_id: int):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": TokenType.ACCESS,
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: int, jti: str):
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id),
               "type": TokenType.REFRESH,
               "jti": jti,
               "iat": now,
               "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
               }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_temp_2fa_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id),
               "type": TokenType.TEMP_2FA,
               "iat": now,
               "exp": now + timedelta(minutes=settings.TEMP_2FA_TOKEN_EXPIRE_MINUTES)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        return TokenPayload(**payload)

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
