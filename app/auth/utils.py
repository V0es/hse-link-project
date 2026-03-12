from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

password_hasher = PasswordHash.recommended()
settings = get_settings()


def hash_password(password: str) -> str:
    """Hash password

    Args:
        password (str): Plain password

    Returns:
        str: Hashed password
    """
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Password verifying password

    Args:
        plain_password (str): Password to verify
        hashed_password (str): Existing password hash

    Returns:
        bool: If password is verified
    """
    return password_hasher.verify(plain_password, hashed_password)


def encode_jwt(
    payload: dict,
    private_key: str = settings.jwt.private_key_path.read_text(),
    algorithm: str = settings.jwt.algorithm,
    expire_minutes: int = settings.jwt.access_token_expire_minutes,
) -> str:
    """JWT encoding function"""

    to_encode = payload.copy()

    # Add fields `exp` and `iat` to payload
    now = datetime.now(timezone.utc)
    if expire_minutes:
        expire = now + timedelta(minutes=expire_minutes)
        to_encode.update(exp=expire, iat=now)
    else:
        to_encode.update(iat=now)

    token = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return token


def decode_jwt(
    token: str,
    public_key: str = settings.jwt.public_key_path.read_text(),
    algorithm: str = settings.jwt.algorithm,
) -> dict:
    """JWT decoding function"""
    payload = jwt.decode(token, public_key, algorithms=[algorithm])
    return payload
