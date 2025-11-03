from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import settings as app_settings

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityService:
    """Сервис для работы с JWT и паролями"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширует пароль"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверяет пароль"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        subject: str, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Создаёт JWT токен"""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                hours=app_settings.jwt_settings.expiration_hours
            )
        to_encode = {"sub": subject, "exp": expire, "iat": datetime.now(timezone.utc)}
        encoded_jwt = jwt.encode(
            to_encode,
            app_settings.jwt_settings.secret_key,
            algorithm=app_settings.jwt_settings.algorithm,
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[str]:
        """Декодирует JWT токен и возвращает subject (user_id)"""
        try:
            payload = jwt.decode(
                token,
                app_settings.jwt_settings.secret_key,
                algorithms=[app_settings.jwt_settings.algorithm],
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return user_id
        except JWTError:
            return None


security_service = SecurityService()
