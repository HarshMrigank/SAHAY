from datetime import datetime, timedelta, timezone
from hmac import compare_digest
import base64
import hashlib
import os

from jose import jwt
from jose.exceptions import JWTError

from .config import settings

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return base64.b64encode(salt + digest).decode()


def verify_password(password: str, encoded: str) -> bool:
    raw = base64.b64decode(encoded.encode())
    salt, expected = raw[:16], raw[16:]
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return compare_digest(actual, expected)


def is_admin_password_valid(email: str, password: str) -> bool:
    return compare_digest(email.casefold(), settings.admin_email.casefold()) and compare_digest(
        password, settings.admin_password
    )


def create_access_token(subject: str, role: str, name: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": subject, "role": role, "name": name, "exp": expires_at},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as error:
        raise ValueError("Invalid or expired access token.") from error
